import flask
import flask_login
from models import db, User, Task
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

        flask.flash('bad credentials!', 'danger')
        return flask.redirect(flask.url_for('login'))

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('home'))

@app.route('/list')
@flask_login.login_required
def list():
    #tasks = Task.query.filter_by(user_id=flask_login.current_user.id).order_by(Task.created_at.desc()).all()

    return flask.render_template("pages/list.html")

@app.route('/list/tasks')
@flask_login.login_required
def tasks():
    tasks = Task.query.filter_by(user_id=flask_login.current_user.id).order_by(Task.created_at.desc()).all()
    return flask.render_template("components/tasks.html", tasks=tasks)


@app.route("/list/create", methods=["POST"])
@flask_login.login_required
def create():
    title = flask.request.form.get('title')
    content = flask.request.form.get('content')
    if (title and content):
        new_task = Task(title=title, content=content, user_id=flask_login.current_user.id)
        db.session.add(new_task)
        db.session.commit()

        #tasks = Task.query.filter_by(user_id=flask_login.current_user.id).order_by(Task.created_at.desc()).all()
        
        return '', 201, {'HX-Trigger': 'newTask'}
        #return flask.render_template("components/tasks.html", tasks=tasks)

    
    flask.flash('missing title or content', 'danger')
    return '', 400, {'HX-Trigger': 'error'}
    return flask.redirect(flask.url_for('list'))

@app.route('/browse')
@flask_login.login_required
def browse():
    return flask.render_template("pages/browse.html")