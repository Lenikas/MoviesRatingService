import typing
from movies.user import User
from movies.film import Film
from flask import Flask, render_template, jsonify, request, abort


server = Flask(__name__)

FILM_STORAGE: typing.List[Film] = []
USER_STORAGE: typing.List[User] = []


@server.route('/movies/api/v1.0/add', methods=['POST'])
def create_film():
    if not request.json or 'name' not in request.json or "year" not in request.json:
        abort(400)
    user = User("lexa", {}, 1)
    name_film = request.json.get('name')
    year_film = request.json.get('year')
    user.add_film(name_film, year_film, FILM_STORAGE)
    return jsonify({'Film': {'name': name_film, 'year': year_film}}), 201


@server.route('/movies/api/v1.0/films', methods=['GET'])
def get_list_films():
    result = {}
    i = 0
    for film in FILM_STORAGE:
        result["FILM{}".format(i)] = (film.create_dict())
        i += 1
    return jsonify({'LIST OF FILMS': result})


@server.route('/movies/api/v1.0/add_review', methods=['POST'])
def add_review():
    user = User("lexa", {}, 1)
    name_film: str = request.json.get('name')
    year_film: int = int(request.json.get('year'))
    review_film: str = request.json.get('review')
    user.add_review(Film(name_film, year_film),
                    FILM_STORAGE, review_film)
    return jsonify({'ADD_REVIEW': {'name': name_film, 'review': review_film}})


@server.route('/movies/api/v1.0/add_mark', methods=['POST'])
def add_mark():
    user = User("lexa", {}, 1)
    name_film: str = request.json.get('name')
    year_film: int = int(request.json.get('year'))
    mark_film: int = int(request.json.get('mark'))
    user.add_review(Film(name_film, year_film),
                    FILM_STORAGE, mark_film)
    return jsonify({'ADD_MARK': {'name': name_film, 'mark': mark_film}})


@server.route('/movies/api/v1.0/get_average/<name>/<year>', methods=['GET'])
def get_average(name, year):
    for film in FILM_STORAGE:
        if film.name == name and int(year) == film.year:
            return jsonify({'AVERAGE': film.average})
    return jsonify({'ERROR': "This film not exist"}), 404


if __name__ == "__main__":
    server.run(debug=True)
