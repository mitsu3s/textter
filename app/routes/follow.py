# app/routes/follow.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.follow import Follow
from app.models.user import User
from app.utils.helpers import (
    get_current_user,
    get_following,
    get_follower,
    get_all_users_base64,
)

bp = Blueprint("follow", __name__)


@bp.route("/follow", methods=["GET", "POST"])
def follow():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        following_username = request.form["following"]
        target_user = User.query.filter_by(username=following_username).first()

        if target_user and target_user != current_user:
            exists = Follow.query.filter_by(
                follower_id=current_user.id, followed_id=target_user.id
            ).first()
            if exists:
                flash("Already following")
            else:
                new_follow = Follow(
                    follower_id=current_user.id, followed_id=target_user.id
                )
                db.session.add(new_follow)
                db.session.commit()
                flash(f"You are now following {target_user.username}", "success")
        else:
            flash("User not found or invalid", "error")

        return redirect(url_for("follow.following"))

    return render_template("textter.html")


@bp.route("/following", methods=["GET"])
def following():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("auth.login"))

    following_list = get_following(current_user.id)
    follower_list = get_follower(current_user.id)
    users_base64 = get_all_users_base64()

    return render_template(
        "following.html",
        users=users_base64,
        following_list=[u.username for u in following_list],
        follower_list=[u.username for u in follower_list],
    )


@bp.route("/delete_following/<string:following_username>")
def delete_following(following_username):
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("auth.login"))

    target_user = User.query.filter_by(username=following_username).first()
    if target_user:
        follow_record = Follow.query.filter_by(
            follower_id=current_user.id, followed_id=target_user.id
        ).first()
        if follow_record:
            db.session.delete(follow_record)
            db.session.commit()
            flash(f"You have unfollowed {target_user.username}", "success")
    return redirect(url_for("follow.following"))


@bp.route("/follower", methods=["GET"])
def follower():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("auth.login"))

    following_list = get_following(current_user.id)
    follower_list = get_follower(current_user.id)
    users_base64 = get_all_users_base64()

    return render_template(
        "follower.html",
        users=users_base64,
        following_list=[u.username for u in following_list],
        follower_list=[u.username for u in follower_list],
    )
