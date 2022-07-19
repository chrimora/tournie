from flask_login import UserMixin
from sqlalchemy.sql import func

from app import db


class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)


class CreateUpdateMixin:
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())


class Account(UserMixin, Base, CreateUpdateMixin):
    name = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)


class TournamentType(Base):
    name = db.Column(db.String(64), unique=True, nullable=False)

    @property
    def code(self):
        return self.name.lower().replace(" ", "")


class Tournament(Base):
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey("tournament_type.id"), nullable=False)

    account = db.relationship("Account", backref=db.backref("tournaments", lazy=True))
    type = db.relationship("TournamentType", lazy=True)

    @classmethod
    def create(cls, account, ttype, player_names):
        """
        Create the objects required for a tournament of the given type
        """
        t = cls(account=account, type=ttype)
        players = []
        for name in player_names:
            p = Player(name=name, tournament=t)
            players.append(p)

        # Ensure even number of players
        ppass = None
        if len(players) % 2 != 0:
            ppass = Player(name="pass", tournament=t)
            players.append(ppass)

        match ttype.code:
            case "roundrobin":
                for r in range(len(players) - 1):
                    round = Round(tournament=t, order=r)
                    _players = [players[0]] + players[1:][r:] + players[1:][:r]

                    # Pair up players
                    for i in range(int(len(_players) / 2)):
                        g = Game(round=round)
                        Result(game=g, player=_players[i])
                        Result(game=g, player=_players[-(i + 1)])
            case _:
                # TODO; raise exception
                pass

        # Required for next step
        db.session.add(t)
        db.session.commit()

        # TODO; probably shouldnt count as a win
        # Auto win games against "pass"
        if ppass:
            for result in Result.query.filter_by(player_id=ppass.id).all():
                t.update(result, won=False)

        return t

    def update(self, result, won=True):
        """
        Update the tournament now that a result is in!
        """
        # Update the game results
        result.won = won
        for other in Result.query.filter(
            Result.game == result.game, Result.id != result.id
        ).all():
            other.won = not won

        # Update tournament games
        match self.type.code:
            case "roundrobin":
                # No actions for this tournie type
                pass
            case _:
                # TODO; raise exception
                pass


class Player(Base):
    name = db.Column(db.String(64), nullable=False)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournament.id"), nullable=False
    )

    tournament = db.relationship("Tournament", backref=db.backref("players", lazy=True))


class Round(Base):
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournament.id"), nullable=False
    )
    order = db.Column(db.Integer, nullable=False)

    tournament = db.relationship("Tournament", backref=db.backref("rounds", lazy=True))


class Game(Base):
    round_id = db.Column(db.Integer, db.ForeignKey("round.id"), nullable=False)

    round = db.relationship("Round", backref=db.backref("games", lazy=True))


class Result(Base, CreateUpdateMixin):
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    won = db.Column(db.Boolean, nullable=True, default=None)
    # Score?

    game = db.relationship("Game", backref=db.backref("results", lazy=True))
    player = db.relationship("Player", backref=db.backref("results", lazy=True))
