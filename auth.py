from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from models import User, db
from forms import LoginForm, RegistrationForm
import secrets

def create_auth_routes(app):
    """Create authentication routes"""
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data) and user.is_active:
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('dashboard')
                flash(f'Witaj, {user.first_name or user.username}!', 'success')
                return redirect(next_page)
            else:
                flash('Nieprawidłowy email lub hasło', 'error')
        
        return render_template('login.html', form=form)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            # Check if this is the first user (make them admin)
            user_count = User.query.count()
            role = 'admin' if user_count == 0 else 'viewer'
            
            # Generate username from first name and email
            first_name = (form.first_name.data or '').lower().replace(' ', '')
            email_prefix = (form.email.data or '').split('@')[0]
            base_username = f"{first_name}_{email_prefix}"
            
            # Ensure username is unique
            username = base_username
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}_{counter}"
                counter += 1
            
            user = User(
                username=username,
                first_name=form.first_name.data,
                email=form.email.data,
                preferred_category=form.preferred_category.data,
                role=role
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            flash(f'Rejestracja zakończona pomyślnie! Witaj, {form.first_name.data}!', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html', form=form)
    
    @app.route('/logout')
    def logout():
        if current_user.is_authenticated:
            flash(f'Do widzenia, {current_user.username}!', 'info')
            logout_user()
        return redirect(url_for('index'))

def create_admin_routes(app):
    """Create admin routes"""
    
    @app.route('/admin')
    @login_required
    def admin_panel():
        if not current_user.can_access_admin():
            flash('Brak uprawnień do panelu administracyjnego', 'error')
            return redirect(url_for('dashboard'))
        
        users = User.query.all()
        return render_template('admin.html', users=users)
    
    @app.route('/admin/user/<int:user_id>/toggle')
    @login_required
    def toggle_user_status(user_id):
        if not current_user.can_access_admin():
            flash('Brak uprawnień', 'error')
            return redirect(url_for('dashboard'))
        
        user = User.query.get_or_404(user_id)
        if user.id == current_user.id:
            flash('Nie możesz dezaktywować własnego konta', 'error')
        else:
            user.is_active = not user.is_active
            db.session.commit()
            status = 'aktywowany' if user.is_active else 'dezaktywowany'
            flash(f'Użytkownik {user.username} został {status}', 'success')
        
        return redirect(url_for('admin_panel'))
    
    @app.route('/admin/user/<int:user_id>/role/<role>')
    @login_required
    def change_user_role(user_id, role):
        if not current_user.can_access_admin():
            flash('Brak uprawnień', 'error')
            return redirect(url_for('dashboard'))
        
        if role not in ['viewer', 'analyst', 'admin']:
            flash('Nieprawidłowa rola', 'error')
            return redirect(url_for('admin_panel'))
        
        user = User.query.get_or_404(user_id)
        if user.id == current_user.id and role != 'admin':
            flash('Nie możesz zmienić własnej roli administratora', 'error')
        else:
            user.role = role
            db.session.commit()
            flash(f'Rola użytkownika {user.username} została zmieniona na {role}', 'success')
        
        return redirect(url_for('admin_panel'))