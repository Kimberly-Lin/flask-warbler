"""User view function tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os
os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app
from unittest import TestCase
from models import db, User, Message, Follows
from flask_wtf import form


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

# Now we can import app
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

app.config['WTF_CSRF_ENABLED'] = False


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.u1 = u1
        self.u2 = u2

        self.u1id = u1.id
        self.u2id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        """Clean up foul transactions after ever test"""

        db.session.rollback()

    def test_valid_user_signup(self):
        """Tests for a valid user signup"""

        with app.test_client() as client:
            user_signup_data = {
                'email': 'test@test.com',
                'username': 'test_user',
                'password': 'HASHED_PASSWORD'
            }

            num_users_before = len(User.query.all())
            resp = client.post("/signup", data=user_signup_data)

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(len(User.query.all()), num_users_before + 1)
    

    def test_invalid_user_signup(self):
        """Test if input field types are wrong. Form invalid on submit"""
        with app.test_client() as client:
            user_signup_data = {
                'email': 'test.com',
                'username': 'testuser',
                'password': 'HASHED_PASSWORD'
            }

            num_users_before = len(User.query.all())
            resp = client.post("/signup", data=user_signup_data)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(User.query.all()), num_users_before)
            self.assertIn('<h2 class="join-message">Join Warbler today.</h2>', html)
