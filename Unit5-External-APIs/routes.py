# ============================================================================
# routes.py - CineMatch Route Definitions
# ============================================================================

from flask import render_template, request, redirect, url_for, flash
from utilities import (
    get_csv_value,
    parse_year,
    parse_rating,
    search_tmdb,
    get_tmdb_movie,
    build_poster_url,
)
import csv
from models import db, Movie, User
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
import requests, os


def admin_required(f):
    """Decorator that requires user to be logged in AND be an admin."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        if not current_user.is_admin:
            flash("Admin access required.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return decorated_function


def register_routes(app):
    """Register all routes with the Flask app"""

    # ========================================================================
    # PUBLIC ROUTES
    # ========================================================================

    @app.route("/")
    def index():
        """Home page with featured movies"""
        movies = Movie.query.order_by(Movie.rating.desc()).limit(6).all()
        return render_template("index.html", movies=movies)

    @app.route("/about")
    def about():
        """About CineMatch page"""
        return render_template("about.html")

    # ========================================================================
    # MOVIE BROWSE & DETAIL
    # ========================================================================

    @app.route("/movies")
    def movies_list():
        """Browse all movies with search, filter, and pagination"""
        query = request.args.get("query", "").strip()
        genre = request.args.get("genre", "").strip()
        year = request.args.get("year", type=int)
        min_rating = request.args.get("min_rating", type=float)
        page = request.args.get("page", 1, type=int)
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
            "movies.html",
            movies=pagination.items,
            pagination=pagination,
            genres=genres,
            query=query,
            selected_genre=genre,
            selected_year=year,
            selected_min_rating=min_rating,
        )

    @app.route("/movie/<int:id>")
    def movie_detail(id):
        """Display detailed information for a single movie"""
        movie = Movie.query.get_or_404(id)
        return render_template("movie_detail.html", movie=movie)

    # ========================================================================
    # MOVIE CRUD (Admin Only)
    # ========================================================================

    @app.route("/add_movie", methods=["GET", "POST"])
    @admin_required
    def add_movie():
        """Add a new movie to the database"""
        if request.method == "POST":
            title = request.form.get("title")
            if not title:
                flash("Title is required!", "error")
                return redirect(url_for("add_movie"))

            movie = Movie(
                title=title,
                year=request.form.get("year", type=int),
                genre=request.form.get("genre"),
                director=request.form.get("director"),
                rating=request.form.get("rating", type=float),
                description=request.form.get("description"),
                poster_url=request.form.get("poster_url")
                or f"https://placehold.co/300x450/gray/white?text={title.replace(' ', '+')}",
            )
            db.session.add(movie)
            db.session.commit()
            flash(f'✓ Movie "{movie.title}" added successfully!', "success")
            return redirect(url_for("movies_list"))

        return render_template("add_movie.html")

    @app.route("/movie/<int:id>/edit", methods=["GET", "POST"])
    @admin_required
    def edit_movie(id):
        """Edit an existing movie"""
        movie = Movie.query.get_or_404(id)

        if request.method == "POST":
            movie.title = request.form.get("title")
            movie.year = request.form.get("year", type=int)
            movie.genre = request.form.get("genre")
            movie.director = request.form.get("director")
            movie.rating = request.form.get("rating", type=float)
            movie.description = request.form.get("description")
            movie.poster_url = (
                request.form.get("poster_url")
                or f"https://placehold.co/300x450/gray/white?text={movie.title.replace(' ', '+')}"
            )

            db.session.commit()
            flash(f'✓ Movie "{movie.title}" updated successfully!', "success")
            return redirect(url_for("movies_list"))

        return render_template("edit_movie.html", movie=movie)

    @app.route("/movie/<int:id>/delete", methods=["POST"])
    @admin_required
    def delete_movie(id):
        """Delete a movie from the database"""
        movie = Movie.query.get_or_404(id)
        title = movie.title
        db.session.delete(movie)
        db.session.commit()
        flash(f'🗑 Movie "{title}" was deleted.', "success")
        return redirect(url_for("movies_list"))

    @app.route("/import_csv", methods=["GET", "POST"])
    @admin_required
    def import_csv():
        """Bulk import movies from a CSV file"""
        if request.method == "POST":
            file = request.files.get("csv_file")
            if not file or not file.filename.lower().endswith(".csv"):
                flash("Please upload a valid .csv file", "error")
                return redirect(url_for("import_csv"))

            try:
                content = file.read().decode("utf-8", errors="replace")
                lines = content.splitlines()
                reader = csv.DictReader(lines)

                imported = 0
                skipped = 0

                for row in reader:
                    title = get_csv_value(
                        row, "Series_Title", "Title", "movie_title", "name", "title"
                    )
                    if not title:
                        skipped += 1
                        continue

                    movie = Movie(
                        title=title,
                        year=parse_year(
                            get_csv_value(row, "Released_Year", "year", "Year")
                        ),
                        genre=get_csv_value(row, "Genre", "genre", "genres"),
                        director=get_csv_value(
                            row, "Director", "director", "directed_by"
                        ),
                        rating=parse_rating(
                            get_csv_value(
                                row, "IMDB_Rating", "rating", "imdb_rating", "Rating"
                            )
                        ),
                        description=get_csv_value(
                            row, "Overview", "description", "plot", "Plot", "Summary"
                        ),
                        poster_url=get_csv_value(
                            row, "Poster_Link", "poster_url", "Poster"
                        )
                        or f"https://placehold.co/300x450/gray/white?text={title.replace(' ', '+')}",
                    )
                    db.session.add(movie)
                    imported += 1

                db.session.commit()
                flash(f"Successfully imported {imported} movies!", "success")
                if skipped:
                    flash(f"Skipped {skipped} entries (missing title)", "warning")
                return redirect(url_for("movies_list"))

            except Exception as e:
                db.session.rollback()
                flash(f"Import failed: {str(e)}", "error")
                return redirect(url_for("import_csv"))

        return render_template("import_csv.html")

    # ========================================================================
    # AUTHENTICATION
    # ========================================================================

    @app.route("/register", methods=["GET", "POST"])
    def register():
        """User registration"""
        if current_user.is_authenticated:
            return redirect(url_for("index"))

        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            if not username or not email or not password:
                flash("All fields are required!", "error")
                return redirect(url_for("register"))

            if password != confirm_password:
                flash("Passwords do not match!", "error")
                return redirect(url_for("register"))

            if len(password) < 6:
                flash("Password must be at least 6 characters.", "error")
                return redirect(url_for("register"))

            if User.query.filter_by(username=username).first():
                flash("Username is already taken! Please choose another one.", "error")
                return redirect(url_for("register"))

            if User.query.filter_by(email=email).first():
                flash(
                    "Email is already registered! Please choose another one.", "error"
                )
                return redirect(url_for("register"))

            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash(f"Welcome to Cinematch, {username}", "success")
            return redirect(url_for("index"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """User login"""
        if current_user.is_authenticated:
            return redirect(url_for("index"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                login_user(user)
                flash(f"Welcome back, {user.username}!", "success")
                return redirect(url_for("index"))
            else:
                flash("Invalid username and password", "error")

        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        """User logout"""
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("index"))

    @app.route("/profile")
    @login_required
    def profile():
        """User profile page"""
        return render_template("profile.html", user=current_user)

    # ========================================================================
    # TMDB SEARCH & IMPORT
    # ========================================================================
    @app.route("/search_tmdb")
    @admin_required
    def search_tmdb_page():
        query = request.args.get("query", "").strip()
        results = []
        if query:
            results = search_tmdb(query)
        return render_template(
            "search_tmdb.html",
            results=results,
            query=query,
            build_poster_url=build_poster_url,
        )

    @app.route("/import_from_tmdb/<int:tmdb_id>", methods=["POST"])
    @admin_required
    def import_from_tmdb(tmdb_id):
        # check if already imported
        if Movie.query.filter_by(tmdb_id=tmdb_id).first():
            flash("This movie is already in the database!", "warning")
            return redirect(url_for("search_tmdb_page"))
        # Fetch the full details from TMDB
        data = get_tmdb_movie(tmdb_id)
        if not data:
            flash("Could not fetch the movie from TMDB!", "error")
            return redirect(url_for("search_tmdb_page"))
        # Extract the year from release date ( "2010-07-15 -> 2010")
        year = None
        if data.get("release_date") and len(data["release_date"]) >= 4:
            year = int(data["release_date"][:4])
        # Get first genre name
        genre = None
        if data.get("genres") and len(data["genres"]) > 0:
            genre = data["genres"][0]["name"]
        # create a Movie object and save it to database
        movie = Movie(
            title=data.get("title", "unknown"),
            year=year,
            genre=genre,
            rating=round(data.get("vote_average", 0), 1),
            description=data.get("overview"),
            poster_url=build_poster_url(data.get("poster_path")),
            tmdb_id=tmdb_id,
        )
        db.session.add(movie)
        db.session.commit()
        flash(f" Imported {movie.title} from TMDB", "success")
        return redirect(url_for("search_tmdb_page"))

    @app.route("/favorite/<int:id>", methods=["POST"])
    @login_required
    def favorite(id):
        # Add a movie to the user's favorites
        movie = Movie.query.get_or_404(id)
        if movie not in current_user.favorite_movies:
            current_user.favorite_movies.append(movie)
            db.session.commit()
            flash(f'💖 Added "{movie.title}" to favorites!', "success")
        return redirect(url_for("movie_detail", id=id))

    @app.route("/unfavorite/<int:id>", methods=["POST"])
    @login_required
    def unfavorite(id):
        # Remove a movie from the user's favorites
        movie = Movie.query.get_or_404(id)
        if movie in current_user.favorite_movies:
            current_user.favorite_movies.remove(movie)
            db.session.commit()
            flash(f'❌ Removed "{movie.title}" from favorites!', "info")
        return redirect(url_for("movie_detail", id=id))

    # ========================================================================
    # WATCHLIST (Lesson 5.4)
    # ========================================================================

    @app.route("/watchlist/add/<int:id>", methods=["POST"])
    @login_required
    def add_to_watchlist(id):
        """Add a movie to the user's watchlist"""
        movie = Movie.query.get_or_404(id)

        if movie not in current_user.watchlist_movies:
            current_user.watchlist_movies.append(movie)
            db.session.commit()
            flash(f'📋 Added "{movie.title}" to watchlist!', "success")

        return redirect(url_for("movie_detail", id=id))

    @app.route("/watchlist/remove/<int:id>", methods=["POST"])
    @login_required
    def remove_from_watchlist(id):
        """Remove a movie from the user's watchlist"""
        movie = Movie.query.get_or_404(id)

        if movie in current_user.watchlist_movies:
            current_user.watchlist_movies.remove(movie)
            db.session.commit()
            flash(f'Removed "{movie.title}" from watchlist.', "info")

        return redirect(url_for("movie_detail", id=id))

    # ========================================================================
    # DASHBOARD (Lesson 5.5)
    # ========================================================================
    @app.route("/dashboard")
    @login_required
    def dashboard():
        user = current_user
        favs = user.favorite_movies
        watch = user.watchlist_movies

        # Stats
        fav_count = len(favs)
        watch_count = len(watch)

        # Average rating of favorites(only movies that have rating)
        rated_favs = [movie.rating for movie in favs if movie.rating]
        avg_rating = round(sum(rated_favs) / len(rated_favs), 1) if rated_favs else 0

        # Top Genre from favorites
        genres = [movie.genre for movie in favs if movie.genre]
        top_genre = max(set(genres), key=genres.count) if genres else None

        return render_template(
            "dashboard.html",
            user=user,
            favs=favs,
            watch=watch,
            fav_count=fav_count,
            watch_count=watch_count,
            avg_rating=avg_rating,
            top_genre=top_genre,
        )

    # ========================================================================
    # PROFILE SETTINGS (Lesson 5.6)
    # ========================================================================
    @app.route("/settings", methods=["GET", "POST"])
    @login_required
    def settings():
        """Edit user profile settings"""
        if request.method == "GET":
            return render_template("settings.html", user=current_user)
        if request.method == "POST":
            action = request.form.get("action")
            # Update Email
            if action == "update_email":
                new_email = request.form.get("email", "").strip().lower()
                if not new_email:
                    flash("Email can not be empty!", "error")
                elif new_email == current_user.email:
                    flash("You chose the same email!", "error")
                elif User.query.filter_by(email=new_email).first():
                    flash("The email is already taken!", "error")
                else:
                    current_user.email = new_email
                    db.session.commit()
                    flash("Email Updated!", "success")
            return redirect(url_for("settings"))

    # ========================================================================
    # ERROR HANDLERS
    # ========================================================================

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/500.html"), 500
