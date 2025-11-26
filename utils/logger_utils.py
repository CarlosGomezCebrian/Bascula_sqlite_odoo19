# logger_utils.py
from functools import wraps
from utils.logger_config import app_logger

def log_function_call(func):
    """Decorador para loggear automáticamente las llamadas a funciones"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = app_logger.getChild(func.__module__)
        logger.debug(f"Llamando función: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Función {func.__name__} ejecutada exitosamente")
            return result
        except Exception as e:
            logger.error(f"Error en función {func.__name__}: {str(e)}", exc_info=True)
            raise
    
    return wrapper

def log_scale_operation(operation_type):
    """Decorador específico para operaciones de báscula"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from utils.logger_config import scale_logger
            scale_logger.info(f"Iniciando operación de báscula: {operation_type}")
            
            try:
                result = func(*args, **kwargs)
                scale_logger.info(f"Operación {operation_type} completada exitosamente")
                return result
            except Exception as e:
                scale_logger.error(f"Error en operación {operation_type}: {str(e)}")
                raise
        return wrapper
    return decorator