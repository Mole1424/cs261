from functools import wraps
from typing import Callable
from datetime import datetime
from flask import Flask, request, session, abort, jsonify

from server import constants
from data.database import db, User, Sector, Company, Article
import data.interface as dt

USER_ID = "user_id"


def is_logged_in() -> bool:
    """Check if the current user is logged in."""
    return USER_ID in session if constants.USER_DEFAULT is None else True


def get_user() -> User | None:
    """Get the current user who is logged in."""
    if constants.USER_DEFAULT is None:
        return dt.get_user_by_id(session[USER_ID]) if is_logged_in() else None
    else:
        return dt.get_user_by_id(constants.USER_DEFAULT)


def ensure_auth(func: Callable[[User], None]):
    """Wrapper to ensure the user is logged in, else abort with 401. If logged in, call given function
    with the current user."""

    @wraps(func)
    def action():
        if is_logged_in():
            return func(get_user())
        else:
            abort(401)

    return action


def get_form_or_default(property_name: str, default: any) -> any:
    return request.form[property_name] if property_name in request.form else default






def create_endpoints(app: Flask) -> None:
    """Register endpoints to the given application."""

    @app.route("/auth/login", methods=("POST",))
    def auth_login():
        if is_logged_in():
            abort(400)

        email = str(get_form_or_default("email", ""))
        password = str(get_form_or_default("password", ""))
        user = dt.get_user_by_email(email)

        if user is not None and user.validate(password):
            session[USER_ID] = user.id
            return jsonify(user.to_dict()), 200  # HTTP 200 OK

        abort(401)  # HTTP 401 Unauthorised

    @app.route("/auth/logout", methods=("GET", "POST"))
    @ensure_auth
    def auth_logout(_user: User):
        # This should ALWAYS be the case, but just to make sure we don't error
        if USER_ID in session:
            del session[USER_ID]

        return "", 200

    @app.route("/data/sectors", methods=("GET",))
    def get_sectors():
        """Return list of sectors in the database."""
        return jsonify(
            list(
                map(Sector.to_dict, sorted(dt.get_all_sectors(), key=lambda s: s.name))
            )
        )

    @app.route("/user", methods=("GET",))
    @ensure_auth
    def auth_get(user: User):
        """Get the current user."""
        return jsonify(user.to_dict()), 200

    @app.route("/user/delete", methods=("POST",))
    @ensure_auth
    def user_delete(user: User):
        """Delete the user's account."""
        db.session.delete(user)
        db.session.commit()

        del session[USER_ID]
        return "", 200

    @app.route("/user/create", methods=("POST",))
    def user_create():
        """Create a new user. Params: name, email, password."""
        name = str(get_form_or_default("name", "")).strip()
        email = str(get_form_or_default("email", "")).strip()
        password = str(get_form_or_default("password", "")).strip()
        opt_email = str(get_form_or_default("optEmail", "false")) == "true"
        login_after = str(get_form_or_default("loginAfter", "false")) == "true"

        if len(name) == 0:
            return jsonify({"error": True, "message": "A name is required"})

        if len(email) == 0:
            return jsonify({"error": True, "message": "An email is required"})

        if len(password) < 5:
            return jsonify(
                {
                    "error": True,
                    "message": "Password must consist of at least 5 characters",
                }
            )

        # Is the email already registered?
        if dt.get_user_by_email(email) is not None:
            return jsonify(
                {"error": True, "message": "This email is already linked to an account"}
            )

        # Create user
        user = dt.create_user(email, name, password, opt_email)

        # Log the user in?
        if login_after:
            session[USER_ID] = user.id

        return jsonify(
            {"error": False, "user": user.to_dict(), "loggedIn": login_after}
        )

    @app.route("/user/change-name", methods=("POST",))
    @ensure_auth
    def user_change_name(user: User):
        """Change the current user's name."""
        new_name = str(request.form["name"]).strip()

        if len(new_name) == 0:
            return jsonify({"error": True, "message": "A name must be provided"})

        user.update_user(new_name, user.email, user.opt_email)

        return jsonify({"error": False, "user": user.to_dict()})

    @app.route("/user/change-password", methods=("POST",))
    @ensure_auth
    def user_change_password(user: User):
        """Params: password, new_password, repeat_new_password."""
        old_password = str(get_form_or_default("password", "")).strip()
        new_password = str(get_form_or_default("newPassword", "")).strip()
        new_password_repeat = str(get_form_or_default("repeatNewPassword", "")).strip()

        # Check old password is correct
        if not user.validate(old_password):
            return jsonify({"error": True, "message": "Password is incorrect"})

        if len(new_password) == 0:
            return jsonify({"error": True, "message": "New password must be provided"})

        # Check new passwords are equal
        if new_password != new_password_repeat:
            return jsonify({"error": True, "message": "New passwords are not equal"})

        # Check that the passwords are not the same
        if new_password == old_password:
            return jsonify(
                {"error": True, "message": "New password is the same as the old"}
            )

        user.update_password(new_password)
        db.session.commit()

        return jsonify({"error": False})

    @app.route("/user/sectors/get", methods=("GET",))
    @ensure_auth
    def user_get_sectors(user: User):
        """
        Get the sectors the current user is interested in.
        {
          name: string;
          id: number;
        }[]
        """

        return jsonify(
            list(map(Sector.to_dict, sorted(user.get_sectors(), key=lambda s: s.name)))
        )

    @app.route("/user/sectors/add", methods=("POST",))
    @ensure_auth
    def user_add_sector(user: User):
        """
        Accepts: 'id' of sector to add to user's profile. Returns { error: bool, message?: str, sector?: Sector }
        """
        try:
            sector_id = int(request.form["id"])
        except ValueError:
            abort(400)
            return

        new_sector = user.add_sector(sector_id)
        if new_sector:
            return jsonify({"error": False, "message": str(new_sector.name)})

        return jsonify({"error": True, "message": "Error adding sector"})

    @app.route("/user/sectors/remove", methods=("POST",))
    @ensure_auth
    def user_remove_sector(user: User):
        """
        Accepts: 'id' of sector to remove from user's profile
        """
        try:
            sector_id = int(request.form["id"])
        except ValueError:
            abort(400)
            return

        user.remove_sector(sector_id)

        return jsonify({"error": False, "user": user.to_dict()})

    # TODO
    @app.route("/news/recent", methods=("GET",))
    def news_recent():
        """
        Return JSON in the form:
        {
          id: number;
          title: string;
          publisher: string;
          published: string;
          overview: string;
          sentimentScore: number;
          sentimentCategory: "very bad" | "bad" | "neutral" | "good" | "very good";
          url: string;
        }[]
        """

        return jsonify(
            [
                {
                    "id": 1,
                    "title": "Man Eats Apple",
                    "publisher": "BBC",
                    "published": "2020-05-21 12:00",
                    "overview": "Man eats an apple, says it was the best apple he'd ever eaten.",
                    "sentimentScore": 0.9,
                    "url": "https://www.bbc.co.uk",
                    "sentimentCategory": "very good",
                },
                {
                    "id": 2,
                    "title": "CEO Fired After Two Hours",
                    "publisher": "The Guardian",
                    "published": "2023-06-19 14:30",
                    "overview": "CEO so terrible he was fired after just two hours on the job.",
                    "sentimentScore": -0.66,
                    "url": "https://www.theguardian.com/uk",
                    "sentimentCategory": "very bad",
                },
            ]
        )
        # Spoof data
        # abort(501)
    
        # TODO
    @app.route("/user/for_you", methods=("GET",))
    @ensure_auth
    def recommend(user: User):
        """
        Return JSON in the form:
        {
          user_id: number;
          company_id: number;
          distance: number;
        }[]
        """
        user.set_distances()
        recommendations = user.soft_recommend(2)
        return jsonify(
            [recommendation.to_dict() for recommendation in recommendations]
        )
    # Not sure it works since db is empty

    # TODO
    # NOT TESTED AT ALL
    @app.route("/user/follow_company", methods=("POST",))
    @ensure_auth
    def follow_company(user: User):
        """
        Accepts: 'company_id' of company to follow
        """
        try:
            company_id = int(request.form["company_id"])
        except ValueError:
            abort(400)
            return
        user.add_company(company_id)
        return jsonify([{"error": True, "message": "Might have worked"}])

    # TODO
    # NOT TESTED AT ALL
    @app.route("/user/unfollow_company", methods=("POST",))
    @ensure_auth
    def unfollow_company(user: User):
        """
        Accepts: 'company_id' of company to unfollow
        """

        try:
            company_id = int(request.form["company_id"])
        except ValueError:
            abort(400)
            return
        user.remove_company(company_id)
        return jsonify([{"error": True, "message": "Might have worked"}])

    # TOTEST
    @app.route("/data/company_details", methods=("POST",))
    @ensure_auth
    def company_details():
        """
        Accepts: id/name/unique-identifier of company, verbose(true for long output of all info, false for short info)

        Returns {
            error: bool,
            id = integer,
            name = string,
            url = string,
            description = string,
            location = string,
            sector_id = integer,
            market_cap = string,
            ceo = string,
            sentiment = float,
            last_scraped = DateTime/String}
        """
        try:
           company_id = int(request.form['company_id'])
           verbose = bool(request.form['verbose'])
        except ValueError:
           abort(400)
           return
        details = single_company_details(company_id, verbose)
        if details:
           return jsonify(details)
        abort(400)
        return

        
    def single_company_details(company_id: int, verbose: bool):
        details = dt.get_company_by_id(company_id)
        if details:
            if verbose:
                return {              
                    "name": details.name,
                    "url": details.url,
                    "description": details.description,
                    "location": details.location,
                    "market_cap": details.market_cap,
                    "ceo": details.ceo,
                    "sentiment": details.sentiment,
                    "last_scraped": details.last_scraped
                }
            else:
                return {
                        
                    "name": details.name,
                    "market_cap": details.market_cap,
                    "sentiment": details.sentiment
                        }
        else:
            return None





    












    """SPOOF STUFF"""




    def insert_spoofed_data():
        spoofed_companies = [
            {'name': 'Acme Corp', 'url': 'http://www.acme.com', 'description': 'Leading provider of anvils and dynamite', 'location': 'Looneyville, USA', 'market_cap': 1000000000, 'ceo': 'Wile E. Coyote', 'last_scraped': datetime.now()},
            {'name': 'Globex Corporation', 'url': 'http://www.globex.com', 'description': 'Global domination through innovation', 'location': 'Springfield, USA', 'market_cap': 2000000000, 'ceo': 'Hank Scorpio', 'last_scraped': datetime.now()},
            {'name': 'Wonka Industries', 'url': 'http://www.wonka.com', 'description': 'Magical candy and chocolate factory', 'location': 'Fantasyland, USA', 'market_cap': 500000000, 'ceo': 'Willy Wonka', 'last_scraped': datetime.now()},
            {'name': 'Stark Industries', 'url': 'http://www.stark.com', 'description': 'Cutting-edge technology and superhero gadgets', 'location': 'New York City, USA', 'market_cap': 10000000000, 'ceo': 'Tony Stark', 'last_scraped': datetime.now()},
            {'name': 'Umbrella Corporation', 'url': 'http://www.umbrella.com', 'description': 'Innovative bioengineering and pharmaceuticals', 'location': 'Raccoon City, USA', 'market_cap': 800000000, 'ceo': 'Albert Wesker', 'last_scraped': datetime.now()},
            {'name': 'Acme Rockets', 'url': 'http://www.acme-rockets.com', 'description': 'Specializing in explosive propulsion systems', 'location': 'Looneyville, USA', 'market_cap': 50000000, 'ceo': 'Marvin the Martian', 'last_scraped': datetime.now()},
            {'name': 'LexCorp', 'url': 'http://www.lexcorp.com', 'description': 'Advancing technology for a better tomorrow', 'location': 'Metropolis, USA', 'market_cap': 3000000000, 'ceo': 'Lex Luthor', 'last_scraped': datetime.now()},
            {'name': 'Tyrell Corporation', 'url': 'http://www.tyrell.com', 'description': 'Creating artificial lifeforms and advanced robotics', 'location': 'Los Angeles, USA', 'market_cap': 4000000000, 'ceo': 'Eldon Tyrell', 'last_scraped': datetime.now()},
            {'name': 'Wayne Enterprises', 'url': 'http://www.wayneenterprises.com', 'description': 'Building a safer Gotham through innovation', 'location': 'Gotham City, USA', 'market_cap': 6000000000, 'ceo': 'Bruce Wayne', 'last_scraped': datetime.now()},
            {'name': 'Gringotts Wizarding Bank', 'url': 'http://www.gringotts.com', 'description': 'Safeguarding wizarding wealth for centuries', 'location': 'Diagon Alley, UK', 'market_cap': 700000000, 'ceo': 'Griphook', 'last_scraped': datetime.now()},
            {'name': 'Spacely Sprockets', 'url': 'http://www.spacelysprockets.com', 'description': 'Premier manufacturer of sprockets for the space age', 'location': 'Orbit City, USA', 'market_cap': 750000000, 'ceo': 'Cosmo Spacely', 'last_scraped': datetime.now()},
            {'name': 'Monsters, Inc.', 'url': 'http://www.monstersinc.com', 'description': 'World\'s top producer of screams and laughter', 'location': 'Monstropolis, USA', 'market_cap': 850000000, 'ceo': 'James P. Sullivan', 'last_scraped': datetime.now()},
            {'name': 'Oceanic Airlines', 'url': 'http://www.oceanicairlines.com', 'description': 'Flying to destinations unknown', 'location': 'Los Angeles, USA', 'market_cap': 920000000, 'ceo': 'Jacob', 'last_scraped': datetime.now()},
            {'name': 'Wayne Enterprises', 'url': 'http://www.wayneenterprises.com', 'description': 'Building a safer Gotham through innovation', 'location': 'Gotham City, USA', 'market_cap': 6000000000, 'ceo': 'Bruce Wayne', 'last_scraped': datetime.now()},
            {'name': 'Duff Beer', 'url': 'http://www.duffbeer.com', 'description': 'The beer that makes the days fly by', 'location': 'Springfield, USA', 'market_cap': 300000000, 'ceo': 'Duffman', 'last_scraped': datetime.now()}
        ]


        for company_data in spoofed_companies:
            company = Company(name=company_data['name'], url=company_data['url'], description=company_data['description'], location=company_data['location'], market_cap=company_data['market_cap'], ceo=company_data['ceo'], last_scraped=company_data['last_scraped'])
            db.session.add(company)




        spoofed_articles = [
    {
        "url": "https://www.bbc.co.uk",
        "headline": "Man Eats Apple",
        "publisher": "BBC",
        "date": datetime.now(),
        "summary": "Man eats an apple, says it was the best apple he'd ever eaten.",
    },
    {
        "url": "https://www.theguardian.com/uk",
        "headline": "CEO Fired After Two Hours",
        "publisher": "The Guardian",
        "date": datetime.now(),
        "summary": "CEO so terrible he was fired after just two hours on the job.",
    },
    {
        "url": "https://www.nytimes.com/",
        "headline": "New Study Finds Chocolate Consumption Linked to Increased Lifespan",
        "publisher": "New York Times",
        "date": datetime.now(),
        "summary": "A comprehensive study suggests that regular consumption of dark chocolate may lead to a longer and healthier life.",
    },
    {
        "url": "https://www.cnn.com/",
        "headline": "World's Largest Pizza Made in Italy",
        "publisher": "CNN",
        "date": datetime.now(),
        "summary": "Italy breaks the Guinness World Record for the largest pizza ever made, measuring 3 meters in diameter and weighing over 5 tons.",
    },
    {
        "url": "https://www.nationalgeographic.com/",
        "headline": "Scientists Discover New Species of Dancing Frog",
        "publisher": "National Geographic",
        "date": datetime.now(),
        "summary": "A team of biologists has discovered a new species of frog in the Amazon rainforest that performs intricate dance moves during mating rituals.",
    },
    {
        "url": "https://www.bbc.co.uk",
        "headline": "Innovative Solar-Powered Car Unveiled at Auto Show",
        "publisher": "BBC",
        "date": datetime.now(),
        "summary": "A revolutionary new car powered entirely by solar energy is showcased at an international auto show, offering a glimpse into the future of sustainable transportation.",
    },
    {
        "url": "https://www.theguardian.com/uk",
        "headline": "World's Tallest Building Completed in Dubai",
        "publisher": "The Guardian",
        "date": datetime.now(),
        "summary": "Dubai completes construction of the world's tallest building, towering over 1 kilometer high and setting a new record in architectural achievement.",
    },
    {
        "url": "https://www.nytimes.com/",
        "headline": "New Breakthrough in Cancer Treatment Offers Hope to Patients",
        "publisher": "New York Times",
        "date": datetime.now(),
        "summary": "Researchers announce a major breakthrough in cancer treatment, with a new therapy showing promising results in clinical trials and offering hope to millions of patients worldwide.",
    },
    {
        "url": "https://www.cnn.com/",
        "headline": "Ancient Artifact Discovered in Egyptian Pyramid",
        "publisher": "CNN",
        "date": datetime.now(),
        "summary": "Archaeologists uncover a rare ancient artifact buried deep within an Egyptian pyramid, shedding new light on the civilization's rich history and culture.",
    },
    {
        "url": "https://www.nationalgeographic.com/",
        "headline": "World's Largest Coral Reef Discovered in Pacific Ocean",
        "publisher": "National Geographic",
        "date": datetime.now(),
        "summary": "Marine biologists stumble upon the largest coral reef ever recorded in the Pacific Ocean, teeming with diverse marine life and offering new opportunities for scientific research and conservation efforts.",
    },
]
        for data in spoofed_articles:
            article = Article(
                url=data['url'],
                headline=data['headline'],
                publisher=data['publisher'],
                date=data['date'],
                summary=data['summary']
            )
            db.session.add(article)
        db.session.commit()
        return
