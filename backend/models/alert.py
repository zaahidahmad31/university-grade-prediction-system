from datetime import datetime
from backend.extensions import db

class AlertType(db.Model):
    """Alert type model"""
    __tablename__ = 'alert_types'
    
    type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.Enum('info', 'warning', 'critical'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    alerts = db.relationship('Alert', backref='alert_type', lazy=True)
    
    def __init__(self, type_name, severity, description=None):
        self.type_name = type_name
        self.severity = severity
        self.description = description
    
    def to_dict(self):
        """Convert alert type to dictionary for API responses"""
        return {
            'type_id': self.type_id,
            'type_name': self.type_name,
            'severity': self.severity,
            'description': self.description
        }
    
    def __repr__(self):
        return f"<AlertType {self.type_name}: {self.severity}>"


class Alert(db.Model):
    """Alert model for student alerts"""
    __tablename__ = 'alerts'
    
    alert_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.enrollment_id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('alert_types.type_id'), nullable=False)
    triggered_date = db.Column(db.DateTime, nullable=False)
    alert_message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.Enum('info', 'warning', 'critical'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    read_date = db.Column(db.DateTime, nullable=True)
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_date = db.Column(db.DateTime, nullable=True)
    resolved_by = db.Column(db.String(20), nullable=True)
    
    # Relationships
    interventions = db.relationship('Intervention', backref='alert', lazy=True)
    
    def __init__(self, enrollment_id, type_id, triggered_date, alert_message, severity):
        self.enrollment_id = enrollment_id
        self.type_id = type_id
        self.triggered_date = triggered_date
        self.alert_message = alert_message
        self.severity = severity
    
    def mark_as_read(self):
        """Mark the alert as read"""
        self.is_read = True
        self.read_date = datetime.utcnow()
        db.session.commit()
    
    def resolve(self, resolved_by):
        """Resolve the alert"""
        self.is_resolved = True
        self.resolved_date = datetime.utcnow()
        self.resolved_by = resolved_by
        db.session.commit()
    
    def to_dict(self):
        """Convert alert to dictionary for API responses"""
        return {
            'alert_id': self.alert_id,
            'enrollment_id': self.enrollment_id,
            'type_id': self.type_id,
            'triggered_date': self.triggered_date.isoformat() if self.triggered_date else None,
            'alert_message': self.alert_message,
            'severity': self.severity,
            'is_read': self.is_read,
            'read_date': self.read_date.isoformat() if self.read_date else None,
            'is_resolved': self.is_resolved,
            'resolved_date': self.resolved_date.isoformat() if self.resolved_date else None,
            'resolved_by': self.resolved_by,
            'alert_type': self.alert_type.to_dict() if self.alert_type else None
        }
    
    def __repr__(self):
        return f"<Alert {self.alert_id} for {self.enrollment_id}: {self.severity}>"


class Intervention(db.Model):
    """Intervention model for student interventions"""
    __tablename__ = 'interventions'
    
    intervention_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.enrollment_id'), nullable=False)
    alert_id = db.Column(db.Integer, db.ForeignKey('alerts.alert_id'), nullable=True)
    faculty_id = db.Column(db.String(20), db.ForeignKey('faculty.faculty_id'), nullable=False)
    intervention_date = db.Column(db.DateTime, nullable=False)
    intervention_type = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    outcome = db.Column(db.Text, nullable=True)
    follow_up_date = db.Column(db.Date, nullable=True)
    is_successful = db.Column(db.Boolean, nullable=True)
    
    def __init__(self, enrollment_id, faculty_id, intervention_date, **kwargs):
        self.enrollment_id = enrollment_id
        self.faculty_id = faculty_id
        self.intervention_date = intervention_date
        
        # Optional fields
        self.alert_id = kwargs.get('alert_id')
        self.intervention_type = kwargs.get('intervention_type')
        self.description = kwargs.get('description')
        self.outcome = kwargs.get('outcome')
        self.follow_up_date = kwargs.get('follow_up_date')
        self.is_successful = kwargs.get('is_successful')
    
    def record_outcome(self, outcome, is_successful):
        """Record the outcome of the intervention"""
        self.outcome = outcome
        self.is_successful = is_successful
        db.session.commit()
    
    def to_dict(self):
        """Convert intervention to dictionary for API responses"""
        return {
            'intervention_id': self.intervention_id,
            'enrollment_id': self.enrollment_id,
            'alert_id': self.alert_id,
            'faculty_id': self.faculty_id,
            'intervention_date': self.intervention_date.isoformat() if self.intervention_date else None,
            'intervention_type': self.intervention_type,
            'description': self.description,
            'outcome': self.outcome,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'is_successful': self.is_successful
        }
    
    def __repr__(self):
        return f"<Intervention {self.intervention_id} for {self.enrollment_id}>"