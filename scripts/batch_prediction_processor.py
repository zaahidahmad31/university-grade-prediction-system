#!/usr/bin/env python
"""
Batch prediction processor using ML Feature Staging table
"""
import sys
import os
from datetime import datetime, date, timedelta

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.extensions import db
from backend.models.prediction import MLFeatureStaging, Prediction
from backend.models.academic import Enrollment
from backend.services.feature_calculator_service import FeatureCalculator
from backend.services.prediction_service import PredictionService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def stage_features_for_all_enrollments():
    """Calculate and stage features for all active enrollments"""
    app = create_app()
    
    with app.app_context():
        feature_calculator = FeatureCalculator()
        
        # Get all active enrollments
        enrollments = Enrollment.query.filter_by(
            enrollment_status='enrolled'
        ).all()
        
        logger.info(f"Staging features for {len(enrollments)} enrollments")
        
        for enrollment in enrollments:
            try:
                # Calculate features
                features = feature_calculator.calculate_features_for_enrollment(
                    enrollment.enrollment_id
                )
                
                # Convert numpy array to list for JSON storage
                feature_dict = {
                    name: float(value) 
                    for name, value in zip(
                        feature_calculator.get_feature_names(), 
                        features.flatten()
                    )
                }
                
                # Create staging record
                staging = MLFeatureStaging(
                    enrollment_id=enrollment.enrollment_id,
                    calculation_date=date.today(),
                    feature_data=feature_dict
                )
                
                db.session.add(staging)
                
            except Exception as e:
                logger.error(f"Error staging features for enrollment {enrollment.enrollment_id}: {str(e)}")
        
        db.session.commit()
        logger.info("Feature staging complete")

def process_staged_predictions(batch_size=10):
    """Process staged features and generate predictions"""
    app = create_app()
    
    with app.app_context():
        prediction_service = PredictionService()
        
        # Get unprocessed staged features
        staged_features = MLFeatureStaging.query.filter_by(
            is_processed=False
        ).limit(batch_size).all()
        
        logger.info(f"Processing {len(staged_features)} staged predictions")
        
        for staged in staged_features:
            try:
                # Generate prediction using staged features
                prediction_result = prediction_service.generate_prediction(
                    staged.enrollment_id,
                    save=True
                )
                
                # Mark as processed
                staged.mark_processed()
                
                logger.info(f"Processed prediction for enrollment {staged.enrollment_id}: "
                          f"{prediction_result['predicted_grade']} "
                          f"(confidence: {prediction_result['confidence_score']:.2f})")
                
            except Exception as e:
                logger.error(f"Error processing staged prediction {staged.staging_id}: {str(e)}")
        
        logger.info("Batch processing complete")

def cleanup_old_staging_records(days_to_keep=30):
    """Clean up old processed staging records"""
    app = create_app()
    
    with app.app_context():
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        old_records = MLFeatureStaging.query.filter(
            MLFeatureStaging.is_processed == True,
            MLFeatureStaging.created_at < cutoff_date
        ).all()
        
        count = len(old_records)
        
        for record in old_records:
            db.session.delete(record)
        
        db.session.commit()
        logger.info(f"Deleted {count} old staging records")

if __name__ == '__main__':
    import argparse
    from datetime import timedelta
    
    parser = argparse.ArgumentParser(description='Batch Prediction Processor')
    parser.add_argument('--stage', action='store_true', 
                       help='Stage features for all enrollments')
    parser.add_argument('--process', action='store_true', 
                       help='Process staged predictions')
    parser.add_argument('--batch-size', type=int, default=10,
                       help='Batch size for processing')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up old staging records')
    parser.add_argument('--all', action='store_true',
                       help='Run complete pipeline')
    
    args = parser.parse_args()
    
    if args.all:
        logger.info("Running complete batch prediction pipeline")
        stage_features_for_all_enrollments()
        process_staged_predictions(args.batch_size)
        cleanup_old_staging_records()
    else:
        if args.stage:
            stage_features_for_all_enrollments()
        
        if args.process:
            process_staged_predictions(args.batch_size)
        
        if args.cleanup:
            cleanup_old_staging_records()
        
        if not any([args.stage, args.process, args.cleanup]):
            parser.print_help()