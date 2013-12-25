"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""

from flaskext import wtf
from flaskext.wtf import validators
from wtforms.ext.appengine.ndb import model_form

from .models import Security


SecurityForm = model_form(Security, wtf.Form, field_args={
    'position': dict(validators=[validators.Required()]),
    'name': dict(validators=[validators.Required()]),
    'team': dict(),
})
