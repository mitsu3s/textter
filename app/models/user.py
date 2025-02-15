from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    userimage = db.Column(db.LargeBinary)
    password_hash = db.Column(db.String(64), nullable=False)

    tweets = db.relationship(
        "Tweet", back_populates="user", cascade="all, delete-orphan", lazy=True
    )
    following = db.relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
        lazy=True,
    )
    followers = db.relationship(
        "Follow",
        foreign_keys="Follow.followed_id",
        back_populates="followed",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self):
        return f"<User {self.username}>"
