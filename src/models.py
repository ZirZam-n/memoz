from datetime import timedelta, date
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

from db import Base, session_gen

duration = [0 for _ in range(20)]
duration[0] = 0
duration[1] = 1
for i in range(2, 20):
    duration[i] = duration[i - 1] + duration[i - 2]


class Card(Base):
    __tablename__ = 'cards'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    creation_date = Column(Date)
    ask_date = Column(Date)
    stage = Column(Integer)

    def __init__(self, *args, **kwargs):
        inst = super().__init__(*args, **kwargs)
        inst.creation_date = date.today()
        inst.ask_date = date.today()

    def __repr__(self):
        return '<Card q="{}">'.format(self.question)

    def apply_solution(self, correct: bool):
        self.stage = self.stage + 1 if correct else 0
        self.ask_date = date.today() + timedelta(days=duration[self.stage])


def get_date_cards_queryset(today):
    session = session_gen()
    return session.query(Card).filter(Card.ask_date <= today), session


def get_date_cards(today):
    qs, session = get_date_cards_queryset(today)
    return qs.all(), session


def get_date_single_card(today):
    qs, session = get_date_cards_queryset(today)
    if qs.count() == 0:
        return None, session
    return qs.first(), session
