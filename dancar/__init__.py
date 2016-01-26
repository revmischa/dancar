from flask import Flask
app = Flask(__name__, static_folder="../ui/www", static_url_path="/static")

# main app setup
from setup import setup_app, setup_users
setup_app(app)

# setup users (now that DB is loaded)
from setup import db
setup_users(app)

# load routes
import dancar.views

