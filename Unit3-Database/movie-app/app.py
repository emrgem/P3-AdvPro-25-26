"""
CineMatch - Movie Discovery Platform
Lesson 3.1 STARTER CODE
"""
from flask import Flask, render_template, request, redirect, url_for, flash
# from sample_movies import movies
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
            # Add all the movies to the session(staging area)
            for movie in movies:
                db.session.add(movie)
            #Commit to database (make changes permanent)
            db.session.commit()
            print(f"Added {len(movies)} movies to database!")
        else:
            print(f"Database already has {Movie.query.count()} movies!")
         
# ============================
# ROUTES
# ============================

@app.route('/')
def index():
    #Get the first 4 movies for homepage preview
    movies = Movie.query.limit(4).all()
    """Homepage with hero section"""
    return render_template('index.html', movies=movies)


@app.route('/movies')
def movies_list():
    """
    Display all movies
    TODO (Later in Unit 3): Change this to query from database instead of list
    """
    movies = Movie.query.order_by(Movie.rating.desc()).all()
    return render_template('movies.html', movies=movies)


@app.route('/about')
def about():
    """About CineMatch page"""
    return render_template('about.html')

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    """Add a new movie to the database"""
    if request.method == 'POST':
        #request.form.get() - retrieves the value from the form field
        #the parameter name must match the 'name' attribute in the HTML Form
        title = request.form.get('title')
        year = request.form.get('year', type=int) #converts str to int
        genre = request.form.get('genre')
        director = request.form.get('director')
        rating = request.form.get('rating', type=float) #converts str to float
        description = request.form.get('description')
        poster_url = request.form.get('poster_url')
        if not poster_url:
            poster_url = f"https://placehold.co/300x450/gray/white?text={title}"

        #Validation with better messages
        if not title:
            flash("❌ Title is required! Please enter a movie Title!","error")
            return redirect(url_for("add_movie"))
        
        #Create a new movie object
        new_movie = Movie(
            title = title,
            year = year,
            genre = genre,
            director = director,
            rating = rating,
            description = description,
            poster_url = poster_url
        )
        #Add to database session(stating area)
        db.session.add(new_movie)
        #Commit to database (make changes permanent)
        db.session.commit()
        
        
        #Redirect to the movies list page
        return redirect(url_for('movies_list'))
        
    #If GET request, just show the form
    return render_template("add_movie.html")

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
    #create tables on first run
    create_tables()
    #load initial movies if database is empty
    load_initial_movies()
    
    # Debug mode: Shows errors and auto-reloads on code changes
    app.run(debug=True, port=5000)
