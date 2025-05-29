from flask import g
from flask.sessions import SecureCookieSessionInterface
from application import create_app
from flask_cors import CORS  # Import Flask-CORS

app = create_app()

# Enable CORS for all routes and origins
CORS(app)

class CustomSessionInterface(SecureCookieSessionInterface):
    """Prevent creating session from API requests."""

    def save_session(self, *args, **kwargs):
        if g.get('login_via_header'):
            return
        return super(CustomSessionInterface, self).save_session(*args,
                                                                **kwargs)


app.session_interface = CustomSessionInterface()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # print_hi('PyCharm')
    app.run(host='0.0.0.0', port=5005, debug=True)
