import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("TRACK_MODIFICATIONS")
