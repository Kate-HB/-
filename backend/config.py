import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SQLITE_URL = f"sqlite:///{(BASE_DIR / 'supermarket.db').as_posix()}"

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', DEFAULT_SQLITE_URL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supermarket-secret-key-2026')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', '24'))
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
