"""
urls.py

URL dispatch route mappings and error handlers

"""
from flask import render_template

from application import app
from application import views


## URL dispatch rules
# App Engine warm up handler
# See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
app.add_url_rule('/_ah/warmup', 'warmup', view_func=views.warmup)

# Home page
app.add_url_rule('/', 'index', view_func=views.index)

# Security
app.add_url_rule('/security/<pos>', 'security', view_func=views.security)

# Securities
app.add_url_rule('/securities', 'securities', view_func=views.securities)

# Security info
app.add_url_rule('/security/<pos>/<int:sec_id>', 'sec_info', view_func=views.sec_info, methods=['GET', 'POST'])

# User portfolio
app.add_url_rule('/<nickname>/portfolio', 'portfolio', view_func=views.portfolio, methods=['GET', 'POST'])

# Delete order
app.add_url_rule('/<nickname>/portfolio/<ord_key>/delete', 'delete_order', view_func=views.delete_order, methods=['GET', 'POST'])

# Comment
app.add_url_rule('/comment', 'comment', view_func=views.comment, methods=['GET', 'POST'])

# Admin - securities
app.add_url_rule('/admin/security', 'admin_security', view_func=views.admin_security, methods=['GET', 'POST'])

# Admin - edit security
app.add_url_rule('/security/<pos>/<int:sec_id>/edit', 'edit_security', view_func=views.edit_security, methods=['GET', 'POST'])

# Admin - delete security
app.add_url_rule('/security/<pos>/<int:sec_id>/delete', view_func=views.delete_security, methods=['POST'])

# Admin - portfolio
app.add_url_rule('/admin/portfolio', 'admin_portfolio', view_func=views.admin_portfolio, methods=['GET', 'POST'])

# Admin - comment
app.add_url_rule('/admin/comment', 'admin_comment', view_func=views.admin_comment, methods=['GET'])

# Admin - trades
app.add_url_rule('/admin/trades', 'admin_trades', view_func=views.admin_trades, methods=['GET'])

## Error handlers
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
