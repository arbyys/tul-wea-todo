from flask import Flask, render_template
import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from models import db, User, Task

load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.getenv('DB_PATH', 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/')
def home():
    
    users = User.query.all()

    return render_template("pages/home.html", users=users)

if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all()
        User.create_default_users()
    
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = os.getenv("APP_PORT", 5000)
    debug = os.getenv("APP_DEBUG", False)

    app.run(host=host, port=port, debug=debug)
