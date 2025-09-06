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
    
    def _parse_salary_data(self, df):
        """Parse salary data from string format like '11 000 - 16 000 PLN'"""
        df_copy = df.copy()
        
        # Parse salary string into min, max, avg
        salary_min_list = []
        salary_max_list = []
        salary_avg_list = []
        
        for _, row in df_copy.iterrows():
            salary_str = row.get('salary', '')
            salary_min = row.get('salary_min', None)
            salary_max = row.get('salary_max', None)
            salary_avg = row.get('salary_avg', None)
            
            # Try to parse from string if numeric values are not available
            if pd.isna(salary_avg) and salary_str and isinstance(salary_str, str):
                try:
                    # Remove 'PLN' and other text
                    salary_clean = salary_str.replace('PLN', '').replace('zł', '').strip()
                    
                    # Handle range format like "11 000 - 16 000"
                    if '-' in salary_clean:
                        parts = salary_clean.split('-')
                        if len(parts) == 2:
                            min_sal = float(parts[0].replace(' ', '').replace(',', ''))
                            max_sal = float(parts[1].replace(' ', '').replace(',', ''))
                            avg_sal = (min_sal + max_sal) / 2
                            
                            salary_min_list.append(min_sal)
                            salary_max_list.append(max_sal)
                            salary_avg_list.append(avg_sal)
                        else:
                            salary_min_list.append(None)
                            salary_max_list.append(None)
                            salary_avg_list.append(None)
                    else:
                        # Single value
                        try:
                            single_val = float(salary_clean.replace(' ', '').replace(',', ''))
                            salary_min_list.append(single_val)
                            salary_max_list.append(single_val)
                            salary_avg_list.append(single_val)
                        except:
                            salary_min_list.append(None)
                            salary_max_list.append(None)
                            salary_avg_list.append(None)
                except:
                    salary_min_list.append(None)
                    salary_max_list.append(None)
                    salary_avg_list.append(None)
            else:
                # Use existing values
                salary_min_list.append(salary_min)
                salary_max_list.append(salary_max)
                salary_avg_list.append(salary_avg)
        
        # Update dataframe
        df_copy['salary_min'] = salary_min_list
        df_copy['salary_max'] = salary_max_list
        df_copy['salary_avg'] = salary_avg_list
        
        return df_copy
    
    def process_salary_data(self, df):
        """Process salary data for analysis"""
        # First parse salary strings
        salary_df = self._parse_salary_data(df)
        
        # Clean salary data
        if 'salary_avg' in salary_df.columns:
            salary_df = salary_df[salary_df['salary_avg'].notna()]
            salary_df = salary_df[salary_df['salary_avg'] > 0]
        
        return salary_df
    
    def get_salary_by_skill(self, df):
        """Calculate average salary by skill"""
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
        df_time['published_date'] = pd.to_datetime(df_time['published_date'], errors='coerce', dayfirst=True)
        df_time = df_time.dropna(subset=['published_date'])
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
        
        if not top_skill_names:
            return pd.DataFrame()
        
        df_time = df.copy()
        df_time['published_date'] = pd.to_datetime(df_time['published_date'], errors='coerce', dayfirst=True)
        df_time = df_time.dropna(subset=['published_date'])
        df_time['date'] = df_time['published_date'].dt.date
        
        result_df = None
        
        for skill in top_skill_names:
            skill_df = df_time[df_time['skills'].apply(
                lambda x: isinstance(x, dict) and skill in x
            )]
            
            if not skill_df.empty:
                daily_counts = skill_df.groupby('date').size().reset_index(name=skill)
                daily_counts['date'] = pd.to_datetime(daily_counts['date'])
                
                if result_df is None:
                    result_df = daily_counts
                else:
                    result_df = result_df.merge(daily_counts, on='date', how='outer')
        
        if result_df is not None and not result_df.empty:
            result_df = result_df.fillna(0)
            result_df = result_df.sort_values('date')
            return result_df
        
        return pd.DataFrame()
    
    def calculate_correlation_matrix(self, df):
        """Calculate correlation matrix for salary analysis"""
        df_with_parsed_salary = self._parse_salary_data(df)
        
        if 'salary_avg' not in df_with_parsed_salary.columns or df_with_parsed_salary['salary_avg'].isna().all():
            return pd.DataFrame()
        
        # Calculate skills count
        skills_counts = []
        for _, row in df_with_parsed_salary.iterrows():
            if isinstance(row.get('skills'), dict):
                skills_counts.append(len(row['skills']))
            else:
                skills_counts.append(0)
        
        df_with_parsed_salary['skillsCount'] = skills_counts
        
        # Prepare data for correlation
        corr_data = df_with_parsed_salary[['salary_avg', 'skillsCount']].copy()
        corr_data = corr_data.dropna()
        
        # Add categorical variables as dummies
        if 'seniority' in df_with_parsed_salary.columns:
            seniority_dummies = pd.get_dummies(df_with_parsed_salary['seniority'], prefix='seniority')
            corr_data = pd.concat([corr_data, seniority_dummies], axis=1)
        
        if 'remote' in df_with_parsed_salary.columns:
            corr_data['remote'] = df_with_parsed_salary['remote'].astype(int)
        
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
    
    def calculate_skills_salary_correlation(self, df):
        """Calculate correlation between individual skills and salary"""
        try:
            df_with_parsed_salary = self._parse_salary_data(df)
            
            if 'salary_avg' not in df_with_parsed_salary.columns or df_with_parsed_salary['salary_avg'].isna().all():
                return {}
            
            # Get all unique skills
            all_skills = set()
            for idx in df_with_parsed_salary.index:
                row_skills = df_with_parsed_salary.loc[idx, 'skills']
                if isinstance(row_skills, dict):
                    all_skills.update(row_skills.keys())
        except Exception as e:
            print(f"Error in calculate_skills_salary_correlation: {e}")
            return {}
        
        skill_correlations = {}
        
        for skill in all_skills:
            # Create binary variable for skill presence
            skill_present = []
            skill_salaries = []
            
            for idx in df_with_parsed_salary.index:
                salary = df_with_parsed_salary.loc[idx, 'salary_avg']
                if pd.notna(salary):
                    row_skills = df_with_parsed_salary.loc[idx, 'skills']
                    has_skill = isinstance(row_skills, dict) and skill in row_skills
                    skill_present.append(1 if has_skill else 0)
                    skill_salaries.append(salary)
            
            if len(skill_present) > 10 and sum(skill_present) >= 3:  # Minimum samples
                try:
                    correlation = np.corrcoef(skill_present, skill_salaries)[0, 1]
                    if not np.isnan(correlation):
                        # Calculate additional statistics
                        with_skill_salaries = [sal for i, sal in enumerate(skill_salaries) if skill_present[i] == 1]
                        without_skill_salaries = [sal for i, sal in enumerate(skill_salaries) if skill_present[i] == 0]
                        
                        skill_correlations[skill] = {
                            'correlation': correlation,
                            'avg_with_skill': np.mean(with_skill_salaries) if with_skill_salaries else 0,
                            'avg_without_skill': np.mean(without_skill_salaries) if without_skill_salaries else 0,
                            'count_with_skill': len(with_skill_salaries),
                            'count_without_skill': len(without_skill_salaries)
                        }
                except:
                    continue
        
        return skill_correlations
