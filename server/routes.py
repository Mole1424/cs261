from functools import wraps
from typing import Callable
from flask import Flask, request, session, abort, jsonify
from collections import Counter

from server import constants
from data.database import db, User, Sector, Company, UserCompany, Article, UserNotification, Notification
import data.interface as interface
from data.database import db, User, Sector

USER_ID = "user_id"


def is_logged_in() -> bool:
    """Check if the current user is logged in."""
    return USER_ID in session and session[USER_ID] is not None if constants.USER_DEFAULT is None else True


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


def get_form_or_default(property_name: str, default: any, action: Callable[[str], any] = None) -> any:
    if value := request.form.get(property_name):
        return action(value) if action else value
    else:
        return default


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
        print("AUTH_GET")
        print(user)
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
        """Accepts: 'id' of sector to remove from user's profile."""
        try:
            sector_id = int(request.form["id"])
        except ValueError:
            abort(400)
            return

        user.remove_sector(sector_id)

        return jsonify({"error": False, "user": user.to_dict()})

    @app.route('/user/notification-stats', methods=("GET",))
    @ensure_auth
    def user_notification_stats(user: User):
        """Get notification statistics."""
        return jsonify({
            "total": len(user.notifications),
            "unread": len(list(filter(lambda un: not un.read, user.notifications)))
        })
    
    @app.route('/user/notifications', methods=("GET",))
    @ensure_auth
    def user_get_notifications(user: User):
        """Get all notifications linked to this user."""
        return jsonify(list(map(UserNotification.to_dict, user.notifications)))

    @app.route('/notification/get', methods=("POST",))
    @ensure_auth
    def notification_get(user: User):
        """Get notification `id`."""
        try:
            notification_id = int(request.form['id'])
        except (ValueError, KeyError):
            abort(400)
            return

        user_notification = UserNotification.get(notification_id, user.id)

        if not user_notification:
            return jsonify({
                "error": True,
                "message": "Cannot find notification"
            })

        return jsonify({
            "error": False,
            "data": user_notification.to_dict()
        })

    @app.route('/notification/mark-as-read', methods=("POST",))
    @ensure_auth
    def mark_notification_as_read(user: User):
        """Mark notification `id` as read."""
        try:
            notification_id = int(request.form['id'])
        except (ValueError, KeyError):
            abort(400)
            return

        user_notification = UserNotification.get(notification_id, user.id)

        if not user_notification:
            return jsonify({
                "error": True,
                "message": "Cannot find notification"
            })

        user_notification.read = True
        db.session.commit()

        return jsonify({
            "error": False,
            "data": user_notification.to_dict()
        })

    @app.route('/notification/read-all', methods=("POST",))
    @ensure_auth
    def notification_mark_all_as_read(user: User):
        """Mark all notifications as read."""
        for notification in user.notifications:
            notification.read = True

        db.session.commit()

        return "", 200

    @app.route('/company/following', methods=("POST",))
    @ensure_auth
    def followed_companies(user: User):
        """
        Accepts string with "sort_by" on how to sort:
        "marketCapAsc"
        "marketCapDesc"
        "sentimentAsc"
        "sentimentDesc"
        defaults to alphabetical if not specified.

        Returns list of companies and details.
        """

        sort_by = request.form.get('sort_by')
        companies = [obj for _, obj in interface.get_followed_companies(user.id)]

        if sort_by == "marketCapAsc":
            companies.sort(key=lambda x: x['marketCap'])
        elif sort_by == "marketCapDesc":
            companies.sort(key=lambda x: x['marketCap'], reverse=True)
        elif sort_by == "sentimentAsc":
            companies.sort(key=lambda x: x['sentiment'])
        elif sort_by == "sentimentDesc":
            companies.sort(key=lambda x: x['sentiment'], reverse=True)
        else:
            companies.sort(key=lambda x: x['name'])

        return jsonify(companies)

    @app.route("/news/article", methods=("POST",))
    def new_article():
        """Get details of a news article. Accepts `id` of article."""
        try:
            article_id = int(request.form['id'])
        except (ValueError, KeyError):
            abort(400)
            return

        article = interface.article_by_id(article_id)

        return jsonify({
               'error': True,
               'articleId': article_id
           } if article is None else {
                'error': False,
                'data': article.to_dict()
            })

    @app.route("/news/recent", methods=("GET",))
    def news_recent():
        """Defaults to 10 most recent articles"""
        return jsonify(list(map(Article.to_dict, interface.recent_articles())))

    @app.route("/user/for-you", methods=("POST",))
    @ensure_auth
    def recommend(user: User):
        """
        Accepts argument `count`.
        Return JSON in the form:
        {
          userId: number;
          companyId: number;
          distance: number;
          company: Company;
        }[]
        """

        def to_dict(uc: UserCompany) -> dict:
            return {
                **uc.to_dict(),
                'company': interface.get_company_details_by_id(uc.company_id, user.id)[1]
            }
        
        def to_dict2(company_id: int) -> dict:
            return {
                'companyId': int(company_id),
                'company': interface.get_company_details_by_id(int(company_id), user.id)[1]
            }

        try:
            count = int(request.form['count'])
        except (ValueError, KeyError):
            count = 5
        if user.hard_ready >= 0:
            user.hard_train()
            recommendations = user.hard_recommend(count)
            for i in range(len(recommendations)):
                if (int(recommendations[i]) == 0):
                    recommendations = recommendations[:i]
                    break
            if len(recommendations) != 0:
                return jsonify(list(map(to_dict2, recommendations)))
        user.set_distances()
        recommendations = user.soft_recommend(count)
        return jsonify(list(map(to_dict, recommendations)))

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

    @app.route("/company/details", methods=("POST",))
    @ensure_auth
    def get_company_details(user: User):
        """
        Accepts: id/name/unique-identifier of company. Also, 'loadStock' flag.
        """
        try:
            company_id = int(request.form['id'])
        except ValueError:
            abort(400)
            return

        load_stock = get_form_or_default("loadStock", "false") == "true"
        company, company_details = interface.get_company_details_by_id(company_id, user.id, load_stock)

        if not company:
            return jsonify({
                "error": True,
                "message": f"Cannot find company with id #{company_id}"
            })

        return jsonify({
            "error": False,
            "data": company_details
        })

    @app.route('/company/popular', methods=("POST",))
    @ensure_auth
    def get_popular_companies(user: User):
        """Return top `count` popular companies."""

        try:
            max_count = int(request.form['count'])
        except (ValueError, KeyError):
            max_count = 10

        company_ids = [user_company.company_id for user_company in db.session.query(UserCompany).all()]
        most_common_companies = [elem for elem, _ in Counter(company_ids).most_common(max_count)]
        popular = [interface.get_company_details_by_id(company_id, user.id)[1] for company_id in most_common_companies]
        return jsonify(popular)

    @app.route('/company/stock', methods=("POST",))
    @ensure_auth
    def get_company_stock(user: User):
        # TODO
        pass

    @app.route('/company/search', methods=("POST",))
    @ensure_auth
    def company_search(user: User):
        """Search companies."""
        print(request.form)

        # ceo?: string
        ceo: str | None = get_form_or_default('ceo', None)

        # companyName?: string
        company_name: str | None = get_form_or_default('name', None)

        # sectors: int[]. List of sector IDs.
        sectors: list[int] | None = request.form.getlist('sectors[]')
        if sectors is not None:
            try:
                sectors = list(map(int, sectors))
            except ValueError:
                sectors = None

        # sentimentRange: [float, float]. [lower, upper) range.
        sentiment_range: list[float] | None = request.form.getlist('sentimentRange[]')
        if sentiment_range is not None:
            if len(sentiment_range) == 2:
                try:
                    sentiment_range = list(map(float, sentiment_range))
                except ValueError:
                    sentiment_range = None
            else:
                sentiment_range = None

        # marketCapRange: [float, float]. [lower, upper) range.
        market_cap_range: list[float] | None = request.form.getlist('marketCapRange[]')
        if market_cap_range is not None:
            if len(market_cap_range) == 2:
                try:
                    market_cap_range = list(map(float, market_cap_range))
                except ValueError:
                    market_cap_range = None
            else:
                market_cap_range = None

        # stockPriceRange: [float, float]. [lower, upper) range.
        stock_price_range: list[float] | None = request.form.getlist('stockPriceRange[]')
        if stock_price_range is not None:
            if len(stock_price_range) == 2:
                try:
                    stock_price_range = list(map(float, stock_price_range))
                except ValueError:
                    stock_price_range = None
            else:
                stock_price_range = None

        companies = interface.search_companies(
            ceo=ceo,
            name=company_name,
            sectors=sectors,
            sentiment=sentiment_range,
            market_cap=market_cap_range,
            stock_price=stock_price_range,
            user_id=user.id
        )

        return jsonify(list(map(lambda c: interface.get_company_details(c, user.id), companies)))
