import hashlib
from datetime import datetime

from micro import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    isadmin = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()


def load_user(username):
    return User.query.filter_by(username=username).first()


class GeoIP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(64), index=True, unique=True)
    city = db.Column(db.String(64))
    region = db.Column(db.String(64))
    country_name = db.Column(db.String(64))
    country_code = db.Column(db.String(2))
    continent = db.Column(db.String(64))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    postal = db.Column(db.String(12))
    flag = db.Column(db.String(64))
    currency_name = db.Column(db.String(64))
    currency_code = db.Column(db.String(4))
    threat = db.Column(db.Boolean)


def Check_password(password, hash):
    if hashlib.sha256(password.encode('utf-8')).hexdigest() == hash:
        return True
    else:
        return False
