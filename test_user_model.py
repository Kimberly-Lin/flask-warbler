"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

from sqlalchemy import exc
from flask_wtf import form
from models import db, User, Message, Follows
from sqlalchemy.sql.schema import UniqueConstraint
from unittest import TestCase
from flask_bcrypt import Bcrypt
from app import app
import os

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


bcrypt = Bcrypt()

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            # password="HASHED_PASSWORD"
            password=bcrypt.generate_password_hash(
                "HASHED_PASSWORD").decode('UTF-8')
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

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)

    def test_user_repr_(self):
        """Does user repr show up properly."""

        self.assertEqual(
            repr(self.u1), f'<User #{self.u1id}: testuser1, test1@test.com>')

    def test_success_follow(self):
        """Does is_following successfully detect when user1 is following user2?"""

        u1_follows_u2 = Follows(
            user_being_followed_id=self.u2id, user_following_id=self.u1id)

        db.session.add(u1_follows_u2)
        db.session.commit()

        self.assertEqual(self.u1.is_following(self.u2), True)

    def test_success_not_follow(self):
        """Does is_following successfully detect when user1 is not following user2?"""

        self.assertEqual(self.u1.is_following(self.u2), False)

    def test_success_being_followed(self):
        """Does is_following successfully detect when user1 is being followed user2?"""

        u2_follows_u1 = Follows(
            user_being_followed_id=self.u1id, user_following_id=self.u2id)

        db.session.add(u2_follows_u1)
        db.session.commit()

        self.assertEqual(self.u1.is_followed_by(self.u2), True)

    def test_success_being_not_followed(self):
        """Does is_followed_by successfully detect when user1 is not followed by user2?"""

        self.assertEqual(self.u1.is_followed_by(self.u2), False)

    def test_valid_user_classmethod_signup(self):
        """Tests for a valid user signup"""

        num_users_before = len(User.query.all())

        User.signup(
            username='testuser',
            email='test@test.com',
            password='password',
            image_url='https://image.cnbcfm.com/api/v1/image/105992231-1561667465295gettyimages-521697453.jpeg?v=1561667497&w=1600&h=900'
        )

        self.assertEqual(len(User.query.all()), num_users_before + 1)

    def test_invalid_user_classmethod_signup_dupe_username(self):
        """Tests for a valid user signup"""

        User.signup(
            username='testuser1',
            email='test@test.com',
            password='password',
            image_url='https://image.cnbcfm.com/api/v1/image/105992231-1561667465295gettyimages-521697453.jpeg?v=1561667497&w=1600&h=900'
        )

        self.assertRaises(exc.IntegrityError)

    def test_invalid_user_classmethod_signup_bad_email(self):
        """Tests for a valid user signup"""

        User.signup(
            username='testuser',
            email='test.com',
            password='password',
            image_url='https://image.cnbcfm.com/api/v1/image/105992231-1561667465295gettyimages-521697453.jpeg?v=1561667497&w=1600&h=900'
        )

        self.assertRaises(exc.IntegrityError)

    def test_invalid_user_classmethod_signup_no_username_input(self):
        """Tests for a valid user signup"""

        User.signup(
            username=None,
            email='test.com',
            password='password',
            image_url='https://image.cnbcfm.com/api/v1/image/105992231-1561667465295gettyimages-521697453.jpeg?v=1561667497&w=1600&h=900'
        )

        self.assertRaises(exc.IntegrityError)

    def test_valid_user_authenticate_method(self):
        """Tests the authenticate method for valid users"""

        user = User.authenticate('testuser1', 'HASHED_PASSWORD')

        self.assertEqual(self.u1, user)

    def test_bad_username_authenticate_method(self):
        """Tests the authenticate method fails for an invalid username."""    

        User.authenticate('testuser', 'HASHED_PASSWORD')

        self.assertRaises(exc.IntegrityError)

    def test_invalid_user_credentials_authenticate_method(self):
        """Tests the authenticate method for invalid user credentials"""

        user = User.authenticate('testuser1', 'BAD_PASSWORD')

        self.assertEqual(user, False)

