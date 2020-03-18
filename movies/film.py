from typing import Any, List, Union


class Film:
    def __init__(
        self, name: str, year: int, list_marks: List[int], list_reviews: List[str]
    ):
        self.name = name
        self.year = year
        self.marks = list_marks
        self.reviews = list_reviews

    def create_dict(self) -> Any:
        return {
            'name': self.name,
            'year': self.year,
            'reviews': self.reviews,
            'marks': self.marks,
        }

    def get_average_mark(self) -> Union[int, float]:
        if len(self.marks) == 0:
            return 0
        sum_marks: int = 0
        for mark in self.marks:
            sum_marks += mark
        return sum_marks / len(self.marks)

    def get_count_reviews(self) -> int:
        return len(self.reviews)

    def get_count_marks(self) -> int:
        return len(self.marks)
