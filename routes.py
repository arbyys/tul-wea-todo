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

@app.route('/logout', methods=["GET"])
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('home'))

@app.route('/list', methods=["GET"])
@flask_login.login_required
def list():
    return flask.render_template("pages/list.html")

@app.route('/browse')
@flask_login.login_required
def browse():
    return flask.render_template("pages/browse.html")

@app.route('/list/tasks', methods=["GET"])
@flask_login.login_required
def tasks():
    query = flask.request.args.get('query')
    if query:
        tasks = Task.query.filter(
            (Task.user_id == flask_login.current_user.id) &
            ((Task.title.ilike(f"%{query}%")) | (Task.content.ilike(f"%{query}%")))
        ).order_by(Task.created_at.desc()).all()
    else:
        tasks = Task.query.filter(Task.user_id == flask_login.current_user.id).order_by(Task.created_at.desc()).all()
    return flask.render_template("components/tasks.html", tasks=tasks)

@app.route("/list/edit/<id>", methods=["POST"])
@flask_login.login_required
def edit(id=-1):
    new_title = flask.request.form.get('title')
    new_content = flask.request.form.get('content')

    task = Task.query.filter_by(id=id, user_id=flask_login.current_user.id).first()

    if task and new_title.strip() and new_content.strip():
        task.title = new_title
        task.content = new_content
        db.session.commit()
        return "", 204, {"HX-Reswap": "none"}
    
    error="this task does not exist!"
    return flask.render_template("components/error.html", content=error), 400, {"HX-Retarget": "#htmx-error"}

@app.route("/list/done/<id>", methods=["PATCH"])
@flask_login.login_required
def done(id=-1):
    task = Task.query.filter_by(id=id, user_id=flask_login.current_user.id).first()

    if task:
        task.is_completed = True
        db.session.commit()
        return "", 204, {"HX-Trigger": "updateList", "HX-Reswap": "none"}
    
    error="this task does not exist!"
    return flask.render_template("components/error.html", content=error), 400, {"HX-Retarget": "#htmx-error"}

@app.route("/list/undone/<id>", methods=["PATCH"])
@flask_login.login_required
def undone(id=-1):
    task = Task.query.filter_by(id=id, user_id=flask_login.current_user.id).first()

    if task:
        task.is_completed = False
        db.session.commit()
        return "", 204, {"HX-Trigger": "updateList", "HX-Reswap": "none"}
    
    error="this task does not exist!"
    return flask.render_template("components/error.html", content=error), 400, {"HX-Retarget": "#htmx-error"}

@app.route("/list/delete/<id>", methods=["DELETE"])
@flask_login.login_required
def remove(id=-1):
    task = Task.query.filter_by(id=id, user_id=flask_login.current_user.id).first()

    if task:
        db.session.delete(task)
        db.session.commit()
        return "", 200, {"HX-Trigger": "updateList", "HX-Reswap": "none"}
    
    error="this task does not exist!"
    return flask.render_template("components/error.html", content=error), 400, {"HX-Retarget": "#htmx-error"}

@app.route("/list/create", methods=["PUT"])
@flask_login.login_required
def create():
    title = flask.request.form.get('title')
    content = flask.request.form.get('content')
    if (title.strip() and content.strip()):
        new_task = Task(title=title, content=content, user_id=flask_login.current_user.id)
        db.session.add(new_task)
        db.session.commit()
        
        return "", 201, {"HX-Trigger": "updateList", "HX-Reswap": "none"}

    error="title or content missing!"
    return flask.render_template("components/error.html", content=error), 400, {"HX-Retarget": "#htmx-error"}
