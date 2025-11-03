"""
CineMatch - Movie Discovery Platform
Lesson 3.1 STARTER CODE
"""
from flask import Flask, render_template, request, redirect, url_for, flash
from sample_movies import movies
from models import db, Movie

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# DATABASE CONFIGURATION
# SQLite database will be stored in instance/cinematch.db
# instance folder is automatically created by Flask
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///cinematch.db'

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#initialize the database
db.init_app(app)


# DATABASE INITIALIZATION
def create_tables():
    """Create all database tables
    This runs once to set up the database"""
    with app.app_context():
        db.create_all()
        print("✅Database tables created!")
    
def load_initial_movies():
    """Checks if the database is empty, and id so adds sample movies"""
    with app.app_context():
        #Check if any movies exist
        if Movie.query.count() == 0:
            print("🎥Loading initial movies!")
            #Create movie objects
            movies = [
                Movie(
                    title="Inception",
                    year=2010,
                    genre="Sci-Fi",
                    director="Christopher Nolan",
                    rating=8.8,
                    description="A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.",
                    poster_url="https://placehold.co/300x450/667eea/ffffff?text=Inception"
                ),
                Movie(
                    title="The Matrix",
                    year=1999,
                    genre="Sci-Fi",
                    director="Wachowski Sisters",
                    rating=8.7,
                    description="A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
                    poster_url="https://placehold.co/300x450/764ba2/ffffff?text=The+Matrix"
                ),
                Movie(
                    title="Interstellar",
                    year=2014,
                    genre="Sci-Fi",
                    director="Christopher Nolan",
                    rating=8.6,
                    description="A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
                    poster_url="https://placehold.co/300x450/f093fb/ffffff?text=Interstellar"
                ),
                Movie(
                    title="The Shawshank Redemption",
                    year=1994,
                    genre="Drama",
                    director="Frank Darabont",
                    rating=9.3,
                    description="Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                    poster_url="https://placehold.co/300x450/4CAF50/ffffff?text=Shawshank"
                ),
                Movie(
                    title="The Dark Knight",
                    year=2008,
                    genre="Action",
                    director="Christopher Nolan",
                    rating=9.0,
                    description="When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest tests.",
                    poster_url="https://placehold.co/300x450/4facfe/ffffff?text=Dark+Knight"
                )
            ]

            
# ============================
# ROUTES
# ============================

@app.route('/')
def index():
    """Homepage with hero section"""
    return render_template('index.html', movies=movies)


@app.route('/movies')
def movies_list():
    """
    Display all movies
    
    TODO (Later in Unit 3): Change this to query from database instead of list
    """
    return render_template('movies.html', movies=movies)


@app.route('/about')
def about():
    """About CineMatch page"""
    return render_template('about.html')


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('errors/500.html'), 500


# =========================
# RUN APPLICATION
# =========================

if __name__ == '__main__':
    # Debug mode: Shows errors and auto-reloads on code changes
    app.run(debug=True, port=5000)
