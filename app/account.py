from urllib.parse import urljoin, urlparse

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models import Account, Tournament, TournamentType

bp = Blueprint("account", __name__, template_folder="templates/account")


# TODO; move this
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html", types=TournamentType.query.all())
    else:
        try:
            name = request.form.get("name")
            password = request.form.get("pass")
            ttype = TournamentType.query.get(request.form.get("type"))
            players = (
                request.form.get("players").strip().splitlines()
            )  # TODO; validation
        except Exception:
            # TODO; logging
            flash("Something went wrong!")
            return redirect(url_for("account.signup"))

        if "pass" in players:
            flash("The name 'pass' is reserved!")
            return redirect(url_for("account.signup"))

        user = Account.query.filter_by(name=name).first()
        if user:
            flash("Account name already exists")
            return redirect(url_for("account.signup"))

        new_user = Account(
            name=name,
            password=generate_password_hash(password, method="sha256"),
        )

        db.session.add(new_user)

        tournament = Tournament.create(new_user, ttype, players)

        db.session.commit()

        login_user(new_user)
        # TODO; redirect to their tournament view
        return redirect(url_for("tournament.games", id=tournament.id))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        name = request.form.get("name")
        password = request.form.get("pass")

        user = Account.query.filter_by(name=name).first()
        if not user or not check_password_hash(user.password, password):
            flash("Please check your login details and try again.")
            return redirect(url_for("account.login"))

        login_user(user)

        next = request.args.get("next")
        if not is_safe_url(next):
            return abort(400)

        # TODO; go to your tournament/filter tournament list
        return redirect(next or url_for("tournament.list"))


@bp.route("/manage")
def manage():
    return render_template("welcome.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("tournament.list"))
