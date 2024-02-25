from functools import wraps
from typing import Callable
from flask import Flask, request, session, abort, jsonify

from server import constants
from data.database import db, User, Sector, Company, UserCompany
import data.interface as interface
from data.database import db, User, Sector, Company, Article

USER_ID = "user_id"


def is_logged_in() -> bool:
    """Check if the current user is logged in."""
    return USER_ID in session if constants.USER_DEFAULT is None else True


def get_user() -> User | None:
    """Get the current user who is logged in."""
    if constants.USER_DEFAULT is None:
        return interface.get_user_by_id(session[USER_ID]) if is_logged_in() else None
    else:
        return interface.get_user_by_id(constants.USER_DEFAULT)


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
        user = interface.get_user_by_email(email)

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
                map(Sector.to_dict, sorted(interface.get_all_sectors(), key=lambda s: s.name))
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
        if interface.get_user_by_email(email) is not None:
            return jsonify(
                {"error": True, "message": "This email is already linked to an account"}
            )

        # Create user
        user = interface.create_user(email, name, password, opt_email)

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

    @app.route('/user/following', methods=("GET",))
    @ensure_auth
    def user_get_following(user: User):
        """Return list of companies the current user is following."""
        return map(lambda uc: uc.company, filter(UserCompany.is_following, UserCompany.get_by_user(user.id)))

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
          sentimentCategory: string
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
                    "sentimentCategory": "Very Positive",
                },
                {
                    "id": 2,
                    "title": "CEO Fired After Two Hours",
                    "publisher": "The Guardian",
                    "published": "2023-06-19 14:30",
                    "overview": "CEO so terrible he was fired after just two hours on the job.",
                    "sentimentScore": -0.66,
                    "url": "https://www.theguardian.com/uk",
                    "sentimentCategory": "Very Negative",
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
        return jsonify(list(map(UserCompany.to_dict, recommendations)))
    # Not sure if it works since db is empty

    # TODO
    # NOT TESTED AT ALL
    @app.route("/company/follow", methods=("POST",))
    @ensure_auth
    def follow_company(user: User):
        """Accepts: 'id' of company to follow."""
        try:
            company_id = int(request.form["id"])
        except ValueError:
            abort(400)
            return

        user.add_company(company_id)

        return "", 200

    # TODO
    # NOT TESTED AT ALL
    @app.route("/company/unfollow", methods=("POST",))
    @ensure_auth
    def unfollow_company(user: User):
        """Accepts: 'id' of company to unfollow."""
        try:
            company_id = int(request.form["id"])
        except ValueError:
            abort(400)
            return

        user.remove_company(company_id)

        return "", 200

    # TODO
    @app.route("/company/details", methods=("POST",))
    @ensure_auth
    def get_company_details(user: User):
        """
        Accepts: id/name/unique-identifier of company.
        """
        try:
            company_id = int(request.form['id'])
        except ValueError:
            abort(400)
            return

        company, company_details = interface.get_company_details(company_id, user.id)

        if not company:
            return jsonify({
                "error": True,
                "message": f"Cannot find company with id #{company_id}"
            })

        return jsonify({
            "error": False,
            "data": company_details
        })

    @app.route('/company/popular', methods=("GET",))
    @ensure_auth
    def get_popular_companies(user: User):
        """Return popular companies."""
        # TODO actually make this return popular companies
        return jsonify(list(map(lambda c: interface.get_company_details(c.id, user.id)[1], db.session.query(Company).all())))
