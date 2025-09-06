import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
import numpy as np
from data_processor import DataProcessor

class ChartGenerator:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.color_palette = px.colors.qualitative.Set3
    
    def create_skills_analysis(self, df):
        """Create skills analysis tab content"""
        skills_counter, skills_levels, skills_by_seniority = self.data_processor.process_skills_data(df)
        skill_weights = self.data_processor.calculate_skill_weights(skills_levels)
        skill_combinations = self.data_processor.get_skill_combinations(df)
        
        # Top 20 skills bar chart
        top_skills = skills_counter.most_common(20)
        skills_df = pd.DataFrame(top_skills, columns=['Umiejętność', 'Liczba ofert'])
        
        fig_skills = px.bar(
            skills_df, 
            x='Liczba ofert', 
            y='Umiejętność',
            title='Top 20 Najpopularniejszych Umiejętności',
            orientation='h'
        )
        fig_skills.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
        
        # Skills by levels
        if skills_levels:
            level_data = []
            for skill, levels in list(skills_levels.items())[:10]:
                for level, count in levels.items():
                    level_data.append({'Umiejętność': skill, 'Poziom': level, 'Liczba': count})
            
            if level_data:
                levels_df = pd.DataFrame(level_data)
                fig_levels = px.bar(
                    levels_df,
                    x='Umiejętność',
                    y='Liczba',
                    color='Poziom',
                    title='Rozkład Poziomów dla Top 10 Umiejętności',
                    barmode='stack'
                )
                fig_levels.update_layout(height=500, xaxis_tickangle=-45)
            else:
                fig_levels = go.Figure()
                fig_levels.add_annotation(text="Brak danych o poziomach umiejętności", 
                                        x=0.5, y=0.5, showarrow=False)
        else:
            fig_levels = go.Figure()
            fig_levels.add_annotation(text="Brak danych o poziomach umiejętności", 
                                    x=0.5, y=0.5, showarrow=False)
        
        # Weighted skills
        if skill_weights:
            weighted_skills = sorted(skill_weights.items(), key=lambda x: x[1], reverse=True)[:15]
            weighted_df = pd.DataFrame(weighted_skills, columns=['Umiejętność', 'Waga'])
            
            fig_weighted = px.bar(
                weighted_df,
                x='Waga',
                y='Umiejętność',
                title='Umiejętności Ważone według Poziomu Zaawansowania',
                orientation='h'
            )
            fig_weighted.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        else:
            fig_weighted = go.Figure()
            fig_weighted.add_annotation(text="Brak danych do analizy wag", 
                                      x=0.5, y=0.5, showarrow=False)
        
        # Skills combinations table
        if skill_combinations:
            combo_data = []
            for combo, count in skill_combinations:
                combo_data.append({
                    'Kombinacja': ' + '.join(combo),
                    'Liczba wystąpień': count,
                    'Procent': f"{(count/len(df)*100):.1f}%"
                })
            
            combo_table = dash_table.DataTable(
                data=combo_data,
                columns=[
                    {'name': 'Kombinacja Umiejętności', 'id': 'Kombinacja'},
                    {'name': 'Liczba wystąpień', 'id': 'Liczba wystąpień'},
                    {'name': 'Procent ofert', 'id': 'Procent'}
                ],
                style_cell={'textAlign': 'left'},
                style_header={'backgroundColor': 'var(--bs-dark)', 'color': 'white'},
                page_size=10
            )
        else:
            combo_table = html.P("Brak danych o kombinacjach umiejętności")
        
        # Skills statistics table
        top_10_skills = skills_counter.most_common(10)
        stats_data = []
        for skill, count in top_10_skills:
            percentage = (count / len(df)) * 100
            stats_data.append({
                'Umiejętność': skill,
                'Liczba ofert': count,
                'Procent': f"{percentage:.1f}%"
            })
        
        stats_table = dash_table.DataTable(
            data=stats_data,
            columns=[
                {'name': 'Umiejętność', 'id': 'Umiejętność'},
                {'name': 'Liczba ofert', 'id': 'Liczba ofert'},
                {'name': 'Procent ofert', 'id': 'Procent'}
            ],
            style_cell={'textAlign': 'left'},
            style_header={'backgroundColor': 'var(--bs-dark)', 'color': 'white'}
        )
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📊 Najpopularniejsze Umiejętności"),
                            dcc.Graph(figure=fig_skills)
                        ])
                    ])
                ], md=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📈 Statystyki Top 10 Umiejętności"),
                            stats_table
                        ])
                    ])
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🔗 Najczęstsze Kombinacje Umiejętności"),
                            combo_table
                        ])
                    ])
                ], md=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("⚖️ Umiejętności Ważone według Poziomu"),
                            dcc.Graph(figure=fig_weighted)
                        ])
                    ])
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📊 Rozkład Poziomów Umiejętności"),
                            dcc.Graph(figure=fig_levels)
                        ])
                    ])
                ], md=6)
            ])
        ])
    
    def create_experience_analysis(self, df):
        """Create experience analysis tab content"""
        if 'seniority' not in df.columns:
            return dbc.Alert("Brak danych o poziomach doświadczenia", color="warning")
        
        # Seniority distribution
        seniority_counts = df['seniority'].value_counts()
        seniority_df = pd.DataFrame({
            'Poziom': seniority_counts.index,
            'Liczba': seniority_counts.values
        })
        fig_seniority = px.bar(
            seniority_df,
            x='Poziom',
            y='Liczba',
            title='Rozkład Poziomów Doświadczenia',
            labels={'Poziom': 'Poziom doświadczenia', 'Liczba': 'Liczba ofert'}
        )
        
        # Skills vs experience heatmap
        skills_counter, _, skills_by_seniority = self.data_processor.process_skills_data(df)
        top_skills = [skill for skill, _ in skills_counter.most_common(15)]
        
        heatmap_data = []
        seniority_levels = list(skills_by_seniority.keys())
        
        for seniority in seniority_levels:
            for skill in top_skills:
                count = skills_by_seniority[seniority].get(skill, 0)
                heatmap_data.append({
                    'Poziom': seniority,
                    'Umiejętność': skill,
                    'Liczba': count
                })
        
        if heatmap_data:
            heatmap_df = pd.DataFrame(heatmap_data)
            heatmap_pivot = heatmap_df.pivot(index='Umiejętność', columns='Poziom', values='Liczba').fillna(0)
            
            fig_heatmap = px.imshow(
                heatmap_pivot,
                title='Heatmapa: Umiejętności vs Poziom Doświadczenia',
                aspect='auto',
                color_continuous_scale='Blues'
            )
            fig_heatmap.update_layout(height=600)
        else:
            fig_heatmap = go.Figure()
            fig_heatmap.add_annotation(text="Brak danych do utworzenia heatmapy", 
                                     x=0.5, y=0.5, showarrow=False)
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📊 Rozkład Poziomów Doświadczenia"),
                            dcc.Graph(figure=fig_seniority)
                        ])
                    ])
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📈 Statystyki Poziomów"),
                            html.Div([
                                html.P(f"Najwięcej ofert: {seniority_counts.index[0]} ({seniority_counts.iloc[0]} ofert)"),
                                html.P(f"Średnio umiejętności na ofertę: {df['skillsCount'].mean():.1f}"),
                                html.P(f"Całkowita liczba poziomów: {len(seniority_counts)}")
                            ])
                        ])
                    ])
                ], md=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🔥 Heatmapa: Umiejętności vs Doświadczenie"),
                            dcc.Graph(figure=fig_heatmap)
                        ])
                    ])
                ], md=12)
            ])
        ])
    
    def create_location_analysis(self, df):
        """Create location analysis tab content"""
        if 'city' not in df.columns:
            return dbc.Alert("Brak danych o lokalizacji", color="warning")
        
        location_stats = self.data_processor.get_location_stats(df)
        
        # Top cities by job count
        city_counts = df['city'].value_counts().head(15)
        fig_cities = px.bar(
            x=city_counts.values,
            y=city_counts.index,
            title='Top 15 Miast według Liczby Ofert',
            orientation='h',
            labels={'x': 'Liczba ofert', 'y': 'Miasto'}
        )
        fig_cities.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        
        # Remote vs on-site distribution
        if 'remote' in df.columns:
            remote_counts = df['remote'].value_counts()
            remote_labels = ['Stacjonarna/Hybrydowa', 'Zdalna']
            
            fig_remote = px.pie(
                values=remote_counts.values,
                names=remote_labels,
                title='Podział: Praca Zdalna vs Stacjonarna/Hybrydowa'
            )
        else:
            fig_remote = go.Figure()
            fig_remote.add_annotation(text="Brak danych o typie pracy", 
                                    x=0.5, y=0.5, showarrow=False)
        
        # City statistics table
        city_stats_data = []
        for city, stats in sorted(location_stats.items(), 
                                key=lambda x: x[1]['total_jobs'], reverse=True)[:10]:
            top_skills_str = ', '.join([skill for skill, _ in stats['top_skills'][:3]])
            avg_salary = stats['salary_stats'].get('mean', 0) if stats['salary_stats'] else 0
            
            city_stats_data.append({
                'Miasto': city,
                'Oferty': stats['total_jobs'],
                'Firmy': stats['companies'],
                'Top umiejętności': top_skills_str,
                'Średnia pensja': f"{avg_salary:,.0f} PLN" if avg_salary > 0 else "Brak danych",
                'Praca zdalna %': f"{stats['remote_ratio']*100:.1f}%"
            })
        
        city_table = dash_table.DataTable(
            data=city_stats_data,
            columns=[
                {'name': 'Miasto', 'id': 'Miasto'},
                {'name': 'Liczba ofert', 'id': 'Oferty'},
                {'name': 'Liczba firm', 'id': 'Firmy'},
                {'name': 'Top umiejętności', 'id': 'Top umiejętności'},
                {'name': 'Średnia pensja', 'id': 'Średnia pensja'},
                {'name': 'Praca zdalna %', 'id': 'Praca zdalna %'}
            ],
            style_cell={'textAlign': 'left', 'fontSize': '12px'},
            style_header={'backgroundColor': 'var(--bs-dark)', 'color': 'white'},
            page_size=10
        )
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🌍 Rozkład Ofert w Miastach"),
                            dcc.Graph(figure=fig_cities)
                        ])
                    ])
                ], md=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🏠 Typ Pracy"),
                            dcc.Graph(figure=fig_remote)
                        ])
                    ])
                ], md=4)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📊 Statystyki Miast"),
                            city_table
                        ])
                    ])
                ], md=12)
            ])
        ])
    
    def create_company_analysis(self, df):
        """Create company analysis tab content"""
        if 'company' not in df.columns:
            return dbc.Alert("Brak danych o firmach", color="warning")
        
        company_stats = self.data_processor.get_company_stats(df)
        
        # Top companies by job count
        company_counts = df['company'].value_counts().head(15)
        fig_companies = px.bar(
            x=company_counts.values,
            y=company_counts.index,
            title='Top 15 Firm z Największą Liczbą Ofert',
            orientation='h',
            labels={'x': 'Liczba ofert', 'y': 'Firma'}
        )
        fig_companies.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
        
        # Company statistics table
        company_stats_data = []
        for company, stats in sorted(company_stats.items(), 
                                   key=lambda x: x[1]['total_jobs'], reverse=True)[:15]:
            top_skills_str = ', '.join([skill for skill, _ in stats['top_skills'][:3]])
            avg_salary = stats['salary_stats'].get('mean', 0) if stats['salary_stats'] else 0
            
            company_stats_data.append({
                'Firma': company,
                'Oferty': stats['total_jobs'],
                'Miasta': stats['cities'],
                'Top umiejętności': top_skills_str,
                'Średnia pensja': f"{avg_salary:,.0f} PLN" if avg_salary > 0 else "Brak danych",
                'Praca zdalna %': f"{stats['remote_ratio']*100:.1f}%"
            })
        
        company_table = dash_table.DataTable(
            data=company_stats_data,
            columns=[
                {'name': 'Firma', 'id': 'Firma'},
                {'name': 'Liczba ofert', 'id': 'Oferty'},
                {'name': 'Miasta', 'id': 'Miasta'},
                {'name': 'Top umiejętności', 'id': 'Top umiejętności'},
                {'name': 'Średnia pensja', 'id': 'Średnia pensja'},
                {'name': 'Praca zdalna %', 'id': 'Praca zdalna %'}
            ],
            style_cell={'textAlign': 'left', 'fontSize': '12px'},
            style_header={'backgroundColor': 'var(--bs-dark)', 'color': 'white'},
            page_size=10
        )
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🏢 Top Firmy Zatrudniające"),
                            dcc.Graph(figure=fig_companies)
                        ])
                    ])
                ], md=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📊 Szczegółowe Statystyki Firm"),
                            company_table
                        ])
                    ])
                ], md=12)
            ])
        ])
    
    def create_trends_analysis(self, df):
        """Create trends analysis tab content"""
        daily_counts = self.data_processor.process_time_series(df)
        skill_trends = self.data_processor.get_skill_trends(df)
        
        if daily_counts.empty:
            return dbc.Alert("Brak danych o datach publikacji ofert", color="warning")
        
        # Job postings over time
        fig_trends = px.line(
            daily_counts,
            x='date',
            y='count',
            title='Trendy Publikacji Ofert w Czasie',
            labels={'date': 'Data', 'count': 'Liczba ofert'}
        )
        
        # Skills trends
        if not skill_trends.empty:
            fig_skill_trends = go.Figure()
            
            skill_columns = [col for col in skill_trends.columns if col != 'date']
            for skill in skill_columns:
                fig_skill_trends.add_trace(go.Scatter(
                    x=skill_trends['date'],
                    y=skill_trends[skill],
                    mode='lines+markers',
                    name=skill,
                    line=dict(width=2)
                ))
            
            fig_skill_trends.update_layout(
                title='Trendy Top 5 Umiejętności w Czasie',
                xaxis_title='Data',
                yaxis_title='Liczba ofert',
                height=500
            )
        else:
            fig_skill_trends = go.Figure()
            fig_skill_trends.add_annotation(text="Brak danych o trendach umiejętności", 
                                          x=0.5, y=0.5, showarrow=False)
        
        # Market summary
        total_jobs = len(df)
        date_range = ""
        if not daily_counts.empty:
            start_date = daily_counts['date'].min().strftime('%Y-%m-%d')
            end_date = daily_counts['date'].max().strftime('%Y-%m-%d')
            date_range = f"Okres: {start_date} - {end_date}"
        
        avg_daily = daily_counts['count'].mean() if not daily_counts.empty else 0
        
        market_summary = dbc.Card([
            dbc.CardBody([
                html.H4("📈 Podsumowanie Rynku"),
                html.P(f"Całkowita liczba ofert: {total_jobs:,}"),
                html.P(date_range),
                html.P(f"Średnio ofert dziennie: {avg_daily:.1f}"),
                html.P(f"Najaktywniejszy dzień: {daily_counts.loc[daily_counts['count'].idxmax(), 'date'].strftime('%Y-%m-%d')}" 
                      if not daily_counts.empty else "Brak danych")
            ])
        ])
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📈 Trendy Publikacji Ofert"),
                            dcc.Graph(figure=fig_trends)
                        ])
                    ])
                ], md=8),
                dbc.Col([market_summary], md=4)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🔥 Trendy Umiejętności"),
                            dcc.Graph(figure=fig_skill_trends)
                        ])
                    ])
                ], md=12)
            ])
        ])
    
    def create_salary_analysis(self, df):
        """Create salary analysis tab content"""
        if 'salary_avg' not in df.columns:
            return dbc.Alert("Brak danych o wynagrodzeniach", color="warning")
        
        salary_df = self.data_processor.process_salary_data(df)
        
        if salary_df.empty:
            return dbc.Alert("Brak poprawnych danych o wynagrodzeniach", color="warning")
        
        skill_salary_stats = self.data_processor.get_salary_by_skill(df)
        correlation_matrix = self.data_processor.calculate_correlation_matrix(df)
        
        # Salary distribution histogram
        fig_salary_dist = px.histogram(
            salary_df,
            x='salary_avg',
            title='Rozkład Wynagrodzeń',
            labels={'salary_avg': 'Wynagrodzenie (PLN)', 'count': 'Liczba ofert'},
            nbins=30
        )
        
        # Top paying skills
        if skill_salary_stats:
            top_paying_skills = sorted(skill_salary_stats.items(), 
                                     key=lambda x: x[1]['mean'], reverse=True)[:15]
            
            skills_salary_df = pd.DataFrame([
                {'Umiejętność': skill, 'Średnia pensja': stats['mean']}
                for skill, stats in top_paying_skills
            ])
            
            fig_skills_salary = px.bar(
                skills_salary_df,
                x='Średnia pensja',
                y='Umiejętność',
                title='Top 15 Najlepiej Płacących Umiejętności',
                orientation='h'
            )
            fig_skills_salary.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
        else:
            fig_skills_salary = go.Figure()
            fig_skills_salary.add_annotation(text="Brak danych o wynagrodzeniach dla umiejętności", 
                                           x=0.5, y=0.5, showarrow=False)
        
        # Salary by seniority
        if 'seniority' in salary_df.columns:
            seniority_salary = salary_df.groupby('seniority')['salary_avg'].agg(['mean', 'count']).reset_index()
            seniority_salary = seniority_salary[seniority_salary['count'] >= 3]  # Minimum samples
            
            fig_seniority_salary = px.bar(
                seniority_salary,
                x='seniority',
                y='mean',
                title='Średnie Wynagrodzenia według Poziomu Doświadczenia',
                labels={'seniority': 'Poziom doświadczenia', 'mean': 'Średnie wynagrodzenie (PLN)'}
            )
        else:
            fig_seniority_salary = go.Figure()
            fig_seniority_salary.add_annotation(text="Brak danych o poziomach doświadczenia", 
                                               x=0.5, y=0.5, showarrow=False)
        
        # Correlation with experience
        if 'skillsCount' in salary_df.columns:
            fig_skills_correlation = px.scatter(
                salary_df,
                x='skillsCount',
                y='salary_avg',
                title='Korelacja: Liczba Umiejętności vs Wynagrodzenie',
                labels={'skillsCount': 'Liczba umiejętności', 'salary_avg': 'Wynagrodzenie (PLN)'},
                trendline='ols'
            )
        else:
            fig_skills_correlation = go.Figure()
            fig_skills_correlation.add_annotation(text="Brak danych o liczbie umiejętności", 
                                                 x=0.5, y=0.5, showarrow=False)
        
        # Salary statistics
        salary_stats = {
            'mean': salary_df['salary_avg'].mean(),
            'median': salary_df['salary_avg'].median(),
            'min': salary_df['salary_avg'].min(),
            'max': salary_df['salary_avg'].max(),
            'std': salary_df['salary_avg'].std(),
            'count': len(salary_df)
        }
        
        stats_card = dbc.Card([
            dbc.CardBody([
                html.H4("💰 Statystyki Wynagrodzeń"),
                html.P(f"Średnia: {salary_stats['mean']:,.0f} PLN"),
                html.P(f"Mediana: {salary_stats['median']:,.0f} PLN"),
                html.P(f"Minimum: {salary_stats['min']:,.0f} PLN"),
                html.P(f"Maksimum: {salary_stats['max']:,.0f} PLN"),
                html.P(f"Odchylenie std: {salary_stats['std']:,.0f} PLN"),
                html.P(f"Liczba ofert z pensją: {salary_stats['count']:,}")
            ])
        ])
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📊 Rozkład Wynagrodzeń"),
                            dcc.Graph(figure=fig_salary_dist)
                        ])
                    ])
                ], md=8),
                dbc.Col([stats_card], md=4)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🏆 Najlepiej Płacące Umiejętności"),
                            dcc.Graph(figure=fig_skills_salary)
                        ])
                    ])
                ], md=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📈 Pensje według Doświadczenia"),
                            dcc.Graph(figure=fig_seniority_salary)
                        ])
                    ])
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🔗 Umiejętności vs Wynagrodzenie"),
                            dcc.Graph(figure=fig_skills_correlation)
                        ])
                    ])
                ], md=6)
            ])
        ])
    
    def create_detailed_analysis(self, df):
        """Create detailed analysis tab content"""
        skills_counter, skills_levels, skills_by_seniority = self.data_processor.process_skills_data(df)
        
        # Skill selector
        skill_options = [{'label': skill, 'value': skill} for skill, _ in skills_counter.most_common(50)]
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🔍 Szczegółowa Analiza Umiejętności"),
                            html.P("Wybierz umiejętność aby zobaczyć szczegółową analizę:"),
                            dcc.Dropdown(
                                id='detailed-skill-selector',
                                options=skill_options,
                                value=skill_options[0]['value'] if skill_options else None,
                                placeholder="Wybierz umiejętność..."
                            )
                        ])
                    ])
                ], md=12)
            ], className="mb-4"),
            
            html.Div(id='detailed-skill-analysis')
        ])
    
    def create_skill_specific_analysis(self, df, skill):
        """Create analysis for a specific skill"""
        # Filter jobs that require this skill
        skill_jobs = df[df['skills'].apply(
            lambda x: isinstance(x, dict) and skill in x
        )]
        
        if skill_jobs.empty:
            return dbc.Alert(f"Brak danych dla umiejętności: {skill}", color="warning")
        
        # Basic metrics
        total_jobs = len(skill_jobs)
        percentage = (total_jobs / len(df)) * 100
        
        # Skill levels distribution
        skill_levels = []
        for _, row in skill_jobs.iterrows():
            if isinstance(row['skills'], dict) and skill in row['skills']:
                skill_levels.append(row['skills'][skill])
        
        level_counts = pd.Series(skill_levels).value_counts()
        
        fig_levels = px.pie(
            values=level_counts.values,
            names=level_counts.index,
            title=f'Rozkład Poziomów dla {skill}'
        )
        
        # Seniority analysis
        seniority_counts = skill_jobs['seniority'].value_counts()
        seniority_df = pd.DataFrame({
            'Seniority': seniority_counts.index,
            'Liczba': seniority_counts.values
        })
        
        fig_seniority = px.bar(
            seniority_df,
            x='Seniority',
            y='Liczba',
            title=f'Rozkład Seniority dla {skill}'
        )
        
        # Top companies and cities
        top_companies = skill_jobs['company'].value_counts().head(10)
        top_cities = skill_jobs['city'].value_counts().head(10)
        
        # Salary analysis if available
        salary_info = ""
        salary_chart = go.Figure()
        if 'salary_avg' in skill_jobs.columns:
            skill_salaries = skill_jobs['salary_avg'].dropna()
            if len(skill_salaries) > 0:
                avg_salary = skill_salaries.mean()
                median_salary = skill_salaries.median()
                salary_info = f"Średnia: {avg_salary:,.0f} PLN | Mediana: {median_salary:,.0f} PLN"
                
                # Salary histogram
                salary_chart = px.histogram(
                    skill_salaries,
                    title=f'Rozkład Wynagrodzeń dla {skill}',
                    labels={'value': 'Wynagrodzenie (PLN)', 'count': 'Liczba ofert'}
                )
        
        return dbc.Container([
            # Overview metrics
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📊 Przegląd Umiejętności"),
                            html.P(f"Umiejętność: {skill}"),
                            html.P(f"Liczba ofert: {total_jobs:,}"),
                            html.P(f"Procent wszystkich ofert: {percentage:.1f}%"),
                            html.P(f"Informacje o wynagrodzeniu: {salary_info if salary_info else 'Brak danych'}")
                        ])
                    ])
                ], md=12)
            ], className="mb-4"),
            
            # Charts
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📊 Poziomy Umiejętności"),
                            dcc.Graph(figure=fig_levels)
                        ])
                    ])
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("👔 Analiza Seniority"),
                            dcc.Graph(figure=fig_seniority)
                        ])
                    ])
                ], md=6)
            ], className="mb-4"),
            
            # Salary analysis
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("💰 Analiza Wynagrodzeń"),
                            dcc.Graph(figure=salary_chart) if salary_info else html.P("Brak danych o wynagrodzeniach dla tej umiejętności")
                        ])
                    ])
                ], md=12)
            ], className="mb-4") if salary_info else [],
            
            # Top lists
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🏢 Top Firmy"),
                            html.Div([
                                html.P(f"{i+1}. {company} ({count} ofert)")
                                for i, (company, count) in enumerate(top_companies.head(5).items())
                            ] if len(top_companies) > 0 else [html.P("Brak danych")])
                        ])
                    ])
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🌍 Top Miasta"),
                            html.Div([
                                html.P(f"{i+1}. {city} ({count} ofert)")
                                for i, (city, count) in enumerate(top_cities.head(5).items())
                            ] if len(top_cities) > 0 else [html.P("Brak danych")])
                        ])
                    ])
                ], md=6)
            ])
        ])
