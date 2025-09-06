import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
import json

class DataProcessor:
    def __init__(self):
        pass
    
    def process_skills_data(self, df):
        """Process skills data for analysis"""
        skills_counter = Counter()
        skills_levels = {}
        skills_by_seniority = {}
        
        for _, row in df.iterrows():
            if isinstance(row['skills'], dict):
                for skill, level in row['skills'].items():
                    skills_counter[skill] += 1
                    
                    # Track skill levels
                    if skill not in skills_levels:
                        skills_levels[skill] = Counter()
                    skills_levels[skill][level] += 1
                    
                    # Track skills by seniority
                    seniority = row.get('seniority', 'Unknown')
                    if seniority not in skills_by_seniority:
                        skills_by_seniority[seniority] = Counter()
                    skills_by_seniority[seniority][skill] += 1
        
        return skills_counter, skills_levels, skills_by_seniority
    
    def calculate_skill_weights(self, skills_levels):
        """Calculate weighted scores for skills based on levels"""
        level_weights = {
            'Junior': 1,
            'Regular': 2,
            'Senior': 3,
            'Expert': 4
        }
        
        skill_weights = {}
        for skill, levels in skills_levels.items():
            total_weight = 0
            total_count = 0
            
            for level, count in levels.items():
                weight = level_weights.get(level, 1)
                total_weight += weight * count
                total_count += count
            
            if total_count > 0:
                skill_weights[skill] = total_weight / total_count
        
        return skill_weights
    
    def get_skill_combinations(self, df, top_n=15):
        """Get most common skill combinations"""
        combinations = Counter()
        
        for _, row in df.iterrows():
            if isinstance(row['skills'], dict):
                skills = sorted(row['skills'].keys())
                if len(skills) > 1:
                    # Create combinations of 2-3 skills
                    for i in range(len(skills)):
                        for j in range(i+1, min(i+4, len(skills))):
                            combo = tuple(skills[i:j+1])
                            combinations[combo] += 1
        
        return combinations.most_common(top_n)
    
    def process_salary_data(self, df):
        """Process salary data for analysis"""
        salary_df = df.copy()
        
        # Clean salary data
        if 'salary_avg' in salary_df.columns:
            salary_df = salary_df[salary_df['salary_avg'].notna()]
            salary_df = salary_df[salary_df['salary_avg'] > 0]
        
        return salary_df
    
    def get_salary_by_skill(self, df):
        """Calculate average salary by skill"""
        if 'salary_avg' not in df.columns:
            return {}
        
        skill_salaries = {}
        salary_df = self.process_salary_data(df)
        
        for _, row in salary_df.iterrows():
            if isinstance(row['skills'], dict) and pd.notna(row['salary_avg']):
                for skill in row['skills'].keys():
                    if skill not in skill_salaries:
                        skill_salaries[skill] = []
                    skill_salaries[skill].append(row['salary_avg'])
        
        # Calculate statistics
        skill_salary_stats = {}
        for skill, salaries in skill_salaries.items():
            if len(salaries) >= 3:  # Minimum samples for reliable statistics
                skill_salary_stats[skill] = {
                    'mean': np.mean(salaries),
                    'median': np.median(salaries),
                    'min': np.min(salaries),
                    'max': np.max(salaries),
                    'count': len(salaries),
                    'std': np.std(salaries)
                }
        
        return skill_salary_stats
    
    def process_time_series(self, df):
        """Process time series data for trend analysis"""
        if 'published_date' not in df.columns:
            return pd.DataFrame()
        
        df_time = df.copy()
        df_time['published_date'] = pd.to_datetime(df_time['published_date'])
        df_time['date'] = df_time['published_date'].dt.date
        
        # Group by date
        daily_counts = df_time.groupby('date').size().reset_index(name='count')
        daily_counts['date'] = pd.to_datetime(daily_counts['date'])
        
        return daily_counts
    
    def get_skill_trends(self, df, top_skills=5):
        """Get trends for top skills over time"""
        if 'published_date' not in df.columns:
            return pd.DataFrame()
        
        # Get top skills
        skills_counter, _, _ = self.process_skills_data(df)
        top_skill_names = [skill for skill, _ in skills_counter.most_common(top_skills)]
        
        df_time = df.copy()
        df_time['published_date'] = pd.to_datetime(df_time['published_date'])
        df_time['date'] = df_time['published_date'].dt.date
        
        skill_trends = {}
        
        for skill in top_skill_names:
            skill_df = df_time[df_time['skills'].apply(
                lambda x: isinstance(x, dict) and skill in x
            )]
            
            daily_counts = skill_df.groupby('date').size().reset_index(name=skill)
            daily_counts['date'] = pd.to_datetime(daily_counts['date'])
            
            if skill_trends:
                skill_trends = skill_trends.merge(daily_counts, on='date', how='outer')
            else:
                skill_trends = daily_counts
        
        if not skill_trends.empty:
            skill_trends = skill_trends.fillna(0)
            skill_trends = skill_trends.sort_values('date')
        
        return skill_trends
    
    def calculate_correlation_matrix(self, df):
        """Calculate correlation matrix for salary analysis"""
        if 'salary_avg' not in df.columns:
            return pd.DataFrame()
        
        # Prepare data for correlation
        corr_data = df[['salary_avg', 'skillsCount']].copy()
        corr_data = corr_data.dropna()
        
        # Add categorical variables as dummies
        if 'seniority' in df.columns:
            seniority_dummies = pd.get_dummies(df['seniority'], prefix='seniority')
            corr_data = pd.concat([corr_data, seniority_dummies], axis=1)
        
        if 'remote' in df.columns:
            corr_data['remote'] = df['remote'].astype(int)
        
        return corr_data.corr()
    
    def get_location_stats(self, df):
        """Get statistics by location"""
        if 'city' not in df.columns:
            return {}
        
        location_stats = {}
        
        for city in df['city'].dropna().unique():
            city_df = df[df['city'] == city]
            
            # Skills analysis for this city
            skills_counter, _, _ = self.process_skills_data(city_df)
            top_skills = skills_counter.most_common(5)
            
            # Salary stats
            salary_stats = {}
            if 'salary_avg' in df.columns:
                city_salaries = city_df['salary_avg'].dropna()
                if len(city_salaries) > 0:
                    salary_stats = {
                        'mean': city_salaries.mean(),
                        'median': city_salaries.median(),
                        'count': len(city_salaries)
                    }
            
            location_stats[city] = {
                'total_jobs': len(city_df),
                'top_skills': top_skills,
                'salary_stats': salary_stats,
                'companies': city_df['company'].nunique(),
                'remote_ratio': city_df['remote'].mean() if 'remote' in city_df.columns else 0
            }
        
        return location_stats
    
    def get_company_stats(self, df):
        """Get statistics by company"""
        if 'company' not in df.columns:
            return {}
        
        company_stats = {}
        
        for company in df['company'].dropna().unique():
            company_df = df[df['company'] == company]
            
            # Skills analysis for this company
            skills_counter, _, _ = self.process_skills_data(company_df)
            top_skills = skills_counter.most_common(3)
            
            # Salary stats
            salary_stats = {}
            if 'salary_avg' in df.columns:
                company_salaries = company_df['salary_avg'].dropna()
                if len(company_salaries) > 0:
                    salary_stats = {
                        'mean': company_salaries.mean(),
                        'median': company_salaries.median(),
                        'count': len(company_salaries)
                    }
            
            company_stats[company] = {
                'total_jobs': len(company_df),
                'top_skills': top_skills,
                'salary_stats': salary_stats,
                'cities': company_df['city'].nunique(),
                'remote_ratio': company_df['remote'].mean() if 'remote' in company_df.columns else 0,
                'seniority_distribution': company_df['seniority'].value_counts().to_dict()
            }
        
        return company_stats
