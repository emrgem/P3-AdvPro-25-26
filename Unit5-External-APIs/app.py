# ============================================================================
# app.py - CineMatch Application Entry Point
# ============================================================================

import os
from dotenv import load_dotenv

# Load environment variables BEFORE other imports
load_dotenv()

from flask import Flask
from routes import register_routes
from db_init import init_db
from models import db, Movie, User, bcrypt
from flask_login import LoginManager, login_user, current_user
from flask_migrate import Migrate

# ============================================================================
# APP CONFIGURATION
# ============================================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-please-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cinematch.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# ============================================================================
# INITIALIZE EXTENSIONS
# ============================================================================

db.init_app(app)
migrate = Migrate(app,db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page!"
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


# ============================================================================
# REGISTER ROUTES
# ============================================================================

register_routes(app)


# ============================================================================
# START APPLICATION
# ============================================================================

if __name__ == '__main__':
    init_db(app)
    app.run(debug=True, port=5000)
