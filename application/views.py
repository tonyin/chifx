"""
views.py

URL route handlers

"""
from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import request, render_template, flash, url_for, redirect

from flask_cache import Cache

from application import app
from decorators import login_required, admin_required
from forms import SecurityForm, OrderForm
from models import Security, Order


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
    return render_template('security.html', pos=pos, user=user, title=title, securities=securities)

@login_required
def sec_info(pos, id):
    """Individual security info"""
    user = scripts.check_user(['sec_info', pos])
    sec = Security.get_by_id(id)
    orders = Order.query(Order.security == sec)
    form = OrderForm()
    if form.validate_on_submit():
        ord = Order(
            user = user[0],
            buysell = form.buysell.data,
            security = sec,
            price = form.price.data,
            volume = form.volume.data,
            active = True
        )
        try:
            ord.put()
            ord_id = ord.key.id()
            flash(u'Order %s successfully saved.' % ord_id, 'success')
            return redirect(url_for('sec_info', pos=pos, id=id))
        except CapabilityDisabledError:
            flash(u'App Engine Datastore is currently in read-only mode.', 'info')
            return redirect(url_for('sec_info', pos=pos, id=id))
    return render_template('sec_info.html', user=user, sec=sec, orders=orders, form=form)

@admin_required
def edit_security(security_id):
    """Edit security attributes"""
    security = Security.get_by_id(security_id)
    form = SecurityForm(obj=security)
    pos = security.position
    if request.method == "POST":
        if form.validate_on_submit():
            security.position = form.data.get('position')
            security.name = form.data.get('name')
            security.team = form.data.get('team')
            security.put()
            flash(u'Security %s successfully saved.' % security_id, 'success')
            return redirect(url_for('security', pos=security.position))
    return render_template('edit_security.html', security=security, form=form)

@admin_required
def delete_security(security_id):
    """Delete security"""
    security = Security.get_by_id(security_id)
    pos = security.position
    try:
        security.key.delete()
        flash(u'Security %s successfully deleted.' % security_id, 'success')
        return redirect(url_for('security', pos))
    except CapabilityDisabledError:
        flash(u'App Engine Datastore is currently in read-only mode.', 'info')
        return redirect(url_for('security', pos))

@admin_required
def admin_list():
    """Admin create/edit view"""
    user = scripts.check_user(['admin_list'])
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
            return redirect(url_for('admin_list'))
        except CapabilityDisabledError:
            flash(u'App Engine Datastore is currently in read-only mode.', 'info')
            return redirect(url_for('admin_list'))
    return render_template('admin_list.html', user=user, securities=securities, form=form)

def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''

