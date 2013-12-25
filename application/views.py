"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import request, render_template, flash, url_for, redirect

from flask_cache import Cache

from application import app
from decorators import login_required, admin_required
from forms import ExampleForm, SecurityForm
from models import ExampleModel, Security


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

# Globals
import globals

def index():
    """Main page"""
    return render_template('index.html')

@login_required
def security(pos):
    """List all securities of pos"""
    title = globals.position[pos]
    securities = Security.query(Security.position == pos)
    form = SecurityForm()
    if form.validate_on_submit():
        sec = Security(
            position=form.position.data,
            name=form.name.data,
            team=form.team.data
        )
        try:
            sec.put()
            sec_id = sec.key.id()
            flash(u'Security %s successfully saved.' % sec_id, 'success')
            return redirect(url_for('security', pos=pos))
        except CapabilityDisabledError:
            flash(u'App Engine Datastore is currently in read-only mode.', 'info')
            return redirect(url_for('security', pos=pos))
    return render_template('security.html', pos=pos, title=title, securities=securities, form=form)

@login_required
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

@login_required
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

def say_hello(username):
    """Contrived example to demonstrate Flask's url routing capabilities"""
    return 'Hello %s' % username

@login_required
def list_examples():
    """List all examples"""
    examples = ExampleModel.query()
    form = ExampleForm()
    if form.validate_on_submit():
        example = ExampleModel(
            example_name=form.example_name.data,
            example_description=form.example_description.data,
            added_by=users.get_current_user()
        )
        try:
            example.put()
            example_id = example.key.id()
            flash(u'Example %s successfully saved.' % example_id, 'success')
            return redirect(url_for('list_examples'))
        except CapabilityDisabledError:
            flash(u'App Engine Datastore is currently in read-only mode.', 'info')
            return redirect(url_for('list_examples'))
    return render_template('list_examples.html', examples=examples, form=form)


@login_required
def edit_example(example_id):
    example = ExampleModel.get_by_id(example_id)
    form = ExampleForm(obj=example)
    if request.method == "POST":
        if form.validate_on_submit():
            example.example_name = form.data.get('example_name')
            example.example_description = form.data.get('example_description')
            example.put()
            flash(u'Example %s successfully saved.' % example_id, 'success')
            return redirect(url_for('list_examples'))
    return render_template('edit_example.html', example=example, form=form)


@login_required
def delete_example(example_id):
    """Delete an example object"""
    example = ExampleModel.get_by_id(example_id)
    try:
        example.key.delete()
        flash(u'Example %s successfully deleted.' % example_id, 'success')
        return redirect(url_for('list_examples'))
    except CapabilityDisabledError:
        flash(u'App Engine Datastore is currently in read-only mode.', 'info')
        return redirect(url_for('list_examples'))


@admin_required
def admin_only():
    """This view requires an admin account"""
    return 'Super-seekrit admin page.'


@cache.cached(timeout=60)
def cached_examples():
    """This view should be cached for 60 sec"""
    examples = ExampleModel.query()
    return render_template('list_examples_cached.html', examples=examples)


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''

