from flask import Blueprint

from app import db
from app.models import TournamentType

bp = Blueprint("command", __name__)


@bp.cli.command("init_db")
def init_db():
    db.create_all()

    for name in ["Round Robin"]:
        tt = TournamentType(name=name)
        db.session.add(tt)
    db.session.commit()
