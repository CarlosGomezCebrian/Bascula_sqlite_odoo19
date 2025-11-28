# db_operations.py

import datetime
import sqlite3
import bcrypt

def check_and_create_admin_user():
    # ... (esta función se mantiene igual)
    current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = None
    try:
        conn = sqlite3.connect('scale_app_DB.db')
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        if user_count == 0:
            print("No se encontraron usuarios. Creando usuario administrador por defecto...")

            password = b"Admin123"
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

            cursor.execute('''
                INSERT INTO users (user_name, creation_date, user_email, password_hash, access_level, active_user, change_password_date, user_create)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            ''', ('Admin',current_date_time, 'admin@example.com', hashed_password.decode('utf-8'),4 , 1, current_date_time, 1))
            
            conn.commit()
            print("Usuario administrador 'admin' creado exitosamente.")
            
        return True
        
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        return False
    finally:
        if conn:
            conn.close()


def verify_login(user_name, password):
    """
    Verifica las credenciales y retorna el nivel de acceso si son válidas
    Retorna: access_level si éxito, None si falla
    """
    conn = None
    user_id = None
    user_active = None
    try:
        conn = sqlite3.connect('scale_app_DB.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id_user, password_hash, access_level, active_user FROM users WHERE user_name = ?", (user_name,))
        result = cursor.fetchone()

        if result:
            user_id, stored_hash, user_access_level, user_active = result
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')) & user_active == 1:
                return user_access_level, user_id
        return None, user_id
            
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        return None
    finally:
        if conn:
            conn.close()

def log_login_attempt( user_id, user_text, success):
        conn = None
        try:
            conn = sqlite3.connect('scale_app_DB.db')
            cursor = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute('''
                INSERT INTO logins (id_user, user_text, datetime, successful_authentication)
                VALUES (?, ?, ?, ?);
            ''', (user_id, user_text, now, success))
            
            conn.commit()
        except sqlite3.Error as e:
            print("Error", f"Error al registrar el intento de login: {e}")
        finally:
            if conn:
                conn.close()  

