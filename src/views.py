import curses
from _curses import KEY_SRESET
from datetime import date

from db import session_gen
from models import get_date_single_card, Card

STATE_HOME = 0
STATE_CARD = 1
STATE_ADD = 2
STATE_HALT = -1


def print_header(scr):
    welcome_msg = 'Welcome to MemoZ'
    height, width = scr.getmaxyx()
    bar = '+' + (width - 2) * '-' + '+'
    spaces = (width - 2 - len(welcome_msg)) // 2 * ' '
    scr.addstr(0, 0, bar)
    scr.addstr(1, 0, '|' + spaces + welcome_msg + spaces + '|')
    scr.addstr(2, 0, bar)
    return 4


def home_view(scr):
    scr.clear()
    current_line = print_header(scr)
    scr.addstr(current_line, 0, "cards are waiting 4 U")
    current_line += 2
    scr.addstr(current_line, 0, "press <s> to review a card")
    current_line += 1
    scr.addstr(current_line, 0, "press <a> to add a card")
    scr.refresh()

    key = scr.getkey()
    if key == 's':
        return STATE_CARD
    elif key == 'a':
        return STATE_ADD
    else:
        return STATE_HALT


def card_view(scr):
    card, session = get_date_single_card(date.today())
    if card is None:
        return STATE_HOME
    show_answer = False

    while True:
        scr.clear()
        current_line = print_header(scr)

        scr.addstr(current_line, 0, "Q: {}".format(card.question.decode('utf-8')))
        current_line += 1

        scr.addstr(current_line, 0, "A: {}".format(card.answer.decode('utf-8') if show_answer else '?!?!'))
        current_line += 2

        scr.addstr(current_line, 0, "press <s> to show/hide answer")
        current_line += 1

        scr.addstr(current_line, 0, "press <y> if you remember the answer")
        current_line += 1

        scr.addstr(current_line, 0, "press <n> if you don't remember the answer")

        scr.refresh()

        key = scr.getkey()
        if key == 's' or key == 'S':
            show_answer = not show_answer
        elif key == 'y' or key == 'Y':
            correct = True
            break
        elif key == 'n' or key == 'N':
            correct = False
            break

    card.apply_solution(correct)
    session.commit()
    session.close()
    return STATE_HOME


def add_view(scr):
    curses.echo()
    scr.clear()
    curses.curs_set(1)
    current_line = print_header(scr)

    scr.addstr(current_line, 0, "Enter the question:")
    current_line += 1
    scr.refresh()
    question = scr.getstr(current_line, 0, 100)
    current_line += 1

    scr.addstr(current_line, 0, "Enter the answer:")
    current_line += 1
    scr.refresh()
    answer = scr.getstr(current_line, 0, 100)
    current_line += 1

    card = Card(question=question, answer=answer)
    session = session_gen()
    session.add(card)
    session.commit()
    session.close()

    curses.curs_set(0)
    curses.noecho()
    return STATE_HOME


view_funcs = dict()
view_funcs[STATE_HOME] = home_view
view_funcs[STATE_CARD] = card_view
view_funcs[STATE_ADD] = add_view
