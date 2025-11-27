# main.py

import os
import sys
import subprocess
import tkinter as tk
import sqlite3
from db_operations.db_create_db import create_database
from db_operations.db_operations import check_and_create_admin_user
from ui.ui_login import LoginApp
from utils.logger_config import app_logger, scale_logger  # Importar el logger

def setup_environment():
    """Configuración inicial del entorno"""
    app_logger.info("Iniciando configuración del entorno de la aplicación")
    
    # Verificar y crear estructura de directorios necesarios
    necessary_dirs = ['logs', 'exports', 'temp']
    for directory in necessary_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            app_logger.info(f"Directorio creado: {directory}")

def check_database_tables():
    """Verificar si las tablas esenciales existen en la base de datos"""
    try:
        conn = sqlite3.connect('scale_app_DB.db')
        cursor = conn.cursor()
        
        # Verificar si la tabla de usuarios existe (tabla clave)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone() is not None
        
        conn.close()
        return table_exists
    except Exception as e:
        app_logger.error(f"Error al verificar tablas de la base de datos: {e}")
        return False

def main():
    """
    Función principal de la aplicación Bascula_sqlite_odoo.
    """
    try:
        app_logger.info("=" * 50)
        app_logger.info("INICIANDO APLICACIÓN BÁSCULA SQLITE ODOO")
        app_logger.info("=" * 50)
        
        # Configurar entorno
        setup_environment()
        
        # Verificar y crear base de datos - CORREGIDO
        if not os.path.exists('scale_app_DB.db') or not check_database_tables():
            app_logger.warning("La base de datos no existe o está incompleta. Creándola...")
            scale_logger.info("Iniciando creación de base de datos")
            
            success = create_database()
            if success:
                app_logger.info("Base de datos creada exitosamente")
                scale_logger.info("Proceso de creación de base de datos finalizado")
            else:
                app_logger.error("Falló la creación de la base de datos")
                raise Exception("No se pudo crear la base de datos")
        else:
            app_logger.info("Base de datos encontrada y verificada")
        
        # Verificar y crear usuario admin
        app_logger.info("Verificando usuario administrador...")
        admin_created = check_and_create_admin_user()
        
        if admin_created:
            app_logger.info("Usuario administrador verificado/creado exitosamente")
        else:
            app_logger.warning("Problema al verificar/crear usuario administrador")
        
        # Iniciar la interfaz gráfica de login
        app_logger.info("Iniciando interfaz gráfica de login")
        scale_logger.info("Inicializando UI de login")
        
        root = tk.Tk()
        app_logger.debug("Ventana principal Tkinter creada")
        
        LoginApp(root)
        app_logger.info("Aplicación de login inicializada")
        
        root.mainloop()
        app_logger.info("Loop principal de la interfaz finalizado")
        
        # Verificar si se requiere reinicio
        if os.environ.get('RESTART_APP') == '1':
            app_logger.info("Solicitud de reinicio detectada - Reiniciando aplicación...")
            scale_logger.info("Reinicio de aplicación iniciado")
            
            # Eliminar la variable de entorno
            del os.environ['RESTART_APP']
            
            # Registrar el reinicio
            app_logger.info("Ejecutando reinicio de la aplicación...")
            
            # Ejecución del reinicio
            os.execv(sys.executable, [sys.executable, sys.argv[0]] + sys.argv[1:])
            
        app_logger.info("Aplicación finalizada correctamente")
        scale_logger.info("Sesión de báscula finalizada")
        
    except Exception as e:
        app_logger.critical(f"Error crítico en la aplicación: {str(e)}", exc_info=True)
        scale_logger.error(f"Error fatal en la aplicación: {str(e)}")
        
        # Mostrar mensaje de error al usuario
        try:
            error_root = tk.Tk()
            error_root.withdraw()  # Ocultar ventana principal
            from tkinter import messagebox
            messagebox.showerror(
                "Error Crítico", 
                f"Ha ocurrido un error crítico en la aplicación:\n{str(e)}\n\nRevisa los logs para más detalles."
            )
            error_root.destroy()
        except:
            pass  # Si falla la UI, al menos tenemos el log
        
        sys.exit(1)

if __name__ == '__main__':
    main()