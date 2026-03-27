"""Programm for your own favorite movies and there ranking to update everytime.
You can see overview as well
"""
from datetime import datetime
import random
import statistics
import movie_storage_sql
import movie_storage_sql as storage
import requests
from requests.exceptions import ConnectionError

API_KEY = "b7cbf531&"
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


def add_movie():
    """opportunity to add a new movie with the own ranking"""
    while True:
        new_movie = input("Enter new movie name: ")
        if movie_storage_sql.movie_exist(new_movie):
            print(f"{new_movie} already exists!")
            print()
            continue
        movie_name_length = len(new_movie)
        if new_movie.strip() == "" or movie_name_length < 1:
            print("Movie name is empty!\n")
            continue
        elif movie_name_length > 179: #longest movie name in history has 179 chars
            print(f"{new_movie} is title is too long. Take a shorter one!\n")
            continue
        try:
            PARAMS['t'] = new_movie
            response = requests.get(URL, params=PARAMS)
            movie_dict = response.json()
            title = movie_dict['Title']
            rating = float(movie_dict['imdbRating'])
            year = int(movie_dict['Year'])
            poster = movie_dict['Poster']
            movie_storage_sql.add_movie(title, year, rating, poster)
            print(f"Movie: {new_movie} succesfully added!")
            print()
            break
        except KeyError:
            print(f"Movie {new_movie} doesn`t exist")
            print()
        except ValueError:
            print("Sorry, your input is invalid! Try again!")
            print()
        except ConnectionError:
            print("No Connection to API!")
            print()


def delete_movie():
    """opportunity do delete one movie"""
    to_delete = input("Enter movie name to delete: ")
    movie_storage_sql.delete_movie(to_delete)
    print(f"Movie: {to_delete} successfully deleted!")
    print()


def update_movie():
    """opportunity to get a movie a new ranking"""
    while True:
        which_movie_to_update = input("Enter movie name: ")
        if not movie_storage_sql.movie_exist(which_movie_to_update):
            print(f"Movie: {which_movie_to_update} doesn't exist!")
            print()
            continue
        try:
            which_new_rating = float(input("Enter new movie rating (0-10) "))
            if not 0 < which_new_rating < 10.1:
                print(f"Rating: {which_new_rating} is invalid")
                print()
                continue
            movie_storage_sql.update_movie(which_movie_to_update,which_new_rating)
            print(f"{which_movie_to_update} successfully updated\n")
            break
        except ValueError:
            print("Sorry, your input is invalid! Try again!")
        print()


def stats():
    """shows some statistic overview of the movie list"""
    movies_list = movie_storage_sql.list_movies()
    if movie_storage_sql.is_movie_list_empty():
        print("Sorry, i can´t show something, Your Movie List is empty!")
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


def random_movie():
    """shows a random movie from the movie list"""
    movies_list = movie_storage_sql.list_movies()
    print(movies_list)
    if movie_storage_sql.is_movie_list_empty():
        print("Sorry, i can´t show something, Your Movie List is empty!")
        print()
        return
    movie_title = random.choice(list(movies_list.keys()))
    movie_year = movies_list[movie_title]['year']
    movie_rating = movies_list[movie_title]['rating']
    print(f"Your movie for tonight: {movie_title} ({movie_year}), its rated {movie_rating}")
    print()


def search_movie():
    """you can type in a part of a name of a movie and it will search for"""
    movies_list = movie_storage_sql.list_movies()
    while True:
        which_movie = input("Enter part of movie name: ")
        if (len(which_movie)) < 1 or which_movie == " ":
            print("Movie name is empty!\n")
            continue
        found = False
        for movie, infos in movies_list.items():
            if which_movie.lower() in movie.lower():
                print(f"{movie} ({infos[YEAR]}), {infos[RATING]}")
                found = True
        if not found:
            print(f"Movie with: {which_movie} doesn´t exist!")
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

def generate_website():
    """Takes the Movie Database, create for every movie a new
    list object, contains it with the html template
    and create the index.html file"""
    movies_dict = movie_storage_sql.list_movies()
    html_template= """
                        <html>
                            <head>
                                <title> My Movie App</title>
                                <link rel="stylesheet" href="style.css"/>
                            </head>
                            <body>
                                <div class="list-movies-title">
                                    <h1>My Movie App</h1>
                                </div>
                                <div>
                                    <ol class="movie-grid">"""
    html_end = """"</ol>
                    </div>
                </body>
            </html>"""
    for movie_title, details in movies_dict.items():
        html_movie = f"""<li>
                            <div class="movie">
                                <img class="movie-poster" src={details['poster']}>
                                <div class="movie-title">{movie_title}</div>
                                <div class="movie-year">{details['year']}</div>
                            </div>
                        </li>"""
        html_template += html_movie
    html_template += html_end
    with open("static/index.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    print("Website successfully created\n")

def main():
    """Dictionary to store the movies and the rating"""
    print("********** My Movies Database **********\n ")
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
            add_movie()
        elif choice == "3":
            delete_movie()
        elif choice == "4":
            update_movie()
        elif choice == "5":
            stats()
        elif choice == "6":
            random_movie()
        elif choice == "7":
            search_movie()
        elif choice == "8":
            sort_movies_by_rating()
        elif choice == "9":
            sort_movies_by_year()
        elif choice == "10":
            generate_website()
        user_need_to_enter = input("Press enter to continue\n ")
        if user_need_to_enter == " ":
            continue
        print("Invalid choice.")
        print()


if __name__ == "__main__":
    main()
