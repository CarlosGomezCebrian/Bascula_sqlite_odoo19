# db_connect.py

import sqlite3

class DatabaseManager:
    def __init__(self, db_path="scale_app_DB.db"):
        self.db_path = db_path

    def connect_db(self):
        """Establecer conexión con la base de datos"""
        try:
            conexion = sqlite3.connect(self.db_path)
            conexion.row_factory = sqlite3.Row  # Para acceso por nombre de columna
            return conexion
        except sqlite3.IntegrityError:
            return None
        except sqlite3.Error as e:
            print(f"Error al conectar con la base de datos: {e}")
            return None
        
    def close_db(self, conexion):
        """Cerrar la conexión con la base de datos"""
        if conexion:
            conexion.close()