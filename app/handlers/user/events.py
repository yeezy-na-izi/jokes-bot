from aiogram import Router
from aiogram.types import Message

router = Router()


@router.edited_message()
async def edited_message_handler(edited_message: Message):
    await edited_message.reply("Аааа - пидр, что-то изменил🤬")
