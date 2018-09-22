from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    students = db.execute(
        'SELECT id,username,email,registered'
        ' FROM user'
        ' ORDER BY username '
    ).fetchall()
    return render_template('blog/index.html', students=students)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_student(id, check_author=True):
    student = get_db().execute(
        'SELECT id, username,email,registered'
        ' FROM user'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if student is None:
        abort(404, "Student id {0} doesn't exist.".format(id))

    if check_author and student['id'] != g.user['id']:
        abort(403)

    return student

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    student = get_student(id)

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        error = None

        if not username:
            error = 'Username is required.'
        if not email:
            error = 'email is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE user SET  username = ?, email = ?'
                ' WHERE id = ?',
                (username, email, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', student=student)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_student(id)
    db = get_db()
    db.execute('DELETE FROM user WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))