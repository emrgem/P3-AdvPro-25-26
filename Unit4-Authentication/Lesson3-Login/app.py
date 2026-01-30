# ============================================================================
# app.py - CineMatch Application Entry Point
# UNIT 4 STARTER CODE
# ============================================================================

from flask import Flask
from routes import register_routes
from db_init import init_db
from models import db, Movie, User, bcrypt
from flask_login import LoginManager, login_user, current_user


# ============================================================================
# APP CONFIGURATION
# ============================================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-please-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cinematch.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# ============================================================================
# INITIALIZE EXTENSIONS
# ============================================================================

# Database
db.init_app(app)

# Password hashing


# ============================================================================
# TODO 1: FLASK-LOGIN SETUP
# 
# Flask-Login manages user sessions (keeping users logged in).
# You need to:
#   1. Create a LoginManager instance
#   2. Initialize it with the app
#   3. Set the login_view (where to redirect if not logged in)
#   4. Set a login message
#
# Reference: https://flask-login.readthedocs.io/en/latest/
# ============================================================================

# Step 1: Create LoginManager instance
login_manager = LoginManager()
# Step 2: Initialize with app
login_manager.init_app(app)
# Step 3: Set login view (name of login route)
login_manager.login_view = 'login'
# Step 4: Set login message and category
login_manager.login_message = "Please log in to access this page!"
login_manager.login_message_category = 'info'

# ============================================================================
# TODO 2: USER LOADER FUNCTION
# 
# Flask-Login needs a way to reload a user from the session.
# This function is called on EVERY request to load the current user.
#
# It should:
#   - Take user_id as a parameter
#   - Query the database for that user
#   - Return the User object (or None if not found)
#
# Hint: Use User.query.get() and convert user_id to int
# ============================================================================

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    # TODO: Return the user with this ID from the database
    return User.query.get(int(user_id))


# ============================================================================
# REGISTER ROUTES (imported from routes.py)
# ============================================================================

register_routes(app)


# ============================================================================
# START APPLICATION
# ============================================================================

if __name__ == '__main__':
    init_db(app)
    app.run(debug=True, port=5000)
