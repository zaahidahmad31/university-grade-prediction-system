import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func
from backend.extensions import db
from backend.models import (
    Enrollment, Attendance, LMSSession, LMSActivity, 
    AssessmentSubmission, Assessment, LMSDailySummary, Student
)
from backend.utils.helpers import safe_float, safe_int
import logging

logger = logging.getLogger(__name__)

class FeatureCalculator:
    """Calculate features matching OULAD format for ML model prediction"""
    
    def __init__(self):
        # Load feature list from model metadata
        with open('ml_models/feature_list.json', 'r') as f:
            self.feature_list = json.load(f)
        
        logger.info(f"Feature calculator initialized with {len(self.feature_list)} features")
    
    def calculate_features_for_enrollment(self, enrollment_id: int, 
                                        as_of_date: Optional[datetime] = None) -> Dict:
        """
        Calculate all features for a single enrollment in OULAD format
        """
        if as_of_date is None:
            as_of_date = datetime.now()
        
        # Get enrollment details
        enrollment = Enrollment.query.get(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment {enrollment_id} not found")
        
        # Convert production data to OULAD-style VLE data
        vle_data = self._convert_to_vle_format(enrollment_id, as_of_date)
        
        # Initialize features dictionary
        features = {}
        
        # Calculate activity features
        features.update(self._calculate_activity_features(vle_data))
        
        # Calculate assessment features
        features.update(self._calculate_assessment_features(enrollment_id, as_of_date))
        
        # Calculate demographic features
        features.update(self._calculate_demographic_features(enrollment))
        
        # Ensure all required features are present
        return self._validate_and_order_features(features)
    
    def _convert_to_vle_format(self, enrollment_id: int, as_of_date: datetime) -> List[Dict]:
        """Convert production data to OULAD VLE format"""
        vle_records = []
        
        # Convert attendance to VLE format
        attendance_records = Attendance.query.filter(
            Attendance.enrollment_id == enrollment_id,
            Attendance.attendance_date <= as_of_date
        ).all()
        
        for attendance in attendance_records:
            if attendance.status == 'present':
                vle_records.append({
                    'date': (attendance.attendance_date - self._get_course_start_date(enrollment_id)).days,
                    'id_site': f'attendance_{attendance.attendance_id}',
                    'sum_click': 30
                })
            elif attendance.status == 'late':
                vle_records.append({
                    'date': (attendance.attendance_date - self._get_course_start_date(enrollment_id)).days,
                    'id_site': f'attendance_{attendance.attendance_id}',
                    'sum_click': 15
                })
        
        # Convert LMS activities to VLE format
        click_mapping = {
            'resource_view': 1,
            'forum_post': 5,
            'forum_reply': 3,
            'assignment_view': 2,
            'quiz_attempt': 10,
            'video_watch': 1,
            'file_download': 2,
            'page_view': 1
        }
        
        activities = LMSActivity.query.join(LMSSession).filter(
            LMSSession.enrollment_id == enrollment_id,
            LMSActivity.activity_timestamp <= as_of_date
        ).all()
        
        for activity in activities:
            vle_records.append({
                'date': (activity.activity_timestamp.date() - self._get_course_start_date(enrollment_id)).days,
                'id_site': activity.resource_id or f'activity_{activity.activity_id}',
                'sum_click': click_mapping.get(activity.activity_type, 1)
            })
        
        return vle_records
    
    def _get_course_start_date(self, enrollment_id: int):
        """Get course start date for relative date calculations"""
        enrollment = Enrollment.query.get(enrollment_id)
        if enrollment and enrollment.offering and enrollment.offering.term:
            return enrollment.offering.term.start_date
        # Default to enrollment date if no term start date
        return enrollment.enrollment_date if enrollment else datetime.now().date()
    
    def _calculate_activity_features(self, vle_data: List[Dict]) -> Dict:
        """Calculate activity-based features from VLE data"""
        features = {}
        
        if not vle_data:
            # Return zero values for all activity features
            return {
                'days_active': 0,
                'total_clicks': 0,
                'unique_materials': 0,
                'activity_rate': 0,
                'avg_clicks_per_active_day': 0,
                'first_activity_day': -1,
                'last_activity_day': -1,
                'weekly_activity_std': 0,
                'activity_regularity': 0,
                'longest_inactivity_gap': 0,
                'weekend_activity_ratio': 0,
                'activity_trend': 0
            }
        
        # Basic activity metrics
        unique_days = set(record['date'] for record in vle_data)
        features['days_active'] = len(unique_days)
        features['total_clicks'] = sum(record['sum_click'] for record in vle_data)
        features['unique_materials'] = len(set(record['id_site'] for record in vle_data))
        
        # Activity rate (percentage of course days active)
        course_days = max(unique_days) - min(unique_days) + 1 if unique_days else 1
        features['activity_rate'] = (features['days_active'] / max(course_days, 1)) * 100
        
        # Average clicks per active day
        features['avg_clicks_per_active_day'] = (
            features['total_clicks'] / features['days_active'] 
            if features['days_active'] > 0 else 0
        )
        
        # First and last activity days
        features['first_activity_day'] = min(unique_days) if unique_days else -1
        features['last_activity_day'] = max(unique_days) if unique_days else -1
        
        # Weekly activity standard deviation
        weekly_clicks = {}
        for record in vle_data:
            week = record['date'] // 7
            weekly_clicks[week] = weekly_clicks.get(week, 0) + record['sum_click']
        
        if len(weekly_clicks) > 1:
            features['weekly_activity_std'] = np.std(list(weekly_clicks.values()))
        else:
            features['weekly_activity_std'] = 0
        
        # Activity regularity (inverse of gaps between active days)
        sorted_days = sorted(unique_days)
        if len(sorted_days) > 1:
            gaps = [sorted_days[i+1] - sorted_days[i] for i in range(len(sorted_days)-1)]
            features['activity_regularity'] = 1 / (np.mean(gaps) + 1) * 100
            features['longest_inactivity_gap'] = max(gaps)
        else:
            features['activity_regularity'] = 0
            features['longest_inactivity_gap'] = 0
        
        # Weekend activity ratio
        weekend_days = sum(1 for day in unique_days if (day % 7) in [5, 6])
        features['weekend_activity_ratio'] = (
            (weekend_days / features['days_active'] * 100) 
            if features['days_active'] > 0 else 0
        )
        
        # Activity trend (slope of activity over time)
        if len(unique_days) > 1:
            x = np.array(sorted(unique_days))
            y = np.array([sum(r['sum_click'] for r in vle_data if r['date'] == d) for d in x])
            coefficients = np.polyfit(x, y, 1)
            features['activity_trend'] = coefficients[0]
        else:
            features['activity_trend'] = 0
        
        return features
    
    def _calculate_assessment_features(self, enrollment_id: int, as_of_date: datetime) -> Dict:
        """Calculate assessment-related features"""
        features = {}
        
        # Get all assessments and submissions
        enrollment = Enrollment.query.get(enrollment_id)
        assessments = Assessment.query.filter(
            Assessment.offering_id == enrollment.offering_id,
            Assessment.due_date <= as_of_date
        ).all()
        
        submissions = AssessmentSubmission.query.filter(
            AssessmentSubmission.enrollment_id == enrollment_id,
            AssessmentSubmission.submission_date <= as_of_date
        ).all()
        
        # Basic submission metrics
        features['submitted_assessments'] = len(submissions)
        features['submission_rate'] = (
            (len(submissions) / len(assessments) * 100) 
            if assessments else 100
        )
        
        # Score metrics
        scores = [safe_float(s.score) for s in submissions if s.score is not None]
        features['avg_score'] = np.mean(scores) if scores else 0
        
        # Scores by assessment type - MAPPING YOUR TYPES TO MODEL EXPECTATIONS
        cma_scores = []  # Continuous assessments (Quiz, Assignment, Participation)
        tma_scores = []  # Tutor marked assessments (Midterm Exam, CMA, TMA)
        exam_scores = [] # Final exams (Final Exam, Exam)
        
        # Type mapping based on your assessment_types table
        TYPE_MAPPING = {
           # Map to CMA (Continuous Assessment)
        'Quiz': 'CMA',
        'Assignment': 'CMA',
        'Participation': 'CMA',
        
        # Map to TMA (Tutor Marked Assessment)
        'Midterm Exam': 'TMA',
        'CMA': 'TMA',  # Your CMA maps to model's TMA
        'TMA': 'TMA',
        
        # Map to Exam
        'Final Exam': 'Exam',
        'Exam': 'Exam'
        }
        
        for submission in submissions:
            if submission.assessment and submission.score is not None:
                score = safe_float(submission.score)
                
                # Get the assessment type name from the relationship
                assessment = submission.assessment
                if assessment and assessment.assessment_type:
                    type_name = assessment.assessment_type.type_name
                    
                    # Map to model expected types
                    model_type = TYPE_MAPPING.get(type_name, None)
                    
                    if model_type == 'CMA':
                        cma_scores.append(score)
                    elif model_type == 'TMA':
                        tma_scores.append(score)
                    elif model_type == 'Exam':
                        exam_scores.append(score)
                        
                    # Debug logging
                    logger.debug(f"Assessment: {assessment.title}, Type: {type_name} -> {model_type}, Score: {score}")
        
        features['avg_score_cma'] = np.mean(cma_scores) if cma_scores else 0
        features['avg_score_tma'] = np.mean(tma_scores) if tma_scores else 0
        features['avg_score_exam'] = np.mean(exam_scores) if exam_scores else 0
        
        # Log the calculated averages for debugging
        logger.info(f"Enrollment {enrollment_id} - CMA: {features['avg_score_cma']:.2f} ({len(cma_scores)} scores), "
                    f"TMA: {features['avg_score_tma']:.2f} ({len(tma_scores)} scores), "
                    f"Exam: {features['avg_score_exam']:.2f} ({len(exam_scores)} scores)")
        
        # Submission timing features
        on_time = 0
        late = 0
        days_early_list = []
        
        for submission in submissions:
            if submission.is_late:
                late += 1
            else:
                on_time += 1
                
            # Calculate days early (negative if late)
            if submission.assessment and submission.assessment.due_date:
                days_diff = (submission.assessment.due_date - submission.submission_date).days
                days_early_list.append(days_diff)
        
        features['on_time_submissions'] = on_time
        features['late_submission_count'] = late
        features['avg_days_early'] = np.mean(days_early_list) if days_early_list else 0
        
        return features
    
    def _calculate_demographic_features(self, enrollment: Enrollment) -> Dict:
        """Calculate demographic features based on student info"""
        features = {}
        
        # Get student information
        student = enrollment.student
        
        # Age band encoding (matching OULAD)
        age_mapping = {
            '0-35': 0,
            '35-55': 1,
            '55+': 2
        }
        features['age_band_encoded'] = age_mapping.get(student.age_band, 0)
        
        # Education level encoding
        education_mapping = {
            'No Formal quals': 0,
            'Lower Than A Level': 1,
            'A Level or Equivalent': 2,
            'HE Qualification': 3,
            'Post Graduate Qualification': 4
        }
        features['highest_education_encoded'] = education_mapping.get(
            student.highest_education, 2
        )
        
        # Other demographic features
        features['num_of_prev_attempts'] = safe_int(student.num_of_prev_attempts)
        features['studied_credits'] = safe_int(student.studied_credits)
        features['has_disability'] = 1 if student.has_disability else 0
        
        return features
    
    def _validate_and_order_features(self, features: Dict) -> np.ndarray:
        """Ensure all features are present and in correct order"""
        # Check for missing features
        missing_features = set(self.feature_list) - set(features.keys())
        if missing_features:
            logger.warning(f"Missing features: {missing_features}")
            # Fill missing features with 0
            for feature in missing_features:
                features[feature] = 0
        
        # Order features according to feature_list
        ordered_features = []
        for name in self.feature_list:
            value = features.get(name, 0)
            # Ensure numeric type
            if isinstance(value, (int, float, np.number)):
                ordered_features.append(float(value))
            else:
                ordered_features.append(0.0)
        
        return np.array(ordered_features).reshape(1, -1)
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names in order"""
        return self.feature_list
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance from model metadata"""
        try:
            with open('ml_models/feature_importance.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Feature importance file not found")
            return {}
        
        
    def debug_feature_calculation(self, enrollment_id: int):
        """Debug method to trace feature calculation"""
        logger.info(f"\n{'='*60}")
        logger.info(f"DEBUG: Feature Calculation for Enrollment {enrollment_id}")
        logger.info(f"{'='*60}")
        
        try:
            # Get enrollment details
            enrollment = Enrollment.query.get(enrollment_id)
            if not enrollment:
                logger.error(f"Enrollment {enrollment_id} not found")
                return
            
            logger.info(f"Student: {enrollment.student_id}")
            logger.info(f"Course: {enrollment.offering.course.course_code}")
            
            # Check data availability
            as_of_date = datetime.now()
            
            # Check attendance data
            attendance_count = Attendance.query.filter_by(enrollment_id=enrollment_id).count()
            logger.info(f"\nAttendance Records: {attendance_count}")
            
            # Check LMS data
            lms_sessions = LMSSession.query.filter_by(enrollment_id=enrollment_id).count()
            logger.info(f"LMS Sessions: {lms_sessions}")
            
            # Check assessments
            submissions = AssessmentSubmission.query.filter_by(enrollment_id=enrollment_id).count()
            logger.info(f"Assessment Submissions: {submissions}")
            
            # Calculate features and log each step
            logger.info("\nCalculating features...")
            
            # Convert to VLE format
            vle_data = self._convert_to_vle_format(enrollment_id, as_of_date)
            logger.info(f"VLE records created: {len(vle_data)}")
            
            if vle_data:
                logger.info(f"Sample VLE record: {vle_data[0]}")
            
            # Calculate activity features
            activity_features = self._calculate_activity_features(vle_data)
            logger.info(f"\nActivity Features:")
            for key, value in activity_features.items():
                logger.info(f"  {key}: {value}")
            
            # Calculate assessment features
            assessment_features = self._calculate_assessment_features(enrollment_id, as_of_date)
            logger.info(f"\nAssessment Features:")
            for key, value in assessment_features.items():
                logger.info(f"  {key}: {value}")
            
            # Calculate demographic features
            demographic_features = self._calculate_demographic_features(enrollment)
            logger.info(f"\nDemographic Features:")
            for key, value in demographic_features.items():
                logger.info(f"  {key}: {value}")
            
            # Combine all features
            all_features = {}
            all_features.update(activity_features)
            all_features.update(assessment_features)
            all_features.update(demographic_features)
            
            # Order features
            ordered_features = self._validate_and_order_features(all_features)
            
            logger.info(f"\nFinal Feature Vector Shape: {ordered_features.shape}")
            logger.info(f"Non-zero features: {np.count_nonzero(ordered_features)}")
            logger.info(f"Feature Statistics:")
            logger.info(f"  Mean: {np.mean(ordered_features):.4f}")
            logger.info(f"  Std: {np.std(ordered_features):.4f}")
            logger.info(f"  Min: {np.min(ordered_features):.4f}")
            logger.info(f"  Max: {np.max(ordered_features):.4f}")
            
            logger.info(f"{'='*60}\n")
            
        except Exception as e:
            logger.error(f"Error in debug feature calculation: {str(e)}")
            import traceback
            traceback.print_exc()