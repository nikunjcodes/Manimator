"""
Logging Configuration for ManimAI Flask Application
Centralized logging setup with proper formatting and handlers
"""

import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging(app):
    """Setup logging configuration for the Flask application"""
    
    # Get configuration from app config
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    log_file = app.config.get('LOG_FILE', 'app.log')
    log_max_bytes = app.config.get('LOG_MAX_BYTES', 10485760)  # 10MB
    log_backup_count = app.config.get('LOG_BACKUP_COUNT', 5)
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else 'logs'
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=log_max_bytes,
            backupCount=log_backup_count
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Setup Flask app logger
    app.logger.setLevel(log_level)
    
    # Log startup message
    app.logger.info(f"ManimAI application started - Log level: {logging.getLevelName(log_level)}")