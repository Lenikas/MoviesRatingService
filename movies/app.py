from typing import Any, List, Union

from flask import Flask, jsonify, make_response, request
from flask_httpauth import HTTPBasicAuth
from movies.film import Film
from movies.user import User

server = Flask(__name__)
auth = HTTPBasicAuth()

FILM_STORAGE: List[Film] = []
USER_STORAGE: List[User] = []


@auth.get_password
def get_password(username: str) -> Union[str, None]:
    for user in USER_STORAGE:
        if user.name == username:
            return str(user.password)
    return None


@auth.error_handler
def unauthorized() -> Any:
    return make_response(jsonify({'ERROR': 'Unauthorized access'}), 401)


@server.route('/movies/api/v1.0/create_account', methods=['POST'])
def add_user() -> Any:
    if (
        not request.json
        or 'username' not in request.json
        or 'password' not in request.json
    ):
        return (
            jsonify({'ERROR': 'Invalid data, please give username and password'}),
            400,
        )

    name_user = request.json.get('username')
    try:
        find_user(name_user, USER_STORAGE)
        return (
            jsonify(
                {
                    'ERROR': 'User with the same name already exist, please choose another name'
                }
            ),
            400,
        )
    except ValueError:
        pass
    password = str(request.json.get('password'))
    #   с хэшами пока не получилось сделать
    USER_STORAGE.append(User(name_user, password, {}))
    return jsonify({'ACTION': {'username': name_user}})


def find_user(username: str, user_storage: List[User]) -> User:
    """Смотрим наличие пользователя в хранилище"""
    for user in user_storage:
        if user.name == username:
            return user
    raise ValueError


@server.route('/movies/api/v1.0/<username>/add', methods=['POST'])
#   @auth.login_required
def create_film(username: str) -> Any:
    """Создаем фильм,если такой уже есть, получаем соответсвующее информирование"""
    if not request.json or 'name' not in request.json or 'year' not in request.json:
        return (
            jsonify({'ERROR': 'Invalid data, please give name and year of film'}),
            400,
        )

    try:
        user = find_user(username, USER_STORAGE)
    except ValueError:
        return jsonify({'ERROR': 'User does not exist'}), 400

    name_film = request.json.get('name')
    year_film = request.json.get('year')
    film = user.add_film(name_film, year_film, FILM_STORAGE)
    if film is None:
        return jsonify({'ERROR': 'This film already exist'})

    FILM_STORAGE.append(film)
    return jsonify({'FILM': {'name': name_film, 'year': year_film}})


@server.route('/movies/api/v1.0/films', methods=['GET'])
#   @auth.login_required
def get_list_films() -> Any:
    """Получаем все имеющиеся фильмы"""
    result = {}
    i = 0
    for film in FILM_STORAGE:
        result['FILM{}'.format(i)] = film.create_dict()
        i += 1
    return jsonify({'LIST OF FILMS': result})


@server.route('/movies/api/v1.0/<username>/add_review', methods=['POST'])
#   @auth.login_required
def add_review(username: str) -> Any:
    """Добавляем ревью к фильму или получаем информацию, что такого фильма еще нет"""
    if (
        not request.json
        or 'name' not in request.json
        or 'year' not in request.json
        or 'review' not in request.json
    ):
        return (
            jsonify(
                {
                    'ERROR': 'Invalid data, please give name and year of film and your review'
                }
            ),
            400,
        )

    try:
        user = find_user(username, USER_STORAGE)
    except ValueError:
        return jsonify({'ERROR': 'User does not exist'}), 404

    name_film: str = request.json.get('name')
    year_film: int = int(request.json.get('year'))
    review_film: str = request.json.get('review')
    film = user.add_review_or_mark(
        Film(name_film, year_film, [], []), FILM_STORAGE, review_film
    )

    if film is None:
        return jsonify({'ERROR': 'This film does not exist'}), 404

    return jsonify({'ADD_REVIEW': {'name': name_film, 'review': review_film}})


