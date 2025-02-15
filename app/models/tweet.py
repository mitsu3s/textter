import datetime
import pytz
from app import db


class Tweet(db.Model):
    __tablename__ = "tweets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(280), nullable=False)
    text = db.Column(db.String(280), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime)

    user = db.relationship("User", back_populates="tweets")

    def __repr__(self):
        return f"<Tweet id={self.id} user_id={self.user_id}>"
