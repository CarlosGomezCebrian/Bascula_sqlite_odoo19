# db_folio_history.py

from db_operations.db_connect import DatabaseManager
from typing import List, Dict, Optional

class FolioHistory:
    def __init__(self):
        self.db_manager = DatabaseManager()


    def get_last_hitory_id(self) -> Optional[str]:
        """
        Obtiene el último folio disponible de la tabla weighing_records.
        
        Returns:
            str: El último folio en formato secuencial (ej: '000001')
            None: Si no hay registros o hay error
        """
        conn = conn = self.db_manager.connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Consultar el último folio
                cursor.execute('''
                    SELECT id_history
                    FROM folio_history 
                    ORDER BY id_history DESC 
                    LIMIT 1
                ''')
                
                result = cursor.fetchone()
                if result and result[0]:
                    # Si hay folio existente, incrementarlo
                    last_folio = result[0]
                    try:
                        # Intentar convertir a número y sumar 1
                        folio_num = int(last_folio)
                        new_folio = folio_num + 1
                        return new_folio  # Formato 6 dígitos con ceros a la izquierda
                    except ValueError:
                        # Si el folio no es numérico, empezar desde 1
                        return 1
                else:
                    return 1
                
            except Exception as e:
                print(f"Error al obtener último folio: {e}")
                return 0
            finally:
                self.db_manager.close_db(conn)
          
    def incert_change(self,data):
        """
        Guarda o actualiza los materiales obtenidos de Odoo en la base de datos local.
        (Usa DatabaseManager para la conexión)
        """
        history_data = data
        conn = self.db_manager.connect_db()
                
        if conn:
            try:
                cursor = conn.cursor()
                id_weighing = history_data.get('id_weighing')
                folio_number= history_data.get('folio_number')
                previous_value= history_data.get('previous_value')
                new_value= history_data.get('new_value')
                datetime_modification= history_data.get('datetime_modification')
                id_user_modificacion= history_data.get('id_user_modificacion')
                history_notes=history_data.get('history_notes')

                cursor.execute('''
                            INSERT INTO folio_history (id_weighing, folio_number, previous_value, new_value, datetime_modification, id_user_modificacion, history_notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?);
                        ''', (id_weighing, folio_number, previous_value, new_value, datetime_modification, id_user_modificacion, history_notes))
                    
                conn.commit()
                return True
                
            except Exception as e:
                print(f"Error al guardar materiales de Odoo: {e}")
                return 0
            finally:
                self.db_manager.close_db(conn)
"""
if __name__ == '__main__':
    folio_history  = FolioHistory()
    id_history = folio_history.get_last_hitory_id()
    print(f"El id_history Es:{id_history}")
"""