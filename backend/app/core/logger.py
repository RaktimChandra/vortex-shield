"""
Enhanced Logging System
Structured logging with context and performance tracking
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
import traceback

class StructuredLogger:
    """Logger with structured output for production"""
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Console handler with JSON formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._get_json_formatter())
        self.logger.addHandler(console_handler)
    
    def _get_json_formatter(self):
        """Custom JSON formatter"""
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno,
                }
                
                # Add exception info if present
                if record.exc_info:
                    log_data['exception'] = {
                        'type': record.exc_info[0].__name__,
                        'message': str(record.exc_info[1]),
                        'traceback': traceback.format_exception(*record.exc_info)
                    }
                
                # Add extra fields
                if hasattr(record, 'extra_data'):
                    log_data['data'] = record.extra_data
                
                return json.dumps(log_data)
        
        return JsonFormatter()
    
    def info(self, message: str, **kwargs):
        """Log info message with extra data"""
        extra = {'extra_data': kwargs} if kwargs else {}
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with extra data"""
        extra = {'extra_data': kwargs} if kwargs else {}
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, exc_info=None, **kwargs):
        """Log error message with exception info"""
        extra = {'extra_data': kwargs} if kwargs else {}
        self.logger.error(message, exc_info=exc_info, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with extra data"""
        extra = {'extra_data': kwargs} if kwargs else {}
        self.logger.debug(message, extra=extra)
    
    def critical(self, message: str, exc_info=None, **kwargs):
        """Log critical message"""
        extra = {'extra_data': kwargs} if kwargs else {}
        self.logger.critical(message, exc_info=exc_info, extra=extra)

# Global loggers
api_logger = StructuredLogger('vortex.api')
ai_logger = StructuredLogger('vortex.ai')
db_logger = StructuredLogger('vortex.database')
security_logger = StructuredLogger('vortex.security')

def log_api_request(method: str, path: str, user_id: int = None, **kwargs):
    """Log API request"""
    api_logger.info(
        f"{method} {path}",
        user_id=user_id,
        method=method,
        path=path,
        **kwargs
    )

def log_ai_prediction(model_name: str, input_data: Dict, output: Any, execution_time: float):
    """Log AI model prediction"""
    ai_logger.info(
        f"AI prediction: {model_name}",
        model=model_name,
        execution_time=execution_time,
        output=output
    )

def log_security_event(event_type: str, user_id: int = None, severity: str = 'INFO', **kwargs):
    """Log security event"""
    security_logger.warning(
        f"Security event: {event_type}",
        event_type=event_type,
        user_id=user_id,
        severity=severity,
        **kwargs
    )
