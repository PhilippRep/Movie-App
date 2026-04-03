"""Programm for your own favorite movies and there ranking to update everytime.
You can see overview as well
"""
import os
import random
import statistics
from movie_storage import movie_storage_sql
import requests
from requests.exceptions import ConnectionError
import json
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("API_KEY")
URL = f"http://www.omdbapi.com/?apikey={API_KEY}&"
PARAMS = {
    "t": ""
}

TITLE = "title"
YEAR = "year"
RATING = "rating"
POSTER = "poster"


def exit_programm():
    """exit the full program and say bye"""
    print("---- Bye! ----")


def menu_movies():
    """shows the menue of all sucjects"""
    print(
        "Menu:\n"
        "0. Exit\n"
        "1. List movies\n"
        "2. Add movie\n"
        "3. Delete movie\n"
        "4. Update movie\n"
        "5. Stats\n"
        "6. Random movie\n"
        "7. Search movie\n"
        "8. Movies sorted by rating\n"
        "9. Movies sorted by year\n"
        "10. Generate website\n")


def list_movies():
    """shows all movies which are included in movie lists"""
    movies_list = movie_storage_sql.list_movies()
    length_of_movies = len(movies_list)
    print(f"{length_of_movies} movie(s) in total")
    for movie, values in movies_list.items():
        print(f"{movie}: {values['rating']}")
    print()


def add_movie(user):
    """opportunity to add a new movie with the own ranking"""
    while True:
        new_movie = input("Enter new movie name: ")
        if movie_storage_sql.movie_exist(new_movie):
            print(f"{user}, {new_movie} already exists!")
            print()
            continue
        movie_name_length = len(new_movie)
        if new_movie.strip() == "" or movie_name_length < 1:
            print("Movie name is empty!\n")
            continue
        elif movie_name_length > 179: #longest movie name in history has 179 chars
            print(f"{user}, {new_movie} is title is too long. Take a shorter one!\n")
            continue
        try:
            PARAMS['t'] = new_movie
            response = requests.get(URL, params=PARAMS)
            if response.status_code != 200:
                print("API request failed")
                continue
            movie_dict = response.json()
            if movie_dict.get("Response") == "False":
                print(f"{user}, Movie {new_movie} does not exist.")
                continue
            title = movie_dict.get('Title')
            rating = movie_dict.get('imdbRating')
            if rating == "N/A":
                rating = None
            else:
                rating = float(rating)
            year = movie_dict.get('Year')
            if year and year.isdigit():
                year = int(year)
            else:
                year = int(year.split("–")[0])
            poster = movie_dict.get('Poster')
            if not poster or poster == "N/A":
                poster = None
            imdb_id = movie_dict.get('imdbID')
            movie_storage_sql.add_movie(title, year, rating, poster, imdb_id)
            print(f"{user}, Movie: {new_movie} succesfully added!")
            print()
            break
        except KeyError:
            print(f"{user}, Movie {new_movie} doesn`t exist")
            print()
        except ValueError:
            print(f"Sorry {user}, your input is invalid! Try again!")
            print()
        except ConnectionError:
            print(f"Sorry {user}, No Connection to API!")
            print()


def delete_movie(user):
    """opportunity do delete one movie"""
    to_delete = input("Enter movie name to delete: ")
    deleted_count = movie_storage_sql.delete_movie(to_delete)
    if deleted_count == 0:
        return "Movie not found"
    else:
        return print(f"{user}, your Movie: {to_delete} is successfully deleted!\n")


def update_movie(user):
    """opportunity to get a movie a new ranking"""
    while True:
        which_movie_to_update = input("Enter movie name: ")
        if not movie_storage_sql.movie_exist(which_movie_to_update):
            print(f"{user}, this Movie: {which_movie_to_update} doesn't exist!")
            print()
            continue
        try:
            which_new_rating = float(input("Enter new movie rating (0-10) "))
            if not 0 < which_new_rating < 10.1:
                print(f"Rating: {which_new_rating} is invalid")
                print()
                continue
            movie_storage_sql.update_movie(which_movie_to_update, which_new_rating)
            print(f"{user}, the {which_movie_to_update} is successfully updated\n")
            break
        except ValueError:
            print(f"Sorry{user}, your input is invalid! Try again!")
        print()


def stats(user):
    """shows some statistic overview of the movie list"""
    movies_list = movie_storage_sql.list_movies()
    if movie_storage_sql.is_movie_list_empty():
        print(f"Sorry{user}, i can´t show something, Your Movie List is empty!")
        print()
        return
    length_of_movies = len(movies_list)
    ratings = []
    for value in movies_list.values():
        ratings.append(value[RATING])
    average_ratings = sum(ratings) / length_of_movies
    round_average_rating = round(average_ratings, 2)
    print(f"Average rating: {round_average_rating}")
    median_rating = statistics.median(ratings)
    round_median_rating = round(median_rating, 2)
    print(f"Median rating: {round_median_rating}")
    best_movie_rating = max(ratings)
    worst_movie_rating = min(ratings)
    for movie, values in movies_list.items():
        if values[RATING] == best_movie_rating:
            print(f"Best movie: {movie}, {best_movie_rating}")
        if values[RATING] == worst_movie_rating:
            print(f"Worst movie: {movie}, {worst_movie_rating}")
    print()


def random_movie(user):
    """shows a random movie from the movie list"""
    movies_list = movie_storage_sql.list_movies()
    print(movies_list)
    if movie_storage_sql.is_movie_list_empty():
        print(f"Sorry{user}, i can´t show something, Your Movie List is empty!")
        print()
        return
    movie_title = random.choice(list(movies_list.keys()))
    movie_year = movies_list[movie_title]['year']
    movie_rating = movies_list[movie_title]['rating']
    print(f"{user}, Your movie for tonight is\n: {movie_title} ({movie_year}), its rated {movie_rating}")
    print()


