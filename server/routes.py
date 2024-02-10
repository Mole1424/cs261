from functools import wraps
from typing import Callable

from flask import Flask, request, session, abort, jsonify

from server import constants
from data.database import db, User, Sector

USER_ID = "user_id"


def is_logged_in() -> bool:
    """Check if the current user is logged in."""
    return USER_ID in session if constants.USER_DEFAULT is None else True


def get_user() -> User | None:
    """Get the current user who is logged in."""
    if constants.USER_DEFAULT is None:
        return User.get_by_id(session[USER_ID]) if is_logged_in() else None
    else:
        return User.get_by_id(constants.USER_DEFAULT)


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
        user = User.get_by_email(email)

        if user is not None and user.validate(password):
            session[USER_ID] = user.id
            return jsonify(user.to_dict()), 200  # HTTP 200 OK

        abort(401)  # HTTP 401 Unauthorised

    @app.route('/auth/logout', methods=("GET", "POST"))
    @ensure_auth
    def auth_logout(_user: User):
        # This should ALWAYS be the case, but just to make sure we don't error
        if USER_ID in session:
            del session[USER_ID]

        return "", 200

    @app.route('/user', methods=("GET",))
    @ensure_auth
    def auth_get(user: User):
        """Get the current user."""
        return jsonify(user.to_dict()), 200

    @app.route('/user/delete', methods=("POST",))
    @ensure_auth
    def user_delete(user: User):
        """Delete the user's account."""
        abort(501)
        # del session[USER_ID]

    @app.route('/user/change-name', methods=("POST",))
    @ensure_auth
    def user_change_name(user: User):
        """Change the current user's name."""
        new_name = str(request.form['name']).strip()

        if len(new_name) == 0:
            return jsonify({
                "error": True,
                "message": "A name must be provided"
            })

        user.update_name(new_name)

        return jsonify({
            "error": False,
            "user": user.to_dict()
        })

    @app.route('/user/change-password', methods=("POST",))
    @ensure_auth
    def user_change_password(user: User):
        """Params: password, new_password, repeat_new_password."""
        old_password = str(get_form_or_default("password", "")).strip()
        new_password = str(get_form_or_default("newPassword", "")).strip()
        new_password_repeat = str(get_form_or_default("repeatNewPassword", "")).strip()

        # Check old password is correct
        if not user.validate(old_password):
            return jsonify({
                "error": True,
                "message": "Password is incorrect"
            })

        if len(new_password) == 0:
            return jsonify({
                "error": True,
                "message": "New password must be provided"
            })

        # Check new passwords are equal
        if new_password != new_password_repeat:
            return jsonify({
                "error": True,
                "message": "New passwords are not equal"
            })

        # Check that the passwords are not the same
        if new_password == old_password:
            return jsonify({
                "error": True,
                "message": "New password is the same as the old"
            })

        # TODO
        user.update_password(new_password)
        return jsonify({
            "error": False
        })

    @app.route('/user/sectors/get', methods=("GET",))
    @ensure_auth
    def user_get_sectors(user: User):
        """
        Get the sectors the current user is interested in.
        {
          name: string;
          id: number;
        }[]
        """

        return jsonify(list(map(Sector.to_dict, user.get_sectors())))

    @app.route('/user/sectors/add', methods=("POST",))
    @ensure_auth
    def user_add_sector(user: User):
        """
        Accepts: 'id' of sector to add to user's profile. Returns { error: bool, message?: str, sector?: Sector }
        """
        abort(501)

    @app.route('/user/sectors/remove', methods=("POST",))
    @ensure_auth
    def user_remove_sector(user: User):
        """
        Accepts: 'id' of sector to remove from user's profile
        """
        try:
            sector_id = int(request.form['id'])
        except ValueError:
            abort(400)
            return

        user.remove_sector(sector_id)

        return jsonify({
            "error": False,
            "user": user.to_dict()
        })

    @app.route('/news/recent', methods=("GET",))
    @ensure_auth
    def news_recent(_user: User):
        """
        Return JSON in the form:
        {
          title: string;
          publisher: string;
          published: string;
          overview: string;
          sentimentScore: number;
          url: string;
        }[]
        """
        abort(501)