@server.route('/movies/api/v1.0/<username>/add_mark', methods=['POST'])
#   @auth.login_required
def add_mark(username: str) -> Any:
    """Добавляем оценку к фильму или получаем информацию, что такого фильма еще нет"""
    if (
        not request.json
        or 'name' not in request.json
        or 'year' not in request.json
        or 'mark' not in request.json
    ):
        return (
            jsonify(
                {
                    'ERROR': 'Invalid data, please give name and year of film and your mark'
                }
            ),
            400,
        )

    try:
        user = find_user(username, USER_STORAGE)
    except ValueError:
        return jsonify({'ERROR': 'User does not exist'}), 404

    name_film: str = request.json.get('name')
    year_film: int = int(request.json.get('year'))
    mark_film: int = int(request.json.get('mark'))
    film = user.add_review_or_mark(
        Film(name_film, year_film, [], []), FILM_STORAGE, mark_film
    )
    if film is None:
        return (
            jsonify(
                {
                    'ERROR': 'This film does not exist or you mark less 0 or more zero, check it'
                }
            ),
            404,
        )

    return jsonify({'ADD_MARK': {'name': name_film, 'mark': mark_film}})


def find_film(name: str, year: str, film_storage: List[Film]) -> Film:
    """Ищем фильм в хранилище по параметрам: название и год"""
    for film in film_storage:
        if film.name == name and int(year) == film.year:
            return film
    raise ValueError


@server.route('/movies/api/v1.0/get_average/<name>/<year>', methods=['GET'])
#   @auth.login_required
def get_average(name: str, year: str) -> Any:
    """Получаем среднюю оценку фильма по его названию и году
    или узнаем,что фильма нет в хранилище"""
    try:
        film: Film = find_film(name, year, FILM_STORAGE)
    except ValueError:
        return jsonify({'ERROR': 'This film not exist'}), 404
    return jsonify({'AVERAGE': film.get_average_mark()})


@server.route('/movies/api/v1.0/get_count_reviews/<name>/<year>', methods=['GET'])
#   @auth.login_required
def get_count_reviews(name: str, year: str) -> Any:
    """Получаем количество отзывов фильма по его названию и году
    или узнаем,что фильма нет в хранилище"""
    try:
        film: Film = find_film(name, year, FILM_STORAGE)
    except ValueError:
        return jsonify({'ERROR': 'This film not exist'}), 404
    return jsonify({'COUNT_REVIEWS': film.get_count_reviews()})


@server.route('/movies/api/v1.0/get_count_marks/<name>/<year>', methods=['GET'])
#   @auth.login_required
def get_count_marks(name: str, year: str) -> Any:
    """Получаем количество оценок фильма по его названию и году
    или узнаем,что фильма нет в хранилище"""
    try:
        film: Film = find_film(name, year, FILM_STORAGE)
    except ValueError:
        return jsonify({'ERROR': 'This film not exist'}), 404
    return jsonify({'COUNT_MARKS': film.get_count_marks()})


@server.route('/movies/api/v1.0/get_films/substring/<substring>', methods=['GET'])
#   @auth.login_required
def get_films_substring(substring: str) -> Any:
    """Получаем список фильмов найденных по подстроке в названии"""
    result: List[str] = []
    for film in FILM_STORAGE:
        if film.name.find(substring) != -1:
            result.append(film.name)
    return jsonify({'FILMS': result})


@server.route('/movies/api/v1.0/get_films/average/<average>', methods=['GET'])
#   @auth.login_required
def get_films_average(average: str) -> Any:
    """Получаем список фильмов, у которых средняя оценка совпадает с запросом"""
    result: List[str] = []
    try:
        float(average)
    except ValueError:
        return jsonify({'ERROR': 'Average rating can not be a string value'}), 404
    for film in FILM_STORAGE:
        if film.get_average_mark() == float(average):
            result.append(film.name)
    return jsonify({'FILMS': result})
