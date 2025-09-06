import os
import json
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, dash_table
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from datetime import datetime
import base64
import logging
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from werkzeug.middleware.proxy_fix import ProxyFix

from data_processor import DataProcessor
from visualizations import ChartGenerator
from models import db, User
from auth import create_auth_routes, create_admin_routes

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask server
server = Flask(__name__)
server.config['SECRET_KEY'] = os.environ.get("SESSION_SECRET", 'your-secret-key-change-this')
server.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
server.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {
        'sslmode': 'prefer',
        'connect_timeout': 10
    }
}
server.wsgi_app = ProxyFix(server.wsgi_app, x_proto=1, x_host=1)

# Initialize database
db.init_app(server)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = 'login'
login_manager.login_message = 'Zaloguj się, aby uzyskać dostęp do tej strony.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create auth routes
create_auth_routes(server)
create_admin_routes(server)

# Initialize Dash app with Flask server
app = dash.Dash(__name__, 
                server=server,
                external_stylesheets=[
                    'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css',
                    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
                ],
                suppress_callback_exceptions=True,
                url_base_pathname='/dashboard/')

app.title = "Dashboard Analizy Ofert Pracy"

# Initialize data processor and chart generator
data_processor = DataProcessor()
chart_generator = ChartGenerator()

def create_protected_layout():
    """Create dashboard layout for authenticated users"""
    # Check if user is authenticated in Flask context
    try:
        if not current_user.is_authenticated:
            return html.Div([
                dbc.Alert("Przekierowywanie do strony logowania...", color="info"),
                dcc.Location(pathname='/login', id='redirect-login')
            ])
    except:
        return html.Div([
            dbc.Alert("Sesja wygasła. Przekierowywanie do logowania...", color="warning"),
            dcc.Location(pathname='/login', id='redirect-login')
        ])
        
    return dbc.Container([
        dcc.Store(id='job-data-store'),
        dcc.Store(id='filtered-data-store'),
        
        # Header with user info
        dbc.Row([
            dbc.Col([
                html.H1("📊 Dashboard Analizy Ofert Pracy", className="text-center mb-2"),
                html.Div(id="user-info-header")
            ])
        ]),
        
        # Navigation
        html.Div(id="navigation-menu"),
        
        # Upload section
        dbc.Card([
            dbc.CardBody([
                html.H4("📁 Wczytaj Dane", className="mb-3"),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        html.I(className="fas fa-cloud-upload-alt fa-2x mb-2"),
                        html.Br(),
                        'Przeciągnij i upuść pliki JSON lub kliknij, aby wybrać'
                    ]),
                    style={
                        'width': '100%', 'height': '60px', 'lineHeight': '60px',
                        'borderWidth': '1px', 'borderStyle': 'dashed',
                        'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px',
                        'borderColor': '#6c757d'
                    },
                    multiple=True
                ),
                html.Div(id='upload-status', className="mt-2")
            ])
        ], className="mb-4"),
        
        # Filters section 
        html.Div(id="filters-section"),
        
        # Summary stats
        dbc.Row([
            dbc.Col([
                html.Div(id='summary-stats')
            ])
        ], className="mb-4"),
        
        # Main content tabs with role-based access
        create_tabs_based_on_role(),
        
        html.Div(id='tab-content', className="mt-4")
    ])

def create_tabs_based_on_role():
    """Create tabs based on user role"""
    # Always show first tab for guests
    base_tabs = [
        dbc.Tab(label="📊 Analiza Umiejętności", tab_id="skills-tab"),
    ]
    
    # Add more tabs only for authenticated users
    if current_user.is_authenticated:
        base_tabs.extend([
            dbc.Tab(label="👤 Analiza Doświadczenia", tab_id="experience-tab"),
            dbc.Tab(label="📍 Analiza Lokalizacji", tab_id="location-tab"),
            dbc.Tab(label="🏢 Analiza Firm", tab_id="company-tab")
        ])
        
        if current_user.can_access_advanced():
            base_tabs.extend([
                dbc.Tab(label="📈 Trendy Czasowe", tab_id="trends-tab"),
                dbc.Tab(label="💰 Analiza Wynagrodzeń", tab_id="salary-tab"),
                dbc.Tab(label="🔍 Szczegółowa Analiza", tab_id="detailed-tab")
            ])
    else:
        # Add clickable tabs for guests to show what's available after login
        base_tabs.extend([
            dbc.Tab(label="👤 Analiza Doświadczenia", tab_id="experience-tab"),
            dbc.Tab(label="📍 Analiza Lokalizacji", tab_id="location-tab"),
            dbc.Tab(label="🏢 Analiza Firm", tab_id="company-tab"),
            dbc.Tab(label="📈 Trendy Czasowe", tab_id="trends-tab"),
            dbc.Tab(label="💰 Analiza Wynagrodzeń", tab_id="salary-tab"),
            dbc.Tab(label="🔍 Szczegółowa Analiza", tab_id="detailed-tab")
        ])
    
    return dbc.Tabs(id="main-tabs", active_tab="skills-tab", children=base_tabs)

