import os


class Config:
    DATABASE_URI = os.environ.get("DATABASE_URI")
    TRACK_MODIFICATIONS = os.environ.get("TRACK_MODIFICATIONS")
