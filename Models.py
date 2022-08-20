from peewee import Model, CharField, DateField, IntegerField, ForeignKeyField, DateTimeField
from db import db
import datetime

class BaseModel(Model):
    class Meta:
        database = db

class Person(BaseModel):
    name = CharField()
    money = IntegerField()

class Transaction(BaseModel):
    user = ForeignKeyField(Person, backref='transaction')
    transaction = CharField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    amount = IntegerField()
    sent_by = CharField()
    received_by = CharField()

class Product(BaseModel):
    name = CharField()
    price = IntegerField()
    description = CharField()   
    image = CharField()