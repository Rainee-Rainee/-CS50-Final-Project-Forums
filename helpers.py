from flask import redirect, session
from functools import wraps

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Redirects the user to index if they aren't logged in.
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return wrapper