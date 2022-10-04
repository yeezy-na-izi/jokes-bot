from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def get_author_keyboard(owner_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Автор", url=f"tg://user?id={owner_id}")
    return keyboard.as_markup()


def yes_or_no_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="Да", callback_data="yes"),
        InlineKeyboardButton(text="Нет", callback_data="no")
    )
    return keyboard.as_markup()


def pagination_keyboard(page, max_page):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="<", callback_data="page_prev"),
        InlineKeyboardButton(text=f"Страница {page}/{max_page}", callback_data="none"),
        InlineKeyboardButton(text=">", callback_data="page_next")
    )
    return keyboard.as_markup()


def add_my_jokes_keyboard(jokes, page, max_page):
    # jokes - список шуток длинной 5
    keyboard = InlineKeyboardBuilder()
    for joke in jokes:
        keyboard.row(
            InlineKeyboardButton(text=f"{joke.text[:15]}...", callback_data=f"joke_{joke.id}")
        )
    keyboard.row(
        InlineKeyboardButton(text="<", callback_data="my_jokes_prev"),
        InlineKeyboardButton(text=f"Страница {page}/{max_page}", callback_data="none"),
        InlineKeyboardButton(text=">", callback_data="my_jokes_next")
    )
    return keyboard.as_markup()


def joke_keyboard(joke_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="Удалить", callback_data=f"delete_{joke_id}"),
        InlineKeyboardButton(text="Изменить", callback_data=f"edit_{joke_id}")
    )
    keyboard.row(
        InlineKeyboardButton(text="Назад", callback_data="back")
    )
    return keyboard.as_markup()
