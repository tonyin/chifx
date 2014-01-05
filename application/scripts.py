"""
scripts.py

Custom scripts.

"""

from google.appengine.api import users
from flask import url_for, flash

from collections import OrderedDict
from itertools import islice
from datetime import datetime

from models import Security, Order, Trade, Portfolio


BOOK_TOP_LEVELS = 4
START_POINTS = 1000

position = {
    'qb': 'Quarterbacks',
    'rb': 'Running Backs',
    'wr': 'Wide Receivers'
}

def check_user(view):
    c_user = users.get_current_user()
    if c_user:
        log = users.create_logout_url(url_for('index'))
    else:
        if view[0] in ('security'):
            log = users.create_login_url(url_for(view[0], pos=view[1]))
        elif view[0] in ('sec_info', 'edit_security'):
            log = users.create_login_url(url_for(view[0], pos=view[1], sec_id=view[2]))
        else:
            log = users.create_login_url(url_for(view[0]))
    
    # Create a new portfolio if new user
    if c_user:
        ptfs = Portfolio.query(Portfolio.user == c_user)
        ptfs = list(ptfs)
        if len(ptfs) == 0:
            ptf = Portfolio(
                user = c_user,
                points = START_POINTS
            )
            ptf.put()
            ptf_id = ptf.key.id()
            flash(u'Portfolio %s successfully created.' % ptf_id, 'success')
    
    return [c_user, log]

def construct_book(sec): 
    """Create buy and sell top depths"""
    # Get sorted
    b1 = Order.query(Order.security == sec, Order.buysell == 'Buy', Order.active == True, ancestor=sec.key).order(-Order.price)
    s1 = Order.query(Order.security == sec, Order.buysell == 'Sell', Order.active == True, ancestor=sec.key).order(Order.price)
    
    # BUYS
    # Combine price volume
    b2 = {}
    for order in b1:
        b2[order.price] = b2.get(order.price, 0) + order.volume
    b2 = OrderedDict(sorted(b2.items(), reverse = True))
    
    # Get top of buy book
    n = list(islice(b2.items(), 0, 1))
    b3 = {}
    if len(n) != 0:
        k = n[0][0]
        b3[k] = n[0][1]
    else:
        k = 0
        b3[k] = 0
    
    # Keep top BOOK_TOP_LEVELS number of prices
    for i in range(BOOK_TOP_LEVELS):
        if k - i - 1 <= 0:
            break
        b3[k-i-1] = b2.get(k-i-1, 0)
    b3 = OrderedDict(sorted(b3.items(), reverse = True))
    
    # SELLS
    # Combine price volume
    s2 = {}
    for order in s1:
        s2[order.price] = s2.get(order.price, 0) + order.volume
    s2 = OrderedDict(sorted(s2.items(), reverse = True))
    
    # Get top of sell book
    n = list(islice(s2.items(), 0, 1))
    s3 = {}
    if len(n) != 0:
        k = n[0][0]
        s3[k] = n[0][1]
    else:
        k = list(islice(b3.items(), 0, 1))[0][0]+1
        s3[k] = 0
    
    # Keep top BOOK_TOP_LEVELS number of prices
    for i in range(BOOK_TOP_LEVELS):
        s3[k+i+1] = s2.get(k+i+1, 0)
    s3 = OrderedDict(sorted(s3.items(), reverse = True))
    
    # Combine books
    book = {'buys':b3, 'sells':s3}
    
    return book

def match_orders(sec):
    """Match orders in cross"""
    # Get buy and sell lists
    b = Order.query(Order.security == sec, Order.buysell == 'Buy', Order.active == True, ancestor=sec.key).order(-Order.price, Order.timestamp)
    s = Order.query(Order.security == sec, Order.buysell == 'Sell', Order.active == True, ancestor=sec.key).order(Order.price, Order.timestamp)
    b = list(b)
    s = list(s)
    
    # Match orders until market uncrosses
    bn = 0
    sn = 0
    while(1):
        if bn + 1 > len(b):
            break
        if sn + 1 > len(s):
            break
        if b[bn].price >= s[sn].price:
            t = Trade()
            t.timestamp = datetime.utcnow()
            t.buy_user = b[bn].user
            t.sell_user = s[sn].user
            t.security = b[bn].security
            t.price = b[bn].price
            if b[bn].volume > s[sn].volume:
                t.volume = s[sn].volume
                b[bn] = b[bn].key.get()
                s[sn] = s[sn].key.get()
                b[bn].volume += -s[sn].volume
                s[sn].active = False
                b[bn].put()
                s[sn].put()
                sn += 1
                
            elif b[bn].volume < s[sn].volume:
                t.volume = b[bn].volume
                b[bn] = b[bn].key.get()
                s[sn] = s[sn].key.get()
                s[sn].volume += -b[bn].volume
                b[bn].active = False
                b[bn].put()
                s[sn].put()
                bn += 1
            elif b[bn].volume == s[sn].volume:
                t.volume = b[bn].volume
                b[bn] = b[bn].key.get()
                s[sn] = s[sn].key.get()
                b[bn].volume = 0
                s[sn].volume = 0
                b[bn].active = False
                s[sn].active = False
                b[bn].put()
                s[sn].put()
                bn += 1
                sn += 1
            t.put()
            
            # Update security last traded price
            #sec.last = t.price
            #sec.put()
            
            continue
        break
