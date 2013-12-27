"""
scripts.py

Custom scripts.

"""

from google.appengine.api import users
from flask import url_for

position = {
    'qb': 'Quarterbacks',
    'rb': 'Running Backs',
    'wr': 'Wide Receivers'
}

def check_user(view):
    user = users.get_current_user()
    if user:
        if view[0] == 'security':
            log = users.create_logout_url(url_for('index'))
        else:
            log = users.create_logout_url(url_for(view[0]))
    else:
        if view[0] == 'security':
            log = users.create_login_url(url_for(view[0], pos=view[1]))
        else:
            log = users.create_login_url(url_for(view[0]))
    return [user, log]
