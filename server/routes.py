from functools import wraps
from typing import Callable

from flask import Flask, request, session, abort, jsonify

from server import constants
from server.database import db, User


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

    @app.route('/auth/login', methods=("POST",))
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

    @app.route('/auth/get', methods=("GET", "POST"))
    @ensure_auth
    def auth_get(user: User):
        """Get the current user."""
        return jsonify(user.to_dict()), 200

    @app.route('/auth/logout', methods=("GET", "POST"))
    @ensure_auth
    def auth_logout(_user: User):
        # This should ALWAYS be the case, but just to make sure we don't error
        if USER_ID in session:
            del session[USER_ID]

        return "", 200
