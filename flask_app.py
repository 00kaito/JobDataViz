import os
import json
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

from models import User, UserRole, db, init_db
from auth import init_auth, admin_required, user_required, get_user_role
from data_processor import DataProcessor
from visualizations import ChartGenerator

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

# Initialize database and auth
init_db(app)
login_manager = init_auth(app)

# Initialize processors
data_processor = DataProcessor()
chart_generator = ChartGenerator()

# Global data store (in production, use Redis or database)
job_data_store = {}

@app.context_processor
def inject_user():
    return {
        'current_user': current_user,
        'user_role': get_user_role()
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Zalogowano jako {user.role.value}', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Nieprawidłowa nazwa użytkownika lub hasło', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Nazwa użytkownika już istnieje', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email już istnieje', 'danger')
            return render_template('register.html')
        
        user = User(username=username, email=email, role=UserRole.USER)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Rejestracja przebiegła pomyślnie! Możesz się zalogować.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Zostałeś wylogowany', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    # Check user permissions
    if not current_user.is_authenticated:
        # Guest access - redirect to skills analysis only
        return redirect(url_for('skills_analysis'))
    
    return render_template('dashboard.html')

@app.route('/skills-analysis')
def skills_analysis():
    # This tab is available to everyone (including guests)
    return render_template('skills_analysis.html')

@app.route('/experience-analysis')
@user_required
def experience_analysis():
    return render_template('experience_analysis.html')

@app.route('/location-analysis')
@user_required
def location_analysis():
    return render_template('location_analysis.html')

@app.route('/company-analysis')
@user_required
def company_analysis():
    return render_template('company_analysis.html')

@app.route('/trends-analysis')
@user_required
def trends_analysis():
    return render_template('trends_analysis.html')

@app.route('/salary-analysis')
@user_required
def salary_analysis():
    return render_template('salary_analysis.html')

@app.route('/detailed-analysis')
@user_required
def detailed_analysis():
    return render_template('detailed_analysis.html')

@app.route('/upload-data', methods=['POST'])
@admin_required
def upload_data():
    if 'file' not in request.files:
        return jsonify({'error': 'Brak pliku'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nie wybrano pliku'}), 400
    
    if file and file.filename.endswith('.json'):
        try:
            content = file.read().decode('utf-8')
            data = json.loads(content)
            
            # Store data globally (in production, use database or cache)
            if isinstance(data, list):
                job_data_store['data'] = data
            else:
                job_data_store['data'] = [data]
            
            return jsonify({
                'success': True, 
                'message': f'Wczytano {len(job_data_store["data"])} ofert pracy'
            })
        except Exception as e:
            return jsonify({'error': f'Błąd wczytywania pliku: {str(e)}'}), 400
    
    return jsonify({'error': 'Nieobsługiwany format pliku'}), 400

@app.route('/api/data')
def get_data():
    """API endpoint to get job data"""
    return jsonify(job_data_store.get('data', []))

@app.route('/api/skills-cooccurrence')
def skills_cooccurrence():
    """API endpoint for skills co-occurrence analysis"""
    selected_skills = request.args.getlist('skills')
    
    if not selected_skills or not job_data_store.get('data'):
        return jsonify([])
    
    # Limit to 3 skills
    if len(selected_skills) > 3:
        selected_skills = selected_skills[:3]
    
    df = pd.DataFrame(job_data_store['data'])
    cooccurring = data_processor.get_cooccurring_skills(df, selected_skills)
    
    return jsonify([{'skill': skill, 'count': count} for skill, count in cooccurring])

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)