from flask import Flask, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from models import User, UserRole, db
import os

def init_auth(app):
    """Initialize authentication system"""
    app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Zaloguj się, aby uzyskać dostęp do tej strony.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return login_manager

def admin_required(f):
    """Decorator requiring admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Dostęp tylko dla administratorów.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """Decorator requiring user or admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_user_or_admin():
            flash('Musisz być zalogowany jako użytkownik.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_role():
    """Get current user role for templates"""
    if current_user.is_authenticated:
        return current_user.role.value
    return 'guest'