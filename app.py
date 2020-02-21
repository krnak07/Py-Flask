from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_pymongo import MongoClient
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from functools import wraps
app = Flask(__name__, static_url_path='/static')

client = MongoClient('mongodb://localhost:27017')
db = client.flaskDB
userDB = db.user_data


@app.route('/')
def index():
    return render_template('welcome.html')

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data
        userDB.insert({"name":name,"username":username,"email":email,"password":password})
        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']
        task=userDB.find({"username":username,"password":password_candidate})
        if task[0] != None:
            session['logged_in'] = True
            session['username'] = username

            flash('You are now logged in', 'success')
            return redirect(url_for('dashboard'))
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')




if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
