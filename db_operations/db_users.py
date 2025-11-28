# db_users.py
import datetime
import bcrypt
from  db_operations.db_connect import DatabaseManager
from typing import List, Dict, Optional

class Users:
    def __init__(self):
        self.db_manager = DatabaseManager()

    def create_new_user(self, user_name, user_email, password, access_level, user_id):
      """
      Crea un nuevo usuario en la tabla 'users' con el nivel de acceso especificado.
      """
      current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      conn = self.db_manager.connect_db() 
      if conn:
        try:
            cursor = conn.cursor()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT INTO users (user_name, creation_date, user_email, password_hash, access_level, active_user, change_password_date, user_create)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            ''', (user_name, current_date_time, user_email, hashed_password.decode('utf-8'), access_level, 1, current_date_time, user_id ))
            conn.commit()
            return True
        except Exception as e:
                print(f"Error al conectar o consultar la base de datos: {e}")
        finally:
              self.db_manager.close_db(conn)
        return False
        
      return False


    def get_active_users(self):
        """
        Se conecta a la base de datos y obtiene los datos
        de los usuarios activos (active_user = 1), incluyendo el nombre del usuario
        que lo creó.
        Retorna:
            Una lista de tuplas con los datos (id_user, user_name, creation_date, 
            user_email, access_level, user_creator_name)
            o una lista vacía si no hay resultados o si ocurre un error.
        """
        results = []
        conn = self.db_manager.connect_db() 
        if conn:
            try:
                cursor = conn.cursor()
                
                comando_sql = """
                SELECT
                 us.id_user,
                 us.user_name,
                 us.creation_date, 
                 us.user_email,
                 us.access_level,
                 us.active_user,  
                 u.user_name as user_create  
                FROM users us
                LEFT JOIN users u ON us.user_create = u.id_user 
                WHERE us.access_level <  4 
                ORDER BY us.id_user ASC;
                """
                cursor.execute(comando_sql)
                rows = cursor.fetchall()
                
                results = rows
            except Exception as e:
                    print(f"Error al conectar o consultar la base de datos: {e}")
            finally:
                self.db_manager.close_db(conn)
            return results
        
        return results

    def update_user(self, user_table_id, user_name, user_email, access_level, active_user, user_id):
      """
      Crea un nuevo usuario en la tabla 'users' con el nivel de acceso especificado.
      """
      current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      conn = self.db_manager.connect_db() 
      if conn:
        try:
            cursor = conn.cursor()
            query ='''
                UPDATE users
                SET
                    user_name = ?,
                    user_email = ?,
                    access_level = ?,
                    active_user = ?,
                    date_last_change = ?,
                    user_changes = ?
                WHERE
                    id_user = ?
            '''
            values =(user_name, user_email, access_level, active_user, current_date_time, user_id, user_table_id )
            cursor.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
                    print(f"Error al conectar o consultar la base de datos: {e}")
        finally:
              self.db_manager.close_db(conn)
        return False
        
      return False 
    

    def change_password(self, user_id, password, user_change_password):
        """
        Crea un nuevo usuario en la tabla 'users' con el nivel de acceso especificado.
        """
        current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")        
        conn = self.db_manager.connect_db() 
        if conn:
            try:
                cursor = conn.cursor()
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute('''
                    UPDATE users 
                    SET password_hash = ?, change_password_date = ?, user_change_password = ?
                    WHERE id_user = ?            
                ''', (hashed_password.decode('utf-8'),current_date_time, user_change_password, user_id ))
                conn.commit()
                return True
            
            except Exception as e:
                    print(f"Error al conectar o consultar la base de datos: {e}")
            finally:
                self.db_manager.close_db(conn)
            return False
        
        return False
    

    
"""
if __name__ == '__main__':
    users  = Users()
    exito  = users.create_new_user( 'Raul', 'raul@email.com', '123456', 1, 1)
    print(f"El nuevo  usuario: {exito}")
    lista_de_usuarios  = users.get_active_users()
    print(f"La  lista  de  usuarios  sctivos es: {lista_de_usuarios}")
"""
