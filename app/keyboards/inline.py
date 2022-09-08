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
        InlineKeyboardButton(text="Назад", callback_data=f"page_prev"),
        InlineKeyboardButton(text=f"Страница {page}/{max_page}", callback_data="none"),
        InlineKeyboardButton(text="Вперёд", callback_data=f"page_next")
    )
    return keyboard.as_markup()
