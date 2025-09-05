from datetime import datetime
from backend.extensions import db

class SystemConfig(db.Model):
    """System configuration model"""
    __tablename__ = 'system_config'
    
    config_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    config_key = db.Column(db.String(50), unique=True, nullable=False)
    config_value = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, config_key, config_value, description=None):
        self.config_key = config_key
        self.config_value = config_value
        self.description = description
    
    def to_dict(self):
        """Convert config to dictionary for API responses"""
        return {
            'config_id': self.config_id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<SystemConfig {self.config_key}>"


class AuditLog(db.Model):
    """Audit log model for tracking system changes"""
    __tablename__ = 'audit_log'
    
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(50), nullable=True)
    record_id = db.Column(db.Integer, nullable=True)
    old_values = db.Column(db.JSON, nullable=True)
    new_values = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, action, **kwargs):
        self.action = action
        
        # Optional fields
        self.user_id = kwargs.get('user_id')
        self.table_name = kwargs.get('table_name')
        self.record_id = kwargs.get('record_id')
        self.old_values = kwargs.get('old_values')
        self.new_values = kwargs.get('new_values')
        self.ip_address = kwargs.get('ip_address')
        self.user_agent = kwargs.get('user_agent')
    
    def to_dict(self):
        """Convert audit log to dictionary for API responses"""
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'action': self.action,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<AuditLog {self.log_id}: {self.action}>"


class ModelVersion(db.Model):
    """Model version for tracking ML model versions"""
    __tablename__ = 'model_versions'
    
    version_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    version_name = db.Column(db.String(50), unique=True, nullable=False)
    model_file_path = db.Column(db.String(255), nullable=True)
    accuracy = db.Column(db.Numeric(5, 2), nullable=True)
    precision_score = db.Column(db.Numeric(5, 2), nullable=True)
    recall_score = db.Column(db.Numeric(5, 2), nullable=True)
    f1_score = db.Column(db.Numeric(5, 2), nullable=True)
    training_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=False)
    feature_list = db.Column(db.JSON, nullable=True)
    hyperparameters = db.Column(db.JSON, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, version_name, **kwargs):
        self.version_name = version_name
        
        # Optional fields
        self.model_file_path = kwargs.get('model_file_path')
        self.accuracy = kwargs.get('accuracy')
        self.precision_score = kwargs.get('precision_score')
        self.recall_score = kwargs.get('recall_score')
        self.f1_score = kwargs.get('f1_score')
        self.training_date = kwargs.get('training_date')
        self.is_active = kwargs.get('is_active', False)
        self.feature_list = kwargs.get('feature_list')
        self.hyperparameters = kwargs.get('hyperparameters')
        self.notes = kwargs.get('notes')
    
    def activate(self):
        """Activate this model version and deactivate all others"""
        # Deactivate all model versions
        ModelVersion.query.update({ModelVersion.is_active: False})
        
        # Activate this version
        self.is_active = True
        db.session.commit()
        
        # Update system config
        config = SystemConfig.query.filter_by(config_key='model_version').first()
        if config:
            config.config_value = self.version_name
            db.session.commit()
    
    def to_dict(self):
        """Convert model version to dictionary for API responses"""
        return {
            'version_id': self.version_id,
            'version_name': self.version_name,
            'model_file_path': self.model_file_path,
            'accuracy': float(self.accuracy) if self.accuracy else None,
            'precision_score': float(self.precision_score) if self.precision_score else None,
            'recall_score': float(self.recall_score) if self.recall_score else None,
            'f1_score': float(self.f1_score) if self.f1_score else None,
            'training_date': self.training_date.isoformat() if self.training_date else None,
            'is_active': self.is_active,
            'feature_list': self.feature_list,
            'hyperparameters': self.hyperparameters,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<ModelVersion {self.version_name}>"