"""Message model tests."""

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

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
# os.environ['DATABASE_URL'] = 'postgres://rainb:qwerty@localhost/warbler-test'

# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test Message Model."""

    def setUp(self):
        """Create test client, add sample data."""

        db.session.rollback()
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_message_repr(self):
        """Does the repr method in the Message model work as expected?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()

        message = Message(text="This is a test.", user_id=u.id)
        db.session.add(message)
        db.session.commit()

        self.assertEqual(
            message.__repr__(),
            f"<Message #{message.id}: {message.user_id}, {message.timestamp}, {message.text}>"
        )

    def test_message_user_relation(self):
        """Does the Message model connect with the User model correctly?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()

        message = Message(text="This is a test.", user_id=u.id)
        db.session.add(message)
        db.session.commit()

        self.assertEqual(u.email, message.user.email)
