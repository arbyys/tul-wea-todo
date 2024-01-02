import flask
import flask_login
from models import db, User, Task
from sqlalchemy import func
from __main__ import app
from werkzeug.security import check_password_hash
import sys
from collections import defaultdict

# WEB routes

@app.route("/")
def home():
    return flask.render_template("pages/home.html")

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
def browse():
    return flask.render_template("pages/browse.html")

@app.route('/list/tasks', methods=["GET"])
@flask_login.login_required
def tasks():
    query = flask.request.args.get('query')
    if query:
        tasks = Task.query \
            .filter(
            (Task.user_id == flask_login.current_user.id) &
            ((Task.title.ilike(f"%{query}%")) | (Task.content.ilike(f"%{query}%")))) \
            .order_by(Task.created_at.desc()) \
            .all()
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

@app.route("/list/update_private", methods=["POST"])
@flask_login.login_required
def update_private():
    is_private = flask.request.form.get("is_private")

    flask_login.current_user.has_private_profile = True if (is_private == "on") else False
    db.session.commit()

    return flask.render_template("components/switch.html"), 200

@app.route("/browse/tasks", methods=["GET"])
def browse_tasks():
    # TODO
    if(flask_login.current_user.is_authenticated):
        print("isyloged", file=sys.stderr)
    else:
        print("isnnnnloged", file=sys.stderr)

    query = flask.request.args.get('query')
    
    if query:
        user_tasks = db.session.query(User, Task) \
            .join(Task) \
            .filter(User.has_private_profile == False) \
            .filter((Task.title.ilike(f"%{query}%")) | 
                    (Task.content.ilike(f"%{query}%")) | 
                    (User.username.ilike(f"%{query}%"))) \
            .order_by(User.username, Task.created_at.desc()) \
            .all()
    else:
        user_tasks = db.session.query(User, Task) \
            .join(Task) \
            .filter(User.has_private_profile == False) \
            .order_by(User.username, Task.created_at.desc()) \
            .all()

    user_tasks_formatted = defaultdict(lambda: [])
    for user, task in user_tasks:
        user_tasks_formatted[user.username].append({
            'title': task.title,
            'content': task.content,
            'is_completed': task.is_completed
        })
    user_tasks_formatted = dict(user_tasks_formatted)

    return flask.render_template("components/user_tasks.html", user_tasks=user_tasks_formatted)

# API routes

@app.route("/api/tasks")
def api_tasks():
    data_type = flask.request.args.get('type', 'json')
    query = flask.request.args.get('query')
    if query:
        tasks = db.session.query(User, Task) \
            .join(Task) \
            .filter(User.has_private_profile == False) \
            .filter((Task.title.ilike(f"%{query}%")) | 
                    (Task.content.ilike(f"%{query}%")) | 
                    (User.username.ilike(f"%{query}%"))) \
            .order_by(User.username, Task.created_at.desc()) \
            .all()
    else:
        tasks = db.session.query(User, Task) \
            .join(Task) \
            .filter(User.has_private_profile == False) \
            .order_by(User.username, Task.created_at.desc()) \
            .all()

    if data_type == 'html':
        return flask.render_template('components/api_tasks.html', data=tasks)
    elif data_type == 'json':
        tasks_formatted = []
        for row in tasks:
            tasks_formatted.append({**row.Task.to_dict(), **row.User.to_dict()})
        return flask.jsonify(data=tasks_formatted)
    else:
        return flask.jsonify(error="invalid data type (must be 'html' or 'json')")
    
@app.route("/api/users_tasks")
def api_users_tasks():
    data_type = flask.request.args.get('type', 'json')
    query = flask.request.args.get('query')
    if query:
        users_tasks = db.session.query(User, Task) \
            .join(Task) \
            .filter(User.has_private_profile == False) \
            .filter((Task.title.ilike(f"%{query}%")) | 
                    (Task.content.ilike(f"%{query}%")) | 
                    (User.username.ilike(f"%{query}%"))) \
            .order_by(User.username, Task.created_at.desc()) \
            .all()
    else:
        users_tasks = db.session.query(User, Task) \
            .join(Task) \
            .filter(User.has_private_profile == False) \
            .order_by(User.username, Task.created_at.desc()) \
            .all()
        
    users_tasks_formatted = defaultdict(lambda: [])
    for user, task in users_tasks:
        users_tasks_formatted[user.username].append({
            'title': task.title,
            'content': task.content,
            'is_completed': task.is_completed
        })
    users_tasks_formatted = dict(users_tasks_formatted)

    if data_type == 'html':
        return flask.render_template('components/api_tasks.html', data=users_tasks_formatted)
    elif data_type == 'json':
        return flask.jsonify(data=users_tasks_formatted)
    else:
        return flask.jsonify(error="invalid data type (must be 'html' or 'json')")