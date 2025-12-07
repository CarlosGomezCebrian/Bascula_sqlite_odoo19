from db_operations.db_connect import DatabaseManager
from typing import List, Dict, Optional

class SearchOperations:
    def __init__(self):
        self.db_manager = DatabaseManager()

    def search_folio_for_text(self, text):
        """Buscar folios por texto en entry"""
        #print(f"En update texto:{text}")

        conn = self.db_manager.connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        wr.id_weighing,
                        wr.folio_number,
                        wr.date_start,
                        wr.date_end,
                        wr.weighing_type,
                        wr.gross_weight,
                        wr.tare_weight,
                        wr.net_weight,
                        wr.scale_record_status,
                        wr.id_status_odoo,
                        wr.notes,
                        wr.saved_in_odoo,
                        v.plates as plates,
                        v.plates || '-' || v.vehicle_type as vehicle_name,
                        t.trailer_name as trailer_name,
                        d.driver_name as driver_name,
                        c.customer_name as customer_name,
                        m.material_name as material_name,
                        u.user_name as user_name,
                        uc.user_name as user_name_closed
                    FROM weighing_records wr
                    LEFT JOIN vehicles v ON wr.id_vehicle = v.id_vehicle
                    LEFT JOIN trailers t ON wr.id_trailer = t.id_trailer  
                    LEFT JOIN drivers d ON wr.id_driver = d.id_driver   
                    LEFT JOIN customers c ON wr.id_customer = c.external_id_customer 
                    LEFT JOIN materials m ON wr.id_material = m.id_material 
                    LEFT JOIN users u ON wr.id_user = u.id_user
                    LEFT JOIN users uc ON wr.id_user_closed = uc.id_user
                    WHERE wr.scale_record_status = 'Cerrado'
                    AND wr.folio_number NOT LIKE '%A'
                    AND (wr.folio_number LIKE ?
                        OR wr.weighing_type LIKE ?
                        OR u.user_name LIKE ?
                        OR uc.user_name LIKE ? 
                        OR v.plates LIKE ?
                        OR v.vehicle_type  LIKE ?
                        OR t.trailer_name LIKE ? 
                        OR d.driver_name LIKE ? 
                        OR c.customer_name LIKE ?
                        OR m.material_name LIKE ?
                        OR wr.notes LIKE ?)
                    ORDER BY wr.id_weighing DESC
                """, (f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%'))
                
                columns = [column[0] for column in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
                
            except Exception as e:
                print(f"Error en la búsqueda:{str(e)} ")
                return []
            finally:
                self.db_manager.close_db(conn)
            

    def get_folios_weighings_closed(self) -> List[Dict]:
            """Obtener pesajes pendientes de la base de datos"""
            conn = None
            try:
                conn = self.db_manager.connect_db()
                cursor = conn.cursor()

                query = """
                    SELECT 
                        wr.id_weighing,
                        wr.folio_number,
                        wr.date_start,
                        wr.date_end,
                        wr.weighing_type,
                        wr.gross_weight,
                        wr.tare_weight,
                        wr.net_weight,
                        wr.scale_record_status,
                        wr.id_status_odoo,
                        wr.notes,
                        wr.saved_in_odoo,
                        v.plates as plates,
                        v.plates || '-' || v.vehicle_type as vehicle_name,
                        t.trailer_name as trailer_name,
                        d.driver_name as driver_name,
                        c.customer_name as customer_name,
                        m.material_name as material_name,
                        u.user_name as user_name,
                        uc.user_name as user_name_closed
                    FROM weighing_records wr
                    LEFT JOIN vehicles v ON wr.id_vehicle = v.id_vehicle
                    LEFT JOIN trailers t ON wr.id_trailer = t.id_trailer  
                    LEFT JOIN drivers d ON wr.id_driver = d.id_driver   
                    LEFT JOIN customers c ON wr.id_customer = c.external_id_customer 
                    LEFT JOIN materials m ON wr.id_material = m.id_material 
                    LEFT JOIN users u ON wr.id_user = u.id_user
                    LEFT JOIN users uc ON wr.id_user_closed = uc.id_user
                    WHERE wr.scale_record_status = 'Cerrado'
                    AND wr.folio_number NOT LIKE '%A'
                    ORDER BY wr.id_weighing DESC
                """
                    
                cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))                    
                return results
                
            except Exception as e:
                    return False, f"Error al buscar folios: {e}"
            finally:
                    self.db_manager.close_db(conn)

    def get_all_folios_weighings_closed(self) -> List[Dict]:
            """Obtener pesajes pendientes de la base de datos"""
            conn = None
            try:
                conn = self.db_manager.connect_db()
                cursor = conn.cursor()

                query = """
                    SELECT 
                        wr.id_weighing,
                        wr.folio_number,
                        wr.date_start,
                        wr.date_end,
                        wr.weighing_type,
                        wr.gross_weight,
                        wr.tare_weight,
                        wr.net_weight,
                        wr.scale_record_status,
                        wr.id_status_odoo,
                        wr.notes,
                        wr.saved_in_odoo,
                        wr.folio_ALM2,
                        v.plates as plates,
                        v.plates || '-' || v.vehicle_type as vehicle_name,
                        t.trailer_name as trailer_name,
                        d.driver_name as driver_name,
                        c.customer_name as customer_name,
                        m.material_name as material_name,
                        u.user_name as user_name,
                        uc.user_name as user_name_closed
                    FROM weighing_records wr
                    LEFT JOIN vehicles v ON wr.id_vehicle = v.id_vehicle
                    LEFT JOIN trailers t ON wr.id_trailer = t.id_trailer  
                    LEFT JOIN drivers d ON wr.id_driver = d.id_driver   
                    LEFT JOIN customers c ON wr.id_customer = c.external_id_customer 
                    LEFT JOIN materials m ON wr.id_material = m.id_material 
                    LEFT JOIN users u ON wr.id_user = u.id_user
                    LEFT JOIN users uc ON wr.id_user_closed = uc.id_user
                    -- WHERE wr.scale_record_status = 'Cerrado'
                    -- AND wr.folio_number NOT LIKE '%A'
                    ORDER BY wr.id_weighing DESC
                """
                    
                cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))                    
                return results
                
            except Exception as e:
                    return False, f"Error al buscar folios: {e}"
            finally:
                    self.db_manager.close_db(conn)

    def get_last_folios_weighings_closed(self) -> List[Dict]:
            """Obtener los ultimos 30 pesajes pendientes de la base de datos"""
            conn = None
            try:
                conn = self.db_manager.connect_db()
                cursor = conn.cursor()

                query = """
                    SELECT 
                        wr.id_weighing,
                        wr.folio_number,
                        wr.date_start,
                        wr.date_end,
                        wr.weighing_type,
                        wr.gross_weight,
                        wr.tare_weight,
                        wr.net_weight,
                        wr.scale_record_status,
                        wr.id_status_odoo,
                        wr.notes,
                        wr.saved_in_odoo,
                        v.plates as plates,
                        v.plates || '-' || v.vehicle_type as vehicle_name,
                        t.trailer_name as trailer_name,
                        d.driver_name as driver_name,
                        c.customer_name as customer_name,
                        m.material_name as material_name,
                        u.user_name as user_name,
                        uc.user_name as user_name_closed
                    FROM weighing_records wr
                    LEFT JOIN vehicles v ON wr.id_vehicle = v.id_vehicle
                    LEFT JOIN trailers t ON wr.id_trailer = t.id_trailer  
                    LEFT JOIN drivers d ON wr.id_driver = d.id_driver   
                    LEFT JOIN customers c ON wr.id_customer = c.external_id_customer 
                    LEFT JOIN materials m ON wr.id_material = m.id_material 
                    LEFT JOIN users u ON wr.id_user = u.id_user
                    LEFT JOIN users uc ON wr.id_user_closed = uc.id_user
                    WHERE wr.scale_record_status = 'Cerrado'
                    AND wr.folio_number NOT LIKE '%A'
                    ORDER BY wr.id_weighing DESC
                    LIMIT 30
                """
                    
                cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))                    
                return results
                
            except Exception as e:
                    return False, f"Error al buscar folios: {e}"
            finally:
                    self.db_manager.close_db(conn)


    def search_folio_for_text_manual(self, text):
        """Buscar folios por texto en entry"""

        conn = self.db_manager.connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        wr.id_weighing,
                        wr.folio_number,
                        wr.date_start,
                        wr.date_end,
                        wr.weighing_type,
                        wr.gross_weight,
                        wr.tare_weight,
                        wr.net_weight,
                        wr.scale_record_status,
                        wr.id_status_odoo,
                        wr.notes,
                        wr.saved_in_odoo,
                        v.plates as plates,
                        v.plates || '-' || v.vehicle_type as vehicle_name,
                        t.trailer_name as trailer_name,
                        d.driver_name as driver_name,
                        c.customer_name as customer_name,
                        m.material_name as material_name,
                        u.user_name as user_name,
                        uc.user_name as user_name_closed
                    FROM weighing_records wr
                    LEFT JOIN vehicles v ON wr.id_vehicle = v.id_vehicle
                    LEFT JOIN trailers t ON wr.id_trailer = t.id_trailer  
                    LEFT JOIN drivers d ON wr.id_driver = d.id_driver   
                    LEFT JOIN customers c ON wr.id_customer = c.external_id_customer 
                    LEFT JOIN materials m ON wr.id_material = m.id_material 
                    LEFT JOIN users u ON wr.id_user = u.id_user
                    LEFT JOIN users uc ON wr.id_user_closed = uc.id_user
                    -- WHERE wr.scale_record_status = 'Cerrado'
                    WHERE wr.folio_number NOT LIKE '%A'
                    AND (wr.folio_number LIKE ?
                        OR wr.weighing_type LIKE ?
                        OR u.user_name LIKE ?
                        OR uc.user_name LIKE ? 
                        OR v.plates LIKE ?
                        OR v.vehicle_type  LIKE ?
                        OR t.trailer_name LIKE ? 
                        OR d.driver_name LIKE ? 
                        OR c.customer_name LIKE ?
                        OR m.material_name LIKE ?
                        OR wr.notes LIKE ?)
                    ORDER BY wr.id_weighing DESC
                """, (f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%', f'%{text}%'))
                
                columns = [column[0] for column in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
                
            except Exception as e:
                print(f"Error en la búsqueda:{str(e)} ")
                return []
            finally:
                self.db_manager.close_db(conn)
    

    def get_last_folios_weighings_manual(self) -> List[Dict]:
            """Obtener los ultimos 30 pesajes pendientes de la base de datos"""
            conn = None
            try:
                conn = self.db_manager.connect_db()
                cursor = conn.cursor()

                query = """
                    SELECT 
                        wr.id_weighing,
                        wr.folio_number,
                        wr.date_start,
                        wr.date_end,
                        wr.weighing_type,
                        wr.gross_weight,
                        wr.tare_weight,
                        wr.net_weight,
                        wr.scale_record_status,
                        wr.id_status_odoo,
                        wr.notes,
                        wr.saved_in_odoo,
                        wr.folio_ALM2,
                        v.plates as plates,
                        v.plates || '-' || v.vehicle_type as vehicle_name,
                        t.trailer_name as trailer_name,
                        d.driver_name as driver_name,
                        c.customer_name as customer_name,
                        m.material_name as material_name,
                        u.user_name as user_name,
                        uc.user_name as user_name_closed
                    FROM weighing_records wr
                    LEFT JOIN vehicles v ON wr.id_vehicle = v.id_vehicle
                    LEFT JOIN trailers t ON wr.id_trailer = t.id_trailer  
                    LEFT JOIN drivers d ON wr.id_driver = d.id_driver   
                    LEFT JOIN customers c ON wr.id_customer = c.external_id_customer 
                    LEFT JOIN materials m ON wr.id_material = m.id_material 
                    LEFT JOIN users u ON wr.id_user = u.id_user
                    LEFT JOIN users uc ON wr.id_user_closed = uc.id_user
                    -- WHERE wr.scale_record_status = 'Cerrado'
                    -- AND wr.folio_number NOT LIKE '%A'
                    ORDER BY wr.id_weighing DESC
                    LIMIT 30
                """
                    
                cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))                    
                return results
                
            except Exception as e:
                    return False, f"Error al buscar folios: {e}"
            finally:
                    self.db_manager.close_db(conn)