# Set layout - static layout with dynamic components
app.layout = dbc.Container([
    dcc.Store(id='job-data-store'),
    dcc.Store(id='filtered-data-store'),
    
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("📊 Dashboard Analizy Ofert Pracy", className="text-center mb-2"),
            html.Div(id="user-info-header")
        ])
    ]),
    
    # Navigation
    html.Div(id="navigation-menu"),
    
    # Upload section (dynamic - will be populated by callback)
    html.Div(id="upload-section"),
    
    # Filters section 
    html.Div(id="filters-section"),
    
    # Summary stats
    dbc.Row([
        dbc.Col([
            html.Div(id='summary-stats')
        ])
    ], className="mb-4"),
    
    # Tabs
    html.Div(id="tabs-container"),
    
    html.Div(id='tab-content', className="mt-4", children=[
        dbc.Alert("Wybierz zakładkę powyżej, aby zobaczyć analizy", color="info")
    ])
])

# Flask routes
@server.route('/')
def index():
    return redirect('/dashboard/')

@server.route('/dashboard/')
def dashboard():
    # Allow both authenticated and guest users
    return app.index()

# Callback for dynamic user interface based on authentication
@app.callback(
    [Output('user-info-header', 'children'),
     Output('navigation-menu', 'children'),
     Output('upload-section', 'children'),
     Output('filters-section', 'children'),
     Output('tabs-container', 'children')],
    [Input('job-data-store', 'data')]  # Trigger on page load
)
def update_ui_based_on_auth(data):
    try:
        if not current_user.is_authenticated:
            # Guest user interface
            user_info = html.Div([
                html.P("Tryb gościa - ograniczony dostęp", className="text-center text-muted mb-1"),
                html.P("Zaloguj się, aby uzyskać pełny dostęp do wszystkich analiz", className="text-center text-muted mb-4")
            ])
            
            # Navigation for guests
            navigation = dbc.Row([
                dbc.Col([
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("Zaloguj się", href="/login", external_link=True)),
                        dbc.NavItem(dbc.NavLink("Zarejestruj się", href="/register", external_link=True))
                    ], pills=True, className="mb-4")
                ])
            ])
            
            # No upload section for guests
            upload_section = html.Div()
            
            # No filters for guests
            filters = html.Div()
            
            # Limited tabs for guests
            tabs = create_tabs_based_on_role()
            
            return user_info, navigation, upload_section, filters, tabs
        
        # User info header
        user_info = html.Div([
            html.P(f"Witaj, {current_user.username}!", className="text-center text-muted mb-1"),
            html.P(f"Rola: {current_user.role.title()}", className="text-center text-muted mb-4")
        ])
        
        # Navigation
        navigation = dbc.Row([
            dbc.Col([
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard/", active=True)),
                    dbc.NavItem(dbc.NavLink("Administracja", href="/admin", external_link=True, disabled=not current_user.can_access_admin())),
                    dbc.NavItem(dbc.NavLink("Wyloguj", href="/logout", external_link=True))
                ], pills=True, className="mb-4")
            ])
        ])
        
        # Upload section (only for admins)
        upload_section = html.Div()
        if current_user.can_access_admin():
            upload_section = dbc.Card([
                dbc.CardBody([
                    html.H4("📁 Wczytaj Dane", className="mb-3"),
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            html.I(className="fas fa-cloud-upload-alt fa-2x mb-2"),
                            html.Br(),
                            'Przeciągnij i upuść pliki JSON lub kliknij, aby wybrać'
                        ]),
                        style={
                            'width': '100%', 'height': '60px', 'lineHeight': '60px',
                            'borderWidth': '1px', 'borderStyle': 'dashed',
                            'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px',
                            'borderColor': '#6c757d'
                        },
                        multiple=True
                    ),
                    html.Div(id='upload-status', className="mt-2")
                ])
            ], className="mb-4")
        
        # Filters (only for advanced users)
        filters = html.Div()
        if current_user.can_access_advanced():
            filters = dbc.Card([
                dbc.CardBody([
                    html.H4("🔍 Filtry", className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Miasta:"),
                            dcc.Dropdown(id='city-filter', multi=True, placeholder="Wszystkie miasta")
                        ], md=2),
                        dbc.Col([
                            html.Label("Poziom doświadczenia:"),
                            dcc.Dropdown(id='seniority-filter', multi=True, placeholder="Wszystkie poziomy")
                        ], md=2),
                        dbc.Col([
                            html.Label("Umiejętności:"),
                            dcc.Dropdown(id='skills-filter', multi=True, placeholder="Wszystkie umiejętności")
                        ], md=2),
                        dbc.Col([
                            html.Label("Firmy:"),
                            dcc.Dropdown(id='company-filter', multi=True, placeholder="Wszystkie firmy")
                        ], md=2),
                        dbc.Col([
                            html.Label("Praca zdalna:"),
                            dcc.Dropdown(
                                id='remote-filter', 
                                options=[{'label': 'Tak', 'value': True}, {'label': 'Nie', 'value': False}],
                                multi=True, 
                                placeholder="Wszystkie"
                            )
                        ], md=2),
                        dbc.Col([
                            html.Label("Kategoria:"),
                            dcc.Dropdown(id='category-filter', multi=True, placeholder="Wszystkie kategorie")
                        ], md=2)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("Resetuj filtry", id="reset-filters", color="secondary", className="mt-3")
                        ])
                    ])
                ])
            ], className="mb-4")
        
        # Tabs based on role
        tabs = create_tabs_based_on_role()
        
        return user_info, navigation, upload_section, filters, tabs
        
    except Exception as e:
        return (
            html.P("Błąd uwierzytelniania", className="text-center text-danger mb-4"),
            html.Div([dcc.Location(pathname='/login', id='redirect')]),
            html.Div(),
            html.Div(),
            html.Div()
        )