def search_movie(user):
    """you can type in a part of a name of a movie and it will search for"""
    movies_list = movie_storage_sql.list_movies()
    while True:
        which_movie = input("Enter part of movie name: ")
        if (len(which_movie)) < 1 or which_movie == " ":
            print(f" {user}, Movie name is empty!\n")
            continue
        found = False
        for movie, infos in movies_list.items():
            if which_movie.lower() in movie.lower():
                print(f"{movie} ({infos[YEAR]}), {infos[RATING]}")
                found = True
        if not found:
            print(f"{user}, Movie with: {which_movie} doesn´t exist!")
        print()
        break


def sort_movies_by_rating():
    """sort movie list by ranking from Good (10) to Bad (0)"""
    movies_dict = movie_storage_sql.list_movies()
    movies_list = list(movies_dict.items())
    sorted_upper_dict = sorted(movies_list, key=lambda movie: movie[1][RATING], reverse=True)
    for title, details in sorted_upper_dict:
        print(f"{title} ({details[YEAR]}): {details[RATING]}")
    print()


def sort_movies_by_year():
    """sort movie list by year from old to young or young to old. users choice"""
    movies_dict = movie_storage_sql.list_movies()
    while True:
        latest_or_youngest = input("Do you want the latest movies first? (Y/N)\n ")
        if latest_or_youngest == "Y":
            movies_list = list(movies_dict.items())
            sorted_upper_dict = sorted(movies_list, key=lambda movie: movie[1][YEAR], reverse=True)
            for title, details in sorted_upper_dict:
                print(f"{title} ({details[YEAR]}): {details[RATING]}")
            print()
            break
        elif latest_or_youngest == "N":
            movies_list = list(movies_dict.items())
            sorted_upper_dict = sorted(movies_list, key=lambda movie: movie[1][YEAR], reverse=False)
            for title, details in sorted_upper_dict:
                print(f"{title} ({details[YEAR]}): {details[RATING]}")
            print()
            break
        else:
            print("Please enter 'Y' or 'N'")

def generate_website(user):
    """Takes the Movie Database, create for every movie a new
    list object, contains it with the html template
    and create the index.html file"""
    movies_dict = movie_storage_sql.list_movies()
    html_template= f"""
                        <html>
                            <head>
                                <title> {user}'s Movie App</title>
                                <link rel="stylesheet" href="style.css"/>
                            </head>
                            <body>
                                <div class="list-movies-title">
                                    <h1>{user}'s Movie App</h1>
                                </div>
                                <div>
                                    <ol class="movie-grid">"""
    html_end = """</ol>
                    </div>
                </body>
            </html>"""
    for movie_title, details in movies_dict.items():
        html_movie = f"""<li>
                            <div class="movie">
                                <a href="https://www.imdb.com/de/title/{details['imdbID']}" target="_blank" class="movie-button">
                                    <img class="movie-poster" src={details['poster']}></a>
                                <div class="movie-title">{movie_title}</div>
                                <div class="movie-year">{details['year']}</div>
                                <div class="movie-rating">{details['rating']}</div>
                            </div>
                        </li>"""
        html_template += html_movie
    html_template += html_end
    with open("static/index.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"{user}, your Website is successfully created\n")

def users():
    """Get the date from a json file with all included users.
    you can choose you as user or create a new one with an own database and website"""
    with open("data/user.json", "r", encoding="utf-8") as f:
        all_users = json.load(f)
    full_users = list(all_users)
    print("Select a User:")
    for user in all_users:
        print(f"{user['id']}. {user['name']}")
    if all_users:
        highest_id = max(user["id"] for user in all_users)
    else:
        highest_id = 0
    print(f"{highest_id + 1}. Create new User")
    print()
    try:
        user_choice = int(input("Enter choice (Number): "))
    except ValueError:
        print("Invalid input. Please enter a number")
        return
    if user_choice == highest_id + 1:
        new_user = input("What is your name? ")
        new_user_dict = {
            "id": highest_id + 1,
            "name": new_user
        }
        full_users.append(new_user_dict)
        with open("data/user.json", "w", encoding="utf-8") as f:
            json.dump(full_users, f, indent=4)
        print(f"Welcome, {new_user}\n")
        return new_user
    for user in all_users:
        if user_choice == user['id']:
            print(f"Welcome back, {user['name']}\n")
            return user['name']

def main():
    """Dictionary to store the movies and the rating"""
    print("********** My Movies Database **********\n ")
    user = users()
    movie_storage_sql.init_db(user)
    while True:
        menu_movies()
        choice = input("Enter choice (0-10): ")
        print()
        if choice == "0":
            exit_programm()
            return
        if choice == "1":
            list_movies()
        elif choice == "2":
            add_movie(user)
        elif choice == "3":
            delete_movie(user)
        elif choice == "4":
            update_movie(user)
        elif choice == "5":
            stats(user)
        elif choice == "6":
            random_movie(user)
        elif choice == "7":
            search_movie(user)
        elif choice == "8":
            sort_movies_by_rating()
        elif choice == "9":
            sort_movies_by_year()
        elif choice == "10":
            generate_website(user)
        user_need_to_enter = input("Press enter to continue\n ")
        if user_need_to_enter == " ":
            continue
        print("Invalid choice.")
        print()


if __name__ == "__main__":
    main()
