"""
CineMatch - Movie Discovery Platform
Lesson 3.1 STARTER CODE
"""
from flask import Flask, render_template, request, redirect, url_for, flash
# from sample_movies import movies
from models import db, Movie
import csv
from utilities import get_csv_value, parse_rating, parse_year

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

        # #Validation with better messages
        # if not title:
        #     flash("❌ Title is required! Please enter a movie Title!","error")
        #     return redirect(url_for("add_movie"))
        
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
        
        #Success message
        flash(f'✅"{title}" was added successfully!','success')
        
        #Redirect to the movies list page
        return redirect(url_for('movies_list'))
        
    #If GET request, just show the form
    return render_template("add_movie.html")

@app.route('/movie/<int:id>/edit', methods = ["GET", "POST"])
def edit_movie(id):
    movie = Movie.query.get_or_404(id) #Get existing movie
    if request.method == 'POST':
        #update the existing movie object
        movie.title = request.form.get('title')
        movie.year = request.form.get('year', type=int) #converts str to int
        movie.genre = request.form.get('genre')
        movie.director = request.form.get('director')
        movie.rating = request.form.get('rating', type=float) #converts str to float
        movie.description = request.form.get('description')
        movie.poster_url = request.form.get('poster_url')
        if not movie.poster_url:
            movie.poster_url = f"https://placehold.co/300x450/gray/white?text={movie.title}"
        # No db.session.add() needed! Object already tracked
        db.session.commit()
        flash(f'Movie "{movie.title}" updated', 'success')
        return redirect(url_for('movies_list'))
    return render_template('edit_movie.html', movie=movie)

@app.route('/movie/<int:id>/delete', methods=['POST'])
def delete_movie(id):
    movie = Movie.query.get_or_404(id) #Get existing movie
    #IMPORTANT: Save title before deleting
    #After db.session.delete(). movie.title becomes None!
    title = movie.title
    # Delete from database
    db.session.delete(movie)
    db.session.commit()
    #Flash a message with saved title
    flash(f'🗑️Movie "{title}" deleted successfully,', 'success')
    return redirect(url_for('movies_list'))

@app.route('/movie/<int:id>')
def movie_detail(id):
    # Query database for movie with this id
    # get_or_404() automatically returns 404 if movie doesn't exist
    movie = Movie.query.get_or_404(id)
    
    # Render the detail template with the movie data
    return render_template('movie_detail.html', movie=movie)

@app.route('/import_csv', methods=['GET', 'POST'])
def import_csv():
    if request.method == 'POST':
        # Step1 - Get the uploaded file
        file = request.files.get('csv_file')
        # Step 2 Validate the file
        if not file or file.filename == '':
            flash("No file selected. Please choose a CSV file", 'error')
            return redirect(url_for('import_csv'))
        if not file.filename.lower().endswith('.csv'):
            flash("Invalid file type. Please upload a CSV file", 'error')
            return redirect(url_for('import_csv'))
        #Step3 - Read and decode the file content
        try:
            file_content = file.read().decode("utf-8", errors="replace")
            lines = file_content.splitlines()
        except Exception as e:
            flash(f"Error reading file:{str(e)}", "error")
            return redirect(url_for("import_csv"))
        #Step4 - Parse CSV with DictReader
        csv_reader = csv.DictReader(lines)
        imported_count = 0
        skipped_count = 0
        #Step5 - Process each row
        try:
            for row_num, row in enumerate(csv_reader, start=2):
                #Get the title - REQUIRED field
                title = get_csv_value(row, 'Series_Title', 'Title', "movie_title", "name", "title")
                if not title:
                    skipped_count +=1
                    continue
                # Get optional fields
                year = parse_year(get_csv_value(row, "Released_Year", "year", "Year", "released_year"))
                genre = get_csv_value(row, 'Genre', "genre", "genres")
                director = get_csv_value(row, "Director", "director", "directed_by")
                rating = parse_rating(get_csv_value(row, "IMDB_Rating", "rating", "Rating", "imdb_rating"))
                description = get_csv_value(row, "Overview", "description", "plot", "Description", "summary")
                poster_url = get_csv_value(row, "Poster_Link", "poster_url", "Poster")
                if not poster_url:
                    poster_url = f"https://placehold.co/300x450/gray/white?text={title}"
                
                # Create the Movie Object
                movie = Movie(
                    title = title,
                    year = year,
                    genre = genre,
                    director = director,
                    rating = rating,
                    description = description,
                    poster_url = poster_url   
                )
                db.session.add(movie)
                imported_count +=1
            #Step 6 - Commit
            db.session.commit()
            #Step7 - Provide user feedback
            if imported_count > 0 :
                flash(f"Successfully imported {imported_count} movies!", 'success')
            if skipped_count > 0 :
                flash(f"Skipped {skipped_count} row (missing title)!", 'warning')
            return redirect(url_for('movies_list'))
        except Exception as e :
            db.session.rollback()
            flash(f"Import Failed! {str(e)}", "error")
            return redirect(url_for("import_csv"))
            
    return render_template("import_csv.html")
    
