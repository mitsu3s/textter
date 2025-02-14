import datetime
import pytz
import hashlib
import secrets
import cv2
import base64

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash,
    make_response,
    get_flashed_messages,
)
from flask_sqlalchemy import SQLAlchemy
from userimage import send_image

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///textter.db"
app.secret_key = secrets.token_bytes(16)
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    userimage = db.Column(db.LargeBinary)
    password_hash = db.Column(db.String(64), nullable=False)

    tweets = db.relationship("Tweet", back_populates="user", cascade="all, delete-orphan", lazy=True)

    following = db.relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
        lazy=True
    )

    followers = db.relationship(
        "Follow",
        foreign_keys="Follow.followed_id",
        back_populates="followed",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<User {self.username}>"


class Tweet(db.Model):
    __tablename__ = "tweets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(280), nullable=False)
    text = db.Column(db.String(280), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship("User", back_populates="tweets")

    def __repr__(self):
        return f"<Tweet id={self.id} user_id={self.user_id}>"


class Follow(db.Model):
    __tablename__ = "follows"

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    follower = db.relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed = db.relationship("User", foreign_keys=[followed_id], back_populates="followers")

    def __repr__(self):
        return f"<Follow follower={self.follower_id} -> followed={self.followed_id}>"


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


@app.route("/", methods=["GET"])
def index():
    session.pop('_flashes', None)
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        remember = request.form.get("remember-me") == "on"

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken", "error")
            return redirect(url_for("register"))

        userimage = cv2.imencode(".jpg", send_image())[1].tobytes()

        user = User(
            username=username,
            userimage=userimage,
            password_hash=hash_password(password)
        )
        db.session.add(user)
        db.session.commit()

        session["username"] = username
        if remember:
            response = make_response(redirect(url_for("home")))
            response.set_cookie("username", username, max_age=60 * 60 * 24)
            return response
        else:
            return redirect(url_for("home"))
        
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        remember = request.form.get("remember-me") == "on"

        user = User.query.filter_by(username=username).first()
        if user and user.password_hash == hash_password(password):
            session["username"] = username
            if remember:
                response = make_response(redirect(url_for("home")))
                response.set_cookie("username", username, max_age=60 * 60 * 24)
                return response
            else:
                return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))

    if request.method == "GET" and request.cookies.get("username"):
        session["username"] = request.cookies.get("username")
        return redirect(url_for("home"))
    
    return render_template("login.html")


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("username", None)
    response = make_response(redirect("/"))
    response.set_cookie("username", "", max_age=0)
    return response


@app.route("/home", methods=["GET", "POST"])
def home():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("login"))

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
        return redirect(url_for("home"))

    following_users = get_following(current_user.id)
    follower_users = get_follower(current_user.id)

    user_ids = [current_user.id] + [u.id for u in following_users]
    tweets = (
        Tweet.query
        .filter(Tweet.user_id.in_(user_ids))
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


@app.route("/tweet", methods=["GET", "POST"])
def tweet():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("login"))

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
        return redirect(url_for("home"))
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


@app.route("/delete_tweet/<int:tweet_id>")
def delete_tweet(tweet_id):
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("login"))

    tweet = Tweet.query.get(tweet_id)
    if tweet and tweet.user_id == current_user.id:
        db.session.delete(tweet)
        db.session.commit()
        flash("Tweet deleted successfully")
    else:
        flash("Tweet not found or not authorized")

    return redirect(url_for("home"))


@app.route("/follow", methods=["GET", "POST"])
def follow():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("login"))

    if request.method == "POST":
        following_username = request.form["following"]
        target_user = User.query.filter_by(username=following_username).first()

        if target_user and target_user != current_user:
            exists = Follow.query.filter_by(
                follower_id=current_user.id,
                followed_id=target_user.id
            ).first()
            if exists:
                flash("Already following")
            else:
                new_follow = Follow(
                    follower_id=current_user.id,
                    followed_id=target_user.id
                )
                db.session.add(new_follow)
                db.session.commit()
                flash(f"You are now following {target_user.username}")
        else:
            flash("User not found or invalid")

        return redirect(url_for("following"))

    return render_template("textter.html")


@app.route("/following", methods=["GET"])
def following():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("login"))

    following_list = get_following(current_user.id)
    follower_list = get_follower(current_user.id)
    users_base64 = get_all_users_base64()

    return render_template(
        "following.html",
        users=users_base64,
        following_list=[u.username for u in following_list],
        follower_list=[u.username for u in follower_list],
    )


@app.route("/delete_following/<string:following_username>")
def delete_following(following_username):
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("login"))

    target_user = User.query.filter_by(username=following_username).first()
    if target_user:
        follow_record = Follow.query.filter_by(
            follower_id=current_user.id,
            followed_id=target_user.id
        ).first()
        if follow_record:
            db.session.delete(follow_record)
            db.session.commit()
            flash(f"You have unfollowed {target_user.username}")
    return redirect(url_for("following"))


@app.route("/follower", methods=["GET"])
def follower():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("login"))

    following_list = get_following(current_user.id)
    follower_list = get_follower(current_user.id)
    users_base64 = get_all_users_base64()

    return render_template(
        "follower.html",
        users=users_base64,
        following_list=[u.username for u in following_list],
        follower_list=[u.username for u in follower_list],
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # app.run()
    app.run(debug=True)
