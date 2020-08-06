"""User views tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


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

from app import app, g

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

app.config['WTF_CSRF_ENABLED'] = False # removes CSRF functionality when testing

db.drop_all()
db.create_all()


class UserViewsTestCase(TestCase):
    """Test User Model."""

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

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_logged_in(self):
        """Test to see if the log in functionality works."""

        with app.test_client() as client:
            d = {"username": "testuser", "password": "HASHED_PASSWORD"}
            resp = client.post('/login', data = d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("/logout", html)

    def test_logged_in_follower_view(self):
        """Test to see if a logged in user can view other user's followers page."""

        with app.test_client() as client:
            # Is there a better way to make it so that we don't have to repeat the log in code?
            #(ie. a function?)
            d = {"username": "testuser", "password": "HASHED_PASSWORD"}
            resp = client.post('/login', data = d, follow_redirects=True)

            other_user = User.signup(
                email="test2@test.com",
                username="testuser2",
                password="HASHED_PASSWORD", 
                image_url=None,
            )

            followed_user = User.query.get_or_404(other_user.id)
            g.user.following.append(followed_user)
            db.session.commit()

            resp = client.get(f'/users/{other_user.id}/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"{self.user.username}", html)

    def test_logged_in_following_view(self):
        """Test to see if a logged in user can view other user's following page."""

        with app.test_client() as client:
            d = {"username": "testuser", "password": "HASHED_PASSWORD"}
            resp = client.post('/login', data = d, follow_redirects=True)

            other_user = User.signup(
                email="test2@test.com",
                username="testuser2",
                password="HASHED_PASSWORD", 
                image_url=None,
            )

            following_user = User.query.get_or_404(other_user.id)
            g.user.followers.append(following_user)
            db.session.commit()

            resp = client.get(f'/users/{other_user.id}/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"{self.user.username}", html)
            
    def test_not_logged_in_follower_view(self):
        """Test to see if a non-logged-in user can not view other user's followers page."""

        with app.test_client() as client:
            other_user = User.signup(
                email="test2@test.com",
                username="testuser2",
                password="HASHED_PASSWORD", 
                image_url=None,
            )

            resp = client.get(f'/users/{other_user.id}/followers', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_not_logged_in_following_view(self):
        """Test to see if a non-logged-in user can not view other user's following page."""

        with app.test_client() as client:
            other_user = User.signup(
                email="test2@test.com",
                username="testuser2",
                password="HASHED_PASSWORD", 
                image_url=None,
            )

            resp = client.get(f'/users/{other_user.id}/following', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_logged_in_add_message(self):
        """Test to see if a logged in user can add a message as themselves."""

        with app.test_client() as client:
            #login
            d = {"username": "testuser", "password": "HASHED_PASSWORD"}
            resp = client.post('/login', data = d, follow_redirects=True)

            #create message
            d = {"text": "Test text!"}
            resp = client.post('/messages/new', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test text!", html)

    def test_not_logged_in_add_message(self):
        """Test to see if a non-logged-in user can not add a message as themselves."""

        with app.test_client() as client:
            #try to create message
            d = {"text": "Test text!"}
            resp = client.post('/messages/new', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
    
    def test_logged_in_delete_message(self):
        """Test to see if a logged in user can delete a message as themselves."""

        with app.test_client() as client:
            #login
            d = {"username": "testuser", "password": "HASHED_PASSWORD"}
            resp = client.post('/login', data = d, follow_redirects=True)

            #create message
            d = {"text": "Test text!"}
            resp = client.post('/messages/new', data=d, follow_redirects=True)
            
            #select message
            new_msg = Message.query.get(g.user.id).first()

            #destroy message
            d = {"text": "Test text!"}
            resp = client.post(f'/messages/{}/delete', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test text!", html)