from flask import Flask, render_template
import os
from dotenv import load_dotenv
from flask_login import LoginManager
from models import db, User, Task

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('APP_KEY', '')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.getenv('DB_PATH', 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)

import routes

@login_manager.user_loader
def user_loader(id):
    return User.query.get(id)

@login_manager.request_loader
def request_loader(request):
    id = request.form.get('id')
    return User.query.get(id)

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized', 401

if __name__ == "__main__":
    # database settings
    db.init_app(app)
    with app.app_context():
        db.create_all()
        User.create_default_users()
    
    # app start
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = os.getenv("APP_PORT", 5000)
    debug = os.getenv("APP_DEBUG", False)

    app.run(host=host, port=port, debug=debug)