# Callback for file upload
@app.callback(
    [Output('job-data-store', 'data'),
     Output('upload-status', 'children')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
     State('job-data-store', 'data')],
    prevent_initial_call=True
)
def update_data(list_of_contents, list_of_names, existing_data):
    if not current_user.is_authenticated or not current_user.can_access_admin():
        return None, dbc.Alert("Brak uprawnień do ładowania danych", color="danger")
        
    if list_of_contents is None:
        if existing_data is None:
            return None, dbc.Alert("Brak wczytanych danych", color="warning")
        return existing_data, dbc.Alert(f"Wczytano {len(existing_data)} ofert pracy", color="success")
    
    all_data = existing_data if existing_data else []
    
    for content, name in zip(list_of_contents, list_of_names):
        try:
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            
            if name.endswith('.json'):
                data = json.loads(decoded.decode('utf-8'))
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
            else:
                return all_data, dbc.Alert(f"Nieobsługiwany format pliku: {name}", color="danger")
                
        except Exception as e:
            return all_data, dbc.Alert(f"Błąd wczytywania pliku {name}: {str(e)}", color="danger")
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_data = []
    for item in all_data:
        if item.get('url') not in seen_urls:
            unique_data.append(item)
            seen_urls.add(item.get('url'))
    
    return unique_data, dbc.Alert(f"Pomyślnie wczytano {len(unique_data)} unikalnych ofert pracy", color="success")

# Callback for updating filter options
@app.callback(
    [Output('city-filter', 'options'),
     Output('seniority-filter', 'options'),
     Output('skills-filter', 'options'),
     Output('company-filter', 'options'),
     Output('category-filter', 'options')],
    [Input('job-data-store', 'data')]
)
def update_filter_options(data):
    if not current_user.is_authenticated or not current_user.can_access_advanced():
        raise PreventUpdate
        
    if not data:
        return [], [], [], [], []
    
    df = pd.DataFrame(data)
    
    # City options
    cities = sorted([city for city in df['city'].dropna().unique() if city])
    city_options = [{'label': city, 'value': city} for city in cities]
    
    # Seniority options
    seniority_levels = sorted([level for level in df['seniority'].dropna().unique() if level])
    seniority_options = [{'label': level, 'value': level} for level in seniority_levels]
    
    # Skills options
    all_skills = set()
    for skills in df['skills'].dropna():
        if isinstance(skills, dict):
            all_skills.update(skills.keys())
    skills_options = [{'label': skill, 'value': skill} for skill in sorted(all_skills)]
    
    # Company options
    companies = sorted([company for company in df['company'].dropna().unique() if company])
    company_options = [{'label': company, 'value': company} for company in companies]
    
    # Category options
    categories = sorted([cat for cat in df['category'].dropna().unique() if cat])
    category_options = [{'label': cat, 'value': cat} for cat in categories]
    
    return city_options, seniority_options, skills_options, company_options, category_options

