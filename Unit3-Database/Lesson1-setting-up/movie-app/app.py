"""
CineMatch - Movie Discovery Platform
Lesson 3.1 STARTER CODE
"""
from flask import Flask, render_template, request, redirect, url_for, flash
from sample_movies import movies

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

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
