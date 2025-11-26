# logger_config.py
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime

class LoggerConfig:
    def __init__(self, app_name="Bascula_sqlite_odoo"):
        self.app_name = app_name
        self.setup_logger()
    
    def setup_logger(self):
        """Configuración del logger para la aplicación de Báscula"""
        
        # Crear directorio de logs
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Obtener el logger principal
        logger = logging.getLogger(self.app_name)
        logger.setLevel(logging.DEBUG)
        
        # Evitar logs duplicados
        if logger.handlers:
            logger.handlers.clear()
        
        # Formato personalizado para báscula
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para archivo principal (rotativo)
        file_handler = RotatingFileHandler(
            f'{log_dir}/bascula_app.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Handler específico para errores
        error_handler = RotatingFileHandler(
            f'{log_dir}/bascula_errors.log',
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # Handler para eventos de báscula
        scale_handler = RotatingFileHandler(
            f'{log_dir}/bascula_events.log',
            maxBytes=5*1024*1024,
            backupCount=7,
            encoding='utf-8'
        )
        scale_handler.setLevel(logging.INFO)
        scale_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        scale_handler.setFormatter(scale_formatter)
        
        # Agregar todos los handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.addHandler(error_handler)
        logger.addHandler(scale_handler)
        
        # Evitar propagación al logger root
        logger.propagate = False
        
        self.logger = logger
    
    def get_logger(self):
        return self.logger
    
    def get_module_logger(self, module_name):
        """Obtener logger para un módulo específico"""
        return self.logger.getChild(module_name)

    def get_scale_logger(self):
        """Obtener logger específico para eventos de báscula"""
        return scale_logger

# Instancia global del logger
app_logger = LoggerConfig().get_logger()

# Logger específico para eventos de báscula
scale_logger = app_logger.getChild('scale_events')

