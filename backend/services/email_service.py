from flask import current_app, render_template_string
from flask_mail import Message
from backend.extensions import mail
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending email notifications"""
    
    def send_alert_email(self, to_email: str, student_name: str, 
                        alert_type: str, course_name: str, message: str):
        """Send alert email to student"""
        try:
            subject = f"Academic Alert: {alert_type.title()} - {course_name}"
            
            # Email template
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2 style="color: #e74c3c;">Academic Alert</h2>
                
                <p>Dear {student_name},</p>
                
                <p>This is an automated alert regarding your performance in <strong>{course_name}</strong>.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Alert Type:</strong> {alert_type.title()}</p>
                    <p><strong>Details:</strong> {message}</p>
                </div>
                
                <p>We encourage you to:</p>
                <ul>
                    <li>Review your current performance in the student dashboard</li>
                    <li>Reach out to your instructor for additional support</li>
                    <li>Visit the academic success center for tutoring resources</li>
                </ul>
                
                <p>Early intervention can make a significant difference in your academic success.</p>
                
                <p>Best regards,<br>
                Academic Success Team</p>
                
                <hr style="margin-top: 30px;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated message from the Grade Prediction System. 
                    Please do not reply to this email.
                </p>
            </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[to_email],
                html=html_body
            )
            
            # Only send in production or if explicitly enabled
            if current_app.config.get('MAIL_ENABLED', False):
                mail.send(msg)
                logger.info(f"Alert email sent to {to_email}")
            else:
                logger.info(f"Email disabled - would send alert to {to_email}")
                
        except Exception as e:
            logger.error(f"Error sending alert email: {str(e)}")
    
    def send_faculty_alert_email(self, to_email: str, faculty_name: str,
                                student_name: str, course_name: str, 
                                alert_message: str):
        """Send alert email to faculty about at-risk student"""
        try:
            subject = f"Student Alert: {student_name} - {course_name}"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2 style="color: #e74c3c;">Student Alert Notification</h2>
                
                <p>Dear {faculty_name},</p>
                
                <p>This notification is to inform you that one of your students requires immediate attention.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Student:</strong> {student_name}</p>
                    <p><strong>Course:</strong> {course_name}</p>
                    <p><strong>Alert:</strong> {alert_message}</p>
                </div>
                
                <p>Recommended actions:</p>
                <ul>
                    <li>Review the student's recent performance</li>
                    <li>Consider scheduling a one-on-one meeting</li>
                    <li>Provide additional resources or support</li>
                    <li>Document any interventions taken</li>
                </ul>
                
                <p>You can view more details in your faculty dashboard.</p>
                
                <p>Best regards,<br>
                Academic Alert System</p>
            </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[to_email],
                html=html_body
            )
            
            if current_app.config.get('MAIL_ENABLED', False):
                mail.send(msg)
                logger.info(f"Faculty alert email sent to {to_email}")
            else:
                logger.info(f"Email disabled - would send faculty alert to {to_email}")
                
        except Exception as e:
            logger.error(f"Error sending faculty alert email: {str(e)}")
    
    def send_weekly_summary(self, to_email: str, name: str, 
                           summary_data: dict):
        """Send weekly performance summary"""
        try:
            subject = "Your Weekly Academic Performance Summary"
            
            # Format the summary data
            courses_html = ""
            for course in summary_data.get('courses', []):
                courses_html += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{course['name']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{course['attendance_rate']}%</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{course['current_grade']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{course['predicted_grade']}</td>
                </tr>
                """
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2 style="color: #3498db;">Weekly Performance Summary</h2>
                
                <p>Dear {name},</p>
                
                <p>Here's your academic performance summary for the week:</p>
                
                <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Course</th>
                            <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Attendance</th>
                            <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Current Grade</th>
                            <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Predicted Grade</th>
                        </tr>
                    </thead>
                    <tbody>
                        {courses_html}
                    </tbody>
                </table>
                
                <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">This Week's Activity</h3>
                    <ul>
                        <li>Total study time: {summary_data.get('total_study_time', 0)} hours</li>
                        <li>Resources accessed: {summary_data.get('resources_accessed', 0)}</li>
                        <li>Assignments submitted: {summary_data.get('assignments_submitted', 0)}</li>
                    </ul>
                </div>
                
                <p>Keep up the good work and remember to check your dashboard for detailed insights!</p>
                
                <p>Best regards,<br>
                Academic Success Team</p>
            </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[to_email],
                html=html_body
            )
            
            if current_app.config.get('MAIL_ENABLED', False):
                mail.send(msg)
                logger.info(f"Weekly summary sent to {to_email}")
            else:
                logger.info(f"Email disabled - would send summary to {to_email}")
                
        except Exception as e:
            logger.error(f"Error sending weekly summary: {str(e)}")