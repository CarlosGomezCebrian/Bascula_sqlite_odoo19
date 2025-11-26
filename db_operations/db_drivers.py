# db_drivers.py

from  db_operations.db_connect import DatabaseManager
from typing import List, Dict, Optional

class Drivers:
    def __init__(self):
        self.db_manager = DatabaseManager()


    def save_drivers_from_odoo(self, drivers):
        """
        Guarda o actualiza los choferes obtenidos de Odoo en la base de datos local.
        Si un conductor no está en la respuesta de Odoo pero sí en la BD local, se desactiva.
        """
        conn = self.db_manager.connect_db()
        records_processed = 0
        
        if conn:
            try:
                cursor = conn.cursor()              
                
                # Obtener todos los external_ids de la respuesta de Odoo
                external_dreversIds_from_odoo = [driver.get('id') for driver in drivers]
                
                # 1. Actualizar o insertar conductores que vienen de Odoo
                for driver in drivers:
                    external_id = driver.get('id')
                    name = driver.get('name')
                    license_number = driver.get('job_title', 'N/A')
                    active = driver.get('active', False)
                    active_status = 1 if active else 0
                    
                    cursor.execute("SELECT id_driver FROM drivers WHERE external_id_driver = ?", (external_id,))
                    existing_driver = cursor.fetchone()
                    
                    if existing_driver:
                        cursor.execute('''
                            UPDATE drivers 
                            SET driver_name = ?, license_number = ?, active_driver = ?
                            WHERE external_id_driver = ?;
                        ''', (name, license_number, active_status, external_id))
                    else:
                        cursor.execute('''
                            INSERT INTO drivers (external_id_driver, driver_name, license_number, active_driver)
                            VALUES (?, ?, ?, ?);
                        ''', (external_id, name, license_number, active_status))
                    
                    records_processed += 1
                
                if external_dreversIds_from_odoo:
                    placeholders = ','.join(['?' for _ in external_dreversIds_from_odoo])
                    
                    cursor.execute(f'''
                        UPDATE drivers 
                        SET active_driver = 0 
                        WHERE external_id_driver NOT IN ({placeholders})
                        AND external_id_driver != 0
                    ''', external_dreversIds_from_odoo)
                    
                    records_updated = cursor.rowcount
                    print(f"Conductores desactivados: {records_updated}")
                
                conn.commit()
                return records_processed
                
            except Exception as e:
                print(f"Error al guardar materiales de Odoo: {e}")
                return 0
            finally:
                self.db_manager.close_db(conn)

    def get_active_drivers(self):
        """
        Se conecta a la base de datos aplicacion_bascula.db y obtiene los datos
        de los choferes activos.    
        """
        results = []
        conn = self.db_manager.connect_db() 
        if conn:
        
            try:
                cursor = conn.cursor()
                
                comando_sql = """
                SELECT id_driver, external_id_driver, driver_name
                FROM drivers
                WHERE active_driver = 1;
                """
                cursor.execute(comando_sql)
                rows = cursor.fetchall()
                
                # Conversión a tuplas, necesaria si row_factory = sqlite3.Row está activo
                results = [tuple(row) for row in rows]
                
            except Exception as e:
                    print(f"Error al conectar o consultar la base de datos: {e}")
            finally:
                self.db_manager.close_db(conn) # Cierre consistente de la conexión
            return results
        
        return results




    def save_customers_from_odoo(self,customers):
        """
        Guarda o actualiza los clientes obtenidos de Odoo en la base de datos local.
        """
        
        conn = self.db_manager.connect_db()
        records_processed = 0
        
        if conn:
            try:
                cursor = conn.cursor()

                external_customersIds_from_odoo =[customer.get("id") for customer in customers]
                
                for customer in customers:
                    external_id = customer.get('id')
                    name = customer.get('name', 'N/A')
                    active = customer.get('active', False)
                    env_code = int(customer.get('x_studio_referencia_ambiente', 'N/A'))
                    id_alm2 = 0
                    customer_discount = 0
                    if env_code > 0:
                        env_code_str = str(env_code)
                        customer_discount_str = env_code_str[:2]
                        id_alm2_str = env_code_str[2:]
                        customer_discount = int(customer_discount_str)
                        id_alm2 = int(id_alm2_str)            
                    company_id_tuple = customer.get('company_id')
                    company_name = company_id_tuple[1] if isinstance(company_id_tuple, list) else 'N/A'
                    active_status = 1 if active else 0

                    cursor.execute("SELECT id_customer FROM customers WHERE external_id_customer = ?", (external_id,))
                    existing_customer = cursor.fetchone()

                    if existing_customer:
                        cursor.execute('''
                            UPDATE customers
                            SET customer_name = ?, environment_code = ?, customer_discount = ?, id_alm2 = ?, company_name = ?, active_customer = ?
                            WHERE external_id_customer = ?;
                        ''', (name, env_code, customer_discount, id_alm2, company_name, active_status, external_id))
                    else:
                        cursor.execute('''
                            INSERT INTO customers (external_id_customer, customer_name, environment_code, customer_discount, id_alm2, company_name, active_customer)
                            VALUES (?, ?, ?, ?, ?, ?, ?);
                        ''', (external_id, name, env_code, customer_discount, id_alm2, company_name, active_status))
                    
                    records_processed += 1

                    if external_customersIds_from_odoo:
                        placeholders = ','.join(['?' for _ in external_customersIds_from_odoo])
                    
                    cursor.execute(f'''
                        UPDATE customers 
                        SET active_customer = 0 
                        WHERE external_id_customer NOT IN ({placeholders})
                        AND external_id_customer != 0
                    ''', external_customersIds_from_odoo)
                    
                    records_updated = cursor.rowcount

                    cursor.execute('''
                        UPDATE customers 
                        SET active_customer = 0 
                        WHERE customer_name LIKE ?
                    ''', ('%ALM2%',))
                    records_updated_alm2 = cursor.rowcount
                    records_updated_total  =records_updated+records_updated_alm2
                print(f"Clientes desactivados: {records_updated_total}")
                    
                conn.commit()
                return records_processed
                
            except Exception as e:
                print(f"Error al guardar materiales de Odoo: {e}")
                return 0
            finally:
                self.db_manager.close_db(conn)

    
""""

if __name__ == '__main__':
    drivers  = Drivers()

    drivers_list  = drivers.get_active_drivers()

    print(f"La  lista  de  Choferes  activos es: {drivers_list}")
"""