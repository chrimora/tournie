from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import case, func

from app import db
from app.models import Game, Player, Result, Round, Tournament

bp = Blueprint("tournament", __name__, template_folder="templates/tournament")


def requires_ownership(func):
    @wraps(func)
    def wrapper(id):
        # If user does not own resource
        if not Tournament.query.filter_by(id=id, account=current_user).scalar():
            # TODO; logging
            print(request.__dict__)
            flash("You do not have access to this tournament")
            return redirect(url_for("account.login", next=request.path))

        return func(id)

    return wrapper


@bp.route("/list")
def list():
    return render_template("list.html", tournaments=Tournament.query.all())


@bp.route("/<id>/ranks")
def ranks(id):
    t = Tournament.query.get(int(id))

    win_case = case([(Result.won == True, 1)], else_=0)
    loss_case = case([(Result.won == False, 1)], else_=0)
    players = (
        Result.query.join(Result.player)
        .with_entities(
            Player.name,
            func.sum(win_case),
            func.sum(loss_case),
        )
        .filter(Player.tournament == t)
        .group_by(Player.id)
    )
    players = sorted(players, key=lambda x: x[1], reverse=True)
    return render_template("ranks.html", tournament=t, players=players)


def games_data(id):
    t = Tournament.query.get(int(id))
    rounds = []
    # TODO; optimise sql
    for r in Round.query.filter_by(tournament=t):
        games = []
        for g in Game.query.filter_by(round=r):
            games.append(
                [
                    {"id": result.id, "name": result.player.name, "won": result.won}
                    for result in Result.query.filter_by(game=g)
                ]
            )
        rounds.append(games)

    return {"tournament": t, "rounds": rounds}


@bp.route("/<id>/games")
def games(id):
    return render_template("games.html", **games_data(id))


@bp.route("/<id>/games/edit")
@login_required
@requires_ownership
def games_edit(id):
    return render_template("games.html", **games_data(id), edit=True)


@bp.route("/<id>/games/edit", methods=["POST"])
@login_required
@requires_ownership
def games_post(id):
    try:
        winner = Result.query.get(int(request.form.get("resultid")))
        Tournament.query.get(int(id)).update(winner)

        db.session.commit()
    except Exception:
        flash("Something went wrong!")

    return redirect(url_for("tournament.games_edit", id=id))
