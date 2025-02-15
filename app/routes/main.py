import datetime
import pytz
from flask import Blueprint, render_template, request, redirect, url_for, session
from app import db
from app.models.tweet import Tweet
from app.utils.helpers import (
    get_current_user,
    get_following,
    get_follower,
    get_all_users_base64,
)

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET"])
def index():
    session.pop("_flashes", None)
    return render_template("home.html")


@bp.route("/home", methods=["GET", "POST"])
def home():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        tweet_text = request.form["tweet"]
        title = request.form["title"]
        jst = pytz.timezone("Asia/Tokyo")
        new_tweet = Tweet(
            user_id=current_user.id,
            title=title,
            text=tweet_text,
            created_at=datetime.datetime.now(jst),
        )
        db.session.add(new_tweet)
        db.session.commit()
        return redirect(url_for("main.home"))

    following_users = get_following(current_user.id)
    follower_users = get_follower(current_user.id)
    user_ids = [current_user.id] + [u.id for u in following_users]
    tweets = (
        Tweet.query.filter(Tweet.user_id.in_(user_ids))
        .order_by(Tweet.created_at.desc())
        .all()
    )
    users_base64 = get_all_users_base64()

    return render_template(
        "textter.html",
        tweets=tweets,
        users=users_base64,
        following_list=[u.username for u in following_users],
        follower_list=[u.username for u in follower_users],
    )
