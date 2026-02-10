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
