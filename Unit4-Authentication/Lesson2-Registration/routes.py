# ============================================================================
# routes.py - CineMatch Route Definitions
# UNIT 4 STARTER CODE
# ============================================================================

from flask import render_template, request, redirect, url_for, flash
from utilities import get_csv_value, parse_year, parse_rating
import csv
from models import db, Movie

# from flask_login import login_user, logout_user, login_required, current_user


def register_routes(app):
    """Register all routes with the Flask app"""
    
    # ========================================================================
    # HOME & PUBLIC ROUTES (No changes needed)
    # ========================================================================
    
    @app.route('/')
    def index():
        """Home page with featured movies"""
        movies = Movie.query.order_by(Movie.rating.desc()).limit(6).all()
        return render_template('index.html', movies=movies)
    
    
    @app.route('/about')
    def about():
        """About CineMatch page"""
        return render_template('about.html')
    
    
    # ========================================================================
    # MOVIE BROWSE & DETAIL (No changes needed)
    # ========================================================================
    
    @app.route('/movies')
    def movies_list():
        """Browse all movies with search, filter, and pagination"""
        query = request.args.get('query', '').strip()
        genre = request.args.get('genre', '').strip()
        year = request.args.get('year', type=int)
        min_rating = request.args.get('min_rating', type=float)
        page = request.args.get('page', 1, type=int)
        per_page = 8

        q = Movie.query

        if query:
            q = q.filter(Movie.title.ilike(f"%{query}%"))
        if genre:
            q = q.filter(Movie.genre == genre)
        if year:
            q = q.filter(Movie.year == year)
        if min_rating:
            q = q.filter(Movie.rating >= min_rating)

        pagination = q.order_by(Movie.rating.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        genres = db.session.query(Movie.genre).distinct().order_by(Movie.genre).all()
        genres = [g[0] for g in genres if g[0]]

        return render_template(
            'movies.html',
            movies=pagination.items,
            pagination=pagination,
            genres=genres,
            query=query,
            selected_genre=genre,
            selected_year=year,
            selected_min_rating=min_rating
        )
    
    
    @app.route('/movie/<int:id>')
    def movie_detail(id):
        """Display detailed information for a single movie"""
        movie = Movie.query.get_or_404(id)
        return render_template('movie_detail.html', movie=movie)
    
    
    # ========================================================================
    # MOVIE CRUD OPERATIONS (No changes needed)
    # ========================================================================
    
    @app.route('/add_movie', methods=['GET', 'POST'])
    def add_movie():
        """Add a new movie to the database"""
        if request.method == 'POST':
            title = request.form.get('title')
            if not title:
                flash("Title is required!", "error")
                return redirect(url_for('add_movie'))

            movie = Movie(
                title=title,
                year=request.form.get('year', type=int),
                genre=request.form.get('genre'),
                director=request.form.get('director'),
                rating=request.form.get('rating', type=float),
                description=request.form.get('description'),
                poster_url=request.form.get('poster_url') or \
                           f"https://placehold.co/300x450/gray/white?text={title.replace(' ', '+')}"
            )
            db.session.add(movie)
            db.session.commit()
            flash(f'✓ Movie "{movie.title}" added successfully!', 'success')
            return redirect(url_for('movies_list'))

        return render_template('add_movie.html')
    
    
    @app.route('/movie/<int:id>/edit', methods=['GET', 'POST'])
    def edit_movie(id):
        """Edit an existing movie"""
        movie = Movie.query.get_or_404(id)

        if request.method == 'POST':
            movie.title = request.form.get('title')
            movie.year = request.form.get('year', type=int)
            movie.genre = request.form.get('genre')
            movie.director = request.form.get('director')
            movie.rating = request.form.get('rating', type=float)
            movie.description = request.form.get('description')
            movie.poster_url = request.form.get('poster_url') or \
                               f"https://placehold.co/300x450/gray/white?text={movie.title.replace(' ', '+')}"

            db.session.commit()
            flash(f'✓ Movie "{movie.title}" updated successfully!', 'success')
            return redirect(url_for('movies_list'))

        return render_template('edit_movie.html', movie=movie)
    
    
    @app.route('/movie/<int:id>/delete', methods=['POST'])
    def delete_movie(id):
        """Delete a movie from the database"""
        movie = Movie.query.get_or_404(id)
        title = movie.title
        db.session.delete(movie)
        db.session.commit()
        flash(f'🗑 Movie "{title}" was deleted.', 'success')
        return redirect(url_for('movies_list'))
    
    
    @app.route('/import_csv', methods=['GET', 'POST'])
    def import_csv():
        """Bulk import movies from a CSV file"""
        if request.method == 'POST':
            file = request.files.get('csv_file')
            if not file or not file.filename.lower().endswith('.csv'):
                flash("Please upload a valid .csv file", 'error')
                return redirect(url_for('import_csv'))

            try:
                content = file.read().decode('utf-8', errors='replace')
                lines = content.splitlines()
                reader = csv.DictReader(lines)

                imported = 0
                skipped = 0

                for row in reader:
                    title = get_csv_value(row, 'Series_Title', 'Title', 'movie_title', 'name', 'title')
                    if not title:
                        skipped += 1
                        continue

                    movie = Movie(
                        title=title,
                        year=parse_year(get_csv_value(row, 'Released_Year', 'year', 'Year')),
                        genre=get_csv_value(row, 'Genre', 'genre', 'genres'),
                        director=get_csv_value(row, 'Director', 'director', 'directed_by'),
                        rating=parse_rating(get_csv_value(row, 'IMDB_Rating', 'rating', 'imdb_rating', 'Rating')),
                        description=get_csv_value(row, 'Overview', 'description', 'plot', 'Plot', 'Summary'),
                        poster_url=get_csv_value(row, 'Poster_Link', 'poster_url', 'Poster') or \
                                   f"https://placehold.co/300x450/gray/white?text={title.replace(' ', '+')}"
                    )
                    db.session.add(movie)
                    imported += 1

                db.session.commit()
                flash(f"Successfully imported {imported} movies!", 'success')
                if skipped:
                    flash(f"Skipped {skipped} entries (missing title)", 'warning')
                return redirect(url_for('movies_list'))

            except Exception as e:
                db.session.rollback()
                flash(f"Import failed: {str(e)}", 'error')
                return redirect(url_for('import_csv'))

        return render_template('import_csv.html')
    
    
    # ========================================================================
    # AUTHENTICATION ROUTES - TODO: Complete the registration route
    # ========================================================================
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """
        User registration route
        
        GET: Display registration form
        POST: Process registration, create user account
        
        Flow:
        1. Check if already logged in → redirect to home
        2. Get form data (username, email, password, confirm_password)
        3. Validate: all fields required, passwords match, min length
        4. Check: username not taken, email not taken
        5. Create user with HASHED password
        6. Auto-login the new user
        7. Redirect to home with success message
        """
        
        # ====================================================================
        # TODO 1: Check if user is already logged in
        # 
        # If user is already authenticated, redirect them to home page.
        # Use: current_user.is_authenticated
        # ====================================================================
        

        
        
        if request.method == 'POST':
            # ================================================================
            # TODO 2: Get form data
            # 
            # Get these values from the form:
            #   - username (strip whitespace)
            #   - email (strip whitespace, convert to lowercase)
            #   - password
            #   - confirm_password
            #
            # Pattern: request.form.get('field_name', '').strip()
            # ================================================================
            
            
            
            # ================================================================
            # TODO 3: Validation - Check required fields
            # 
            # If username, email, or password is empty:
            #   - Flash error message
            #   - Redirect back to register
            # ================================================================
            

            
            # ================================================================
            # TODO 4: Validation - Check passwords match
            # 
            # If password != confirm_password:
            #   - Flash error message: 'Passwords do not match!'
            #   - Redirect back to register
            # ================================================================
            

            
            # ================================================================
            # TODO 5: Validation - Check password length
            # 
            # If password is less than 6 characters:
            #   - Flash error message
            #   - Redirect back to register
            # ================================================================
            

            
            
            # ================================================================
            # TODO 6: Check if username already exists
            # 
            # Query database to check if username is taken:
            #   User.query.filter_by(username=username).first()
            # 
            # If it returns a user (not None), username is taken.
            # Flash error and redirect.
            # ================================================================
            

            
            
            # ================================================================
            # TODO 7: Check if email already exists
            # 
            # Same pattern as username check above.
            # ================================================================
            

            
            
            # ================================================================
            # TODO 8: Create new user with HASHED password
            # 
            # Steps:
            #   1. Create User object: User(username=username, email=email)
            #   2. Hash password: user.set_password(password)
            #   3. Add to session: db.session.add(user)
            #   4. Commit: db.session.commit()
            #
            # IMPORTANT: Use set_password(), don't set password_hash directly!
            # ================================================================
            
            # Create user object
            
            # Hash the password (THIS IS THE KEY LINE!)
            
            # Save to database
            
            
            # ================================================================
            # TODO 9: Auto-login and redirect
            # 
            # Steps:
            #   1. Log in the user: login_user(user)
            #   2. Flash welcome message
            #   3. Redirect to home page
            # ================================================================
            
            # Log the user in
            
            # Success message
            
            # Redirect to home
            return redirect(url_for('index'))
        
        
        # GET request - show the registration form
        return render_template('register.html')
    
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        return render_template('login.html')
    
    
    @app.route('/logout')
    def logout():
        return redirect(url_for('index'))    

    
    
    # ========================================================================
    # ERROR HANDLERS (No changes needed)
    # ========================================================================
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return render_template('errors/500.html'), 500
