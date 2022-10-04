import aiohttp
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.config import Config
from app.db.functions import Joke, User
from app.keyboards.inline import yes_or_no_keyboard, pagination_keyboard, add_my_jokes_keyboard, joke_keyboard
from app.states import States

router = Router()
joke_on_page = 2
answer_dict = {
    'да': 'Пизда',
    'мда, треш': 'Пиздец',
    'пиздец': 'Мда, треш',
    'нет': 'Пидора ответ',
    'пидора ответ': 'Шлюхи аргумент',
    'шлюхи аргумент': 'Аргумент не нужен, пидор обнаружен',
    'аргумент не нужен, пидор обнаружен': 'Пидр засекречен твой анал не вечен',
    'пидр засекречен твой анал не вечен': 'Мой анал не вечен твой анал помечен',
    'мой анал не вечен твой анал помечен': 'Пошел нахуй',
}
headers = {
    'authority': 'vt.tiktok.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '^\\^Google',
    'dnt': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 '
                  'Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '^\\?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-US,en;q=0.9',
}

cookies = {
    'tt_webid_v2': '6935199750005992455',
    'tt_webid': '6935199750005992455',
    's_v_web_id': 'verify_kt9s1t0p_8eYwKjg1_4rZb_8qLr_9aXn_1j2kWm7xMxY6',
}


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
    user = await User.get(telegram_id=callback_query.from_user.id)
    await Joke.create(text=data["text"], user=user)
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


@router.message(Command(commands=["my_jokes"]))
async def my_jokes_handler(message: Message, state: FSMContext):
    user = await User.get(telegram_id=message.from_user.id)
    jokes = await Joke.filter(user=user)
    if not jokes:
        await message.answer("У вас нет добавленных шуток")
        return

    text = "<b>Список всех твоих шуток:</b> \n\n"

    await state.set_state(States.my_jokes)
    await state.set_data({"page": 1, "user": message.from_user.id})
    await message.answer(
        text,
        reply_markup=add_my_jokes_keyboard(jokes=jokes[:5], page=1, max_page=len(jokes) // 5 + 1)
    )


@router.callback_query(text="my_jokes_next")
async def my_jokes_next_handler(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = await User.get(telegram_id=callback_query.from_user.id)
    jokes = await Joke.filter(user=user)

    if len(jokes) // 5 + 1 <= data["page"]:
        await callback_query.answer()
        return
    if data["user"] != callback_query.from_user.id:
        await callback_query.answer()
        return

    page = data["page"] + 1
    await state.set_data({"page": page, "user": callback_query.from_user.id})

    text = "<b>Список всех твоих шуток:</b> \n\n"

    await callback_query.message.edit_text(
        text, reply_markup=add_my_jokes_keyboard(
            jokes=jokes[5 * (page - 1):5 * page],
            page=page,
            max_page=len(jokes) // 5 + 1
        )
    )
    await callback_query.answer()


@router.callback_query(text="my_jokes_prev")
async def my_jokes_prev_handler(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = await User.get(telegram_id=callback_query.from_user.id)
    jokes = await Joke.filter(user=user)

    if data["page"] <= 1:
        await callback_query.answer()
        return
    if data["user"] != callback_query.from_user.id:
        await callback_query.answer()
        return

    page = data["page"] - 1
    await state.set_data({"page": page, "user": callback_query.from_user.id})

    text = "<b>Список всех твоих шуток:</b> \n\n"

    await callback_query.message.edit_text(
        text, reply_markup=add_my_jokes_keyboard(
            jokes=jokes[5 * (page - 1):5 * page],
            page=page,
            max_page=len(jokes) // 5 + 1
        )
    )
    await callback_query.answer()


@router.callback_query(text="back")
async def back_handler(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data["user"] != callback_query.from_user.id:
        await callback_query.answer()
        return
    user = await User.get(telegram_id=data["user"])
    jokes = await Joke.filter(user=user)
    if not jokes:
        await callback_query.message.edit_text("У вас нет добавленных шуток")
        return

    text = "<b>Список всех твоих шуток:</b> \n\n"

    await state.set_state(States.my_jokes)
    await state.set_data({"page": 1, "user": callback_query.from_user.id})
    await callback_query.message.edit_text(
        text
    )
    await callback_query.message.edit_reply_markup(
        add_my_jokes_keyboard(jokes=jokes[:5], page=1, max_page=len(jokes) // 5 + 1)
    )


@router.callback_query(lambda x: x.data.startswith("joke_") and x.data[5:].isdigit(), state=States.my_jokes)
async def joke_callback_handler(callback_query: CallbackQuery, state: FSMContext):
    joke_id = int(callback_query.data[5:])
    joke = await Joke.get(id=joke_id)
    data = await state.get_data()
    if data["user"] != callback_query.from_user.id:
        await callback_query.answer()
        return

    text = (
        f'<b>Шутка</b> \n\n'
        f'{joke.text}'
    )
    await callback_query.message.edit_text(text)
    await callback_query.message.edit_reply_markup(joke_keyboard(joke_id=joke_id))

    await callback_query.answer()


@router.callback_query(lambda x: x.data.startswith("delete_") and x.data[7:].isdigit(), state=States.my_jokes)
async def delete_joke_handler(callback_query: CallbackQuery, state: FSMContext):
    joke_id = int(callback_query.data[7:])
    joke = await Joke.get(id=joke_id)
    data = await state.get_data()
    if data["user"] != callback_query.from_user.id:
        await callback_query.answer()
        return

    await joke.delete()
    await callback_query.message.edit_text("Шутка удалена")


@router.callback_query(lambda x: x.data.startswith("edit_") and x.data[5:].isdigit(), state=States.my_jokes)
async def edit_joke_handler(callback_query: CallbackQuery, state: FSMContext):
    joke_id = int(callback_query.data[5:])
    data = await state.get_data()
    if data["user"] != callback_query.from_user.id:
        await callback_query.answer()
        return

    await state.set_state(States.edit_joke)
    await state.set_data({"joke_id": joke_id, "user": callback_query.from_user.id})
    await callback_query.message.edit_text("Введите новый текст шутки")

    await callback_query.answer()


@router.message(state=States.edit_joke)
async def edit_joke_text_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    if data["user"] != message.from_user.id:
        return

    joke_id = data["joke_id"]
    joke = await Joke.get(id=joke_id)
    joke.text = message.text
    await joke.save()
    await state.clear()
    await message.answer("Шутка изменена")


@router.message()
async def all_message(message: Message, bot: Bot, config: Config):
    text = message.text

    if text.startswith('https://www.tiktok.com/') or text.startswith('https://vt.tiktok.com/'):
        try:
            video = await return_tik_tok_video(text)
            await message.reply_video(video)
        except KeyError:
            await message.reply("Видео не найдено")
            await bot.send_message(config.settings.owner_id, f"Видео не найдено: {text}")
        except Exception as e:
            print(e)

    if text.lower() in answer_dict:
        await message.reply(answer_dict[text.lower()])


async def return_tik_tok_video(link) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(link, headers=headers, cookies=cookies) as resp:
            video_id = resp.url.path.split('/')[-1].split('?')[0]

        link = f'https://www.tiktok.com/api/item/detail/?itemId={video_id}'
        async with session.get(link, headers=headers, cookies=cookies) as resp:
            if resp.status == 200:
                data = await resp.json()
                download_url = data['itemInfo']['itemStruct']['video']['downloadAddr']
        return download_url
