import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "tournaments.sqlite")
SQLALCHEMY_TRACK_MODIFICATIONS = False

CSRF_ENABLED = True
CSRF_SESSION_KEY = "secret"

SECRET_KEY = "secret"
