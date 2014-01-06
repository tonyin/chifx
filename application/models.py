"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb


class Security(ndb.Model):
    """Security entity"""
    position = ndb.StringProperty(required=True, choices=["qb","rb","wr"])
    name = ndb.StringProperty(required=True)
    team = ndb.StringProperty()

class Order(ndb.Model):
    """Orders on a security"""
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.UserProperty(required=True)
    security = ndb.StructuredProperty(Security)
    buysell = ndb.StringProperty(required=True, choices=["Buy","Sell"])
    price = ndb.IntegerProperty(required=True)
    volume = ndb.IntegerProperty(required=True)
    active = ndb.BooleanProperty(required=True)

class Trade(ndb.Model):
    """Trades which are matched Orders"""
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    buy_user = ndb.UserProperty()
    sell_user = ndb.UserProperty()
    security = ndb.StructuredProperty(Security)
    price = ndb.IntegerProperty(required=True)
    volume = ndb.IntegerProperty(required=True)

class Portfolio(ndb.Model):
    """Portfolio storing order and trade info"""
    user = ndb.UserProperty(required=True)
    points = ndb.IntegerProperty(required=True)
