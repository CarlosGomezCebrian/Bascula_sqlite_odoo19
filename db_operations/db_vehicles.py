# db_materials.py

from db_operations.db_connect import DatabaseManager
from typing import List, Dict, Optional

class Vehicles:
    def __init__(self):
        self.db_manager = DatabaseManager()


    def save_vehicles_from_odoo(self, vehicles):
        """
        Guarda o actualiza los vehículos obtenidos de Odoo en la base de datos local.
        """
        conn = self.db_manager.connect_db()
        records_processed = 0
        
        if conn:
            try:
                cursor = conn.cursor()
                external_vehiclesIds_from_odoo = [vehicle.get('id') for vehicle in vehicles]

                for vehicle in vehicles:
                    external_id = vehicle.get('id')
                    plates = vehicle.get('license_plate', 'N/A')
                    vehicle_type_tuple = vehicle.get('model_id')
                    vehicle_type = vehicle_type_tuple[1] if isinstance(vehicle_type_tuple, list) else 'N/A'
                    vehicle_tara = int(vehicle.get('x_studio_tara'))
                    active = vehicle.get('active', False)
                    active_status = 1 if active else 0

                    cursor.execute("SELECT id_vehicle FROM vehicles WHERE external_id_vehicle = ?", (external_id,))
                    existing_vehicle = cursor.fetchone()

                    if existing_vehicle:
                        cursor.execute('''
                            UPDATE vehicles
                            SET plates = ?, vehicle_type = ?, vehicle_tara =?, active_vehicle = ?
                            WHERE external_id_vehicle = ?;
                        ''', (plates, vehicle_type, vehicle_tara, active_status, external_id))
                    else:
                        cursor.execute('''
                            INSERT INTO vehicles (external_id_vehicle, plates, vehicle_type, vehicle_tara, active_vehicle)
                            VALUES (?, ?, ?, ?, ?);
                        ''', (external_id, plates, vehicle_type, vehicle_tara, active_status))
                    
                    records_processed += 1

                if external_vehiclesIds_from_odoo:
                    placeholders = ','.join(['?' for _ in external_vehiclesIds_from_odoo])
                    
                    cursor.execute(f'''
                        UPDATE vehicles 
                        SET active_vehicle = 0 
                        WHERE external_id_vehicle NOT IN ({placeholders})
                        AND external_id_vehicle != 0
                        ''', external_vehiclesIds_from_odoo)
                    
                    records_updated = cursor.rowcount
                    print(f"Vehículos desactivados: {records_updated}")
                    
                conn.commit()
                return records_processed
                
            except Exception as e:
                print(f"Error al guardar materiales de Odoo: {e}")
                return 0
            finally:
                self.db_manager.close_db(conn)

    def get_active_vehicles(self):
        """
        Se conecta a la base de datos aplicacion_bascula.db y obtiene los datos
        de los vehículos activos (active_vehicle = 1).
        
        Retorna:
            Una lista de tuplas con los datos (id_vehicle, external_id_vehicle, vehicle_name)
            o una lista vacía si no hay resultados o si ocurre un error.
        """
        results = []
        conn = self.db_manager.connect_db() 
        if conn:
        
            try:
                cursor = conn.cursor()
                
                comando_sql = """
                SELECT id_vehicle, external_id_vehicle, plates, vehicle_type, vehicle_tara
                FROM vehicles
                WHERE active_vehicle = 1;
                """
                cursor.execute(comando_sql)
                rows = cursor.fetchall()
                
                # Conversión a tuplas, necesaria si row_factory = sqlite3.Row está activo
                results = [tuple(row) for row in rows]
                
            except Exception as e:
                    print(f"Error al conectar o consultar la base de datos: {e}")
            finally:
                self.db_manager.close_db(conn) 
            return results
        return results

        


   