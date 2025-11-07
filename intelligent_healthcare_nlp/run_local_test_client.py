from importlib import import_module

# Import the Flask app object without running the server
mod = import_module('src.web.app')
app = getattr(mod, 'app', None)
if app is None:
    print('No app object found in src.web.app')
else:
    client = app.test_client()
    resp = client.get('/test')
    print('status_code=', resp.status_code)
    print('data=', resp.get_data(as_text=True))
