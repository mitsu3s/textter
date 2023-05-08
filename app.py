from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import datetime
import pytz
import hashlib
import secrets
import cv2
import base64
from userimage import send_image


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///textter.db"
app.secret_key = secrets.token_bytes(16)
db = SQLAlchemy(app)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    userimage = db.Column(db.LargeBinary)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return "<User %r>" % self.username


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(280), nullable=False)
    text = db.Column(db.String(280), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return "<Tweet %r>" % self.username


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    following = db.Column(db.String(255))

    def __repr__(self):
        return "<Follow %r>" % self.username


class Follower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    follower = db.Column(db.String(255))

    def __repr__(self):
        return "<Follower %r>" % self.username


def get_following():
    following = Follow.query.filter_by(username=session["username"]).first()
    if following:
        following_list = following.following.split(",")
    else:
        following_list = []
    return following_list


def get_follower():
    follower = Follower.query.filter_by(username=session["username"]).first()
    if follower:
        follower_list = follower.follower.split(",")
    else:
        follower_list = []
    return follower_list


def get_user():
    users = User.query.all()
    for user in users:
        user.userimage = base64.b64encode(user.userimage).decode("utf-8")
    return users


@app.route("/", methods=["GET"])
def index():
    return render_template("home.html")


@app.route("/follow", methods=["GET", "POST"])
def follow():
    if request.method == "POST":
        following = request.form["following"]
        user = Follow.query.filter_by(username=session["username"]).first()
        new_follower = User.query.filter_by(username=following).first()

        if new_follower and not following == session["username"]:
            if user:
                following_list = user.following.split(",")
                if following not in following_list:
                    user.following += "," + following
                    db.session.commit()
                else:
                    flash("Already following")
                    return redirect(url_for("home"))
            else:
                follow = Follow(username=session["username"], following=following)
                db.session.add(follow)
                db.session.commit()
            follower = Follower.query.filter_by(username=following).first()
            if follower:
                follower.follower += "," + session["username"]
                db.session.commit()
            else:
                new_follower = Follower(
                    username=following, follower=session["username"]
                )
                db.session.add(new_follower)
                db.session.commit()
        else:
            flash("Not Found User")
        return redirect(url_for("following"))
    return render_template("textter.html")


@app.route("/unfollow", methods=["GET", "POST"])
def unfollow():
    if request.method == "POST":
        unfollowing = request.form["unfollowing"]
        user = Follow.query.filter_by(username=session["username"]).first()

        if user:
            following_list = user.following.split(",")
            if unfollowing in following_list:
                following_list.remove(unfollowing)
                following_list = [i for i in following_list if i]
                if len(following_list) > 0:
                    user.following = ",".join(following_list)
                else:
                    db.session.delete(user)
                follower = Follower.query.filter_by(username=unfollowing).first()
                if follower:
                    follower_list = follower.follower.split(",")
                    follower_list.remove(session["username"])
                    follower_list = [i for i in follower_list if i]
                    if len(follower_list) > 0:
                        follower.follower = ",".join(follower_list)
                    else:
                        db.session.delete(follower)
                    db.session.commit()
                return redirect(url_for("home"))
            else:
                flash("Not Found Unfollow User")
        else:
            flash("No one is following you")
        return redirect(url_for("home"))
    return render_template("textter.html")


@app.route("/home", methods=["GET", "POST"])
def home():
    if "username" not in session:
        return redirect("/login")
    if request.method == "POST":
        tweet = request.form["tweet"]
        title = request.form["title"]
        tweet = Tweet(username=session["username"], text=tweet, title=title)
        db.session.add(tweet)
        db.session.commit()

    tweet_list = []
    tweet_list.append(session["username"])

    following = Follow.query.filter_by(username=session["username"]).first()
    if following:
        following_list = following.following.split(",")
        if following_list:
            tweet_list.extend(following_list)
    else:
        following_list = []
    follower_list = Follower.query.filter_by(username=session["username"]).first()
    if follower_list:
        follower_list = follower_list.follower.split(",")
    else:
        follower_list = []

    tweets = (
        Tweet.query.filter(Tweet.username.in_(tweet_list))
        .order_by(Tweet.created_at.desc())
        .all()
    )
    users = User.query.all()
    for user in users:
        user.userimage = base64.b64encode(user.userimage).decode("utf-8")

    return render_template(
        "textter.html",
        tweets=tweets,
        users=users,
        following_list=following_list,
        follower_list=follower_list,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            userimage = cv2.imencode(".jpg", send_image())[1].tobytes()
            password_hash = hash_password(password)
            user = User(username=username, userimage=userimage, password=password_hash)
            db.session.add(user)
            db.session.commit()
            session["username"] = username

            return redirect(url_for("home"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_hash = hash_password(password)
        user = User.query.filter_by(username=username).first()
        if user:
            if password_hash == user.password:
                session["username"] = username
                return redirect("/home")
            else:
                return redirect("/")
        else:
            return redirect("/")
    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("username", None)
    return redirect("/")


@app.route("/tweet", methods=["GET", "POST"])
def tweet():
    if request.method == "POST":
        if "username" not in session:
            return redirect("/login")
        tweet = request.form["tweet"]
        title = request.form["title"]
        jst = pytz.timezone("Asia/Tokyo")
        tweet = Tweet(
            username=session["username"],
            title=title,
            text=tweet,
            created_at=datetime.datetime.now(jst),
        )
        db.session.add(tweet)
        db.session.commit()
        return redirect("/home")
    else:
        following_list = get_following()
        follower_list = get_follower()
        users = get_user()
    return render_template(
        "tweet.html",
        following_list=following_list,
        follower_list=follower_list,
        users=users,
    )


@app.route("/delete_tweet/<tweet_id>")
def delete_tweet(tweet_id):
    tweet = Tweet.query.get(tweet_id)
    db.session.delete(tweet)
    db.session.commit()
    flash("Tweet deleted successfully")
    return redirect(url_for("home"))


@app.route("/following", methods=["GET"])
def following():
    if request.method == "GET":
        if "username" not in session:
            return redirect("/login")
        following_list = get_following()
        follower_list = get_follower()
        users = get_user()

        return render_template(
            "following.html",
            users=users,
            following_list=following_list,
            follower_list=follower_list,
        )
    else:
        return redirect("/")


@app.route("/delete_following/<following_id>")
def delete_following(following_id):
    if request.method == "GET":
        if "username" not in session:
            return redirect("/login")
        following = Follow.query.filter_by(username=session["username"]).first()

        following_list = following.following.split(",")
        following_list.remove(following_id)
        following_list = [i for i in following_list if i]

        if len(following_list) > 0:
            following.following = ",".join(following_list)
        else:
            db.session.delete(following)

        follower = Follower.query.filter_by(username=following_id).first()

        follower_list = follower.follower.split(",")
        follower_list.remove(session["username"])
        follower_list = [i for i in follower_list if i]
        if len(follower_list) > 0:
            follower.follower = ",".join(follower_list)
        else:
            db.session.delete(follower)
        db.session.commit()

        return redirect(url_for("home"))
    else:
        return redirect("/")


@app.route("/follower", methods=["GET"])
def follower():
    if request.method == "GET":
        if "username" not in session:
            return redirect("/login")
        following_list = get_following()
        follower_list = get_follower()
        users = get_user()

        return render_template(
            "follower.html",
            users=users,
            following_list=following_list,
            follower_list=follower_list,
        )
    else:
        return redirect("/")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
