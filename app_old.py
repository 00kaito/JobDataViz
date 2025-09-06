import os
import json
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import base64
import io
from data_processor import DataProcessor
from visualizations import ChartGenerator
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Dash app
app = dash.Dash(__name__, 
                external_stylesheets=[
                    'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css',
                    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
                ],
                suppress_callback_exceptions=True)

app.title = "Dashboard Analizy Ofert Pracy"

# Initialize data processor and chart generator
data_processor = DataProcessor()
chart_generator = ChartGenerator()

# App layout
app.layout = dbc.Container([
    dcc.Store(id='job-data-store'),
    dcc.Store(id='filtered-data-store'),
    
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("📊 Dashboard Analizy Ofert Pracy", className="text-center mb-4"),
            html.P("Kompleksowa analiza rynku pracy z interaktywnymi wizualizacjami", 
                   className="text-center text-muted mb-4")
        ])
    ]),
    
    # Upload section
    dbc.Card([
        dbc.CardBody([
            html.H4("📁 Wczytaj Dane", className="mb-3"),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    html.I(className="fas fa-cloud-upload-alt fa-2x mb-2"),
                    html.Br(),
                    'Przeciągnij i upuść pliki JSON lub ',
                    html.A('wybierz pliki', className="text-primary")
                ]),
                style={
                    'width': '100%',
                    'height': '100px',
                    'lineHeight': '100px',
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '10px',
                    'textAlign': 'center',
                    'margin': '10px',
                    'cursor': 'pointer'
                },
                multiple=True,
                className="border-secondary"
            ),
            html.Div(id='upload-status', className="mt-3")
        ])
    ], className="mb-4"),
    
    # Filters section
    dbc.Card([
        dbc.CardBody([
            html.H4("🔍 Filtry", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Miasto:", className="form-label"),
                    dcc.Dropdown(id='city-filter', multi=True, placeholder="Wybierz miasta...")
                ], md=3),
                dbc.Col([
                    html.Label("Poziom doświadczenia:", className="form-label"),
                    dcc.Dropdown(id='seniority-filter', multi=True, placeholder="Wybierz poziomy...")
                ], md=3),
                dbc.Col([
                    html.Label("Umiejętności:", className="form-label"),
                    dcc.Dropdown(id='skills-filter', multi=True, placeholder="Wybierz umiejętności...")
                ], md=3),
                dbc.Col([
                    html.Label("Firma:", className="form-label"),
                    dcc.Dropdown(id='company-filter', multi=True, placeholder="Wybierz firmy...")
                ], md=3)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Typ pracy:", className="form-label"),
                    dcc.Dropdown(
                        id='remote-filter',
                        options=[
                            {'label': 'Zdalna', 'value': True},
                            {'label': 'Stacjonarna/Hybrydowa', 'value': False}
                        ],
                        multi=True,
                        placeholder="Wybierz typ pracy..."
                    )
                ], md=3),
                dbc.Col([
                    html.Label("Kategoria:", className="form-label"),
                    dcc.Dropdown(id='category-filter', multi=True, placeholder="Wybierz kategorie...")
                ], md=3),
                dbc.Col([
                    dbc.Button("🔄 Resetuj filtry", id="reset-filters", color="secondary", className="mt-4")
                ], md=3)
            ])
        ])
    ], className="mb-4"),
    
    # Summary statistics
    html.Div(id='summary-stats', className="mb-4"),
    
    # Main content tabs
    dbc.Tabs([
        dbc.Tab(label="🎯 Analiza Umiejętności", tab_id="skills-tab"),
        dbc.Tab(label="📊 Poziomy Doświadczenia", tab_id="experience-tab"),
        dbc.Tab(label="🌍 Analiza Lokalizacji", tab_id="location-tab"),
        dbc.Tab(label="🏢 Analiza Firm", tab_id="company-tab"),
        dbc.Tab(label="📈 Trendy Rynkowe", tab_id="trends-tab"),
        dbc.Tab(label="💰 Analiza Wynagrodzeń", tab_id="salary-tab"),
        dbc.Tab(label="🔍 Szczegółowa Analiza", tab_id="detailed-tab")
    ], id="main-tabs", active_tab="skills-tab"),
    
    # Tab content with loading
    dcc.Loading(
        id="loading",
        type="dot",
        children=html.Div(id='tab-content', className="mt-4"),
        color="#0d6efd",
        style={'margin-top': '20px'},
        overlay_style={"visibility": "visible", "opacity": .7, "backgroundColor": "rgba(0,0,0,0.1)"},
        custom_spinner=html.Div([
            html.Div([
                html.I(className="fas fa-chart-bar fa-3x text-primary mb-3"),
                html.Br(),
                html.H5("Ładowanie analizy danych...", className="text-primary fw-bold mb-2"),
                html.P("To może potrwać kilka sekund", className="text-muted mb-0")
            ], className="text-center p-4 shadow-sm", style={
                'backgroundColor': 'rgba(255,255,255,0.98)', 
                'border': '2px solid #0d6efd', 
                'border-radius': '12px',
                'min-width': '300px'
            })
        ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'min-height': '200px'})
    )
    
], fluid=True)

