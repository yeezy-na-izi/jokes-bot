from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.BigIntField(pk=True)
    telegram_id = fields.BigIntField()


class Joke(Model):
    id = fields.BigIntField(pk=True)
    text = fields.TextField()
