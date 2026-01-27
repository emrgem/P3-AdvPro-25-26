# ============================================================================
# models.py - CineMatch Database Models
# Unit 4 STARTER CODE
# ============================================================================

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

#TODO:Import UserMixin

#TODO:Import Bcrypt

db = SQLAlchemy()

#TODO: Bcrypt Instance


# ============================================================================
# USER MODEL - TODO: Complete this model
# 
# The User model stores registered users of CineMatch.
# 
# IMPORTANT CONCEPTS:
#   - UserMixin: Provides required methods for Flask-Login
#   - password_hash: We store a HASH, never the actual password!
#   - set_password(): Hashes password during registration
#   - check_password(): Verifies password during login
# ============================================================================

class User(db.Model):
    """
    User Model - represents registered users of CineMatch
    
    UserMixin provides these methods automatically:
    - is_authenticated: Returns True if user is logged in
    - is_active: Returns True if account is active
    - is_anonymous: Returns False for real users
    - get_id(): Returns the user's ID as a string
    """
    
    # ========================================================================
    # TODO 1: Define the database columns
    # 
    # You need these columns:
    #   - id: Integer, primary key
    #   - username: String(80), unique, not nullable
    #   - email: String(120), unique, not nullable
    #   - password_hash: String(256), not nullable  <-- NOT "password"!
    #   - created_at: DateTime with timezone, default to now
    #
    # Pattern: Look at the Movie model below for reference!
    # ========================================================================
    
    id = db.Column(db.Integer, primary_key=True)
    
    # TODO: Add username column (String, max 80 chars, unique, required)
    
    # TODO: Add email column (String, max 120 chars, unique, required)
    
    # TODO: Add password_hash column (String, max 256 chars, required)
    # IMPORTANT: Name it password_hash, NOT password!
    
    # Timestamp - already done for you
    created_at = db.Column(db.DateTime(timezone=True), 
                          default=lambda: datetime.now(timezone.utc))
    
    
    # ========================================================================
    # TODO 2: Implement set_password method
    # 
    # This method is called during REGISTRATION to hash the password.
    # 
    # Steps:
    #   1. Use bcrypt.generate_password_hash(password) to create hash
    #   2. Decode the result to UTF-8 string: .decode('utf-8')
    #   3. Store in self.password_hash
    #
    # Example: self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    # ========================================================================
    
    def set_password(self, password):
        """
        Hash and store a password securely.
        Called during REGISTRATION.
        
        Args:
            password (str): The plain text password from the form
        """
        # TODO: Hash the password and store in self.password_hash
    
    
    # ========================================================================
    # TODO 3: Implement check_password method
    # 
    # This method is called during LOGIN to verify the password.
    # 
    # Steps:
    #   1. Use bcrypt.check_password_hash(self.password_hash, password)
    #   2. Return the result (True if match, False otherwise)
    #
    # Note: bcrypt handles the comparison securely!
    # ========================================================================
    
    def check_password(self, password):
        """
        Verify a password against the stored hash.
        Called during LOGIN.
        
        Args:
            password (str): The plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        # TODO: Check if password matches the stored hash
    
    
    def __repr__(self):
        return f'<User {self.username}>'


# ============================================================================
# MOVIE MODEL (From Unit 3 - No changes needed)
# Use this as a REFERENCE for the User model columns!
# ============================================================================

class Movie(db.Model):
    """Movie Model - represents movie table in database"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer)
    genre = db.Column(db.String(50))
    director = db.Column(db.String(100))
    rating = db.Column(db.Float)
    description = db.Column(db.Text)
    poster_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(timezone=True), 
                          default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Movie: {self.title} ({self.year})>"
