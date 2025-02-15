import cv2
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    make_response,
)
from app import db
from app.models.user import User
from app.utils.helpers import hash_password
from app.services.userimage import send_image

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        remember = request.form.get("remember-me") == "on"

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken", "error")
            return redirect(url_for("auth.register"))

        image = send_image()
        _, buffer = cv2.imencode(".jpg", image)
        userimage = buffer.tobytes()

        user = User(
            username=username,
            userimage=userimage,
            password_hash=hash_password(password),
        )
        db.session.add(user)
        db.session.commit()

        session["username"] = username
        if remember:
            response = make_response(redirect(url_for("main.home")))
            response.set_cookie("username", username, max_age=60 * 60 * 24)
            return response
        else:
            return redirect(url_for("main.home"))

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        remember = request.form.get("remember-me") == "on"

        user = User.query.filter_by(username=username).first()
        if user and user.password_hash == hash_password(password):
            session["username"] = username
            if remember:
                response = make_response(redirect(url_for("main.home")))
                response.set_cookie("username", username, max_age=60 * 60 * 24)
                return response
            else:
                return redirect(url_for("main.home"))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for("auth.login"))

    if request.method == "GET" and request.cookies.get("username"):
        session["username"] = request.cookies.get("username")
        return redirect(url_for("main.home"))

    return render_template("login.html")


@bp.route("/logout", methods=["GET"])
def logout():
    session.pop("username", None)
    response = make_response(redirect(url_for("main.index")))
    response.set_cookie("username", "", max_age=0)
    return response
