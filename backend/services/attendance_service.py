# backend/services/attendance_service.py - FIXED VERSION
from backend.models.tracking import Attendance
from backend.models.academic import Enrollment, CourseOffering, Course
from backend.models.user import Student, User
from backend.extensions import db
from sqlalchemy import func, desc, and_, case
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)

class AttendanceService:
    
    @staticmethod
    def mark_attendance(enrollment_id, attendance_date, status, check_in_time=None, notes=None, recorded_by=None):
        """Mark or update attendance for a student"""
        try:
            # Validate enrollment exists
            enrollment = Enrollment.query.get(enrollment_id)
            if not enrollment:
                logger.error(f"Enrollment {enrollment_id} not found")
                return None
            
            # Validate status
            valid_statuses = ['present', 'absent', 'late', 'excused']
            if status not in valid_statuses:
                logger.error(f"Invalid status: {status}")
                return None
            
            # Check if attendance already exists for this date
            existing_attendance = Attendance.query.filter_by(
                enrollment_id=enrollment_id,
                attendance_date=attendance_date
            ).first()
            
            if existing_attendance:
                # Update existing record
                existing_attendance.status = status
                existing_attendance.check_in_time = check_in_time
                existing_attendance.notes = notes
                existing_attendance.recorded_by = recorded_by
                existing_attendance.created_at = datetime.utcnow()
                attendance_record = existing_attendance
                logger.info(f"Updated attendance record {existing_attendance.attendance_id}")
            else:
                # Create new record
                attendance_record = Attendance(
                    enrollment_id=enrollment_id,
                    attendance_date=attendance_date,
                    status=status,
                    check_in_time=check_in_time,
                    notes=notes,
                    recorded_by=recorded_by
                )
                db.session.add(attendance_record)
                logger.info(f"Created new attendance record for enrollment {enrollment_id}")
            
            db.session.commit()
            return attendance_record
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error marking attendance: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def bulk_mark_attendance(attendance_data, recorded_by=None):
        """Mark attendance for multiple students"""
        results = []
        successful_count = 0
        
        try:
            for data in attendance_data:
                try:
                    # Validate required fields
                    if not all(key in data for key in ['enrollment_id', 'attendance_date', 'status']):
                        results.append({
                            'enrollment_id': data.get('enrollment_id', 'unknown'),
                            'success': False,
                            'error': 'Missing required fields'
                        })
                        continue
                    
                    # Mark individual attendance
                    result = AttendanceService.mark_attendance(
                        enrollment_id=data['enrollment_id'],
                        attendance_date=data['attendance_date'],
                        status=data['status'],
                        check_in_time=data.get('check_in_time'),
                        notes=data.get('notes'),
                        recorded_by=recorded_by
                    )
                    
                    if result:
                        results.append({
                            'enrollment_id': data['enrollment_id'],
                            'success': True,
                            'attendance_id': result.attendance_id,
                            'action': 'created'
                        })
                        successful_count += 1
                    else:
                        results.append({
                            'enrollment_id': data['enrollment_id'],
                            'success': False,
                            'error': 'Failed to save attendance record'
                        })
                        
                except Exception as e:
                    logger.error(f"Error processing attendance for enrollment {data.get('enrollment_id')}: {str(e)}")
                    results.append({
                        'enrollment_id': data.get('enrollment_id', 'unknown'),
                        'success': False,
                        'error': str(e)
                    })
            
            logger.info(f"Bulk attendance completed: {successful_count}/{len(attendance_data)} successful")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk attendance marking: {str(e)}")
            return []
    
    @staticmethod
    def get_course_roster(offering_id, attendance_date=None):
        """Get course roster with attendance status for a specific date"""
        try:
            if attendance_date is None:
                attendance_date = date.today()
            
            logger.info(f"Getting roster for offering {offering_id} on {attendance_date}")
            
            # Join with User table to get email
            roster_query = db.session.query(
                Enrollment.enrollment_id,
                Enrollment.student_id,
                Student.first_name,
                Student.last_name,
                User.email,
                Attendance.attendance_id,
                Attendance.status.label('attendance_status'),
                Attendance.check_in_time,
                Attendance.notes
            ).select_from(Enrollment).join(
                Student, Enrollment.student_id == Student.student_id
            ).join(
                User, User.user_id == Student.user_id
            ).outerjoin(
                Attendance, and_(
                    Attendance.enrollment_id == Enrollment.enrollment_id,
                    Attendance.attendance_date == attendance_date
                )
            ).filter(
                Enrollment.offering_id == offering_id,
                Enrollment.enrollment_status == 'enrolled'
            ).order_by(Student.last_name, Student.first_name)
            
            roster_data = roster_query.all()
            logger.info(f"Found {len(roster_data)} students in roster")
            
            roster = []
            for student in roster_data:
                roster.append({
                    'enrollment_id': student.enrollment_id,
                    'student_id': student.student_id,
                    'name': f"{student.first_name} {student.last_name}",
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'attendance_id': student.attendance_id,
                    'status': student.attendance_status or 'not_marked',
                    'check_in_time': student.check_in_time.strftime('%H:%M') if student.check_in_time else None,
                    'notes': student.notes
                })
            
            logger.info(f"Successfully built roster with {len(roster)} students")
            return roster
            
        except Exception as e:
            logger.error(f"Error getting course roster: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def get_attendance_summary(offering_id, start_date=None, end_date=None):
        """Get attendance summary for a course offering"""
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)  # Last 30 days
            
            # FIXED: Updated case() function syntax
            summary_query = db.session.query(
                Student.student_id,
                Student.first_name,
                Student.last_name,
                User.email,
                func.count(Attendance.attendance_id).label('total_classes'),
                func.sum(case((Attendance.status == 'present', 1), else_=0)).label('present_count'),
                func.sum(case((Attendance.status == 'absent', 1), else_=0)).label('absent_count'),
                func.sum(case((Attendance.status == 'late', 1), else_=0)).label('late_count'),
                func.sum(case((Attendance.status == 'excused', 1), else_=0)).label('excused_count')
            ).select_from(Enrollment).join(
                Student, Enrollment.student_id == Student.student_id
            ).join(
                User, User.user_id == Student.user_id
            ).join(
                Attendance, Attendance.enrollment_id == Enrollment.enrollment_id
            ).filter(
                Enrollment.offering_id == offering_id,
                Attendance.attendance_date >= start_date,
                Attendance.attendance_date <= end_date
            ).group_by(
                Student.student_id, Student.first_name, Student.last_name, User.email
            ).all()
            
            summary = []
            for record in summary_query:
                total = record.total_classes or 0
                present = record.present_count or 0
                attendance_rate = (present / total * 100) if total > 0 else 0
                
                summary.append({
                    'student_id': record.student_id,
                    'student_name': f"{record.first_name} {record.last_name}",
                    'email': record.email,
                    'total_classes': total,
                    'present_count': present,
                    'absent_count': record.absent_count or 0,
                    'late_count': record.late_count or 0,
                    'excused_count': record.excused_count or 0,
                    'attendance_rate': round(attendance_rate, 2)
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting attendance summary: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def get_student_attendance(student_id, course_offering_id=None, start_date=None, end_date=None):
        """Get attendance records for a specific student"""
        try:
            query = db.session.query(
                Attendance.attendance_date,
                Attendance.status,
                Attendance.check_in_time,
                Attendance.notes,
                Course.course_code,
                Course.course_name,
                CourseOffering.section_number
            ).select_from(Attendance).join(
                Enrollment, Attendance.enrollment_id == Enrollment.enrollment_id
            ).join(
                CourseOffering, Enrollment.offering_id == CourseOffering.offering_id
            ).join(
                Course, CourseOffering.course_id == Course.course_id
            ).filter(
                Enrollment.student_id == student_id
            )
            
            # Apply filters
            if course_offering_id:
                query = query.filter(Enrollment.offering_id == course_offering_id)
            
            if start_date:
                query = query.filter(Attendance.attendance_date >= start_date)
            
            if end_date:
                query = query.filter(Attendance.attendance_date <= end_date)
            
            # Order by date descending
            query = query.order_by(desc(Attendance.attendance_date))
            
            attendance_records = query.all()
            
            records = []
            for record in attendance_records:
                records.append({
                    'date': record.attendance_date.isoformat(),
                    'status': record.status,
                    'check_in_time': record.check_in_time.strftime('%H:%M') if record.check_in_time else None,
                    'notes': record.notes,
                    'course_code': record.course_code,
                    'course_name': record.course_name,
                    'section': record.section_number
                })
            
            return records
            
        except Exception as e:
            logger.error(f"Error getting student attendance: {str(e)}")
            return []
    
    @staticmethod
    def get_student_attendance_stats(student_id, course_offering_id=None):
        """Get attendance statistics for a student"""
        try:
            # FIXED: Updated case() function syntax
            query = db.session.query(
                func.count(Attendance.attendance_id).label('total_classes'),
                func.sum(case((Attendance.status == 'present', 1), else_=0)).label('present_count'),
                func.sum(case((Attendance.status == 'absent', 1), else_=0)).label('absent_count'),
                func.sum(case((Attendance.status == 'late', 1), else_=0)).label('late_count'),
                func.sum(case((Attendance.status == 'excused', 1), else_=0)).label('excused_count')
            ).select_from(Attendance).join(
                Enrollment, Attendance.enrollment_id == Enrollment.enrollment_id
            ).filter(
                Enrollment.student_id == student_id
            )
            
            if course_offering_id:
                query = query.filter(Enrollment.offering_id == course_offering_id)
            
            result = query.first()
            
            total = result.total_classes or 0
            present = result.present_count or 0
            attendance_rate = (present / total * 100) if total > 0 else 0
            
            return {
                'total_classes': total,
                'present_count': present,
                'absent_count': result.absent_count or 0,
                'late_count': result.late_count or 0,
                'excused_count': result.excused_count or 0,
                'attendance_rate': round(attendance_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting student attendance stats: {str(e)}")
            return {
                'total_classes': 0,
                'present_count': 0,
                'absent_count': 0,
                'late_count': 0,
                'excused_count': 0,
                'attendance_rate': 0
            }
    
    @staticmethod
    def delete_attendance(attendance_id):
        """Delete an attendance record"""
        try:
            attendance = Attendance.query.get(attendance_id)
            if attendance:
                db.session.delete(attendance)
                db.session.commit()
                logger.info(f"Deleted attendance record {attendance_id}")
                return True
            return False
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting attendance: {str(e)}")
            return False
    
    @staticmethod
    def get_course_attendance_dates(offering_id, limit=30):
        """Get list of dates when attendance was taken for a course"""
        try:
            dates_query = db.session.query(
                func.distinct(Attendance.attendance_date)
            ).join(
                Enrollment, Attendance.enrollment_id == Enrollment.enrollment_id
            ).filter(
                Enrollment.offering_id == offering_id
            ).order_by(
                desc(Attendance.attendance_date)
            ).limit(limit)
            
            dates = [row[0] for row in dates_query.all()]
            return dates
            
        except Exception as e:
            logger.error(f"Error getting attendance dates: {str(e)}")
            return []

# Create service instance
attendance_service = AttendanceService()