# Callback for filtering data
@app.callback(
    Output('filtered-data-store', 'data'),
    [Input('job-data-store', 'data'),
     Input('city-filter', 'value'),
     Input('seniority-filter', 'value'),
     Input('skills-filter', 'value'),
     Input('company-filter', 'value'),
     Input('remote-filter', 'value'),
     Input('category-filter', 'value')],
    prevent_initial_call=True
)
def filter_data(data, cities, seniority, skills, companies, remote, categories):
    if not current_user.is_authenticated:
        return data if data else []
    
    if not current_user.can_access_advanced():
        return data if data else []
        
    if not data:
        return []
    
    df = pd.DataFrame(data)
    
    # Apply filters (only if user has advanced access)
    if current_user.can_access_advanced():
        if cities:
            df = df[df['city'].isin(cities)]
        if seniority:
            df = df[df['seniority'].isin(seniority)]
        if companies:
            df = df[df['company'].isin(companies)]
        if remote is not None:
            df = df[df['remote'].isin(remote)]
        if categories:
            df = df[df['category'].isin(categories)]
        if skills:
            # Filter by skills - job must have at least one of the selected skills
            def has_required_skills(job_skills):
                if not isinstance(job_skills, dict):
                    return False
                return any(skill in job_skills for skill in skills)
            df = df[df['skills'].apply(has_required_skills)]
    
    return df.to_dict('records')

# Callback for reset filters
@app.callback(
    [Output('city-filter', 'value'),
     Output('seniority-filter', 'value'),
     Output('skills-filter', 'value'),
     Output('company-filter', 'value'),
     Output('remote-filter', 'value'),
     Output('category-filter', 'value')],
    [Input('reset-filters', 'n_clicks')],
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    if not current_user.is_authenticated or not current_user.can_access_advanced():
        raise PreventUpdate
        
    if n_clicks:
        return None, None, None, None, None, None
    return dash.no_update

# Callback for summary stats
@app.callback(
    Output('summary-stats', 'children'),
    [Input('filtered-data-store', 'data')]
)
def update_summary_stats(data):
    if not data:
        return dbc.Alert("Brak danych do wyświetlenia", color="info")
    
    df = pd.DataFrame(data)
    
    # Calculate statistics
    total_jobs = len(df)
    unique_companies = df['company'].nunique()
    unique_cities = df['city'].nunique()
    remote_jobs = df['remote'].sum() if 'remote' in df.columns else 0
    # Calculate average skills count
    avg_skills = 0
    if not df.empty:
        skills_counts = []
        for _, row in df.iterrows():
            if isinstance(row.get('skills'), dict):
                skills_counts.append(len(row['skills']))
        avg_skills = sum(skills_counts) / len(skills_counts) if skills_counts else 0
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{total_jobs:,}", className="text-primary mb-0"),
                    html.P("Ofert pracy", className="text-muted mb-0")
                ])
            ])
        ], md=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{unique_companies:,}", className="text-success mb-0"),
                    html.P("Firm", className="text-muted mb-0")
                ])
            ])
        ], md=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{unique_cities:,}", className="text-info mb-0"),
                    html.P("Miast", className="text-muted mb-0")
                ])
            ])
        ], md=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{remote_jobs:,}", className="text-warning mb-0"),
                    html.P("Praca zdalna", className="text-muted mb-0")
                ])
            ])
        ], md=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{avg_skills:.1f}", className="text-danger mb-0"),
                    html.P("Śr. umiejętności", className="text-muted mb-0")
                ])
            ])
        ], md=2)
    ])

