import logging
import os
import functools

def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    file_handler = logging.FileHandler('debug.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Create a global logger instance
logger = setup_logger('gradio_app', level=logging.DEBUG if os.environ.get('DEBUG') else logging.INFO)

def debug_func(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}")
            raise
    return wrapper

def get_error_report():
    with open('debug.log', 'r') as f:
        return f.read()
