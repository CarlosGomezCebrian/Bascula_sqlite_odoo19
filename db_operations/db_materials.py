# db_materials.py

from db_operations.db_connect import DatabaseManager
from typing import List, Dict, Optional

class Materials:
    def __init__(self):
        self.db_manager = DatabaseManager()


    def save_materials_from_odoo(self,materials):
        """
        Guarda o actualiza los materiales obtenidos de Odoo en la base de datos local.
        (Usa DatabaseManager para la conexión)
        """
        conn = self.db_manager.connect_db()
        records_processed = 0
        
        # Se elimina el bloque try/finally externo, ya que DatabaseManager.connect_db ya maneja la conexión.
        # Ahora el cierre se hace en el bloque finally general.
        if conn:
            try:
                cursor = conn.cursor()
                
                external_materialsIds_from_odoo = [material.get('id') for material in materials]

                for material in materials:
                    external_id = material.get('id')
                    name = material.get('display_name', 'N/A')
                    udm = material.get('uom_name')
                    product_category_tuple = material.get('categ_id')
                    material_category = product_category_tuple[1] if isinstance(product_category_tuple, list) else 'N/A'
                    spd = material.get('x_studio_spd', False)
                    spd_status = 1 if spd else 0
                    active = material.get('active', False)
                    active_status = 1 if active else 0

                    cursor.execute("SELECT id_material FROM materials WHERE external_id_material = ?", (external_id,))
                    existing_material = cursor.fetchone()
                    
                    if existing_material:
                        cursor.execute('''
                            UPDATE materials
                            SET material_name = ?, udm = ?, category = ?, spd = ?, active_material = ?
                            WHERE external_id_material = ?;
                        ''', (name, udm, material_category, spd_status, active_status, external_id))                
                    else:
                        cursor.execute('''
                            INSERT INTO materials (external_id_material, material_name, category, udm, spd, active_material)
                            VALUES (?, ?, ?, ?, ?, ?);
                        ''', (external_id, name, material_category, udm, spd_status, active_status))
                    records_processed += 1
                        
                if external_materialsIds_from_odoo:
                    placeholders = ','.join(['?' for _ in external_materialsIds_from_odoo])
                    
                    cursor.execute(f'''
                        UPDATE materials 
                        SET active_material = 0 
                        WHERE external_id_material NOT IN ({placeholders})
                        AND external_id_material != 0
                    ''', external_materialsIds_from_odoo)

                    records_updated = cursor.rowcount
                print(f"Materiales desactivados: {records_updated}")
                
                conn.commit()
                return records_processed
                
            except Exception as e:
                print(f"Error al guardar materiales de Odoo: {e}")
                return 0
            finally:
                self.db_manager.close_db(conn)

    def get_active_materials(self):
        """
        Se conecta a la base de datos aplicacion_bascula.db usando DatabaseManager
        y obtiene los datos de los materiales activos (active_material = 1).
        
        Retorna:
            Una lista de tuplas con los datos (id_material, external_id_material, material_name, spd)
            o una lista vacía si no hay results o si ocurre un error.
        """
        results = []
        conn = self.db_manager.connect_db() 
        if conn:
            try:
                cursor = conn.cursor()
                
                comando_sql = """
                SELECT id_material, external_id_material, material_name, spd
                FROM materials
                WHERE active_material = 1;
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
        
        # Retorna lista vacía si la conexión inicial falló
        return results 


