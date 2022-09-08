from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    add_joke_text = State()
    all_jokes = State()
    my_jokes = State()
    edit_joke = State()
