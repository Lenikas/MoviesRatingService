from typing import List
from movies.film import Film


class User:
    def __init__(self, name: str, list_reviews: List[str], identification: int):
        self.name = name
        self.reviews = list_reviews
        self.id = identification

    def add_film(self, film: Film, storage: List[Film]):
        storage.append(film)

    def add_mark(self):

