from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy import func, and_
from backend.extensions import db
from backend.models import (
    Student, Faculty, Course, CourseOffering, Enrollment,
    Prediction, Alert, Attendance, Assessment, AssessmentSubmission,
    User, LMSDailySummary
)
import logging

logger = logging.getLogger(__name__)

class ReportsService:
    """Service for generating various reports"""
    
    def get_executive_summary(self, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """Get executive summary report"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            # User statistics
            total_students = Student.query.count()
            active_students = db.session.query(Student).join(
                Enrollment
            ).filter(
                Enrollment.enrollment_status == 'enrolled'
            ).distinct().count()
            
            total_faculty = Faculty.query.count()
            total_courses = Course.query.count()
            # Count all course offerings as active since is_active doesn't exist
            active_courses = CourseOffering.query.count()
            
            # Prediction statistics
            total_predictions = Prediction.query.filter(
                Prediction.prediction_date.between(start_date, end_date)
            ).count()
            
            high_risk_students = Prediction.query.filter(
                and_(
                    Prediction.prediction_date.between(start_date, end_date),
                    Prediction.risk_level == 'high'
                )
            ).distinct(Prediction.enrollment_id).count()
            
            # Alert statistics
            total_alerts = Alert.query.filter(
                Alert.triggered_date.between(start_date, end_date)
            ).count()
            
            unresolved_alerts = Alert.query.filter(
                and_(
                    Alert.triggered_date.between(start_date, end_date),
                    Alert.is_resolved == False
                )
            ).count()
            
            # Average attendance rate
            attendance_records = db.session.query(Attendance).filter(
                Attendance.attendance_date.between(start_date, end_date)
            ).all()
            
            if attendance_records:
                present_count = sum(1 for a in attendance_records if a.status == 'present')
                total_count = len(attendance_records)
                avg_attendance = (present_count / total_count) if total_count > 0 else 0
            else:
                avg_attendance = 0
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'users': {
                    'total_students': total_students,
                    'active_students': active_students,
                    'total_faculty': total_faculty
                },
                'courses': {
                    'total_courses': total_courses,
                    'active_courses': active_courses
                },
                'predictions': {
                    'total_predictions': total_predictions,
                    'high_risk_students': high_risk_students
                },
                'alerts': {
                    'total_alerts': total_alerts,
                    'unresolved_alerts': unresolved_alerts
                },
                'performance': {
                    'average_attendance': float(avg_attendance) * 100
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {str(e)}")
            return {}
    
    def get_student_performance_report(self, course_id: int = None) -> Dict:
        """Get student performance report"""
        try:
            query = db.session.query(
                Student,
                Enrollment,
                func.avg(AssessmentSubmission.score).label('avg_score'),
                func.count(Attendance.attendance_id).label('total_classes'),
                func.sum(Attendance.status == 'present').label('classes_attended')
            ).join(
                Enrollment, Student.student_id == Enrollment.student_id
            ).outerjoin(
                AssessmentSubmission, Enrollment.enrollment_id == AssessmentSubmission.enrollment_id
            ).outerjoin(
                Attendance, Enrollment.enrollment_id == Attendance.enrollment_id
            )
            
            if course_id:
                query = query.join(
                    CourseOffering, Enrollment.offering_id == CourseOffering.offering_id
                ).filter(CourseOffering.course_id == course_id)
            
            query = query.group_by(Student.student_id, Enrollment.enrollment_id)
            
            results = query.all()
            
            students = []
            for student, enrollment, avg_score, total_classes, classes_attended in results:
                attendance_rate = (classes_attended / total_classes * 100) if total_classes > 0 else 0
                
                # Get latest prediction
                latest_prediction = Prediction.query.filter_by(
                    enrollment_id=enrollment.enrollment_id
                ).order_by(Prediction.prediction_date.desc()).first()
                
                students.append({
                    'student_id': student.student_id,
                    'name': f"{student.first_name} {student.last_name}",
                    'average_score': float(avg_score) if avg_score else 0,
                    'attendance_rate': float(attendance_rate),
                    'predicted_grade': latest_prediction.predicted_grade if latest_prediction else 'N/A',
                    'risk_level': latest_prediction.risk_level if latest_prediction else 'N/A'
                })
            
            # Calculate overall statistics
            if students:
                overall_avg_score = sum(s['average_score'] for s in students) / len(students)
                overall_avg_attendance = sum(s['attendance_rate'] for s in students) / len(students)
                at_risk_count = sum(1 for s in students if s['risk_level'] in ['high', 'medium'])
            else:
                overall_avg_score = 0
                overall_avg_attendance = 0
                at_risk_count = 0
            
            return {
                'students': students,
                'summary': {
                    'total_students': len(students),
                    'average_score': overall_avg_score,
                    'average_attendance': overall_avg_attendance,
                    'at_risk_students': at_risk_count
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating student performance report: {str(e)}")
            return {'students': [], 'summary': {}}
    
    def get_course_analytics_report(self) -> Dict:
        """Get course analytics report"""
        try:
            courses = db.session.query(
                Course,
                CourseOffering,
                func.count(Enrollment.enrollment_id).label('enrolled_students'),
                func.avg(AssessmentSubmission.score).label('avg_score')
            ).join(
                CourseOffering, Course.course_id == CourseOffering.course_id
            ).outerjoin(
                Enrollment, CourseOffering.offering_id == Enrollment.offering_id
            ).outerjoin(
                AssessmentSubmission, Enrollment.enrollment_id == AssessmentSubmission.enrollment_id
            ).group_by(Course.course_id, CourseOffering.offering_id).all()
            
            course_list = []
            for course, offering, enrolled, avg_score in courses:
                # Get prediction statistics
                pred_stats = db.session.query(
                    Prediction.risk_level,
                    func.count(Prediction.prediction_id)
                ).join(
                    Enrollment, Prediction.enrollment_id == Enrollment.enrollment_id
                ).filter(
                    Enrollment.offering_id == offering.offering_id
                ).group_by(Prediction.risk_level).all()
                
                risk_distribution = {risk: count for risk, count in pred_stats}
                
                course_list.append({
                    'course_code': course.course_code,
                    'course_name': course.course_name,
                    'faculty': f"{offering.faculty.first_name} {offering.faculty.last_name}" if offering.faculty else 'N/A',
                    'enrolled_students': enrolled,
                    'average_score': float(avg_score) if avg_score else 0,
                    'risk_distribution': risk_distribution
                })
            
            return {
                'courses': course_list,
                'total_courses': len(course_list)
            }
            
        except Exception as e:
            logger.error(f"Error generating course analytics report: {str(e)}")
            return {'courses': [], 'total_courses': 0}
    
    def get_attendance_trends_report(self, days: int = 30) -> Dict:
        """Get attendance trends report"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Daily attendance rates
            daily_attendance = db.session.query(
                Attendance.attendance_date,
                func.count(Attendance.attendance_id).label('total'),
                func.sum(Attendance.status == 'present').label('present')
            ).filter(
                Attendance.attendance_date >= start_date
            ).group_by(Attendance.attendance_date).order_by(Attendance.attendance_date).all()
            
            trends = []
            for date, total, present in daily_attendance:
                rate = (present / total * 100) if total > 0 else 0
                trends.append({
                    'date': date.isoformat(),
                    'attendance_rate': float(rate),
                    'total_students': total,
                    'present_students': present
                })
            
            # Overall statistics
            overall_total = sum(t['total_students'] for t in trends)
            overall_present = sum(t['present_students'] for t in trends)
            overall_rate = (overall_present / overall_total * 100) if overall_total > 0 else 0
            
            return {
                'trends': trends,
                'summary': {
                    'period_days': days,
                    'average_attendance_rate': overall_rate,
                    'total_records': overall_total
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating attendance trends report: {str(e)}")
            return {'trends': [], 'summary': {}}
    
    def get_system_usage_report(self) -> Dict:
        """Get system usage report"""
        try:
            # User login statistics
            active_users_today = User.query.filter(
                User.last_login >= datetime.now().date()
            ).count()
            
            active_users_week = User.query.filter(
                User.last_login >= datetime.now() - timedelta(days=7)
            ).count()
            
            # LMS activity
            lms_activity = db.session.query(
                func.count(LMSDailySummary.summary_id).label('total_activities'),
                func.avg(LMSDailySummary.total_minutes).label('avg_minutes')
            ).filter(
                LMSDailySummary.summary_date >= datetime.now() - timedelta(days=7)
            ).first()
            
            # Predictions generated
            predictions_today = Prediction.query.filter(
                Prediction.prediction_date >= datetime.now().date()
            ).count()
            
            predictions_week = Prediction.query.filter(
                Prediction.prediction_date >= datetime.now() - timedelta(days=7)
            ).count()
            
            return {
                'user_activity': {
                    'active_users_today': active_users_today,
                    'active_users_week': active_users_week
                },
                'lms_usage': {
                    'total_activities_week': lms_activity.total_activities if lms_activity else 0,
                    'average_minutes_per_day': float(lms_activity.avg_minutes) if lms_activity and lms_activity.avg_minutes else 0
                },
                'predictions': {
                    'generated_today': predictions_today,
                    'generated_week': predictions_week
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating system usage report: {str(e)}")
            return {}