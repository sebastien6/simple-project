from datetime import datetime
from flask import render_template, request, session
from flask import redirect, url_for, jsonify
from functools import wraps

from micro import db
from micro.main import bp
from micro.models import User, load_user
from micro.api import Geolocation, GetUserIP, GetWeather, Currency_Change_Rate


# Decorator for authenticated users
def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper


# Decorator for users with admin privileges
def is_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return wrapper

@bp.before_app_request
def before_request():
    if 'logged_in' in session:
        user = load_user(session['logged_in'])
        user.last_seen = datetime.utcnow()
        db.session.commit()


# Website home page
@bp.route('/', defaults={'ip': None})
@bp.route('/<ip>/')
@authenticate
def home(ip):
    if ip is not None:
        session['ip'] = ip

    if 'ip' not in session:
        session['ip'] = GetUserIP(request)
    
    # session['ip'] = '50.101.59.87'
    data = Geolocation(session['ip'])
    weather = GetWeather(data)
    currency = Currency_Change_Rate(data.currency_code)
    return render_template('index.html',
                           title='Home',
                           user=session['logged_in'],
                           data=data,
                           weather=weather,
                           currency=currency)


@bp.route('/admin', methods=['GET', 'POST'])
@authenticate
@is_admin
def admin():
    if request.method == 'POST':
        action = request.form['action']
        if action == 'update':
            try:
                user = load_user(request.form['username'])
                if user.isadmin:
                    user.isadmin = False
                    if session['logged_in'] == request.form['username']:
                        session.pop('admin', None)
                else:
                    if session['logged_in'] == request.form['username']:
                        session['admin'] = True
                    user.isadmin = True
                db.session.commit()
                
                user = load_user(request.form['username'])
                s = {'success': True}
                return jsonify(s)
            except:
                s = {'success': False}
                return jsonify(s)
        elif action == 'delete':
            user = load_user(request.form['username'])
            if user.isadmin or (session['logged_in'] == request.form['username']):
                s = {'success': False}
                return jsonify(s)
            else:
                db.session.delete(user)
                db.session.commit()
            
            
            user = load_user(request.form['username'])
            if user is None:
                s = {'success': True}
                return jsonify(s)
            else:
                s = {'success': False}
                return jsonify(s)

    users = User.query.all()
    return render_template('admin.html', title='Admin', users=users)



