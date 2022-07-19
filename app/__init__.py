from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object("settings")

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "account.login"

    from app.models import Account

    @login_manager.user_loader
    def load_user(user_id):
        return Account.query.get(int(user_id))

    from app import account, commands, tournament

    @app.route("/")
    def welcome():
        return render_template("welcome.html")

    app.register_blueprint(account.bp, url_prefix="/account")
    app.register_blueprint(tournament.bp, url_prefix="/tournament")

    app.register_blueprint(commands.bp)

    return app
