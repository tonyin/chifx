"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb


class ExampleModel(ndb.Model):
    """Example Model"""
    example_name = ndb.StringProperty(required=True)
    example_description = ndb.TextProperty(required=True)
    added_by = ndb.UserProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)

class Security(ndb.Model):
    """Security entity"""
    position = ndb.StringProperty(required=True, choices=["qb","rb","wr"])
    name = ndb.StringProperty(required=True)
    team = ndb.StringProperty()

class Order(ndb.Model):
    """Orders on a security"""
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.UserProperty(required=True)
    buysell = ndb.BooleanProperty(required=True)
    security = ndb.StructuredProperty(Security)
    price = ndb.FloatProperty(required=True)
    volume = ndb.IntegerProperty(required=True)
    active = ndb.BooleanProperty(required=True)

class Trade(ndb.Model):
    """Trades which are matched Orders"""
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    buy_order = ndb.StructuredProperty(Order)
    sell_order = ndb.StructuredProperty(Order)

class Portfolio(ndb.Model):
    """Portfolio storing order and trade info"""
    user = ndb.UserProperty(required=True)
    orders = ndb.StructuredProperty(Order, repeated=True)
    trades = ndb.StructuredProperty(Trade, repeated=True)
