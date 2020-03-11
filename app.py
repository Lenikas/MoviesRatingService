import typing
from movies.user import User
from movies.film import Film
from flask import Flask, render_template, jsonify


server = Flask(__name__)

FILM_STORAGE: typing.List[Film] = [Film("a", 2010, [5], ["abcd"]), Film("b", 2010, [5], ["abcd"])]


@server.route('/movies/api/v1.0/films', methods=['GET'])
def get_list_films():
    result = {}
    i = 0
    for film in FILM_STORAGE:
        result["FILM{}".format(i)] = (film.create_dict())
        i += 1
    return jsonify({'LIST OF FILMS': result})


if __name__ == "__main__":
    server.run(debug=True)
