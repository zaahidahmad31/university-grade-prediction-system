from flask import Blueprint, request, jsonify, current_app
from backend.models import Prediction, Student, Enrollment
from backend.extensions import db
from backend.utils.api import api_response, error_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.prediction_service import PredictionService
import logging

logger = logging.getLogger('prediction')

prediction_bp = Blueprint('prediction', __name__)

# Initialize prediction service
prediction_service = PredictionService()

@prediction_bp.route('/student/<string:student_id>', methods=['GET'])
@jwt_required()
def get_student_predictions(student_id):
    """Get predictions for a student"""
    try:
        # Get current user
        current_user = get_jwt_identity()
        
        # Check if student is requesting their own data or if user is faculty/admin
        if current_user['user_type'] == 'student' and current_user['username'] != student_id:
            return error_response('Unauthorized access', 403)
        
        # Get all active enrollments for the student
        enrollments = db.session.query(Enrollment).filter(
            Enrollment.student_id == student_id,
            Enrollment.enrollment_status == 'enrolled'
        ).all()
        
        predictions = []
        for enrollment in enrollments:
            # Get latest prediction for each enrollment
            latest_prediction = prediction_service.get_latest_prediction(enrollment.enrollment_id)
            if latest_prediction:
                # Add course info
                latest_prediction['course_code'] = enrollment.offering.course.course_code
                latest_prediction['course_name'] = enrollment.offering.course.course_name
                predictions.append(latest_prediction)
        
        return api_response({
            'predictions': predictions,
            'count': len(predictions)
        }, 'Predictions retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting student predictions: {str(e)}")
        return error_response(f'Error retrieving predictions: {str(e)}', 500)

@prediction_bp.route('/course/<int:offering_id>', methods=['GET'])
@jwt_required()
def get_course_predictions(offering_id):
    """Get predictions for all students in a course"""
    try:
        # Check if user is faculty or admin
        current_user = get_jwt_identity()
        if current_user['user_type'] not in ['faculty', 'admin']:
            return error_response('Unauthorized access', 403)
        
        # Get all enrollments for the course
        enrollments = db.session.query(Enrollment).filter(
            Enrollment.offering_id == offering_id,
            Enrollment.enrollment_status == 'enrolled'
        ).all()
        
        predictions = []
        for enrollment in enrollments:
            latest_prediction = prediction_service.get_latest_prediction(enrollment.enrollment_id)
            if latest_prediction:
                # Add student info
                student = enrollment.student
                latest_prediction['student_id'] = student.student_id
                latest_prediction['student_name'] = f"{student.first_name} {student.last_name}"
                predictions.append(latest_prediction)
        
        # Sort by risk level (high, medium, low)
        risk_order = {'high': 0, 'medium': 1, 'low': 2}
        predictions.sort(key=lambda x: risk_order.get(x['risk_level'], 3))
        
        return api_response({
            'offering_id': offering_id,
            'predictions': predictions,
            'count': len(predictions),
            'at_risk_count': sum(1 for p in predictions if p['risk_level'] in ['high', 'medium'])
        }, 'Course predictions retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting course predictions: {str(e)}")
        return error_response(f'Error retrieving predictions: {str(e)}', 500)

@prediction_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_predictions():
    """Generate new predictions"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        if not data:
            return error_response('No data provided', 400)
        
        # Check what type of generation is requested
        generation_type = data.get('type', 'individual')
        
        if generation_type == 'individual':
            # Generate for specific student/enrollment
            if current_user['user_type'] == 'student':
                # Students can only generate their own predictions
                student_id = current_user['username']
            else:
                # Faculty/admin can specify student
                student_id = data.get('student_id')
                if not student_id:
                    return error_response('Student ID required', 400)
            
            # Get enrollments
            enrollments = db.session.query(Enrollment).filter(
                Enrollment.student_id == student_id,
                Enrollment.enrollment_status == 'enrolled'
            ).all()
            
            if not enrollments:
                return error_response('No active enrollments found', 404)
            
            results = []
            for enrollment in enrollments:
                try:
                    prediction = prediction_service.generate_prediction(
                        enrollment.enrollment_id,
                        save=True
                    )
                    
                    # Add course info
                    prediction['course_code'] = enrollment.offering.course.course_code
                    prediction['course_name'] = enrollment.offering.course.course_name
                    results.append({
                        'enrollment_id': enrollment.enrollment_id,
                        'status': 'success',
                        'prediction': prediction
                    })
                except Exception as e:
                    logger.error(f"Failed to generate prediction for enrollment {enrollment.enrollment_id}: {str(e)}")
                    results.append({
                        'enrollment_id': enrollment.enrollment_id,
                        'status': 'error',
                        'error': str(e)
                    })
            
            return api_response({
                'student_id': student_id,
                'results': results,
                'success_count': sum(1 for r in results if r['status'] == 'success')
            }, 'Predictions generated successfully')
            
        elif generation_type == 'batch':
            # Batch generation for a course (faculty/admin only)
            if current_user['user_type'] not in ['faculty', 'admin']:
                return error_response('Unauthorized for batch generation', 403)
            
            offering_id = data.get('offering_id')
            if not offering_id:
                return error_response('Offering ID required for batch generation', 400)
            
            # Run batch prediction
            results = prediction_service.batch_generate_predictions(offering_id)
            
            return api_response({
                'offering_id': offering_id,
                'results': results,
                'total_processed': len(results),
                'success_count': sum(1 for r in results if r['status'] == 'success')
            }, 'Batch predictions generated successfully')
            
        else:
            return error_response('Invalid generation type', 400)
            
    except Exception as e:
        logger.error(f"Error generating predictions: {str(e)}")
        return error_response(f'Error generating predictions: {str(e)}', 500)

@prediction_bp.route('/history/<int:enrollment_id>', methods=['GET'])
@jwt_required()
def get_prediction_history(enrollment_id):
    """Get prediction history for an enrollment"""
    try:
        # Check authorization
        current_user = get_jwt_identity()
        enrollment = Enrollment.query.get(enrollment_id)
        
        if not enrollment:
            return error_response('Enrollment not found', 404)
        
        # Check if user has access
        if current_user['user_type'] == 'student' and current_user['username'] != enrollment.student_id:
            return error_response('Unauthorized access', 403)
        
        # Get prediction history
        limit = request.args.get('limit', 10, type=int)
        history = prediction_service.get_prediction_history(enrollment_id, limit)
        
        # Add course info
        course_info = {
            'course_code': enrollment.offering.course.course_code,
            'course_name': enrollment.offering.course.course_name,
            'student_id': enrollment.student_id,
            'student_name': f"{enrollment.student.first_name} {enrollment.student.last_name}"
        }
        
        return api_response({
            'enrollment_id': enrollment_id,
            'course_info': course_info,
            'history': history,
            'count': len(history)
        }, 'Prediction history retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting prediction history: {str(e)}")
        return error_response(f'Error retrieving history: {str(e)}', 500)

@prediction_bp.route('/at-risk', methods=['GET'])
@jwt_required()
def get_at_risk_students():
    """Get all at-risk students (faculty/admin only)"""
    try:
        current_user = get_jwt_identity()
        if current_user['user_type'] not in ['faculty', 'admin']:
            return error_response('Unauthorized access', 403)
        
        # Get parameters
        offering_id = request.args.get('offering_id', type=int)
        risk_levels = request.args.getlist('risk_level') or ['high', 'medium']
        
        # Get at-risk students
        at_risk = prediction_service.get_at_risk_students(offering_id, risk_levels)
        
        return api_response({
            'students': at_risk,
            'count': len(at_risk),
            'filters': {
                'offering_id': offering_id,
                'risk_levels': risk_levels
            }
        }, 'At-risk students retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting at-risk students: {str(e)}")
        return error_response(f'Error retrieving at-risk students: {str(e)}', 500)

@prediction_bp.route('/explain/<int:prediction_id>', methods=['GET'])
@jwt_required()
def explain_prediction(prediction_id):
    """Get explanation for a specific prediction"""
    try:
        # Get prediction
        prediction = Prediction.query.get(prediction_id)
        if not prediction:
            return error_response('Prediction not found', 404)
        
        # Check authorization
        current_user = get_jwt_identity()
        enrollment = Enrollment.query.get(prediction.enrollment_id)
        
        if current_user['user_type'] == 'student' and current_user['username'] != enrollment.student_id:
            return error_response('Unauthorized access', 403)
        
        # Get features from snapshot
        features = prediction.feature_snapshot
        if not features:
            return error_response('Feature data not available for this prediction', 404)
        
        # Get explanation from model service
        from backend.services.model_service import ModelService
        model_service = ModelService()
        
        # Convert features dict to array in correct order
        feature_names = model_service.get_feature_list()
        feature_array = np.array([[features.get(name, 0) for name in feature_names]])
        
        explanation = model_service.explain_prediction(
            feature_array,
            prediction.predicted_grade,
            float(prediction.confidence_score)
        )
        
        return api_response({
            'prediction_id': prediction_id,
            'explanation': explanation,
            'prediction_date': prediction.prediction_date.isoformat()
        }, 'Prediction explanation retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error explaining prediction: {str(e)}")
        return error_response(f'Error getting explanation: {str(e)}', 500)
    
@prediction_bp.route('/debug/<int:enrollment_id>', methods=['GET'])
@jwt_required()
def debug_prediction(enrollment_id):
    """Debug endpoint to check feature calculation and prediction process"""
    try:
        current_user = get_jwt_identity()
        
        # Check authorization
        enrollment = Enrollment.query.get(enrollment_id)
        if not enrollment:
            return error_response('Enrollment not found', 404)
            
        if current_user['user_type'] == 'student' and current_user['username'] != enrollment.student_id:
            return error_response('Unauthorized access', 403)
        
        # Initialize services
        from backend.services.feature_calculator import FeatureCalculator
        from backend.services.model_service import ModelService
        
        feature_calculator = FeatureCalculator()
        model_service = ModelService()
        
        # Step 1: Calculate features
        features = feature_calculator.calculate_features_for_enrollment(enrollment_id)
        feature_names = feature_calculator.get_feature_names()
        
        # Create feature dictionary for debugging
        feature_dict = {}
        feature_array = features.flatten() if hasattr(features, 'flatten') else features
        
        for i, name in enumerate(feature_names):
            if i < len(feature_array):
                feature_dict[name] = float(feature_array[i])
        
        # Step 2: Get raw model prediction
        predicted_class, confidence, risk_level = model_service.predict(features)
        
        # Step 3: Get some sample data stats
        from backend.models import Attendance, LMSActivity, AssessmentSubmission
        
        # Get attendance stats
        attendance_count = Attendance.query.filter_by(enrollment_id=enrollment_id).count()
        present_count = Attendance.query.filter_by(
            enrollment_id=enrollment_id,
            status='present'
        ).count()
        
        # Get LMS activity count
        lms_activity_count = db.session.query(LMSActivity).join(
            LMSSession,
            LMSSession.session_id == LMSActivity.session_id
        ).filter(
            LMSSession.enrollment_id == enrollment_id
        ).count()
        
        # Get assessment submissions
        submission_count = AssessmentSubmission.query.filter_by(
            enrollment_id=enrollment_id
        ).count()
        
        # Create debug response
        debug_info = {
            'enrollment_id': enrollment_id,
            'student_id': enrollment.student_id,
            'course': f"{enrollment.offering.course.course_code} - {enrollment.offering.course.course_name}",
            
            'raw_data_stats': {
                'total_attendance_records': attendance_count,
                'present_count': present_count,
                'attendance_rate': (present_count / attendance_count * 100) if attendance_count > 0 else 0,
                'lms_activities': lms_activity_count,
                'assessment_submissions': submission_count
            },
            
            'calculated_features': feature_dict,
            'feature_statistics': {
                'total_features': len(feature_array),
                'zero_features': sum(1 for f in feature_array if f == 0),
                'non_zero_features': sum(1 for f in feature_array if f != 0),
                'feature_mean': float(np.mean(feature_array)),
                'feature_std': float(np.std(feature_array)),
                'feature_min': float(np.min(feature_array)),
                'feature_max': float(np.max(feature_array))
            },
            
            'model_prediction': {
                'predicted_class': predicted_class,
                'predicted_grade': predicted_grade,
                'confidence': float(confidence),
                'risk_level': risk_level
            },
            
            'model_info': model_service.get_model_info()
        }
        
        return api_response(debug_info, 'Debug information retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Debug error: {str(e)}', 500)