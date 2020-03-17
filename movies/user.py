from typing import Any, Dict, List, Union

from movies.film import Film


class User:
    def __init__(
        self, name: str, password: str, reviews: Dict[str, str],
    ):
        self.name = name
        self.password = password
        self.reviews = reviews

    def add_review_or_mark(
        self, film: Film, storage: List[Film], data: Any
    ) -> Union[Film, None]:
        needed_film = None
        for item in storage:
            if item.name == film.name and item.year == film.year:
                needed_film = item
                break

        if needed_film is not None:
            if isinstance(data, str):
                needed_film.reviews.append(data)

            if isinstance(data, int):
                if data < 0 or data > 10:
                    return None
                needed_film.marks.append(data)

            self.reviews[film.name + str(film.year)] = data
            return needed_film
        return None

    def add_film(self, name: str, year: int, storage: List[Film]) -> Union[Film, None]:
        for film in storage:
            if film.name == name and int(film.year) == year:
                return None
        film = Film(name, year, [], [])
        return film
