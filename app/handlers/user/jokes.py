from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.states import States
from app.db.functions import Joke
from app.keyboards.inline import yes_or_no_keyboard, pagination_keyboard

router = Router()
joke_on_page = 2


@router.message(Command(commands=["add_joke"]))
async def add_joke_handler(message: Message, state: FSMContext):
    await message.answer("Напиши текст шутки")
    await state.set_state(States.add_joke_text)


@router.message(state=States.add_joke_text)
async def add_joke_text_handler(message: Message, state: FSMContext):
    await message.answer(
        f"Вы правда хотите добавить эту шутку?\n\n{message.text}",
        reply_markup=yes_or_no_keyboard()
    )
    await state.set_data({"text": message.text})


@router.callback_query(state=States.add_joke_text, text="yes")
async def add_joke_yes_handler(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await Joke.create(text=data["text"])
    await callback_query.message.edit_text("Шутка добавлена")
    await callback_query.answer("Шутка добавлена", show_alert=False)
    await state.clear()


@router.callback_query(state=States.add_joke_text, text="no")
async def add_joke_no_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Шутка не добавлена")
    await callback_query.answer("Шутка не добавлена", show_alert=False)
    await state.clear()


@router.message(Command(commands=["joke"]))
async def joke_handler(message: Message):
    joke = await Joke.get_random()
    await message.answer(joke.text)


@router.message(Command(commands=["all_jokes"]))
async def all_jokes_handler(message: Message, state: FSMContext):
    jokes = await Joke.get_all()
    text = "<b>Список всех шуток:</b> \n\n"
    await state.set_state(States.all_jokes)
    await state.set_data({"page": 1, "user": message.from_user.id})
    for joke in jokes[0:joke_on_page]:
        text += f"{joke.text} \n\n"

    await message.answer(text, reply_markup=pagination_keyboard(1, len(jokes) // 2 + 1))


@router.callback_query(state=States.all_jokes, text="page_next")
async def all_jokes_next_handler(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    jokes = await Joke.get_all()
    text = "<b>Список всех шуток:</b> \n\n"
    if len(jokes) // joke_on_page + 1 <= data["page"]:
        await callback_query.answer()
        return
    if data["user"] != callback_query.from_user.id:
        await callback_query.answer()
        return
    page = data["page"] + 1
    await state.set_data({"page": page, "user": callback_query.from_user.id})
    for joke in jokes[(page - 1) * joke_on_page:page * joke_on_page]:
        text += f"{joke.text} \n\n"

    await callback_query.message.edit_text(
        text, reply_markup=pagination_keyboard(page, len(jokes) // joke_on_page + 1)
    )
    await callback_query.answer()


@router.callback_query(state=States.all_jokes, text="page_prev")
async def all_jokes_prev_handler(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    jokes = await Joke.get_all()
    text = "<b>Список всех шуток:</b> \n\n"
    if data["page"] <= 1:
        await callback_query.answer()
        return
    if data["user"] != callback_query.from_user.id:
        await callback_query.answer()
        return
    page = data["page"] - 1
    await state.set_data({"page": page, "user": callback_query.from_user.id})
    for joke in jokes[(page - 1) * joke_on_page:page * joke_on_page]:
        text += f"{joke.text} \n\n"

    await callback_query.message.edit_text(
        text, reply_markup=pagination_keyboard(page, len(jokes) // joke_on_page + 1)
    )
    await callback_query.answer()
