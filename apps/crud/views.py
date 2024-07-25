from apps.crud.forms import UserForm
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from apps.app import db
from apps.crud.models import User
import string
import random

crud = Blueprint(
    'crud',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@crud.route('/users')
@login_required
def users():
    if current_user.is_admin == False:
        return render_template('bertapp/index.html')
    users = User.query.all()
    return render_template('crud/index.html', users=users)

@crud.route('/users/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    form = UserForm()
    user = User.query.filter_by(id=user_id).first()

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('crud.users'))
    
    return render_template('crud/edit.html', user=user, form=form)

@crud.route('/users/<user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('crud.users'))

def generate_random_string(length=20):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string