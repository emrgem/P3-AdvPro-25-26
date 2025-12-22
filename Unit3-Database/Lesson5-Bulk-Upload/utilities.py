# ============================================================================
# HELPER FUNCTIONS FOR CSV IMPORT
# ============================================================================

def parse_year(value):
    """
    Safely parse year from CSV data.
    
    Why we need this:
    - CSV data comes as strings, but our database expects integers
    - Some rows might have empty values, invalid text, or weird formats
    - This function handles all edge cases gracefully
    """
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
    """
    Safely parse rating from CSV data.
    
    Why we need this:
    - Ratings might be strings like "9.3" or empty
    - We want 0.0-10.0 range for our database
    """
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
    """
    Get value from CSV row, trying multiple possible column names.
    
    Why we need this:
    - Different CSV files use different column names
    - IMDB uses "Series_Title", others might use "title" or "Title"
    - This function tries all variations and returns the first match
    """
    for key in keys:
        if key in row and row[key]:
            return str(row[key]).strip()
    return None