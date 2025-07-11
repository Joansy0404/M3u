#!/usr/bin/env python3
"""
Logger Configuration Module
Handles logging setup and configuration
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logger(name="m3u_editor", log_level=logging.INFO, log_dir="logs"):
    """
    Setup comprehensive logging configuration
    
    Args:
        name: Logger name
        log_level: Logging level
        log_dir: Directory for log files
    
    Returns:
        Configured logger instance
    """
    # Create logs directory
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler for detailed logs (with rotation)
    log_file = os.path.join(log_dir, 'processing.log')
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # File handler for errors only
    error_file = os.path.join(log_dir, 'errors.log')
    error_handler = RotatingFileHandler(
        error_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger


def setup_debug_logger(name="m3u_debug", log_dir="logs"):
    """Setup debug-specific logger"""
    return setup_logger(name, logging.DEBUG, log_dir)


def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger()
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}")
            raise
    
    return wrapper


def create_session_logger(session_id, log_dir="logs"):
    """Create a logger for a specific processing session"""
    session_log_dir = os.path.join(log_dir, "sessions")
    os.makedirs(session_log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(session_log_dir, f"session_{session_id}_{timestamp}.log")
    
    logger = logging.getLogger(f"session_{session_id}")
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    return logger


class LogContext:
    """Context manager for logging operations"""
    
    def __init__(self, operation_name, logger=None):
        self.operation_name = operation_name
        self.logger = logger or logging.getLogger()
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = datetime.now() - self.start_time
        
        if exc_type is None:
            self.logger.info(f"Operation completed: {self.operation_name} (Duration: {duration})")
        else:
            self.logger.error(f"Operation failed: {self.operation_name} - {exc_val} (Duration: {duration})")
        
        return False  # Don't suppress exceptions


def log_performance(operation_name):
    """Decorator to log performance metrics"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger()
            start_time = datetime.now()
            
            logger.info(f"Starting {operation_name}")
            
            try:
                result = func(*args, **kwargs)
                duration = datetime.now() - start_time
                logger.info(f"Completed {operation_name} in {duration}")
                return result
                
            except Exception as e:
                duration = datetime.now() - start_time
                logger.error(f"Failed {operation_name} after {duration}: {e}")
                raise
        
        return wrapper
    return decorator
