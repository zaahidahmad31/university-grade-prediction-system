#!/usr/bin/env python
"""
Script to verify feature calculations
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.extensions import db
from backend.models.academic import Enrollment
from backend.services.feature_calculator_service import FeatureCalculator
import json
import numpy as np

def verify_features():
    """Verify feature calculations for a sample enrollment"""
    app = create_app()
    
    with app.app_context():
        # Get a sample enrollment
        enrollment = Enrollment.query.first()
        if not enrollment:
            print("No enrollments found!")
            return
        
        print(f"Testing feature calculation for enrollment {enrollment.enrollment_id}")
        print(f"Student: {enrollment.student.first_name} {enrollment.student.last_name}")
        print("-" * 50)
        
        # Initialize feature calculator
        calculator = FeatureCalculator()
        
        # Load expected features
        with open('ml_models/feature_list.json', 'r') as f:
            expected_features = json.load(f)
        
        print(f"Expected {len(expected_features)} features:")
        print(expected_features)
        print("-" * 50)
        
        try:
            # Calculate features
            features = calculator.calculate_features_for_enrollment(enrollment.enrollment_id)
            
            print(f"Successfully calculated {features.shape[1]} features")
            print("\nFeature values:")
            
            # Print each feature with its value
            feature_values = features.flatten()
            for i, (name, value) in enumerate(zip(expected_features, feature_values)):
                print(f"{i+1:3d}. {name:30s}: {value:10.2f}")
            
            # Check for any NaN or infinite values
            if np.any(np.isnan(feature_values)):
                print("\nWARNING: Found NaN values in features!")
                nan_indices = np.where(np.isnan(feature_values))[0]
                for idx in nan_indices:
                    print(f"  - {expected_features[idx]} is NaN")
            
            if np.any(np.isinf(feature_values)):
                print("\nWARNING: Found infinite values in features!")
                inf_indices = np.where(np.isinf(feature_values))[0]
                for idx in inf_indices:
                    print(f"  - {expected_features[idx]} is infinite")
            
            # Test conversion to dict (for staging)
            feature_dict = {
                name: float(value) 
                for name, value in zip(expected_features, feature_values)
            }
            
            print(f"\nSuccessfully converted to dictionary with {len(feature_dict)} entries")
            
            # Test JSON serialization
            json_str = json.dumps(feature_dict)
            print(f"Successfully serialized to JSON ({len(json_str)} characters)")
            
        except Exception as e:
            print(f"ERROR calculating features: {str(e)}")
            import traceback
            traceback.print_exc()

def check_data_availability():
    """Check what data is available for feature calculation"""
    app = create_app()
    
    with app.app_context():
        enrollment = Enrollment.query.first()
        if not enrollment:
            print("No enrollments found!")
            return
        
        print(f"\nData availability for enrollment {enrollment.enrollment_id}:")
        print("-" * 50)
        
        # Check attendance
        from backend.models.tracking import Attendance
        attendance_count = Attendance.query.filter_by(
            enrollment_id=enrollment.enrollment_id
        ).count()
        print(f"Attendance records: {attendance_count}")
        
        # Check LMS sessions
        from backend.models.tracking import LMSSession
        session_count = LMSSession.query.filter_by(
            enrollment_id=enrollment.enrollment_id
        ).count()
        print(f"LMS sessions: {session_count}")
        
        # Check LMS activities
        from backend.models.tracking import LMSActivity
        activity_count = LMSActivity.query.join(LMSSession).filter(
            LMSSession.enrollment_id == enrollment.enrollment_id
        ).count()
        print(f"LMS activities: {activity_count}")
        
        # Check assessments
        from backend.models.assessment import AssessmentSubmission
        submission_count = AssessmentSubmission.query.filter_by(
            enrollment_id=enrollment.enrollment_id
        ).count()
        print(f"Assessment submissions: {submission_count}")
        
        # Check student demographics
        student = enrollment.student
        print(f"\nStudent demographics:")
        print(f"  Age band: {student.age_band}")
        print(f"  Education: {student.highest_education}")
        print(f"  Previous attempts: {student.num_of_prev_attempts}")
        print(f"  Studied credits: {student.studied_credits}")
        print(f"  Has disability: {student.has_disability}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Verify feature calculations')
    parser.add_argument('--check-data', action='store_true', 
                       help='Check data availability')
    
    args = parser.parse_args()
    
    if args.check_data:
        check_data_availability()
    
    verify_features()