# Callback for file upload
@app.callback(
    [Output('job-data-store', 'data'),
     Output('upload-status', 'children')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
     State('job-data-store', 'data')]
)
def update_data(list_of_contents, list_of_names, existing_data):
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
     Input('category-filter', 'value')]
)
def filter_data(data, cities, seniority, skills, companies, remote, categories):
    if not data:
        return []
    
    df = pd.DataFrame(data)
    
    # Apply filters
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
    [Input('reset-filters', 'n_clicks')]
)
def reset_filters(n_clicks):
    if n_clicks:
        return None, None, None, None, None, None
    return dash.no_update

# Callback for summary statistics
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
    
    # Salary statistics
    salary_info = ""
    if 'salary_avg' in df.columns:
        salary_df = df[df['salary_avg'].notna()]
        if not salary_df.empty:
            avg_salary = salary_df['salary_avg'].mean()
            salary_info = f" | Średnie wynagrodzenie: {avg_salary:,.0f} PLN"
    
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

# Callback for tab content
@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'active_tab'),
     Input('filtered-data-store', 'data')]
)
def update_tab_content(active_tab, data):
    if not data:
        return dbc.Alert("Brak danych do wyświetlenia. Wczytaj pliki JSON z ofertami pracy.", color="info")
    
    df = pd.DataFrame(data)
    
    if active_tab == "skills-tab":
        return chart_generator.create_skills_analysis(df)
    elif active_tab == "experience-tab":
        return chart_generator.create_experience_analysis(df)
    elif active_tab == "location-tab":
        return chart_generator.create_location_analysis(df)
    elif active_tab == "company-tab":
        return chart_generator.create_company_analysis(df)
    elif active_tab == "trends-tab":
        return chart_generator.create_trends_analysis(df)
    elif active_tab == "salary-tab":
        return chart_generator.create_salary_analysis(df)
    elif active_tab == "detailed-tab":
        return chart_generator.create_detailed_analysis(df)
    
    return html.Div("Wybierz zakładkę aby zobaczyć analizę")

# Callback for detailed skill analysis
@app.callback(
    Output('detailed-skill-analysis', 'children'),
    [Input('detailed-skill-selector', 'value'),
     Input('filtered-data-store', 'data')]
)
def update_detailed_skill_analysis(selected_skill, data):
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
    if not selected_skills or not data:
        return html.P("Wybierz umiejętności, aby zobaczyć najczęściej współwystępujące z nimi.", 
                     style={'color': 'white', 'textAlign': 'center', 'padding': '20px'})
    
    # Limit to 3 skills maximum
    if len(selected_skills) > 3:
        selected_skills = selected_skills[:3]
    
    df = pd.DataFrame(data)
    data_processor = DataProcessor()
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

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=5000)