# Callback for tab content with role-based access
@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'active_tab'),
     Input('filtered-data-store', 'data')],
    prevent_initial_call=True
)
def update_tab_content(active_tab, data):
    # Don't process if no active tab (prevents callback error for guests)
    if not active_tab:
        raise PreventUpdate
        
    # Check permissions for tabs that require authentication
    if active_tab != "skills-tab" and not current_user.is_authenticated:
        return dbc.Alert([
            html.H5("🔒 Treść dostępna dla zalogowanych użytkowników"),
            html.P("Ta sekcja wymaga zalogowania. Zarejestruj się lub zaloguj, aby uzyskać dostęp do pełnych analiz."),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Zaloguj się", href="/login", external_link=True, color="primary", className="me-2"),
                    dbc.Button("Zarejestruj się", href="/register", external_link=True, color="secondary")
                ])
            ])
        ], color="info")
        
    if not data:
        message = "Brak danych do wyświetlenia."
        if current_user.is_authenticated and current_user.can_access_admin():
            message += " Wczytaj pliki JSON z ofertami pracy używając sekcji 'Wczytaj Dane' powyżej."
        else:
            message += " Administrator musi wczytać dane aby były dostępne."
        return dbc.Alert(message, color="info")
    
    df = pd.DataFrame(data)
    
    # Check permissions for advanced tabs
    if active_tab in ["trends-tab", "salary-tab", "detailed-tab"] and current_user.is_authenticated and not current_user.can_access_advanced():
        return dbc.Alert(f"Brak uprawnień do tej sekcji. Wymagana rola: analyst lub admin. Twoja rola: {current_user.role}", color="warning")
    
    if active_tab == "skills-tab":
        return chart_generator.create_skills_analysis(df)
    elif active_tab == "experience-tab" and current_user.is_authenticated:
        return chart_generator.create_experience_analysis(df)
    elif active_tab == "location-tab" and current_user.is_authenticated:
        return chart_generator.create_location_analysis(df)
    elif active_tab == "company-tab" and current_user.is_authenticated:
        return chart_generator.create_company_analysis(df)
    elif active_tab == "trends-tab" and current_user.is_authenticated and current_user.can_access_advanced():
        return chart_generator.create_trends_analysis(df)
    elif active_tab == "salary-tab" and current_user.is_authenticated and current_user.can_access_advanced():
        return chart_generator.create_salary_analysis(df)
    elif active_tab == "detailed-tab" and current_user.is_authenticated and current_user.can_access_advanced():
        return chart_generator.create_detailed_analysis(df)
    
    return html.Div("Wybierz zakładkę aby zobaczyć analizę")

# Callback for detailed skill analysis
@app.callback(
    Output('detailed-skill-analysis', 'children'),
    [Input('detailed-skill-selector', 'value'),
     Input('filtered-data-store', 'data')]
)
def update_detailed_skill_analysis(selected_skill, data):
    if not current_user.is_authenticated or not current_user.can_access_advanced():
        return dbc.Alert("Brak uprawnień do tej funkcji", color="warning")
        
    if not selected_skill or not data:
        return dbc.Alert("Wybierz umiejętność aby zobaczyć szczegółową analizę", color="info")
    
    df = pd.DataFrame(data)
    return chart_generator.create_skill_specific_analysis(df, selected_skill)

# Callback for co-occurring skills
@app.callback(
    Output('cooccurrence-results', 'children'),
    [Input('skill-selector', 'value'),
     Input('filtered-data-store', 'data')]
)
def update_cooccurrence_results(selected_skills, data):
    if not current_user.is_authenticated:
        return html.P("Musisz być zalogowany", style={'color': 'white', 'textAlign': 'center', 'padding': '20px'})
        
    if not selected_skills or not data:
        return html.P("Wybierz umiejętności, aby zobaczyć najczęściej współwystępujące z nimi.", 
                     style={'color': 'white', 'textAlign': 'center', 'padding': '20px'})
    
    # Limit to 3 skills maximum
    if len(selected_skills) > 3:
        selected_skills = selected_skills[:3]
    
    df = pd.DataFrame(data)
    cooccurring = data_processor.get_cooccurring_skills(df, selected_skills)
    
    if not cooccurring:
        return html.P("Brak współwystępujących umiejętności dla wybranych opcji.", 
                     style={'color': 'white', 'textAlign': 'center', 'padding': '20px'})
    
    # Create table with results
    cooccurrence_data = []
    for skill, count in cooccurring:
        cooccurrence_data.append({
            'Umiejętność': skill,
            'Liczba współwystąpień': count
        })
    
    return dash_table.DataTable(
        data=cooccurrence_data,
        columns=[
            {'name': 'Współwystępująca Umiejętność', 'id': 'Umiejętność'},
            {'name': 'Liczba wystąpień', 'id': 'Liczba współwystąpień'}
        ],
        style_cell={
            'textAlign': 'left',
            'backgroundColor': '#343a40',
            'color': 'white',
            'border': '1px solid rgba(255, 255, 255, 0.2)',
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        style_header={
            'backgroundColor': '#6c757d',
            'color': 'white',
            'fontWeight': 'bold',
            'border': '1px solid rgba(255, 255, 255, 0.3)'
        },
        style_data={
            'backgroundColor': '#343a40',
            'color': 'white'
        }
    )

# Create database tables
with server.app_context():
    db.create_all()

if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0', port=5000)