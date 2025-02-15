import hashlib
import base64
from flask import session
from app.models.user import User


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_current_user():
    if "username" not in session:
        return None
    return User.query.filter_by(username=session["username"]).first()


def get_following(user_id):
    user = User.query.get(user_id)
    if not user:
        return []
    return [f.followed for f in user.following]


def get_follower(user_id):
    user = User.query.get(user_id)
    if not user:
        return []
    return [f.follower for f in user.followers]


def get_all_users_base64():
    users = User.query.all()
    for u in users:
        if u.userimage:
            u.userimage = base64.b64encode(u.userimage).decode("utf-8")
        else:
            u.userimage = ""
    return users
