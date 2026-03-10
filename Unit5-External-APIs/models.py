# ============================================================================
# models.py - CineMatch Database Models
# ============================================================================

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


# ============================================================================
# ASSOCIATION TABLE: User ↔ Movie Favorites (Lesson 5.3)
# ============================================================================

favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True)
)


# ============================================================================
# ASSOCIATION TABLE: User ↔ Movie Watchlist (Lesson 5.4)
# ============================================================================

watchlist = db.Table('watchlist',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True)
)


# ============================================================================
# USER MODEL
# ============================================================================

class User(UserMixin, db.Model):
    """Registered users of CineMatch"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), 
                          default=lambda: datetime.now(timezone.utc))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Many-to-many: User ↔ Movie favorites
    favorite_movies = db.relationship('Movie', secondary=favorites,
                                      backref='favorited_by')
    
    # Many-to-many: User ↔ Movie watchlist
    watchlist_movies = db.relationship('Movie', secondary=watchlist,
                                       backref='watchlisted_by')
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


# ============================================================================
# MOVIE MODEL
# ============================================================================

class Movie(db.Model):
    """Movie in the CineMatch catalog"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer)
    genre = db.Column(db.String(50))
    director = db.Column(db.String(100))
    rating = db.Column(db.Float)
    description = db.Column(db.Text)
    poster_url = db.Column(db.String(500))
    tmdb_id = db.Column(db.Integer, unique=True, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), 
                          default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Movie: {self.title} ({self.year})>"
