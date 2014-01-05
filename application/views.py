"""
views.py

URL route handlers

"""
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import request, render_template, flash, url_for, redirect

from flask_cache import Cache

from application import app
from decorators import login_required, admin_required
from forms import SecurityForm, OrderForm
from models import Security, Order, Trade, Portfolio


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

# Custom scripts
import scripts

def index():
    """Main page"""
    user = scripts.check_user(['index'])
    return render_template('index.html', user=user)

@login_required
def security(pos):
    """List all securities of pos"""
    user = scripts.check_user(['security', pos])
    title = scripts.position[pos]
    securities = Security.query(Security.position == pos)
    return render_template('security.html', user=user, pos=pos, title=title, securities=securities)

@login_required
def sec_info(pos, sec_id):
    """Individual security info"""
    user = scripts.check_user(['sec_info', pos, sec_id])
    sec = Security.get_by_id(sec_id)
    book = scripts.construct_book(sec)
    orders = Order.query(Order.security == sec, Order.active == True).order(-Order.timestamp)
    form = OrderForm()
    if form.validate_on_submit():
        portfolio = Portfolio.query(Portfolio.user == user[0])
        ptf = portfolio.get()
        new_points = ptf.points - form.volume.data
        if new_points >= 0:
            ptf.points = new_points
            ptf.put()
            ord = Order(
                user = user[0],
                buysell = form.buysell.data,
                security = sec,
                price = form.price.data,
                volume = form.volume.data,
                active = True,
                parent = sec.key
            )
            try:
                ord.put()
                ord_id = ord.key.id()
                flash(u'Order %s successfully saved.' % ord_id, 'success')
                scripts.match_orders(sec)
                return redirect(url_for('sec_info', pos=pos, sec_id=sec_id))
            except CapabilityDisabledError:
                flash(u'App Engine Datastore is currently in read-only mode.', 'info')
                return redirect(url_for('sec_info', pos=pos, sec_id=sec_id))
        else:
            flash(u'Only %d points left.' % ptf.points)
    return render_template('sec_info.html', user=user, pos=pos, sec=sec, book=book, orders=orders, form=form)

@admin_required
def edit_security(pos, sec_id):
    """Edit security attributes"""
    user = scripts.check_user(['edit_security', pos, sec_id])
    sec = Security.get_by_id(sec_id)
    form = SecurityForm(obj=sec)
    if request.method == "POST":
        if form.validate_on_submit():
            sec.position = form.data.get('position')
            sec.name = form.data.get('name')
            sec.team = form.data.get('team')
            sec.put()
            flash(u'Security %s successfully saved.' % sec_id, 'success')
            return redirect(url_for('admin_security'))
    return render_template('edit_security.html', user=user, sec=sec, form=form)

@admin_required
def delete_security(pos, sec_id):
    """Delete security"""
    sec = Security.get_by_id(sec_id)
    try:
        sec.key.delete()
        flash(u'Security %s successfully deleted.' % sec_id, 'success')
        return redirect(url_for('admin_security'))
    except CapabilityDisabledError:
        flash(u'App Engine Datastore is currently in read-only mode.', 'info')
        return redirect(url_for('admin_security'))

@login_required
def portfolio(nickname):
    """List all points, orders, and trades in a user's portfolio"""
    user = scripts.check_user(['portfolio'])
    orders = Order.query(Order.user == user[0], Order.active == True).order(Order.security.name, -Order.timestamp)
    trades = Trade.query(ndb.OR(Trade.buy_user == user[0], Trade.sell_user == user[0]))
    portfolio = Portfolio.query(Portfolio.user == user[0])
    ptf = portfolio.get()
    return render_template('portfolio.html', user=user, orders=orders, trades=trades, portfolio=ptf)

@login_required
def delete_order(nickname, ord_key):
    """Delete order"""
    user = scripts.check_user(['portfolio'])
    try:
        portfolio = Portfolio.query(Portfolio.user == user[0])
        ptf = portfolio.get()
        ord = ndb.Key(urlsafe=ord_key)
        ptf.points = ptf.points + ord.get().volume
        ptf.put()
        ndb.Key(urlsafe=ord_key).delete()
        flash(u'Order %s successfully deleted.' % ord_key, 'success')
        return redirect(url_for('portfolio', nickname=nickname))
    except CapabilityDisabledError:
        flash(u'App Engine Datastore is currently in read-only mode.', 'info')
        return redirect(url_for('portfolio', nickname=nickname))

@admin_required
def admin_security():
    """Admin manage securities"""
    user = scripts.check_user(['admin_security'])
    securities = Security.query()
    form = SecurityForm()
    if form.validate_on_submit():
        sec = Security(
            position = form.position.data,
            name = form.name.data,
            team = form.team.data
        )
        try:
            sec.put()
            sec_id = sec.key.id()
            flash(u'Security %s successfully saved.' % sec_id, 'success')
            return redirect(url_for('admin_security'))
        except CapabilityDisabledError:
            flash(u'App Engine Datastore is currently in read-only mode.', 'info')
            return redirect(url_for('admin_security'))
    return render_template('admin_security.html', user=user, securities=securities, form=form)

@admin_required
def admin_portfolio():
    """Admin manage portfolios"""
    user = scripts.check_user(['admin_portfolio'])
    portfolios = Portfolio.query()
    return render_template('admin_portfolio.html', user=user, portfolios=portfolios)

@admin_required
def edit_portfolio():
    return

def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''
