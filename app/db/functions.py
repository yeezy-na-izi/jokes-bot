from tortoise.exceptions import DoesNotExist

from app.db import models
import random


class User(models.User):
    @classmethod
    async def is_registered(cls, telegram_id: int) -> [models.User, bool]:
        try:
            return await cls.get(telegram_id=telegram_id)
        except DoesNotExist:
            return False

    @classmethod
    async def register(cls, telegram_id) -> [models.User, bool]:
        await User(telegram_id=telegram_id).save()

    @classmethod
    async def get_count(cls) -> int:
        return await cls.all().count()


class Joke(models.Joke):
    @classmethod
    async def get_random(cls) -> models.Joke:
        return random.choice(await cls.all())

    @classmethod
    async def get_all(cls) -> [models.Joke]:
        return await cls.all()
