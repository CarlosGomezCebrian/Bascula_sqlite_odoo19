# db_operations.py

from db_operations.db_connect import DatabaseManager


class OdooConfig:
    def __init__(self):
        self.db_manager = DatabaseManager()


    def save_odoo_api_settings(self, odoo_url, db_name, user_email, api_key):
        """
        Guarda la configuración de la API de Odoo en la base de datos.
        """
        conn = self.db_manager.connect_db()
        if conn:   
            try:
                cursor = conn.cursor()
                
                settings = {
                    'odoo_url': odoo_url,
                    'odoo_db_name': db_name,
                    'odoo_api_user_email': user_email,
                    'odoo_api_key': api_key
                }
                
                for key, value in settings.items():
                    cursor.execute('''
                        INSERT INTO app_settings (setting_key, setting_value)
                        VALUES (?, ?)
                        ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value;
                    ''', (key, value))
                    
                conn.commit()
                return True
            except Exception as e:
                print(f"Error al guardar datos de Odoo: {e}")
                return False
            finally:
                self.db_manager.close_db(conn)

    def get_odoo_config(self):
        """
        Obtiene la configuración de la API de Odoo desde la base de datos.
        """
        conn = self.db_manager.connect_db()
        if conn:
                
            try:
                cursor = conn.cursor()
                
                config = {}
                cursor.execute("SELECT setting_key, setting_value FROM app_settings WHERE setting_key LIKE 'odoo_%'")
                results = cursor.fetchall()
                
                for key, value in results:
                    config[key] = value
                
                required_keys = ['odoo_url', 'odoo_db_name', 'odoo_api_user_email', 'odoo_api_key']
                if all(key in config and config[key] for key in required_keys):
                    return config
                else:
                    return None
                    
            except Exception as e:
                print(f"Error al obtener la configuración de Odoo: {e}")
                return None
            finally:
                self.db_manager.close_db(conn)



if __name__=='__main__':

    odoo_config = OdooConfig()
    odoo_data = odoo_config.get_odoo_config()

    print(f"odoo_data: {odoo_data}")