import re
import time
from flask import render_template, request, session
from flask import redirect, url_for, make_response
from functools import wraps, update_wrapper

from micro import db
from micro.models import User, Check_password, load_user
from micro.auth import bp

# Decorator to turn off caching
def no_cache(view):
    @wraps(view)
    def no_cache_impl(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, '\
                                            'no-cache, '\
                                            'must-revalidate, '\
                                            'max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache_impl, view)


@bp.route('/login', methods=['GET', 'POST'])
@no_cache
def login():
    if 'logged_in' in session:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        if load_user(request.form['username']) is None:
            return render_template("auth/login.html",
                                   title='Login',
                                   alert={'type': 'alert-warning',
                                          'subject': "Username:",
                                          'msg': '''Invalid username, please make 
                                          sure to register prior sign in.'''})
        else:
            user = load_user(request.form['username'])
            validPwd = Check_password(request.form['pwd'], user.password_hash)
            if validPwd:
                session['logged_in'] = request.form['username']
                if user.isadmin:
                    session['admin'] = True
                    if 'ip' not in session:
                        return redirect(url_for('auth.adminip'))

                return redirect(url_for('main.home'))
            else:
                return render_template("auth/login.html",
                                       alert={'type': 'alert-warning',
                                              'subject':"Username:",
                                              'msg':"Invalid password. try-again"})

    return render_template('auth/login.html', title='Login', alert=None)
    

@bp.route('/adminip', methods=['GET', 'POST'])
def adminip():
    if request.method == 'POST':
        if 'ip' in request.form:
            return redirect(url_for('main.home', ip=request.form['ip']))
        else:
            alert = {'type': 'alert-warning',
                     'subject': "IP Adress: ",
                     'msg': "Missing IP address"}
            render_template('auth/adminip.html', title='Login', alert=alert)

    return render_template('auth/adminip.html', title='Login', alert=None)

@bp.route("/register", methods=['GET', 'POST'])
@no_cache
def register():
    if 'logged_in' in session:
        return redirect(url_for('main.home'))

    if request.method == "POST":
        alert = {'type': '', 'subject': '', 'msg': ''}
        error = False

        username_pattern = re.match('[a-zA-Z0-9._-]{4,50}',
                                    request.form['username'])
        email_pattern = re.match('[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$',
                                 request.form['email'])
        pwd_pattern = re.match("(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,}",
                               request.form['password'])

        if not username_pattern:
            alert = {'type': 'alert-warning',
                     'subject': "username: ",
                     'msg': '''Can contain only letter, number,
 underscore, and dot, between 4 and 50 characters'''}
            error = True
        elif not email_pattern:
            alert = {'type': 'alert-warning', 
                     'subject': "Email format: ", 
                     'msg': "Please enter a valid email format"}
            error = True
        elif not pwd_pattern:
            alert = {'type': 'alert-warning', 
                     'subject': "Email format: ", 
                     'msg': "Please enter a valid email format"}
            error = True
        elif request.form['password'] != request.form['confirm_password']:
            alert = {'type': 'alert-warning', 
                     'subject': "Password: ", 
                     'msg': "Password and confirmed password don't match"}
            error = True
        elif (User.query.filter_by(username=request.form['email']).first()
              is not None):
            alert = {'type': 'alert-warning',
                     'subject': "Email: ",
                     'msg': '''This email address is already registered,
 please try to sign in'''}
            error = True
        elif load_user(request.form['username']) is not None:
            alert = {'type': 'alert-warning', 
                     'subject': "Username: ", 
                     'msg': "Sorry, this username is already taken"}
            error = True

        if error:
            return render_template("auth/register.html", 
                                   title='Register', 
                                   alert=alert)
        else:
            u = User(username=request.form['username'],
                     firstname=request.form['first_name'],
                     lastname=request.form['last_name'],
                     email=request.form['email'])
            u.set_password(request.form['password'])
            if len(User.query.all()) == 0:
                u.isadmin = True
            db.session.add(u)
            db.session.commit()

            if load_user(request.form['username']) is None:
                return render_template(
                    "auth/register.html",
                    title='Register',
                    alert={'type': 'alert-danger',
                           'subject': "Registration Error: ",
                           'msg': '''Account registration failed,
 please try again.'''})
            else:
                return render_template(
                    "auth/register.html",
                    alert={'type': 'alert-success',
                           'subject': "Account creation: ",
                           'msg': "account successfuly created!"})

    return render_template("auth/register.html", title='Register', alert=None)


@bp.route('/logout')
@no_cache
def logout():
    # remove the username from the session if it's there
    session.pop('logged_in', None)
    session.pop('ip', None)
    if 'admin' in session:
        session.pop('admin', None)
    
    return redirect(url_for('auth.login'))

