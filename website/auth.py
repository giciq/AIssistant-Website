from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from website import user_collection
from .models import User

auth = Blueprint('auth', __name__)
@auth.route('/contact', methods=['GET', 'POST'])
@auth.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        if request.form.get('username'):
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')

            user = user_collection.find_one({"email": email})
            username_base = user_collection.find_one({"first_name": username})

            if username_base:
                flash('Username is already used!', category='error')
            elif user:
                flash('Email is already in use!', category='error')
            elif len(password) < 8:
                flash('Password must be at least 8 characters.', category='error')
            else:
                new_user = {
                    "email": email,
                    "first_name": username,
                    "password": generate_password_hash(password, method='sha256')
                }
                user_collection.insert_one(new_user)
                registered = user_collection.find_one({"email": email})
                login_user(User(registered), remember=True)
                flash('Account has been created!', category='success')
                return redirect(url_for('views.home'))
        else:
            email = request.form.get('email')
            password = request.form.get('password')

            user = user_collection.find_one({"email": email})
            if user:
                if check_password_hash(user['password'], password):
                    flash('You have logged in!', category='success')
                    user_obj = User(user)
                    login_user(user_obj, remember=True)
                    return redirect(url_for('views.home'))
                else:
                    flash('It is a wrong password!', category='error')
            else:
                flash('Email does not exist!', category="error")

    if request.path == '/':
        return render_template("main.html", user=current_user)
    else:
        return render_template("contact.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.main'))
