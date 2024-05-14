from peewee import *

database = MySQLDatabase('xiaohongdouapi', **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'host': 'localhost', 'user': 'xiaohongdouapi', 'password': 'DtcxSyP7aMW8Edws'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class User(BaseModel):
    create_time = DateTimeField(null=True)
    email = CharField(null=True)
    phone = CharField(null=True)
    update_time = DateTimeField(null=True)

    class Meta:
        table_name = 'User'

