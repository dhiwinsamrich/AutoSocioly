import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional
import json

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record):
        """Format log record as structured JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'platform'):
            log_entry['platform'] = record.platform
        if hasattr(record, 'action'):
            log_entry['action'] = record.action
        if hasattr(record, 'duration'):
            log_entry['duration_ms'] = record.duration
        
        return json.dumps(log_entry)

def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_file: bool = True,
    enable_json: bool = True
) -> None:
    """
    Setup comprehensive logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        max_file_size: Maximum size of log files before rotation
        backup_count: Number of backup files to keep
        enable_console: Enable console logging
        enable_file: Enable file logging
        enable_json: Enable JSON structured logging
    """
    
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    json_formatter = StructuredFormatter()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # File handlers
    if enable_file:
        # Main application log
        app_handler = RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        app_handler.setLevel(level)
        app_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(app_handler)
        
        # Error log
        error_handler = RotatingFileHandler(
            os.path.join(log_dir, 'error.log'),
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # API log
        api_handler = RotatingFileHandler(
            os.path.join(log_dir, 'api.log'),
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        api_handler.setLevel(level)
        api_handler.setFormatter(detailed_formatter)
        
        # Create API logger
        api_logger = logging.getLogger('api')
        api_logger.addHandler(api_handler)
        api_logger.propagate = False
        
        # Social media platform logs
        for platform in ['facebook', 'instagram', 'linkedin', 'x', 'reddit', 'pinterest']:
            platform_handler = RotatingFileHandler(
                os.path.join(log_dir, f'{platform}.log'),
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            platform_handler.setLevel(level)
            platform_handler.setFormatter(detailed_formatter)
            
            platform_logger = logging.getLogger(f'platform.{platform}')
            platform_logger.addHandler(platform_handler)
            platform_logger.propagate = False
    
    # JSON structured logging
    if enable_json:
        json_handler = TimedRotatingFileHandler(
            os.path.join(log_dir, 'structured.log'),
            when='midnight',
            interval=1,
            backupCount=backup_count,
            encoding='utf-8'
        )
        json_handler.setLevel(level)
        json_handler.setFormatter(json_formatter)
        root_logger.addHandler(json_handler)
    
    # Configure specific loggers
    # Reduce noise from third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    logging.getLogger('watchfiles').setLevel(logging.WARNING)  # Suppress watchfiles change detection logs
    logging.getLogger('watchfiles.main').setLevel(logging.WARNING)  # Specifically target watchfiles.main logger
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured successfully. Level: {log_level}, Directory: {log_dir}")

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    return logging.getLogger(name)

def log_api_call(logger_name: str, method: str, endpoint: str, status_code: int, duration: float, **kwargs):
    """Log API call with structured data"""
    logger = get_logger(logger_name)
    logger.info(
        f"API {method} {endpoint} - Status: {status_code} - Duration: {duration:.2f}ms",
        extra={
            'action': 'api_call',
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'duration': duration,
            **kwargs
        }
    )

def log_social_media_action(platform: str, action: str, success: bool, **kwargs):
    """Log social media platform actions"""
    logger = get_logger(f'platform.{platform}')
    status = "SUCCESS" if success else "FAILED"
    
    logger.info(
        f"{action.upper()} - {platform} - {status}",
        extra={
            'action': action,
            'platform': platform,
            'success': success,
            **kwargs
        }
    )