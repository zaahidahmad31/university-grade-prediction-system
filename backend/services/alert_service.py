from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import and_, or_
from backend.extensions import db
from backend.models import (
    Alert, AlertType, Enrollment, Student, Faculty,
    Attendance, LMSDailySummary, Prediction, Assessment,
    AssessmentSubmission, CourseOffering
)
from backend.services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)

class AlertService:
    """Service for managing student alerts and notifications"""
    
    def __init__(self):
        self.email_service = EmailService()
        
        # Initialize thresholds with defaults
        self._thresholds_loaded = False
        self.ATTENDANCE_THRESHOLD = 70
        self.LOW_ENGAGEMENT_THRESHOLD = 30
        self.FAILING_GRADE_THRESHOLD = 50
        self.MISSING_ASSIGNMENTS_THRESHOLD = 2
    
    def _load_thresholds(self):
        """Load thresholds from database config - called when needed"""
        if self._thresholds_loaded:
            return
            
        try:
            from backend.models.system import SystemConfig
            
            # Alert thresholds - load from config or use defaults
            attendance_config = SystemConfig.query.filter_by(config_key='alert_attendance_threshold').first()
            if attendance_config:
                self.ATTENDANCE_THRESHOLD = int(attendance_config.config_value)
            
            engagement_config = SystemConfig.query.filter_by(config_key='alert_engagement_threshold').first()
            if engagement_config:
                self.LOW_ENGAGEMENT_THRESHOLD = int(engagement_config.config_value)
            
            grade_config = SystemConfig.query.filter_by(config_key='alert_grade_threshold').first()
            if grade_config:
                self.FAILING_GRADE_THRESHOLD = int(grade_config.config_value)
            
            assignments_config = SystemConfig.query.filter_by(config_key='alert_missing_threshold').first()
            if assignments_config:
                self.MISSING_ASSIGNMENTS_THRESHOLD = int(assignments_config.config_value)
            
            self._thresholds_loaded = True
            logger.info("Alert thresholds loaded from database")
            
        except Exception as e:
            logger.warning(f"Could not load thresholds from database, using defaults: {str(e)}")
            self._thresholds_loaded = True  # Prevent repeated attempts
        
    def check_and_create_alerts(self, enrollment_id: int = None):
        """
        Check all alert conditions and create alerts as needed
        
        Args:
            enrollment_id: Optional - check specific enrollment or all if None
        """
        # Load thresholds if not already loaded
        self._load_thresholds()
        
        try:
            if enrollment_id:
                enrollments = [Enrollment.query.get(enrollment_id)]
            else:
                # Get all active enrollments
                enrollments = Enrollment.query.filter_by(
                    enrollment_status='enrolled'
                ).all()
            
            logger.info(f"Checking alerts for {len(enrollments)} enrollments")
            
            for enrollment in enrollments:
                if enrollment:
                    self._check_attendance_alert(enrollment)
                    self._check_engagement_alert(enrollment)
                    self._check_grade_risk_alert(enrollment)
                    self._check_missing_assignments_alert(enrollment)
                    self._check_improvement_needed_alert(enrollment)
            
            db.session.commit()
            logger.info("Alert checking completed")
            
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
            db.session.rollback()
            raise
    
    def _check_attendance_alert(self, enrollment: Enrollment):
        """Check if student has low attendance"""
        try:
            # Calculate attendance rate for last 30 days
            thirty_days_ago = datetime.now().date() - timedelta(days=30)
            
            attendance_records = Attendance.query.filter(
                and_(
                    Attendance.enrollment_id == enrollment.enrollment_id,
                    Attendance.attendance_date >= thirty_days_ago
                )
            ).all()
            
            if not attendance_records:
                return
            
            present_count = sum(1 for a in attendance_records 
                              if a.status in ['present', 'late'])
            total_count = len(attendance_records)
            attendance_rate = (present_count / total_count * 100) if total_count > 0 else 100
            
            if attendance_rate < self.ATTENDANCE_THRESHOLD:
                # Check if alert already exists in last 7 days
                recent_alert = self._get_recent_alert(
                    enrollment.enrollment_id, 'Low Attendance', days=7
                )
                
                if not recent_alert:
                    self._create_alert(
                        enrollment_id=enrollment.enrollment_id,
                        type_name='Low Attendance',
                        severity='warning',
                        message=f"Attendance rate is {attendance_rate:.1f}% (below {self.ATTENDANCE_THRESHOLD}% threshold)"
                    )
                    
        except Exception as e:
            logger.error(f"Error checking attendance alert: {str(e)}")
    
    def _check_engagement_alert(self, enrollment: Enrollment):
        """Check if student has low LMS engagement"""
        try:
            # Get engagement data for last 7 days
            seven_days_ago = datetime.now().date() - timedelta(days=7)
            
            daily_summaries = LMSDailySummary.query.filter(
                and_(
                    LMSDailySummary.enrollment_id == enrollment.enrollment_id,
                    LMSDailySummary.summary_date >= seven_days_ago
                )
            ).all()
            
            if not daily_summaries:
                return
            
            # Calculate average daily engagement
            total_activities = sum(
                s.resource_views + s.forum_posts + s.pages_viewed 
                for s in daily_summaries
            )
            avg_activities = total_activities / len(daily_summaries)
            
            # Get course average for comparison
            course_avg = self._get_course_average_engagement(enrollment.offering_id)
            
            if avg_activities < (course_avg * self.LOW_ENGAGEMENT_THRESHOLD / 100):
                recent_alert = self._get_recent_alert(
                    enrollment.enrollment_id, 'Low Engagement', days=7
                )
                
                if not recent_alert:
                    self._create_alert(
                        enrollment_id=enrollment.enrollment_id,
                        type_name='Low Engagement',
                        severity='info',
                        message=f"LMS activity is {avg_activities:.1f} per day (course average: {course_avg:.1f})"
                    )
                    
        except Exception as e:
            logger.error(f"Error checking engagement alert: {str(e)}")
    
    def _check_grade_risk_alert(self, enrollment: Enrollment):
        """Check if student is at risk of failing based on predictions"""
        try:
            # Get latest prediction
            latest_prediction = Prediction.query.filter_by(
                enrollment_id=enrollment.enrollment_id
            ).order_by(Prediction.prediction_date.desc()).first()
            
            if not latest_prediction:
                return
            
            # Check if predicted to fail or high risk
            if (latest_prediction.predicted_grade == 'F' or 
                latest_prediction.risk_level == 'high'):
                
                recent_alert = self._get_recent_alert(
                    enrollment.enrollment_id, 'Failing Grade Risk', days=3
                )
                
                if not recent_alert:
                    self._create_alert(
                        enrollment_id=enrollment.enrollment_id,
                        type_name='Failing Grade Risk',
                        severity='critical',
                        message=f"Predicted grade: {latest_prediction.predicted_grade} with {latest_prediction.confidence_score:.0%} confidence"
                    )
                    
        except Exception as e:
            logger.error(f"Error checking grade risk alert: {str(e)}")
    
    def _check_missing_assignments_alert(self, enrollment: Enrollment):
        """Check if student has missing assignments"""
        try:
            # Get all published assessments for the course that are past due
            assessments = Assessment.query.filter_by(
                offering_id=enrollment.offering_id,
                is_published=True
            ).filter(
                Assessment.due_date <= datetime.now()
            ).all()
            
            if not assessments:
                return
            
            # Count missing submissions
            missing_count = 0
            for assessment in assessments:
                submission = AssessmentSubmission.query.filter_by(
                    assessment_id=assessment.assessment_id,
                    enrollment_id=enrollment.enrollment_id
                ).first()
                
                # Check if no submission exists (missing)
                if not submission:
                    missing_count += 1
                # Or if submission exists but has no score (submitted but not graded is OK)
                # We only count it as missing if there's no submission at all
            
            if missing_count >= self.MISSING_ASSIGNMENTS_THRESHOLD:
                recent_alert = self._get_recent_alert(
                    enrollment.enrollment_id, 'Missing Assignments', days=7
                )
                
                if not recent_alert:
                    self._create_alert(
                        enrollment_id=enrollment.enrollment_id,
                        type_name='Missing Assignments',
                        severity='warning',
                        message=f"{missing_count} assignments are missing or not submitted"
                    )
                    
        except Exception as e:
            logger.error(f"Error checking missing assignments alert: {str(e)}")
    
    def _check_improvement_needed_alert(self, enrollment: Enrollment):
        """Check if student's performance is declining"""
        try:
            # Get last 5 predictions to check trend
            predictions = Prediction.query.filter_by(
                enrollment_id=enrollment.enrollment_id
            ).order_by(Prediction.prediction_date.desc()).limit(5).all()
            
            if len(predictions) < 3:
                return
            
            # Simple trend analysis - check if risk level is increasing
            risk_levels = {'low': 0, 'medium': 1, 'high': 2}
            risk_values = [risk_levels.get(p.risk_level, 0) for p in predictions]
            
            # Check if risk is increasing (newer predictions have higher risk)
            if risk_values[0] > risk_values[-1] and risk_values[0] >= 1:
                recent_alert = self._get_recent_alert(
                    enrollment.enrollment_id, 'Improvement Needed', days=7
                )
                
                if not recent_alert:
                    self._create_alert(
                        enrollment_id=enrollment.enrollment_id,
                        type_name='Improvement Needed',
                        severity='warning',
                        message=f"Performance trend shows declining grades - current risk level: {predictions[0].risk_level}"
                    )
                    
        except Exception as e:
            logger.error(f"Error checking improvement alert: {str(e)}")
    
    def _create_alert(self, enrollment_id: int, type_name: str, 
                     severity: str, message: str):
        """Create a new alert"""
        try:
            # Get or create alert type
            alert_type = AlertType.query.filter_by(type_name=type_name).first()
            if not alert_type:
                alert_type = AlertType(
                    type_name=type_name,
                    severity=severity,
                    description=message
                )
                db.session.add(alert_type)
                db.session.flush()
            
            # Create alert
            alert = Alert(
                enrollment_id=enrollment_id,
                type_id=alert_type.type_id,
                triggered_date=datetime.now(),
                alert_message=message,
                severity=severity
            )
            db.session.add(alert)
            
            logger.info(f"Created {severity} alert for enrollment {enrollment_id}: {type_name}")
            
            # Send email notification for critical alerts
            if severity == 'critical':
                self._send_alert_email(alert, enrollment_id)
                
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
    
    def _get_recent_alert(self, enrollment_id: int, type_name: str, 
                         days: int) -> Optional[Alert]:
        """Check if similar alert exists in recent days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        alert_type = AlertType.query.filter_by(type_name=type_name).first()
        if not alert_type:
            return None
        
        return Alert.query.filter(
            and_(
                Alert.enrollment_id == enrollment_id,
                Alert.type_id == alert_type.type_id,
                Alert.triggered_date >= cutoff_date
            )
        ).first()
    
    def _get_course_average_engagement(self, offering_id: int) -> float:
        """Calculate average engagement for a course"""
        # This is simplified - in production, calculate from all students
        return 10.0  # Default average activities per day
    
    def _send_alert_email(self, alert: Alert, enrollment_id: int):
        """Send email notification for critical alerts"""
        try:
            # Get student and course info
            enrollment = Enrollment.query.get(enrollment_id)
            if not enrollment:
                return
            
            student = enrollment.student
            course = enrollment.offering.course
            
            # Send to student
            self.email_service.send_alert_email(
                to_email=student.user.email,
                student_name=f"{student.first_name} {student.last_name}",
                alert_type=alert.severity,
                course_name=course.course_name,
                message=alert.alert_message
            )
            
            # Also send to faculty for critical alerts
            if alert.severity == 'critical' and enrollment.offering.faculty:
                faculty = enrollment.offering.faculty
                self.email_service.send_faculty_alert_email(
                    to_email=faculty.user.email,
                    faculty_name=f"{faculty.first_name} {faculty.last_name}",
                    student_name=f"{student.first_name} {student.last_name}",
                    course_name=course.course_name,
                    alert_message=alert.alert_message
                )
                
        except Exception as e:
            logger.error(f"Error sending alert email: {str(e)}")
    
    def get_student_alerts(self, student_id: int, 
                          unread_only: bool = False) -> List[Dict]:
        """Get all alerts for a student"""
        # Load thresholds if needed
        self._load_thresholds()
        
        query = db.session.query(Alert, AlertType, Enrollment, CourseOffering)\
            .join(AlertType)\
            .join(Enrollment)\
            .join(CourseOffering)\
            .filter(Enrollment.student_id == student_id)
        
        if unread_only:
            query = query.filter(Alert.is_read == False)
        
        alerts = query.order_by(Alert.triggered_date.desc()).all()
        
        return [
            {
                'alert_id': alert.alert_id,
                'type': alert_type.type_name,
                'severity': alert.severity,
                'message': alert.alert_message,
                'course_name': offering.course.course_name,
                'triggered_date': alert.triggered_date.isoformat(),
                'is_read': alert.is_read,
                'is_resolved': alert.is_resolved
            }
            for alert, alert_type, enrollment, offering in alerts
        ]
    
    def mark_alert_read(self, alert_id: int):
        """Mark an alert as read"""
        alert = Alert.query.get(alert_id)
        if alert:
            alert.is_read = True
            alert.read_date = datetime.now()
            db.session.commit()
    
    def resolve_alert(self, alert_id: int, resolved_by: str):
        """Mark an alert as resolved"""
        alert = Alert.query.get(alert_id)
        if alert:
            alert.is_resolved = True
            alert.resolved_date = datetime.now()
            alert.resolved_by = resolved_by
            db.session.commit()
    
    def get_alert_summary(self, faculty_id: int = None) -> Dict:
        """Get summary of alerts"""
        # Load thresholds if needed
        self._load_thresholds()
        
        query = db.session.query(
            Alert.severity,
            db.func.count(Alert.alert_id).label('count')
        ).filter(
            Alert.is_resolved == False
        )
        
        if faculty_id:
            # Filter by faculty's courses
            query = query.join(Enrollment)\
                .join(CourseOffering)\
                .filter(CourseOffering.faculty_id == faculty_id)
        
        results = query.group_by(Alert.severity).all()
        
        summary = {
            'total': 0,
            'critical': 0,
            'warning': 0,
            'info': 0
        }
        
        for severity, count in results:
            summary[severity] = count
            summary['total'] += count
        
        return summary