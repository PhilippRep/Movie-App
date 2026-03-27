from sqlalchemy import create_engine, text


# Define the database URL
DB_URL = "sqlite:///data/movies.db"

# Create the engine
engine = create_engine(DB_URL, echo=True, connect_args={"timeout": 10})

# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster TEXT NOT NULL
        )
    """))

    connection.commit()


TITLE = "Title"
YEAR = "Year of release"
RATING = "Rating"

def list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT title, year, rating, poster FROM movies"))
        movies = result.fetchall()

    return {row[0]: {"year": row[1], "rating": row[2], "poster": row[3]} for row in movies}


def add_movie(title, year, rating, poster):
    """Add a new movie to the database."""
    with engine.begin() as connection:
        try:
            connection.execute(text("INSERT INTO movies (title, year, rating, poster) VALUES (:title, :year, :rating, :poster)"),
                               {"title": title, "year": year, "rating": rating, "poster": poster})
        except KeyError as e:
            print(f"Movie {title} doesn't exist")
        except Exception as e:
            print(f"Error: {e}")

def delete_movie(title):
    """Delete a movie from the database."""
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM movies WHERE title= :title"),
                           {"title": title})

def update_movie(title, rating):
    """Update a movie's rating in the database."""
    with engine.begin() as connection:
        connection.execute(text(" UPDATE movies SET rating= :rating WHERE title= :title"),
                           {"title": title, "rating": rating})

def movie_exist(title):
    movies = list_movies()
    return title in movies

def is_movie_list_empty():
    """Prüft, ob Liste Inhalte hat oder nicht"""
    movies = list_movies()
    is_empty = False
    if (len(movies)) == 0:
        is_empty = True
    return is_empty





