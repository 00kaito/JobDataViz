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
                            
                            # Filter out unrealistic salary values (below 4k or above 60k PLN)
                            if 4000 <= avg_sal <= 60000:
                                salary_min_list.append(min_sal)
                                salary_max_list.append(max_sal)
                                salary_avg_list.append(avg_sal)
                            else:
                                salary_min_list.append(None)
                                salary_max_list.append(None)
                                salary_avg_list.append(None)
                        else:
                            salary_min_list.append(None)
                            salary_max_list.append(None)
                            salary_avg_list.append(None)
                    else:
                        # Single value
                        try:
                            single_val = float(salary_clean.replace(' ', '').replace(',', ''))
                            
                            # Filter out unrealistic salary values (below 4k or above 60k PLN)
                            if 4000 <= single_val <= 60000:
                                salary_min_list.append(single_val)
                                salary_max_list.append(single_val)
                                salary_avg_list.append(single_val)
                            else:
                                salary_min_list.append(None)
                                salary_max_list.append(None)
                                salary_avg_list.append(None)
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
        
        # First parse salary data for the entire dataframe
        df_with_salary = self._parse_salary_data(df)
        
        company_stats = {}
        
        for company in df_with_salary['company'].dropna().unique():
            company_df = df_with_salary[df_with_salary['company'] == company]
            
            # Skills analysis for this company
            skills_counter, _, _ = self.process_skills_data(company_df)
            top_skills = skills_counter.most_common(3)
            
            # Salary stats - now using parsed salary data
            salary_stats = {}
            if 'salary_avg' in company_df.columns:
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
        """Calculate correlation between individual skills and salary - simplified version"""
        try:
            df_with_parsed_salary = self._parse_salary_data(df)
            
            if 'salary_avg' not in df_with_parsed_salary.columns or df_with_parsed_salary['salary_avg'].isna().all():
                return {}
            
            # Get salary data as lists for faster processing
            salaries = df_with_parsed_salary['salary_avg'].dropna().tolist()
            skills_data = df_with_parsed_salary['skills'].dropna().tolist()
            
            if len(salaries) < 10:
                return {}
            
            # Get unique skills from limited sample to avoid timeout
            all_skills = set()
            for skills_dict in skills_data[:200]:  # Limit to first 200 records (increased)
                if isinstance(skills_dict, dict):
                    all_skills.update(skills_dict.keys())
            
            # Limit to top 100 most common skills (increased from 50)
            all_skills = list(all_skills)[:100]
            
            skill_correlations = {}
            
            for skill in all_skills:
                with_skill_salaries = []
                without_skill_salaries = []
                
                # Simplified data collection
                for i, skills_dict in enumerate(skills_data):
                    if i < len(salaries) and isinstance(skills_dict, dict):
                        if skill in skills_dict:
                            with_skill_salaries.append(salaries[i])
                        else:
                            without_skill_salaries.append(salaries[i])
                
                # Only calculate if we have enough samples
                if len(with_skill_salaries) >= 3 and len(without_skill_salaries) >= 3:
                    avg_with = np.mean(with_skill_salaries)
                    avg_without = np.mean(without_skill_salaries)
                    
                    skill_correlations[skill] = {
                        'correlation': (avg_with - avg_without) / max(avg_with, avg_without, 1),  # Simplified correlation
                        'avg_with_skill': avg_with,
                        'avg_without_skill': avg_without,
                        'count_with_skill': len(with_skill_salaries),
                        'count_without_skill': len(without_skill_salaries)
                    }
            
            return skill_correlations
            
        except Exception as e:
            print(f"Error in calculate_skills_salary_correlation: {e}")
            return {}
    
    def get_skills_by_category(self, df):
        """Get skills analysis by category"""
        try:
            skills_by_category = {}
            category_skill_counts = {}
            
            for _, row in df.iterrows():
                skills = row.get('skills', {})
                category = row.get('category', 'Nieokreślona')
                
                if isinstance(skills, dict):
                    for skill in skills.keys():
                        if skill not in skills_by_category:
                            skills_by_category[skill] = {}
                        
                        if category not in skills_by_category[skill]:
                            skills_by_category[skill][category] = 0
                        
                        skills_by_category[skill][category] += 1
                        
                        # Count total occurrences for pie chart
                        if skill not in category_skill_counts:
                            category_skill_counts[skill] = {}
                        if category not in category_skill_counts[skill]:
                            category_skill_counts[skill][category] = 0
                        category_skill_counts[skill][category] += 1
            
            # Find most common category for each skill
            skill_main_categories = {}
            for skill, categories in skills_by_category.items():
                if categories:
                    main_category = max(categories.items(), key=lambda x: x[1])
                    skill_main_categories[skill] = {
                        'main_category': main_category[0],
                        'count': main_category[1],
                        'total_count': sum(categories.values()),
                        'all_categories': categories
                    }
            
            return skill_main_categories, category_skill_counts
            
        except Exception as e:
            print(f"Error in get_skills_by_category: {e}")
            return {}, {}
    
    def get_top_skills_by_category(self, df):
        """Get top 3 skills for each category"""
        try:
            category_skills = {}
            
            for _, row in df.iterrows():
                skills = row.get('skills', {})
                category = row.get('category', 'Nieokreślona')
                
                if isinstance(skills, dict):
                    if category not in category_skills:
                        category_skills[category] = {}
                    
                    for skill in skills.keys():
                        if skill not in category_skills[category]:
                            category_skills[category][skill] = 0
                        category_skills[category][skill] += 1
            
            # Get top 3 skills for each category
            top_skills_by_category = {}
            for category, skills in category_skills.items():
                if skills:
                    # Sort skills by count and get top 3
                    sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)[:3]
                    top_skills_by_category[category] = sorted_skills
            
            return top_skills_by_category
            
        except Exception as e:
            print(f"Error in get_top_skills_by_category: {e}")
            return {}
    
    def get_cooccurring_skills(self, df, selected_skills):
        """Get skills that most frequently co-occur with selected skills"""
        try:
            if not selected_skills:
                return []
            
            skill_cooccurrences = {}
            
            for _, row in df.iterrows():
                skills = row.get('skills', {})
                if isinstance(skills, dict):
                    skill_list = list(skills.keys())
                    
                    # Check if any of the selected skills are in this job's skills
                    has_selected_skill = any(skill in skill_list for skill in selected_skills)
                    
                    if has_selected_skill:
                        # Count co-occurrences for all other skills
                        for skill in skill_list:
                            if skill not in selected_skills:
                                if skill not in skill_cooccurrences:
                                    skill_cooccurrences[skill] = 0
                                skill_cooccurrences[skill] += 1
            
            # Sort by frequency and return top 5
            sorted_skills = sorted(skill_cooccurrences.items(), key=lambda x: x[1], reverse=True)[:5]
            return sorted_skills
            
        except Exception as e:
            print(f"Error in get_cooccurring_skills: {e}")
            return []