# =============================================================================
# SEARCH ROUTE
# =============================================================================

@app.route('/search')
def search(): 
    # =========================================================================
    # STEP 1: Extract search parameters from URL query string
    # =========================================================================
    # request.args contains all URL parameters (?key=value&key2=value2)
    # .get() returns None if parameter is missing (safer than direct access)
    # .strip() removes leading/trailing whitespace from user input
    query = request.args.get('query', '').strip()
    genre = request.args.get('genre', '').strip()
    year = request.args.get('year',type=int)
    min_rating = request.args.get('min_rating',type=float)
    
    
    # =========================================================================
    # STEP 2: Start with base query (all movies)
    # =========================================================================
    # We don't call .all() yet - we build the query first, then execute
    # This is called "lazy evaluation" - the database query runs only when needed
    movies = Movie.query
    
    
    # =========================================================================
    # STEP 3: Apply filters dynamically (only if values provided)
    # =========================================================================
    # Each filter chains onto the previous query
    # This pattern allows combining multiple filters flexibly
    
    # --- Title Search (partial match, case-insensitive) ---
    if query:
        # .ilike() = case-Insensitive LIKE query
        # % = wildcard (matches any characters)
        # f'%{query}%' = matches "query" anywhere in the title
        # Example: '%matrix%' matches "The Matrix", "Matrix Reloaded", "matrix"
        movies = movies.filter(Movie.title.ilike(f"%{query}%"))
    
    # --- Genre Filter (exact match) ---
    if genre:
        # .filter_by() is simpler syntax for exact equality matches
        # Equivalent to: .filter(Movie.genre == genre)
        movies = movies.filter_by(genre=genre)
    
    # --- Year Filter (exact match) ---
    if year:
        # Only apply if year was provided and successfully converted to int
        movies = movies.filter_by(year=year)
    
    # --- Minimum Rating Filter (greater than or equal) ---
    if min_rating:
        # .filter() allows comparison operators: >=, <=, >, <, ==, !=
        # Must use Movie.rating >= value syntax (not filter_by)
        movies = movies.filter(Movie.rating >= min_rating)
    
    # =========================================================================
    # STEP 4: Execute query and get results
    # =========================================================================
    # .order_by() sorts results (desc() = highest first)
    # .all() executes the query and returns a list of Movie objects
    results = movies.order_by(Movie.rating.desc()).all()
    
    
    # =========================================================================
    # STEP 5: Get unique genres for the dropdown filter
    # =========================================================================
    # This queries all distinct genre values from the database
    # Used to populate the genre dropdown dynamically
    genres = db.session.query(Movie.genre).distinct().order_by(Movie.genre).all()
    
    # distinct() Removes duplicates, so each genre appears only once.
    # genres is a list of tuples: [('Action',), ('Comedy',), ('Sci-Fi',)]
    # Extract just the genre strings, filtering out None values
    genres = [g[0] for g in genres if g[0]]
    
    # =========================================================================
    # STEP 6: Render template with all data
    # =========================================================================
    # Pass both results AND original search values back to template
    # This allows the form to "remember" what the user searched for
    
    return render_template('movies.html',
                           movies = results,
                           genres=genres,
                           query=query,
                           selected_genre = genre,
                           selected_year = year,
                           selected_rating = min_rating)


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
