# db_trailers.py

from db_operations.db_connect import DatabaseManager
from typing import List, Dict, Optional

class Trailers:
    def __init__(self):
        self.db_manager = DatabaseManager()


    def save_trailers_from_odoo(self,trailers):
        """
        Guarda o actualiza los remolques obtenidos de Odoo en la base de datos local.
        """
        conn = self.db_manager.connect_db()
        records_processed = 0
        if conn:
            try:
                cursor = conn.cursor()
                external_trailersIds_from_odoo = [trailer.get('id') for trailer in trailers]

                for trailer in trailers:
                    external_id = trailer.get('id')
                    trailer_name = trailer.get('name')
                    trailer_category_tuple = trailer.get('category_id')
                    trailer_category = trailer_category_tuple[1] if isinstance(trailer_category_tuple, list) else 'N/A'
                    equipo_tara = int(trailer.get('x_studio_equipo_tara'))
                    active = trailer.get('active', False)
                    active_status = 1 if active else 0

                    cursor.execute("SELECT id_trailer FROM trailers WHERE external_id_trailer = ?", (external_id,))
                    existing_traile = cursor.fetchone()

                    if existing_traile:
                        cursor.execute('''
                            UPDATE trailers
                            SET trailer_name = ?, category_trailer = ?, equipo_tara = ?, active_trailer = ?
                            WHERE external_id_trailer = ?;
                        ''', ( trailer_name, trailer_category, equipo_tara, active_status, external_id))
                    else:
                        cursor.execute('''
                            INSERT INTO trailers (external_id_trailer, trailer_name, category_trailer, equipo_tara, active_trailer)
                            VALUES (?, ?, ?, ?, ?);
                        ''', (external_id, trailer_name, trailer_category, equipo_tara, active_status))
                    
                    records_processed += 1

                if external_trailersIds_from_odoo:
                    placeholders = ','.join(['?' for _ in external_trailersIds_from_odoo])
                    
                    cursor.execute(f'''
                        UPDATE trailers 
                        SET active_trailer = 0 
                        WHERE external_id_trailer NOT IN ({placeholders})
                        AND external_id_trailer != 0
                        ''', external_trailersIds_from_odoo)
                    
                    records_updated = cursor.rowcount
                    print(f"Remolques desactivados: {records_updated}")
                    
                conn.commit()
                return records_processed
                
            except Exception as e:
                print(f"Error al guardar materiales de Odoo: {e}")
                return 0
            finally:
                self.db_manager.close_db(conn)

    def get_active_trailers(self):
        """
        Se conecta a la base de datos aplicacion_bascula.db y obtiene los datos
        de los remolques activos (active_trailers = 1).
        
        """
        results = []
        conn = self.db_manager.connect_db() 
        if conn:
        
            try:
                cursor = conn.cursor()
                
                comando_sql = """
                SELECT id_trailer, external_id_trailer, trailer_name, category_trailer, equipo_tara
                FROM trailers
                WHERE active_trailer = 1;
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
    
"""
if __name__ == '__main__':
    clientes  = Trailers()

    lista_de_clientes  = clientes.get_active_trailers()

    print(f"La  lista  de  clientes  sctivos es: {lista_de_clientes}")
"""