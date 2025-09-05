import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime

def setup_logger(name, log_file=None):
    """Create a logger with file and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    if logger.handlers:
        logger.handlers = []
    
    # Create logs directory
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Console handler with colored output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Format with colors for console
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler with rotation
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        
        # Standard formatter for file
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(file_formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
    
    # Add console handler
    logger.addHandler(console_handler)
    
    return logger

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output"""
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[91m\033[1m',  # Bold Red
        'RESET': '\033[0m'    # Reset
    }
    
    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        return super().format(record)

def setup_app_logging(app):
    """Configure application logging"""
    # Set up main application logger
    main_logger = setup_logger('app', 'logs/app.log')
    app.logger.handlers = main_logger.handlers
    app.logger.setLevel(main_logger.level)
    
    # Set up specialized loggers
    setup_logger('auth', 'logs/auth.log')
    setup_logger('db', 'logs/db.log')
    setup_logger('prediction', 'logs/prediction.log')
    
    # Log app startup
    app.logger.info(f"Application started in {app.config['ENV']} mode")
    
    return app