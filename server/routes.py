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


def create_endpoints(app: Flask) -> None:
    """Register endpoints to the given application."""

    @app.route('/auth/login', methods=("POST",))
    def auth_login():
        email = str(request.form['email'])
        password = str(request.form['password'])
        user = db.User.get_by_email(email)

        # Does the user exist, and is the password correct?
        if user is not None and user.validate(password):
            session[USER_ID] = user.id
            return "OK", 200  # HTTP 200 OK

        abort(401)  # HTTP 401 Unauthorised

    @app.route('/auth/check', methods=("GET", "POST"))
    def auth_check():
        """DEBUG: check if logged in."""
        if is_logged_in():
            return "OK", 200
        else:
            abort(401)

    @app.route('/auth/get', methods=("GET", "POST"))
    @ensure_auth
    def auth_get(user: User):
        """Get the current user."""
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "opt_email": user.opt_email
        }), 200

    @app.route('/auth/logout', methods=("GET", "POST"))
    @ensure_auth
    def auth_logout(_user: User):
        del session[USER_ID]