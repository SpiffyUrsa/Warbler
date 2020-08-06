"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

# os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
os.environ['DATABASE_URL'] = 'postgres://rainb:qwerty@localhost/warbler-test'

# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test User Model."""

    def setUp(self):
        """Create test client, add sample data."""

        db.session.rollback()
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        db.session.commit()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        """Does the repr method work as expected?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(
            u.__repr__(), f"<User #{u.id}: {u.username}, {u.email}>")

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""

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
        u1.following.append(u2)

        db.session.commit()

        self.assertTrue(u1.is_following(u2))

    def test_is_not_following(self):
        """Does is_following successfully detect when user1 is not following user2?"""

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
        u1.following.append(u2)

        db.session.commit()

        self.assertFalse(u2.is_following(u1))

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""

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
        u1.followers.append(u2)

        db.session.commit()

        self.assertTrue(u1.is_followed_by(u2))

    def test_is_not_followed_by(self):
        """Does is_followed_by successfully detect when user1 is not followed by user2?"""

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
        u1.followers.append(u2)

        db.session.commit()

        self.assertFalse(u2.is_followed_by(u1))

    def test_sign_up(self):
        """Does User.signup successfully create a new user given valid credentials?"""

        # add u1 to db
        u1 = User.signup("testuser1", "test1@test.com",
                         "HASHED_PASSWORD", None)

        # check if u1 is in db
        response = User.query.get(u1.id)
        self.assertEqual(response, u1)

    def test_sign_up_invalid(self):
        """Does User.signup fail to create a new user if any of the validations
        (e.g. uniqueness, non-nullable fields) fail?"""

        u1 = User.signup("testuser1", "test1@test.com",
                         "HASHED_PASSWORD", None)

        created = True
        try:
            u2 = User.signup("testuser1", "test2@test.com",
                             "HASHED_PASSWORD", None)
        except IntegrityError:
            created = False

        self.assertFalse(created)

    def test_authenticate(self):
        """ Does User.authenticate successfully return a user when given valid credentials?"""

        u1 = User.signup("testuser1", "test1@test.com",
                         "HASHED_PASSWORD", None)
        auth_user = User.authenticate("testuser1", "HASHED_PASSWORD")

        self.assertEqual(u1, auth_user)

    def test_authenticate_invalid_username(self):
        """Does User.authenticate fail when the username is invalid?"""

        u1 = User.signup("testuser1", "test1@test.com",
                         "HASHED_PASSWORD", None)
        auth_user = User.authenticate("testuser2", "HASHED_PASSWORD")

        self.assertFalse(auth_user)

    def test_authenticate_invalid_password(self):
        """Does User.authenticate fail when the password is invalid?"""

        u1 = User.signup("testuser1", "test1@test.com",
                         "HASHED_PASSWORD", None)
        auth_user = User.authenticate("testuser1", "WRONG_HASHED_PASSWORD")

        self.assertFalse(auth_user)
