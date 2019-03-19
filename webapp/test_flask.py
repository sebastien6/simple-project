#!/usr/bin/env python
import unittest
import os
import tempfile
from flask import Flask, request

from micro import app, db
from micro.models import User, Check_password, load_user
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True
    SECRET_KEY = 'secret'
    USER_ADMIN = 'admin'
    USER_USER1 = 'user'
    PASSWORD = 'Passw0rd!'

class BasicTestCase(unittest.TestCase):

    def test_login(self):
        """Flask webserver: Ensure flask was set up correctly by testing login page status code."""
        tester = app.test_client(self)
        response = tester.get('/auth/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_home(self):
        """Flask webserver test: Ensure flask was set up correctly by testing home page redirection non authenticated users."""
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 302)


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.init_app(self.app)
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(Check_password('dog', u.password_hash))
        self.assertTrue(Check_password('cat', u.password_hash))

    def test_user_creation(self):
        u1 = User(username=TestConfig.USER_ADMIN, email='admin@example.com', isadmin=True)
        u2 = User(username=TestConfig.USER_USER1, email='user@example.com', isadmin=False)
        u1.set_password(TestConfig.PASSWORD)
        u2.set_password(TestConfig.PASSWORD)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        u1 = load_user(TestConfig.USER_ADMIN)
        u2 = load_user(TestConfig.USER_USER1)
        self.assertTrue(u1.isadmin)
        self.assertFalse(u2.isadmin)


if __name__ == '__main__':
    unittest.main()