# ============================================================================
# DATABASE INITIALIZATION (No changes needed)
# ============================================================================
from models import db, Movie

def init_db(app):
    """Create database tables and load sample data if empty"""
    with app.app_context():
        db.create_all()
        print("✓ Database tables created/verified")

        if Movie.query.count() == 0:
            print("🎬 Loading initial sample movies...")

            samples = [
                Movie(
                    title="Inception",
                    year=2010,
                    genre="Sci-Fi",
                    director="Christopher Nolan",
                    rating=8.8,
                    description="A thief who steals corporate secrets through dream-sharing technology...",
                    poster_url="https://placehold.co/300x450/667eea/ffffff?text=Inception"
                ),
                Movie(
                    title="The Matrix",
                    year=1999,
                    genre="Sci-Fi",
                    director="Wachowski Sisters",
                    rating=8.7,
                    description="A computer hacker learns the truth about his reality...",
                    poster_url="https://placehold.co/300x450/764ba2/ffffff?text=The+Matrix"
                ),
                Movie(
                    title="The Shawshank Redemption",
                    year=1994,
                    genre="Drama",
                    director="Frank Darabont",
                    rating=9.3,
                    description="Two imprisoned men find friendship and eventual redemption...",
                    poster_url="https://placehold.co/300x450/4CAF50/ffffff?text=Shawshank"
                ),
                Movie(
                    title="The Dark Knight",
                    year=2008,
                    genre="Action",
                    director="Christopher Nolan",
                    rating=9.0,
                    description="Batman faces the Joker in Gotham City...",
                    poster_url="https://placehold.co/300x450/4facfe/ffffff?text=Dark+Knight"
                ),
                Movie(
                    title="Pulp Fiction",
                    year=1994,
                    genre="Crime",
                    director="Quentin Tarantino",
                    rating=8.9,
                    description="Various interconnected stories of criminals in Los Angeles...",
                    poster_url="https://placehold.co/300x450/FF6B6B/ffffff?text=Pulp+Fiction"
                ),
                Movie(
                    title="Interstellar",
                    year=2014,
                    genre="Sci-Fi",
                    director="Christopher Nolan",
                    rating=8.6,
                    description="A team of explorers travel through a wormhole...",
                    poster_url="https://placehold.co/300x450/f093fb/ffffff?text=Interstellar"
                ),
            ]

            db.session.bulk_save_objects(samples)
            db.session.commit()
            print(f"  Added {len(samples)} sample movies")
