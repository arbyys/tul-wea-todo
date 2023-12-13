import flask
import flask_login
from models import User, Task
from __main__ import app
from werkzeug.security import check_password_hash

@app.route("/")
def home():
    users = User.query.all()

    return flask.render_template("pages/home.html", users=users)

@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        return flask.render_template("pages/login.html")
    else: # POST
        username = flask.request.form['username']
        password = flask.request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('list'))

        return 'Bad login'

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('home'))

@app.route('/list')
@flask_login.login_required
def list():
    tasks = Task.query.filter_by(user_id=flask_login.current_user.id).order_by(Task.created_at.desc()).all()

    return flask.render_template("pages/list.html", tasks=tasks)

@app.route('/browse')
@flask_login.login_required
def browse():
    return flask.render_template("pages/browse.html")