# db_save_folio.py

import sqlite3
from typing import List, Dict, Optional
from logic.logic_odoo_records import OdooAPI

class WeighingDBManager:
    def __init__(self):
        self.db_path = 'scale_app_DB.db'
        self.folio_id = None
        self.get_folio_id = None
    
    def get_last_folio(self) -> Optional[str]:
        """
        Obtiene el último folio disponible de la tabla weighing_records.
        
        Returns:
            str: El último folio en formato secuencial (ej: '000001')
            None: Si no hay registros o hay error
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Consultar el último folio
            cursor.execute('''
                SELECT folio_number
                FROM weighing_records 
                ORDER BY id_weighing DESC 
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
                    return f"{new_folio:06d}"  # Formato 6 dígitos con ceros a la izquierda
                except ValueError:
                    # Si el folio no es numérico, empezar desde 1
                    return "000001"
            else:
                # No hay registros, empezar desde 1
                return "000001"
                
        except sqlite3.Error as e:
            print(f"Error al obtener último folio: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def get_next_folio(self) -> str:
        """
        Obtiene el siguiente folio disponible. Si no puede obtenerlo de la BD,
        retorna un folio por defecto.
        
        Returns:
            str: Folio siguiente disponible
        """
        folio = self.get_last_folio()
        if folio:
            return folio
        else:
            # Folio por defecto en caso de error
            return "000001"
        
    def save_weighing_record(self, weighing_data):
        """
        Guarda un registro de pesaje en la base de datos.
        
        Args:
            weighing_data: Objeto DataWeighing con los datos del pesaje
            
        Returns:
            bool: True si se guardó correctamente, False si hubo error
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Adaptar a la estructura REAL de la tabla weighing_records
            sql = """
            INSERT INTO weighing_records (
                folio_number, date_start, gross_weight,tare_weight, date_end, net_weight, 
                id_changes, weighing_type, notes, folio_ALM2, weight_original,
                id_customer, id_vehicle, id_trailer, id_driver, id_material, id_user
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            # Mapear los datos a la estructura real de la tabla
            values = (
                weighing_data.folio,
                weighing_data.date_start,      # date_start
                weighing_data.gross_weight,        # gross_weight
                weighing_data.tare_weight,         # tare_weight
                weighing_data.date_end,         # date_end
                weighing_data.peso_neto,         # net_weight
                weighing_data.id_changes,     # id_changes
                weighing_data.tipo_pesaje,       # weighing_type
                weighing_data.notes,             # notes
                weighing_data.folio_ALM2,
                weighing_data.weight_original,
                weighing_data.id_customer,        # external_id_customer
                weighing_data.id_vehicle,       # id_vehicle
                weighing_data.id_trailer,       # id_trailer
                weighing_data.id_driver,         # id_driver
                weighing_data.id_material,       # id_material
                weighing_data.id_usuario         # id_user
            )
            
            cursor.execute(sql, values)
            conn.commit()
            
            # Obtener el siguiente folio después de guardar
            siguiente_folio = self.get_next_folio()
            self.folio_id = cursor.lastrowid
            self.get_folio_id = OdooAPI(self.folio_id)

            #print(f'El id del folio insertado es: {self.folio_id}')
            self.get_folio_id.create_record_scale()

            return True, siguiente_folio
            
        except sqlite3.Error as e:
            print(f"Error al guardar registro de pesaje: {e}")
            return False, None
        finally:
            if conn:
                conn.close()

    def save_manual_weighing_record(self, weighing_data):
        """
        Guarda un registro de pesaje en la base de datos.
        
        Args:
            weighing_data: Objeto DataWeighing con los datos del pesaje
            
        Returns:
            bool: True si se guardó correctamente, False si hubo error
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Adaptar a la estructura REAL de la tabla weighing_records
            sql = """
            INSERT INTO weighing_records (
                folio_number, date_start, gross_weight,tare_weight, date_end, net_weight, 
                id_changes, weighing_type, notes, folio_ALM2, weight_original,
                id_customer, id_vehicle, id_trailer, id_driver, id_material, id_user, scale_record_status, id_user_closed
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            # Mapear los datos a la estructura real de la tabla
            values = (
                weighing_data.folio,
                weighing_data.date_start,      # date_start
                weighing_data.gross_weight,        # gross_weight
                weighing_data.tare_weight,         # tare_weight
                weighing_data.date_end,         # date_end
                weighing_data.net_weight,         # net_weight
                weighing_data.id_changes,     # id_changes
                weighing_data.weighing_type,       # weighing_type
                weighing_data.notes,             # notes
                weighing_data.folio_ALM2,
                weighing_data.weight_original,
                weighing_data.id_customer,        # external_id_customer
                weighing_data.id_vehicle,       # id_vehicle
                weighing_data.id_trailer,       # id_trailer
                weighing_data.id_driver,         # id_driver
                weighing_data.id_material,       # id_material
                weighing_data.id_usuario,         # id_user
                weighing_data.scale_record_status,
                weighing_data.id_usuario
            )
            
            cursor.execute(sql, values)
            conn.commit()
            
            # Obtener el siguiente folio después de guardar
            siguiente_folio = self.get_next_folio()
            self.folio_id = cursor.lastrowid
            self.get_folio_id = OdooAPI(self.folio_id)

            #print(f'El id del folio insertado es: {self.folio_id}')
            self.get_folio_id.create_record_scale()

            return True, siguiente_folio
            
        except sqlite3.Error as e:
            print(f"Error al guardar registro de pesaje: {e}")
            return False, None
        finally:
            if conn:
                conn.close()


    def update_weighing_manual(self, weighing_data: dict) -> bool:
        """
        Ejecuta el UPDATE final para cerrar un registro de pesaje 
        en la tabla weighing_records usando los datos del diccionario.
        """
        conn = None
        result = {'exito': False, 'updated_row': None}
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # La consulta UPDATE actualizada con todos los campos
            query = """
                UPDATE weighing_records
                SET 
                    folio_number = ?,
                    date_start = ?,
                    gross_weight = ?,
                    tare_weight = ?,
                    date_end = ?,
                    net_weight = ?,
                    id_changes = ?,
                    weighing_type = ?,
                    notes = ?,
                    folio_ALM2 = ?,
                    weight_original = ?,
                    id_customer = ?,
                    id_vehicle = ?,
                    id_trailer = ?,
                    id_driver = ?,
                    id_material = ?,
                    id_user = ?,
                    scale_record_status = ?,
                    saved_in_Odoo = ?,
                    id_user_closed = ?
                WHERE 
                    id_weighing = ?;
            """

            # Los valores para los placeholders, en el orden de la consulta
            #id_changes = weighing_data.get('id_changes', 0)
            values = (
                    weighing_data.folio,                     # folio_number
                    weighing_data.date_start,                # date_start
                    weighing_data.gross_weight,              # gross_weight
                    weighing_data.tare_weight,               # tare_weight
                    weighing_data.date_end,                  # date_end
                    weighing_data.net_weight,                # net_weight
                    weighing_data.id_changes,                # id_changes
                    weighing_data.weighing_type,             # weighing_type
                    weighing_data.notes,                     # notes
                    weighing_data.folio_ALM2,                # folio_ALM2
                    weighing_data.weight_original,           # weight_original
                    weighing_data.id_customer,               # id_customer
                    weighing_data.id_vehicle,                # id_vehicle
                    weighing_data.id_trailer,                # id_trailer
                    weighing_data.id_driver,                 # id_driver
                    weighing_data.id_material,               # id_material
                    weighing_data.id_usuario,                # id_user (nota: se usa id_usuario del objeto)
                    weighing_data.scale_record_status,       # scale_record_status
                    weighing_data.saved_in_Odoo,
                    weighing_data.id_usuario,            # id_user_closed
                    weighing_data.id_weighing                # id_weighing (para WHERE)
                )
            
            cursor.execute(query, values)
            conn.commit()
            self.folio_id = weighing_data.id_weighing
            
            # Solo crear la API y llamar al método si tenemos un folio_id válido
            if self.folio_id:
                self.get_folio_id = OdooAPI(self.folio_id)
                self.get_folio_id.create_record_scale()
            
            if cursor.rowcount > 0:                
                # Ahora obtener todos los datos con los JOINs
                select_query = """
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
                        wr.folio_ALM2,
                        wr.weight_original,
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
                    WHERE wr.id_weighing = ?;
                """
                
                cursor.execute(select_query, (weighing_data.id_weighing,))
                updated_row = cursor.fetchone()
                if updated_row:
                    column_names = [description[0] for description in cursor.description]
                    # Crear diccionario con los datos actualizados
                    updated_row = dict(zip(column_names, updated_row))
                
                    result['exito'] = True
                    result['updated_row'] = updated_row
                
            else:
                print(f"⚠️ No se encontró el registro con ID {weighing_data.id_weighing} para actualizar.")

        except sqlite3.Error as e:
            print(f"❌ Error al actualizar el pesaje ID {weighing_data.id_weighing}: {e}")
        finally:
            if conn:
                conn.close()
        
        return result

    

    def get_pending_weighings(self) -> List[Dict]:
        """Obtener pesajes pendientes de la base de datos"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = """
                SELECT 
                    wr.id_weighing,
                    wr.folio_number,
                    wr.date_start,
                    wr.weighing_type,
                    wr.gross_weight,
                    wr.net_weight,
                    wr.tare_weight,
                    wr.folio_ALM2,
                    wr.weight_original,
                    wr.notes,
                    v.plates as plates,
                    v.plates || '-' || v.vehicle_type as vehicle_name,
                    v.vehicle_tara as vehicle_tara,
                    t.trailer_name as trailer_name,
                    t.equipo_tara as equipo_tara,
                    d.driver_name as driver_name,
                    c.customer_name as customer_name,
                    m.material_name as material_name,
                    u.user_name as user_name
                FROM weighing_records wr
                LEFT JOIN vehicles v ON wr.id_vehicle = v.id_vehicle
                LEFT JOIN trailers t ON wr.id_trailer = t.id_trailer
                LEFT JOIN drivers d ON wr.id_driver = d.id_driver
                LEFT JOIN customers c ON wr.id_customer = c.external_id_customer
                LEFT JOIN materials m ON wr.id_material = m.id_material
                LEFT JOIN users u ON wr.id_user = u.id_user
                WHERE wr.scale_record_status = 'Pendiente' 
                AND wr.folio_number NOT LIKE '%A'
                -- OR wr.scale_record_status IS NULL --
                ORDER BY wr.id_weighing DESC
             """
                   
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
            
        except sqlite3.Error as e:
            print(f"Error al cargar pesajes pendientes: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def close_weighing_input(self, weighing_closed_data: dict) -> bool:
        """
        Ejecuta el UPDATE final para cerrar un registro de pesaje 
        en la tabla weighing_records usando los datos del diccionario.
        """
        conn = None
        result = {'exito': False, 'updated_row': None}
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # La consulta UPDATE usa placeholders (?) para seguridad
            query = """
                UPDATE weighing_records
                SET 

                    tare_weight = ?,
                    date_end = ?,
                    net_weight = ?,
                    id_changes = ?,
                    scale_record_status = ?,
                    id_user_closed = ?,
                    notes = ?
                WHERE 
                    id_weighing = ?;
            """

            # Los valores para los placeholders, en el orden de la consulta
            id_changes = weighing_closed_data.get('id_changes', 0)
            values = (
                weighing_closed_data['tare_weight'],
                weighing_closed_data['date_end'],
                weighing_closed_data['net_weight'],
                id_changes,
                weighing_closed_data['scale_record_status'],
                weighing_closed_data['id_user_closed'],
                weighing_closed_data['notes'],  
                weighing_closed_data['id_weighing']
            )
            
            cursor.execute(query, values)
            conn.commit()
            self.folio_id = weighing_closed_data['id_weighing']
            self.get_folio_id = OdooAPI(self.folio_id)

            #print(f'El id del folio actualizado es: {self.folio_id}')
            self.get_folio_id.create_record_scale()
            
            if cursor.rowcount > 0:                
            # Ahora obtener todos los datos con los JOINs
                select_query = """
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
                    WHERE wr.id_weighing = ?;
                """
                
                cursor.execute(select_query, (weighing_closed_data['id_weighing'],))
                updated_row = cursor.fetchone()
                if updated_row:
                    column_names = [description[0] for description in cursor.description]
                # Crear diccionario con los datos actualizados
                    updated_row = dict(zip(column_names, updated_row))
                
                    result['exito'] = True
                    result['updated_row'] = updated_row
                
            else:
                print(f"⚠️ No se encontró el registro con ID {weighing_closed_data['id_weighing']} para cerrar.")

        except sqlite3.Error as e:
            print(f"❌ Error al cerrar el pesaje ID {weighing_closed_data.get('id_weighing', 'N/A')}: {e}")
        finally:
            if conn:
                conn.close()
        
        return result
    
    def close_weighing_input_alm2(self, weighing_closed_data_alm2: dict) -> bool:
        """
        Ejecuta el UPDATE final para cerrar un registro de pesaje 
        en la tabla weighing_records usando los datos del diccionario.
        """
        conn = None
        #exito = False
        result = {'exito': False, 'updated_row': None}
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # La consulta UPDATE usa placeholders (?) para seguridad
            query = """
                UPDATE weighing_records
                SET 
                    gross_weight = ?,
                    tare_weight = ?,
                    date_end = ?,
                    net_weight = ?,
                    id_changes = ?,
                    scale_record_status = ?,
                    id_user_closed = ?,
                    notes = ?
                WHERE 
                    id_weighing = ?;
            """

            # Los valores para los placeholders, en el orden de la consulta
            id_changes = weighing_closed_data_alm2.get('id_changes', 0)
            values = (
                weighing_closed_data_alm2['gross_weight'],
                weighing_closed_data_alm2['tare_weight'],
                weighing_closed_data_alm2['date_end'],
                weighing_closed_data_alm2['net_weight'],
                id_changes,
                weighing_closed_data_alm2['scale_record_status'],
                weighing_closed_data_alm2['id_user_closed'],
                weighing_closed_data_alm2['notes'],  
                weighing_closed_data_alm2['id_weighing']
            )
            
            cursor.execute(query, values)
            conn.commit()
            self.folio_id = weighing_closed_data_alm2['id_weighing']
            self.get_folio_id = OdooAPI(self.folio_id)

            self.get_folio_id.create_record_scale()
            
            if cursor.rowcount > 0:
                #print(f"✅ Pesaje ID {weighing_closed_data_alm2['id_weighing']} (Folio: {weighing_closed_data_alm2['folio_number']}) cerrado exitosamente.")
                select_query = """
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
                    WHERE wr.id_weighing = ?;
                """
                
                cursor.execute(select_query, (weighing_closed_data_alm2['id_weighing'],))
                updated_row = cursor.fetchone()
                if updated_row:
                    column_names = [description[0] for description in cursor.description]
                # Crear diccionario con los datos actualizados
                    updated_row = dict(zip(column_names, updated_row))                
                    result['exito'] = True
                    result['updated_row'] = updated_row
                #exito = True
            else:
                print(f"⚠️ No se encontró el registro con ID {weighing_closed_data_alm2['id_weighing']} para cerrar.")
                #exito = False 
        except sqlite3.Error as e:
            print(f"❌ Error al cerrar el pesaje ID {weighing_closed_data_alm2.get('id_weighing', 'N/A')}: {e}")
        finally:
            if conn:
                conn.close()
        
        return result


    def close_weighing_output(self, weighing_closed_data: dict) -> bool:
        """
        Ejecuta el UPDATE final para cerrar un registro de pesaje 
        en la tabla weighing_records usando los datos del diccionario.
        """
        conn = None
        result = {'exito': False, 'updated_row': None}
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # La consulta UPDATE usa placeholders (?) para seguridad
            query = """
                UPDATE weighing_records
                SET 
                    gross_weight = ?,
                    date_end = ?,
                    net_weight = ?,
                    id_changes = ?,
                    scale_record_status = ?,
                    id_user_closed = ?,
                    notes = ?
                WHERE 
                    id_weighing = ?;
            """

            # Los valores para los placeholders, en el orden de la consulta
            id_changes = weighing_closed_data.get('id_changes', 0)
            values = (
                weighing_closed_data['gross_weight'],
                weighing_closed_data['date_end'],
                weighing_closed_data['net_weight'],
                id_changes,
                weighing_closed_data['scale_record_status'],
                weighing_closed_data['id_user_closed'],
                weighing_closed_data['notes'],
                weighing_closed_data['id_weighing']
                    
            )
            
            cursor.execute(query, values)
            conn.commit()
            self.folio_id = weighing_closed_data['id_weighing']
            self.get_folio_id = OdooAPI(self.folio_id)
            self.get_folio_id.create_record_scale()
            
            if cursor.rowcount > 0:                
            # Ahora obtener todos los datos con los JOINs
                select_query = """
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
                    WHERE wr.id_weighing = ?;
                """
                
                cursor.execute(select_query, (weighing_closed_data['id_weighing'],))
                updated_row = cursor.fetchone()
                if updated_row:
                    column_names = [description[0] for description in cursor.description]
                # Crear diccionario con los datos actualizados
                    updated_row = dict(zip(column_names, updated_row))                
                    result['exito'] = True
                    result['updated_row'] = updated_row
            else:
                print(f"⚠️ No se encontró el registro con ID {weighing_closed_data['id_weighing']} para cerrar.")

        except sqlite3.Error as e:
            print(f"❌ Error al cerrar el pesaje ID {weighing_closed_data.get('id_weighing', 'N/A')}: {e}")
        finally:
            if conn:
                conn.close()
        print(f"Resultado de la  base de datos outpput: {result}")
        return result
    

    def get_folios_weighings(self) -> List[Dict]:
        """Obtener pesajes pendientes de la base de datos"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
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
                ORDER BY wr.id_weighing DESC
             """
                   
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
            
        except sqlite3.Error as e:
            print(f"Error al cargar pesajes: {e}")
            return []
        finally:
            if conn:
                conn.close()

    