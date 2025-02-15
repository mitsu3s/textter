import datetime
from app import db


class Follow(db.Model):
    __tablename__ = "follows"

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime)

    follower = db.relationship(
        "User", foreign_keys=[follower_id], back_populates="following"
    )
    followed = db.relationship(
        "User", foreign_keys=[followed_id], back_populates="followers"
    )

    def __repr__(self):
        return f"<Follow follower={self.follower_id} -> followed={self.followed_id}>"
