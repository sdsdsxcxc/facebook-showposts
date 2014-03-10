from webapp2_extras.routes import RedirectRoute
import handlers

secure_scheme = 'https'

_routes = [
    RedirectRoute('/', handlers.HomeHandler, name='MainPage', strict_slash=True),
]

def get_routes():
    return _routes

def add_routes(app):
    if app.debug:
        secure_scheme = 'http'
    for r in _routes:
        app.router.add(r)
