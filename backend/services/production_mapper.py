# src/data/production_mapper.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
from ..utils.logger import setup_logger
from ..utils.config import Config

logger = setup_logger(__name__)

class ProductionToOULADMapper:
    """
    Maps production database format to OULAD format.
    This is the key component for avoiding conflicts between training and production.
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.mapping_rules = self.config.get("feature_mapping", "transformation_rules")
   
    def map_attendance_to_vle(
       self,
       attendance_records: pd.DataFrame,
       course_start_date: datetime
   ) -> pd.DataFrame:
       """
       Convert attendance records to VLE-style activity data.
       
       Args:
           attendance_records: DataFrame with columns [attendance_date, status, enrollment_id]
           course_start_date: Course start date for calculating days_from_start
           
       Returns:
           DataFrame in VLE format [id_student, id_site, date, sum_click]
       """
       logger.info("Mapping attendance records to VLE format...")
       
       # Check if DataFrame is empty or missing required columns
       if attendance_records.empty:
           logger.info("No attendance records to map")
           return pd.DataFrame(columns=['id_student', 'id_site', 'date', 'sum_click', 'code_module', 'code_presentation'])
       
       required_columns = ['attendance_date', 'status', 'student_id']
       missing_columns = [col for col in required_columns if col not in attendance_records.columns]
       
       if missing_columns:
           logger.warning(f"Missing required columns: {missing_columns}")
           return pd.DataFrame(columns=['id_student', 'id_site', 'date', 'sum_click', 'code_module', 'code_presentation'])
       
       # Add attendance_id if missing
       if 'attendance_id' not in attendance_records.columns:
           attendance_records = attendance_records.copy()
           attendance_records['attendance_id'] = range(len(attendance_records))
       
       vle_records = []
       
       for _, record in attendance_records.iterrows():
           # Calculate days from course start
           attendance_date = pd.to_datetime(record['attendance_date'])
           days_from_start = (attendance_date - course_start_date).days
           
           # Apply mapping rules based on attendance status
           if record['status'] == 'present':
               clicks = 30  # Full engagement
           elif record['status'] == 'late':
               clicks = 15  # Partial engagement
           else:
               continue  # Skip absent/excused
           
           vle_records.append({
               'id_student': record['student_id'],
               'id_site': f"attendance_{record['attendance_id']}",
               'date': days_from_start,
               'sum_click': clicks,
               'code_module': record.get('code_module', 'NA'),
               'code_presentation': record.get('code_presentation', 'NA')
           })
       
       vle_df = pd.DataFrame(vle_records)
       logger.info(f"Mapped {len(attendance_records)} attendance records to {len(vle_df)} VLE records")
       
       return vle_df
   
    def map_lms_activities_to_vle(
       self,
       lms_activities: pd.DataFrame,
       course_start_date: datetime
   ) -> pd.DataFrame:
       """
       Convert LMS activities to VLE-style click data.
       
       Args:
           lms_activities: DataFrame with LMS activity records
           course_start_date: Course start date
           
       Returns:
           DataFrame in VLE format
       """
       logger.info("Mapping LMS activities to VLE format...")
       
       # Check if empty
       if lms_activities.empty:
           logger.info("No LMS activities to map")
           return pd.DataFrame(columns=['id_student', 'id_site', 'date', 'sum_click', 'code_module', 'code_presentation'])
       
       # Get click mapping for different activity types
       activity_click_map = {
           'resource_view': 1,
           'forum_post': 5,
           'forum_reply': 3,
           'assignment_view': 2,
           'quiz_attempt': 10,
           'video_watch': 1,
           'file_download': 2,
           'page_view': 1
       }
       
       vle_records = []
       
       # Group by student, resource, and date
       grouped = lms_activities.groupby([
           'student_id',
           'resource_id',
           pd.to_datetime(lms_activities['activity_timestamp']).dt.date
       ])
       
       for (student_id, resource_id, activity_date), group in grouped:
           # Calculate days from start
           days_from_start = (activity_date - course_start_date.date()).days
           
           # Sum clicks for all activities on this resource on this day
           total_clicks = 0
           for _, activity in group.iterrows():
               activity_type = activity.get('activity_type', 'page_view')
               clicks = activity_click_map.get(activity_type, 1)
               total_clicks += clicks
           
           vle_records.append({
               'id_student': student_id,
               'id_site': resource_id,
               'date': days_from_start,
               'sum_click': total_clicks,
               'code_module': group.iloc[0].get('code_module', 'NA'),
               'code_presentation': group.iloc[0].get('code_presentation', 'NA')
           })
       
       vle_df = pd.DataFrame(vle_records)
       logger.info(f"Mapped {len(lms_activities)} LMS activities to {len(vle_df)} VLE records")
       
       return vle_df
   
    def map_assessments_to_oulad(
       self,
       assessment_submissions: pd.DataFrame,
       assessments_metadata: pd.DataFrame,
       course_start_date: datetime
   ) -> Tuple[pd.DataFrame, pd.DataFrame]:
       """
       Map production assessment data to OULAD format.
       
       Returns:
           Tuple of (student_assessment_df, assessments_df)
       """
       logger.info("Mapping assessments to OULAD format...")
       
       # Map assessment types
       assessment_type_map = {
           'quiz': 'CMA',
           'assignment': 'TMA',
           'midterm_exam': 'Exam',
           'final_exam': 'Exam',
           'homework': 'TMA',
           'project': 'TMA'
       }
       
       # Create OULAD assessments metadata
       oulad_assessments = []
       for _, assess in assessments_metadata.iterrows():
           assess_type = assessment_type_map.get(
               assess.get('type_name', '').lower(),
               'TMA'
           )
           
           # Calculate days from start for due date
           due_date = pd.to_datetime(assess['due_date'])
           days_from_start = (due_date - course_start_date).days
           
           oulad_assessments.append({
               'id_assessment': assess['assessment_id'],
               'code_module': assess.get('code_module', 'NA'),
               'code_presentation': assess.get('code_presentation', 'NA'),
               'assessment_type': assess_type,
               'date': days_from_start,
               'weight': assess.get('weight', 0)
           })
       
       # Create OULAD student assessment submissions
       oulad_submissions = []
       for _, submission in assessment_submissions.iterrows():
           # Calculate submission date from start
           submit_date = pd.to_datetime(submission['submission_date'])
           days_from_start = (submit_date - course_start_date).days
           
           # Normalize score to 0-100 if needed
           score = submission['score']
           if 'max_score' in submission and submission['max_score'] > 0:
               score = (score / submission['max_score']) * 100
           
           oulad_submissions.append({
               'id_assessment': submission['assessment_id'],
               'id_student': submission['student_id'],
               'date_submitted': days_from_start,
               'is_banked': 0,  # Default to not banked
               'score': score
           })
       
       assessments_df = pd.DataFrame(oulad_assessments)
       submissions_df = pd.DataFrame(oulad_submissions)
       
       logger.info(f"Mapped {len(assessments_metadata)} assessments and {len(assessment_submissions)} submissions")
       
       return submissions_df, assessments_df
   
    def map_student_info_to_oulad(
       self,
       student_info: pd.DataFrame,
       enrollments: pd.DataFrame
   ) -> pd.DataFrame:
       """
       Map production student info to OULAD format.
       """
       logger.info("Mapping student info to OULAD format...")
       
       oulad_students = []
       
       for _, student in student_info.iterrows():
           # Get enrollment info
           student_enrollments = enrollments[
               enrollments['student_id'] == student['student_id']
           ]
           
           for _, enrollment in student_enrollments.iterrows():
               # Map education levels
               education_map = {
                   'high_school': 'A Level or Equivalent',
                   'bachelors': 'HE Qualification',
                   'masters': 'Post Graduate Qualification',
                   'phd': 'Post Graduate Qualification',
                   'none': 'No Formal quals'
               }
               
               # Map age to age bands
               if 'age' in student:
                   age = student['age']
                   if age < 35:
                       age_band = '0-35'
                   elif age < 55:
                       age_band = '35-55'
                   else:
                       age_band = '55+'
               else:
                   age_band = student.get('age_band', '0-35')
               
               oulad_students.append({
                   'code_module': enrollment.get('code_module', 'NA'),
                   'code_presentation': enrollment.get('code_presentation', 'NA'),
                   'id_student': student['student_id'],
                   'gender': student.get('gender', 'M'),
                   'region': student.get('region', 'East Anglian Region'),
                   'highest_education': education_map.get(
                       student.get('highest_education', '').lower(),
                       'A Level or Equivalent'
                   ),
                   'imd_band': student.get('imd_band', '50-60%'),
                   'age_band': age_band,
                   'num_of_prev_attempts': enrollment.get('num_of_prev_attempts', 0),
                   'studied_credits': student.get('studied_credits', 60),
                   'disability': student.get('disability', 'N'),
                   'final_result': enrollment.get('final_result', 'Pass')
               })
       
       student_df = pd.DataFrame(oulad_students)
       logger.info(f"Mapped {len(student_info)} students to OULAD format")
       
       return student_df
   
    def combine_vle_sources(
       self,
       attendance_vle: pd.DataFrame,
       lms_vle: pd.DataFrame
   ) -> pd.DataFrame:
       """
       Combine VLE data from multiple sources.
       """
       logger.info("Combining VLE data from multiple sources...")
       
       # Handle empty DataFrames
       if attendance_vle.empty and lms_vle.empty:
           logger.warning("Both VLE sources are empty")
           return pd.DataFrame(columns=['id_student', 'id_site', 'date', 'sum_click', 'code_module', 'code_presentation'])
       
       # Concatenate dataframes
       combined = pd.concat([attendance_vle, lms_vle], ignore_index=True)
       
       # Group by student, site, and date to combine clicks
       grouped = combined.groupby([
           'id_student',
           'id_site',
           'date',
           'code_module',
           'code_presentation'
       ])['sum_click'].sum().reset_index()
       
       logger.info(f"Combined VLE data: {len(combined)} -> {len(grouped)} records")
       
       return grouped
   
    def validate_mapping(
       self,
       original_data: Dict[str, pd.DataFrame],
       mapped_data: Dict[str, pd.DataFrame]
   ) -> Dict[str, bool]:
       """
       Validate that mapping preserves essential information.
       """
       validation_results = {}
       
       # Check student coverage
       original_students = set(original_data.get('students', pd.DataFrame())['student_id']) if 'students' in original_data and not original_data['students'].empty else set()
       mapped_students = set(mapped_data.get('student_info', pd.DataFrame())['id_student']) if 'student_info' in mapped_data and not mapped_data['student_info'].empty else set()
       
       validation_results['student_coverage'] = len(
           original_students - mapped_students
       ) == 0
       
       # Check activity preservation
       if 'attendance' in original_data and 'student_vle' in mapped_data and not original_data['attendance'].empty and not mapped_data['student_vle'].empty:
           original_active_days = original_data['attendance'].groupby(
               'student_id'
           )['attendance_date'].nunique()
           
           mapped_active_days = mapped_data['student_vle'].groupby(
               'id_student'
           )['date'].nunique()
           
           # Allow some tolerance (within 10%)
           if len(original_active_days) > 0:
               coverage_ratio = len(mapped_active_days) / len(original_active_days)
               validation_results['activity_coverage'] = coverage_ratio > 0.9
           else:
               validation_results['activity_coverage'] = True
       else:
           validation_results['activity_coverage'] = True
       
       # Check assessment coverage
       if 'assessment_submissions' in original_data and 'student_assessment' in mapped_data:
           original_assessments = len(original_data['assessment_submissions'])
           mapped_assessments = len(mapped_data['student_assessment'])
           
           validation_results['assessment_coverage'] = (
               mapped_assessments >= original_assessments * 0.95
           ) if original_assessments > 0 else True
       else:
           validation_results['assessment_coverage'] = True
       
       return validation_results
   
    def map_production_to_oulad(
       self,
       production_data: Dict[str, pd.DataFrame],
       course_info: Dict[str, any]
   ) -> Dict[str, pd.DataFrame]:
       """
       Complete mapping from production format to OULAD format.
       
       Args:
           production_data: Dictionary with production tables
           course_info: Course metadata including start_date
           
       Returns:
           Dictionary with OULAD-formatted dataframes
       """
       logger.info("Starting production to OULAD mapping...")
       
       oulad_data = {}
       
       # Get course start date
       course_start = pd.to_datetime(course_info['start_date'])
       
       # Map attendance to VLE
       if 'attendance' in production_data:
           attendance_vle = self.map_attendance_to_vle(
               production_data['attendance'],
               course_start
           )
       else:
           attendance_vle = pd.DataFrame(columns=['id_student', 'id_site', 'date', 'sum_click', 'code_module', 'code_presentation'])
       
       # Map LMS activities to VLE
       if 'lms_activities' in production_data:
           lms_vle = self.map_lms_activities_to_vle(
               production_data['lms_activities'],
               course_start
           )
       else:
           lms_vle = pd.DataFrame(columns=['id_student', 'id_site', 'date', 'sum_click', 'code_module', 'code_presentation'])
       
       # Combine VLE sources
       oulad_data['student_vle'] = self.combine_vle_sources(
           attendance_vle,
           lms_vle
       )
       
       # Map assessments
       if 'assessment_submissions' in production_data and 'assessments' in production_data:
           student_assess, assess_meta = self.map_assessments_to_oulad(
               production_data['assessment_submissions'],
               production_data['assessments'],
               course_start
           )
           oulad_data['student_assessment'] = student_assess
           oulad_data['assessments'] = assess_meta
       else:
           oulad_data['student_assessment'] = pd.DataFrame()
           oulad_data['assessments'] = pd.DataFrame()
       
       # Map student info
       if 'students' in production_data and 'enrollments' in production_data:
           oulad_data['student_info'] = self.map_student_info_to_oulad(
               production_data['students'],
               production_data['enrollments']
           )
       else:
           oulad_data['student_info'] = pd.DataFrame()
       
       # Validate mapping
       validation = self.validate_mapping(production_data, oulad_data)
       logger.info(f"Mapping validation results: {validation}")
       
       logger.info("Production to OULAD mapping complete")
       
       return oulad_data