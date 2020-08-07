"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


from app import app, CURR_USER_KEY, g
import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

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

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.session.rollback()
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        db.session.commit()

        user = User.signup(
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD",
            image_url=None,
        )

        self.user = user

        self.client = app.test_client()

    def test_add_message(self):
        """Can users add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_logged_in_add_message(self):
        """Test to see if a logged in user can add a message as themselves."""

        with app.test_client() as client:
            # login
            d = {"username": "testuser", "password": "HASHED_PASSWORD"}
            resp = client.post('/login', data=d, follow_redirects=True)

            # create message
            d = {"text": "Test text!"}
            resp = client.post('/messages/new', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test text!", html)

    def test_not_logged_in_add_message(self):
        """Test to see if a non-logged-in user can not add a message as themselves."""

        with app.test_client() as client:
            # try to create message
            d = {"text": "Test text!"}
            resp = client.post('/messages/new', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_logged_in_delete_message(self):
        """Test to see if a logged in user can delete a message as themselves."""

        with app.test_client() as client:
            # login
            d = {"username": "testuser", "password": "HASHED_PASSWORD"}
            resp = client.post('/login', data=d, follow_redirects=True)

            # create message
            d = {"text": "Test text!"}
            resp = client.post('/messages/new', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test text!", html)

            # select message
            new_msg = g.user.messages[0]

            # destroy message
            d = {"text": "Test text!"}
            resp = client.post(
                f'/messages/{new_msg.id}/delete', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Test text!", html)

    def test_not_logged_in_delete_message(self):
        """Test to see if a non-logged-in user can not delete a message."""

        with app.test_client() as client:
            # login
            d = {"username": "testuser", "password": "HASHED_PASSWORD"}
            resp = client.post('/login', data=d, follow_redirects=True)

            # create message
            d = {"text": "Test text!"}
            resp = client.post('/messages/new', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            # confirm message exists
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test text!", html)

            # select msg
            testuser = User.query.filter(User.username == 'testuser').first()
            new_msg = testuser.messages[0]

            # logout
            resp = client.post('/logout', follow_redirects=True)

            # try to delete message id 0
            resp = client.post(f'/messages/{new_msg.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_logged_in_cant_post_as_other_user(self):
        """Test to confirm that a user can't post a message as another user."""

        with app.test_client() as client:
            # login
            d = {"username": "testuser", "password": "HASHED_PASSWORD"}
            resp = client.post('/login', data=d, follow_redirects=True)

            # create message
            d = {"text": "Test text!"}
            resp = client.post('/messages/new', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            # select message
            new_msg = g.user.messages[0]

            # check if message.user is g.user
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(new_msg.user, g.user)

    def test_logged_in_cant_delete_other_user_msg(self):
        """Test to confirm that a user can't delete a message from another user."""

        with app.test_client() as client:
            # login as testuser
            d = {"username": "testuser", "password": "HASHED_PASSWORD"}
            resp = client.post('/login', data=d, follow_redirects=True)

            # create message
            d = {"text": "Test text!"}
            resp = client.post('/messages/new', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            # select message
            new_msg = g.user.messages[0]

            # logout
            resp = client.post('/logout', follow_redirects=True)

            # sign up as testuser2
            other_user = User.signup(
                email="test2@test.com",
                username="testuser2",
                password="HASHED_PASSWORD",
                image_url=None,
            )

            # login as testuser2
            d = {"username": "testuser2", "password": "HASHED_PASSWORD"}
            resp = client.post('/login', data=d, follow_redirects=True)

            # check if testuser2 can delete testuser1's msg
            resp = client.post(
                f'/messages/{new_msg.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
