"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""

from flaskext import wtf
from flaskext.wtf import validators
from wtforms_appengine.ndb import model_form

from models import Security, Order, Portfolio, Comment


SecurityForm = model_form(Security, wtf.Form, field_args={
    'position': dict(validators=[validators.Required()]),
    'name': dict(validators=[validators.Required()]),
    'team': dict(),
})

OrderForm = model_form(Order, wtf.Form, field_args={
    'buysell': dict(validators=[validators.Required()]),
    'price': dict(validators=[validators.Required(), validators.NumberRange(min=1,max=100)]),
    'volume': dict(validators=[validators.Required(), validators.NumberRange(min=1,max=1000)]),
})

CommentForm = model_form(Comment, wtf.Form, field_args={
    'name': dict(validators=[validators.Required()]),
    'comment': dict(validators=[validators.Required()]),
})
