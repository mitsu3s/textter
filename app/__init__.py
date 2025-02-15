import os
import secrets
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.routes import main

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    app.secret_key = secrets.token_bytes(16)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import auth, main, tweet, follow

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(tweet.bp)
    app.register_blueprint(follow.bp)

    return app
