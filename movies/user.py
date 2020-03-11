from typing import List, Dict, Any
from movies.film import Film


class User:
    def __init__(self, name: str, reviews: Dict, identification: int):
        self.name = name
        self.reviews = reviews
        self.id = identification

    def add_review(self, film: Film, storage: List[Film], data: Any):
        needed_film = ""
        for item in storage:
            if item.name == film.name and item.year == film.year:
                needed_film = item
                break
        if needed_film != "":
            if type(data) == str:
                needed_film.reviews.append(data)
            if type(data) == int:
                needed_film.marks.append(data)
            needed_film.average = needed_film.get_average_mark()
            self.reviews[film.name] = (data,)
        else:
            return "This film not exist, please add this"

    def add_film(self, name: str, year: int, storage: List[Film]):
        for film in storage:
            if film.name == name and int(film.year) == year:
                return "This film already exist"
        film = Film(name, year, [], [], 0)
        storage.append(film)
