from typing import List


class Film:
    def __init__(self, name: str, year: int, list_marks: List[input],
                 list_reviews: List[str], average_mark: float = 0,):
        self.name = name
        self.year = year
        self.marks = list_marks
        self.average = average_mark
        self.reviews = list_reviews

    def create_dict(self):
        return {
            'name': self.name,
            'year': self.year,
            'reviews': self.reviews,
            'marks': self.marks,
            'average_mark': self.get_average_mark()
        }

    def add_comment(self, text: str):
        self.reviews.append(text)

    def add_rating(self, mark: int):
        self.marks.append(mark)

    def add_year(self, year: int):
        self.year = year

    def get_average_mark(self):
        if len(self.marks) == 0:
            self.average = 0
        else:
            sum_marks: int = 0
            for mark in self.marks:
                sum_marks += mark
            self.average = sum_marks / len(self.marks)



