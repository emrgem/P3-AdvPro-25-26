# ============================================================================
# models.py - CineMatch Database Models
# ============================================================================

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime, timezone

db = SQLAlchemy()
bcrypt = Bcrypt()

# ============================================================================
# ASSOCIATION TABLE: User ↔ Movie Favorites
# ============================================================================

favorites = db.Table(
    "favorites",
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "movie_id",
        db.Integer,
        db.ForeignKey("movie.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

# ============================================================================
# USER MODEL
# ============================================================================


class User(UserMixin, db.Model):
    __tablename__ = "user"

    __table_args__ = (
        db.UniqueConstraint("username", name="uq_user_username"),
        db.UniqueConstraint("email", name="uq_user_email"),
    )

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    # Password hashes must NOT be unique
    password_hash = db.Column(db.String(256), nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    favorite_movies = db.relationship(
        "Movie", secondary=favorites, back_populates="favorited_by"
    )

    # ------------------------
    # Authentication helpers
    # ------------------------

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


# ============================================================================
# MOVIE MODEL
# ============================================================================


class Movie(db.Model):
    __tablename__ = "movie"

    __table_args__ = (db.UniqueConstraint("tmdb_id", name="uq_movie_tmdb_id"),)

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer)
    genre = db.Column(db.String(50))
    director = db.Column(db.String(100))
    rating = db.Column(db.Float)
    description = db.Column(db.Text)
    poster_url = db.Column(db.String(500))

    # Nullable but UNIQUE when present
    tmdb_id = db.Column(db.Integer, nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    favorited_by = db.relationship(
        "User", secondary=favorites, back_populates="favorite_movies"
    )

    def __repr__(self) -> str:
        return f"<Movie {self.title} ({self.year})>"
