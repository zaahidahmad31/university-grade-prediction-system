# src/features/unified_feature_calculator.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import logging
from scipy import stats
from sklearn.preprocessing import LabelEncoder
from ..utils.logger import setup_logger
from ..utils.config import Config
from ..utils.constants import RANDOM_STATE

logger = setup_logger(__name__)

class UnifiedFeatureCalculator:
    """
    Unified feature calculator that works with both OULAD and production data.
    This ensures consistency between training and production environments.
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.feature_order = self.config.get_feature_order()
        self.label_encoders = {}
        
    def calculate_features(
        self,
        student_data: Dict[str, pd.DataFrame],
        course_length: Optional[int] = None,
        calculation_point: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Calculate all features for students.
        
        Args:
            student_data: Dictionary with OULAD-format data
            course_length: Total course length in days
            calculation_point: Day to calculate features up to (for temporal features)
            
        Returns:
            DataFrame with all features
        """
        logger.info("Starting feature calculation...")
        
        # Extract dataframes with proper defaults
        student_info = student_data.get('student_info', pd.DataFrame())
        student_vle = student_data.get('student_vle', pd.DataFrame())
        student_assessment = student_data.get('student_assessment', pd.DataFrame())
        assessments = student_data.get('assessments', pd.DataFrame())
        
        # Ensure DataFrames have proper columns if empty
        if student_vle.empty:
            student_vle = pd.DataFrame(columns=['id_student', 'code_module', 'code_presentation', 'id_site', 'date', 'sum_click'])
        
        if student_assessment.empty:
            student_assessment = pd.DataFrame(columns=['id_student', 'id_assessment', 'score', 'date_submitted'])
        
        if assessments.empty:
            assessments = pd.DataFrame(columns=['id_assessment', 'assessment_type', 'date'])
        
        # Get unique students
        if not student_info.empty:
            students = student_info[['id_student', 'code_module', 'code_presentation']].drop_duplicates()
        elif not student_vle.empty:
            # Extract from VLE data if no student info
            students = student_vle[['id_student', 'code_module', 'code_presentation']].drop_duplicates()
        else:
            # If both are empty, return empty features
            logger.warning("No student data found")
            return pd.DataFrame()
        
        all_features = []
        
        for _, student in students.iterrows():
            student_id = student['id_student']
            module = student.get('code_module', 'NA')
            presentation = student.get('code_presentation', 'NA')
            
            # Filter data for this student - handle empty DataFrames
            if not student_vle.empty and all(col in student_vle.columns for col in ['id_student', 'code_module', 'code_presentation']):
                student_vle_data = student_vle[
                    (student_vle['id_student'] == student_id) &
                    (student_vle['code_module'] == module) &
                    (student_vle['code_presentation'] == presentation)
                ]
            else:
                student_vle_data = pd.DataFrame(columns=['id_site', 'date', 'sum_click'])
            
            if not student_assessment.empty and 'id_student' in student_assessment.columns:
                student_assess_data = student_assessment[
                    student_assessment['id_student'] == student_id
                ]
            else:
                student_assess_data = pd.DataFrame(columns=['id_assessment', 'score'])
            
            # Calculate features
            features = {'id_student': student_id}
            
            # Activity features
            activity_features = self._calculate_activity_features(
                student_vle_data,
                course_length,
                calculation_point
            )
            features.update(activity_features)
            
            # Assessment features
            assessment_features = self._calculate_assessment_features(
                student_assess_data,
                assessments,
                calculation_point
            )
            features.update(assessment_features)
            
            # Temporal features
            temporal_features = self._calculate_temporal_features(
                student_vle_data,
                calculation_point
            )
            features.update(temporal_features)
            
            # Demographic features - with defaults for missing data
            if not student_info.empty and student_id in student_info['id_student'].values:
                student_rows = student_info[student_info['id_student'] == student_id]
                if not student_rows.empty:
                    student_row = student_rows.iloc[0]
                    demographic_features = self._calculate_demographic_features(student_row)
                    features.update(demographic_features)
                else:
                    features.update(self._get_default_demographic_features())
            else:
                features.update(self._get_default_demographic_features())
            
            all_features.append(features)
        
        # Create dataframe
        features_df = pd.DataFrame(all_features)
        
        # Ensure all features are present
        for feature in self.feature_order:
            if feature not in features_df.columns:
                features_df[feature] = 0
        
        logger.info(f"Calculated features for {len(features_df)} students")
        
        return features_df
    
    def _get_default_demographic_features(self) -> Dict[str, Union[int, float]]:
        """Get default demographic features when student info is missing"""
        return {
            'age_band_encoded': 0,
            'highest_education_encoded': 2,
            'num_of_prev_attempts': 0,
            'studied_credits': 60,
            'has_disability': 0
        }
    
    def _calculate_activity_features(
        self,
        vle_data: pd.DataFrame,
        course_length: Optional[int] = None,
        calculation_point: Optional[int] = None
    ) -> Dict[str, float]:
        """Calculate activity-based features"""
        features = {}
        
        # Filter data up to calculation point if specified
        if calculation_point is not None and not vle_data.empty and 'date' in vle_data.columns:
            vle_data = vle_data[vle_data['date'] <= calculation_point]
        
        if vle_data.empty or 'date' not in vle_data.columns:
            # Return zeros for all activity features
            return {
                'days_active': 0,
                'total_clicks': 0,
                'unique_materials': 0,
                'activity_rate': 0.0,
                'avg_clicks_per_active_day': 0.0,
                'first_activity_day': 0,
                'last_activity_day': 0
            }
        
        # Basic activity metrics
        features['days_active'] = vle_data['date'].nunique()
        features['total_clicks'] = vle_data['sum_click'].sum() if 'sum_click' in vle_data.columns else 0
        features['unique_materials'] = vle_data['id_site'].nunique() if 'id_site' in vle_data.columns else 0
        
        # Calculate activity rate
        if calculation_point is not None:
            days_elapsed = max(calculation_point, 1)
        elif course_length is not None:
            days_elapsed = course_length
        else:
            days_elapsed = max(vle_data['date'].max() - vle_data['date'].min() + 1, 1)
        
        features['activity_rate'] = (features['days_active'] / days_elapsed) * 100
        
        # Average clicks per active day
        features['avg_clicks_per_active_day'] = (
            features['total_clicks'] / features['days_active']
            if features['days_active'] > 0 else 0
        )
        
        # First and last activity
        features['first_activity_day'] = vle_data['date'].min() if not vle_data.empty else 0
        features['last_activity_day'] = vle_data['date'].max() if not vle_data.empty else 0
        
        return features
    
    def _calculate_assessment_features(
        self,
        assessment_data: pd.DataFrame,
        assessments_meta: pd.DataFrame,
        calculation_point: Optional[int] = None
    ) -> Dict[str, float]:
        """Calculate assessment-based features"""
        features = {}
        
        # Filter assessments up to calculation point
        if calculation_point is not None and not assessments_meta.empty and 'date' in assessments_meta.columns:
            valid_assessments = assessments_meta[
                assessments_meta['date'] <= calculation_point
            ]['id_assessment'].tolist()
            
            if not assessment_data.empty and 'id_assessment' in assessment_data.columns:
                assessment_data = assessment_data[
                    assessment_data['id_assessment'].isin(valid_assessments)
                ]
        
        # Basic counts
        features['submitted_assessments'] = len(assessment_data) if not assessment_data.empty else 0
        
        # Submission rate
        if not assessments_meta.empty:
            total_assessments = len(assessments_meta)
            if calculation_point is not None and 'date' in assessments_meta.columns:
                total_assessments = len(
                    assessments_meta[assessments_meta['date'] <= calculation_point]
                )
            features['submission_rate'] = (
                features['submitted_assessments'] / total_assessments * 100
                if total_assessments > 0 else 0
            )
        else:
            features['submission_rate'] = 0
        
        if assessment_data.empty or 'score' not in assessment_data.columns:
            # Return zeros for score features
            return {
                **features,
                'avg_score': 0.0,
                'avg_score_cma': 0.0,
                'avg_score_tma': 0.0,
                'avg_score_exam': 0.0,
                'on_time_submissions': 0,
                'avg_days_early': 0.0,
                'late_submission_count': 0
            }
        
        # Average scores
        features['avg_score'] = assessment_data['score'].mean()
        
        # Scores by assessment type
        if not assessments_meta.empty and 'assessment_type' in assessments_meta.columns:
            merged = assessment_data.merge(
                assessments_meta[['id_assessment', 'assessment_type']],
                on='id_assessment',
                how='left'
            )
            
            for assess_type in ['CMA', 'TMA', 'Exam']:
                if 'assessment_type' in merged.columns:
                    type_scores = merged[
                        merged['assessment_type'] == assess_type
                    ]['score']
                    features[f'avg_score_{assess_type.lower()}'] = (
                        type_scores.mean() if len(type_scores) > 0 else 0
                    )
                else:
                    features[f'avg_score_{assess_type.lower()}'] = 0
        else:
            features['avg_score_cma'] = 0
            features['avg_score_tma'] = 0
            features['avg_score_exam'] = 0
        
        # Submission timing
        if (not assessments_meta.empty and 'date_submitted' in assessment_data.columns 
            and 'date' in assessments_meta.columns and 'id_assessment' in assessment_data.columns):
            merged = assessment_data.merge(
                assessments_meta[['id_assessment', 'date']],
                on='id_assessment',
                how='left'
            )
            
            if 'date' in merged.columns and 'date_submitted' in merged.columns:
                merged['days_early'] = merged['date'] - merged['date_submitted']
                
                features['on_time_submissions'] = len(merged[merged['days_early'] >= 0])
                features['avg_days_early'] = merged['days_early'].mean() if len(merged) > 0 else 0
                features['late_submission_count'] = len(merged[merged['days_early'] < 0])
            else:
                features['on_time_submissions'] = 0
                features['avg_days_early'] = 0
                features['late_submission_count'] = 0
        else:
            features['on_time_submissions'] = 0
            features['avg_days_early'] = 0
            features['late_submission_count'] = 0
        
        return features
    
    def _calculate_temporal_features(
        self,
        vle_data: pd.DataFrame,
        calculation_point: Optional[int] = None
    ) -> Dict[str, float]:
        """Calculate temporal pattern features"""
        features = {}
        
        if vle_data.empty or 'date' not in vle_data.columns:
            return {
                'weekly_activity_std': 0.0,
                'activity_regularity': 0.0,
                'longest_inactivity_gap': 0,
                'weekend_activity_ratio': 0.0,
                'activity_trend': 0.0
            }
        
        # Filter data
        if calculation_point is not None:
            vle_data = vle_data[vle_data['date'] <= calculation_point]
        
        if vle_data.empty:
            return {
                'weekly_activity_std': 0.0,
                'activity_regularity': 0.0,
                'longest_inactivity_gap': 0,
                'weekend_activity_ratio': 0.0,
                'activity_trend': 0.0
            }
        
        # Weekly activity standard deviation
        vle_data = vle_data.copy()  # Avoid SettingWithCopyWarning
        vle_data['week'] = vle_data['date'] // 7
        
        if 'sum_click' in vle_data.columns:
            weekly_clicks = vle_data.groupby('week')['sum_click'].sum()
        else:
            weekly_clicks = vle_data.groupby('week').size()
            
        features['weekly_activity_std'] = weekly_clicks.std() if len(weekly_clicks) > 1 else 0
        
        # Activity regularity (inverse of coefficient of variation)
        if weekly_clicks.mean() > 0 and len(weekly_clicks) > 1:
            cv = weekly_clicks.std() / weekly_clicks.mean()
            features['activity_regularity'] = 1 / (1 + cv)
        else:
            features['activity_regularity'] = 0
        
        # Longest inactivity gap
        if len(vle_data) > 1:
            sorted_dates = sorted(vle_data['date'].unique())
            gaps = [sorted_dates[i+1] - sorted_dates[i] for i in range(len(sorted_dates)-1)]
            features['longest_inactivity_gap'] = max(gaps) if gaps else 0
        else:
            features['longest_inactivity_gap'] = 0
        
        # Weekend activity ratio (assuming course starts on Monday)
        vle_data['day_of_week'] = vle_data['date'] % 7
        
        if 'sum_click' in vle_data.columns:
            weekend_clicks = vle_data[vle_data['day_of_week'].isin([5, 6])]['sum_click'].sum()
            total_clicks = vle_data['sum_click'].sum()
        else:
            weekend_clicks = len(vle_data[vle_data['day_of_week'].isin([5, 6])])
            total_clicks = len(vle_data)
            
        features['weekend_activity_ratio'] = (
            weekend_clicks / total_clicks if total_clicks > 0 else 0
        )
        
        # Activity trend (linear regression slope)
        if len(weekly_clicks) > 2:
            weeks = np.arange(len(weekly_clicks))
            slope, _, _, _, _ = stats.linregress(weeks, weekly_clicks.values)
            features['activity_trend'] = slope
        else:
            features['activity_trend'] = 0
        
        return features
    
    def _calculate_demographic_features(
        self,
        student_row: pd.Series
    ) -> Dict[str, Union[int, float]]:
        """Calculate demographic features"""
        features = {}
        
        # Age band encoding
        age_band_map = {
            '0-35': 0,
            '35-55': 1,
            '55+': 2
        }
        features['age_band_encoded'] = age_band_map.get(
            student_row.get('age_band', '0-35'),
            0
        )
        
        # Education level encoding
        education_map = {
            'No Formal quals': 0,
            'Lower Than A Level': 1,
            'A Level or Equivalent': 2,
            'HE Qualification': 3,
            'Post Graduate Qualification': 4
        }
        features['highest_education_encoded'] = education_map.get(
            student_row.get('highest_education', 'A Level or Equivalent'),
            2
        )
        
        # Direct features
        features['num_of_prev_attempts'] = int(
            student_row.get('num_of_prev_attempts', 0)
        )
        features['studied_credits'] = int(
            student_row.get('studied_credits', 60)
        )
        
        # Disability flag
        features['has_disability'] = 1 if student_row.get('disability', 'N') == 'Y' else 0
        
        return features
    
    def get_feature_vector(
        self,
        features_df: pd.DataFrame,
        student_id: Optional[int] = None
    ) -> np.ndarray:
        """
        Get feature vector in correct order for model input.
        
        Args:
            features_df: DataFrame with calculated features
            student_id: Optional specific student ID
            
        Returns:
            Feature vector(s) as numpy array
        """
        if student_id is not None:
            features_df = features_df[features_df['id_student'] == student_id]
        
        # Ensure all features are present
        for feature in self.feature_order:
            if feature not in features_df.columns:
                features_df[feature] = 0
        
        # Select features in correct order
        feature_matrix = features_df[self.feature_order].values
        
        return feature_matrix
    
    def calculate_features_from_production(
        self,
        production_data: Dict[str, pd.DataFrame],
        mapper: 'ProductionToOULADMapper',
        course_info: Dict[str, any]
    ) -> pd.DataFrame:
        """
        Calculate features from production data by first mapping to OULAD format.
        
        Args:
            production_data: Production format data
            mapper: ProductionToOULADMapper instance
            course_info: Course metadata
            
        Returns:
            DataFrame with calculated features
        """
        logger.info("Calculating features from production data...")
        
        # Map to OULAD format
        oulad_data = mapper.map_production_to_oulad(production_data, course_info)
        
        # Calculate features using standard method
        features_df = self.calculate_features(
            oulad_data,
            course_length=course_info.get('course_length', 269),
            calculation_point=course_info.get('calculation_point')
        )
        
        return features_df