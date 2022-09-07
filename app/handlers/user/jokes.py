from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.states import States

from app.db.functions import Joke

router = Router()


@router.message(Command(commands=["add_joke"]))
async def add_joke_handler(message: Message, state: FSMContext):
    await message.answer("Напиши текст шутки")
    await state.set_state(States.add_joke_text)


@router.message(state=States.add_joke_text)
async def add_joke_text_handler(message: Message, state: FSMContext):
    await Joke.create(text=message.text)
    await message.answer("Шутка успешно добавлена")
    await state.clear()


@router.message(Command(commands=["joke"]))
async def joke_handler(message: Message):
    joke = await Joke.get_random()
    await message.answer(joke.text)


@router.message(Command(commands=["all_jokes"]))
async def all_jokes_handler(message: Message):
    jokes = await Joke.get_all()
    text = "<b>Список всех шуток:</b> \n\n"
    for joke in jokes:
        text += f"{joke.text} \n\n"
    await message.answer(text)
