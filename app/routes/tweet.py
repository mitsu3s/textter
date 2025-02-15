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

bp = Blueprint("tweet", __name__)


@bp.route("/tweet", methods=["GET", "POST"])
def tweet():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        title = request.form["title"]
        tweet_text = request.form["tweet"]
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
    else:
        following_list = get_following(current_user.id)
        follower_list = get_follower(current_user.id)
        users_base64 = get_all_users_base64()

        return render_template(
            "tweet.html",
            following_list=[u.username for u in following_list],
            follower_list=[u.username for u in follower_list],
            users=users_base64,
        )


@bp.route("/delete/<int:tweet_id>")
def delete_tweet(tweet_id):
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("auth.login"))

    tweet = Tweet.query.get(tweet_id)
    if tweet and tweet.user_id == current_user.id:
        db.session.delete(tweet)
        db.session.commit()

    return redirect(url_for("main.home"))
