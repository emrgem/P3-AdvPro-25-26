# ============================================================================
# utilities.py - CineMatch Helper Functions
# ============================================================================

import requests
import os


# ============================================================================
# CSV IMPORT HELPERS
# ============================================================================

def parse_year(value):
    """Safely parse year from CSV data."""
    if not value:
        return None
    try:
        year = int(str(value).strip())
        if 1888 <= year <= 2030:
            return year
        return None
    except (ValueError, TypeError):
        return None


def parse_rating(value):
    """Safely parse rating (0.0-10.0) from CSV data."""
    if not value:
        return None
    try:
        rating = float(str(value).strip())
        if 0.0 <= rating <= 10.0:
            return rating
        return None
    except (ValueError, TypeError):
        return None


def get_csv_value(row, *keys):
    """Get value from CSV row, trying multiple possible column names."""
    for key in keys:
        if key in row and row[key]:
            return str(row[key]).strip()
    return None


# ============================================================================
# TMDB API HELPERS (Lesson 5.1)
# ============================================================================

def search_tmdb(query):
    """Search TMDB for movies matching the query string.
    
    Args:
        query: Movie title to search for
        
    Returns:
        List of movie results, or empty list on error
    """
    api_key = os.getenv('TMDB_API_KEY')
    url = "https://api.themoviedb.org/3/search/movie"

    try:
        response = requests.get(url, params={
            "api_key": api_key,
            "query": query
        })
        response.raise_for_status()
        data = response.json()
        return data.get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"TMDB API Error: {e}")
        return []


def get_tmdb_movie(tmdb_id):
    """Fetch full details for a specific movie by TMDB ID.
    
    Args:
        tmdb_id: The TMDB movie ID
        
    Returns:
        Movie data dictionary, or None on error
    """
    api_key = os.getenv('TMDB_API_KEY')

    try:
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        response = requests.get(url, params={"api_key": api_key})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"TMDB API Error: {e}")
        return None


def build_poster_url(poster_path, size="w500"):
    """Build a full TMDB poster URL from a poster path.
    
    Args:
        poster_path: The path from TMDB (e.g., '/abc123.jpg')
        size: Image size - w92, w185, w500, or original
        
    Returns:
        Full URL string, or placeholder if no poster available
    """
    if poster_path:
        return f"https://image.tmdb.org/t/p/{size}{poster_path}"
    return "https://placehold.co/500x750/1a1a2e/667eea?text=No+Poster"



# ============================================================
# AI HELPER — Google Gemini (Lesson 6.1)
# ============================================================
from google import genai
import os
from dotenv import load_dotenv
# Load environment variables BEFORE other imports
load_dotenv()
# Create a Gemini client (uses GEMINI_API_KEY from .env)
# gemini_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
gemini_client = genai.Client(api_key="AIzaSyC9n22LviKJinDfAFTyqguun70py3LOSis")
def get_ai_response(prompt):
    """Send a prompt to Gemini and get a text response."""
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None
    
def get_movie_recommendations(favorite_movies):
    """Get AI Recommendations based on user's favorites
    """
    if not favorite_movies:
        return """Add some favorite movies first, then I can 
                  give you personalized recommendations!
                """
    # Build a list of titles + genres for context
    movie_list = ""
    for movie in favorite_movies:
        movie_list += f"- {movie.title}"
        if movie.genre:
            movie_list += f" ({movie.genre})"
        if movie.rating:
            movie_list += f" [{movie.rating}]"
        movie_list += "\n"
    
    # Prepare the prompt for AI
    prompt = f"""
            Based on this user's favorite movies, recommend 5 movies they would enjoy.
            USER'S FAVORITES:
            {movie_list}
            For each recommendation, provide:
            - Movie title (year)
            - One sentence explaining why they'd like it based on their favorites.
            Rules:
            - Only suggest real movies that actually exist
            - Do not suggest any movie alredy in user's list
            - Keep explanations brief and specific
    """
    # Send it to Gemini
    return get_ai_response(prompt) 