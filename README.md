# Warbler

## Overview
- This application is designed as a Twitter clone. Users can create a profile, post messages, follow other users, and "like" different messages.

## Setup
- Creating a virtual environment and installing dependencies
```
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```
- Creating and seeding the database
```
(venv) $ createdb warbler
(venv) $ python seed.py
```
- Starting the server
```
(venv) $ flask run
```

## Running the Tests
- To run a file containing unittests:
```
FLASK_ENV=production python -m unittest <name-of-python-file>
```
