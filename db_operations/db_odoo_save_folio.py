# db_odoo_save_folio.py

from db_operations.db_connect import DatabaseManager
from utils.logger_config import app_logger  # ✅ Logger centralizado
from typing import List, Dict

class OdooDBManager:
    def __init__(self, folio_id):
        # ✅ Logger específico para Odoo DB
        self.logger = app_logger.getChild('OdooDBManager')
        self.logger.info(f"🚀 Inicializando OdooDBManager para folio_id: {folio_id}")
        
        self.db_manager = DatabaseManager()
        self.folio_id = folio_id

    def get_folios_weighings(self) -> List[Dict]:
        """Obtener pesajes de la base de datos con filtro por self.folio_id."""
        self.logger.debug(f"📋 Obteniendo pesajes para folio_id: {self.folio_id}")
        
        # Definir la cláusula WHERE condicionalmente
        where_clause = ""
        parameters = []
        
        if self.folio_id is not None:
            # Usamos '?' como marcador de posición para la inyección segura de datos
            where_clause = " WHERE wr.id_weighing = ?" 
            parameters.append(self.folio_id)
            self.logger.debug(f"🔍 Aplicando filtro por folio_id: {self.folio_id}")
        else:
            self.logger.warning("⚠️ folio_id es None, obteniendo todos los registros")
            
        query = f"""
            SELECT 
                wr.id_weighing,
                wr.folio_number,
                wr.date_start,
                wr.date_end,
                wr.days_open_folio,
                wr.weighing_type,
                wr.gross_weight,
                wr.tare_weight,
                wr.net_weight,
                wr.scale_record_status,
                wr.weight_original,
                wr.id_status_odoo,
                wr.notes,
                v.external_id_vehicle,
                t.external_id_trailer,
                d.external_id_driver,
                c.external_id_customer,
                m.external_id_material,
                u.user_name AS user_name_open,
                uc.user_name AS user_name_closed
            FROM weighing_records wr
            LEFT JOIN vehicles v ON wr.id_vehicle = v.id_vehicle
            LEFT JOIN trailers t ON wr.id_trailer = t.id_trailer 
            LEFT JOIN drivers d ON wr.id_driver = d.id_driver 
            LEFT JOIN customers c ON wr.id_customer = c.external_id_customer 
            LEFT JOIN materials m ON wr.id_material = m.id_material 
            LEFT JOIN users u ON wr.id_user = u.id_user
            LEFT JOIN users uc ON wr.id_user_closed = uc.id_user
            {where_clause}  
            ORDER BY wr.id_weighing DESC
        """
        
        self.logger.debug(f"📝 Ejecutando consulta SQL con parámetros: {parameters}")
               
        conn = self.db_manager.connect_db()
        
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, parameters)                
                results = [dict(row) for row in cursor.fetchall()]
                
                self.logger.info(f"✅ Obtenidos {len(results)} registros de pesajes")
                if results:
                    self.logger.debug(f"📊 Primer registro: ID {results[0].get('id_weighing')}, Folio: {results[0].get('folio_number')}")
                
                return results
            except Exception as e:
                error_msg = f"❌ Error al cargar pesajes: {e}"
                self.logger.error(error_msg, exc_info=True)
                return []
            finally:
                self.db_manager.close_db(conn)
                self.logger.debug("🔌 Conexión a base de datos cerrada")
        else:
            self.logger.error("❌ No se pudo establecer conexión con la base de datos")
            return []

    def save_odoo_id_weighings(self, registro_id):
        """Guardar el ID de Odoo en la base de datos local"""
        self.logger.info(f"💾 Guardando Odoo ID {registro_id} para folio {self.folio_id}")
        
        if self.folio_id is None:
            self.logger.error("❌ No se puede guardar Odoo ID - folio_id es None")
            return False
            
        id_weighing = self.folio_id
        conn = self.db_manager.connect_db()
        
        if not conn:
            self.logger.error("❌ No se pudo conectar a la base de datos")
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute('''
                    UPDATE weighing_records
                    SET id_status_odoo = ?
                    WHERE id_weighing = ?;
                ''', (registro_id, id_weighing))
            
            conn.commit()  # Guardar los cambios en la base de datos
            
            # Verificar si se actualizó alguna fila
            if cursor.rowcount > 0:
                self.logger.info(f"✅ Registro actualizado en SQLite. ID: {id_weighing}, Odoo ID: {registro_id}")
                return True
            else:
                self.logger.warning(f"⚠️ No se encontró el registro para actualizar. ID: {id_weighing}")
                return False
                
        except Exception as e:
            error_msg = f"❌ Error al actualizar Odoo ID en base de datos: {e}"
            self.logger.error(error_msg, exc_info=True)
            return False
        finally:
            self.db_manager.close_db(conn)
            self.logger.debug("🔌 Conexión a base de datos cerrada")

    def saved_in_Odoo_status(self, status):
        """Actualizar el estado de sincronización con Odoo"""
        status_text = "exitoso" if status == 1 else "fallido"
        self.logger.info(f"🔄 Actualizando estado de sincronización Odoo a: {status_text} para folio {self.folio_id}")
        
        if self.folio_id is None:
            self.logger.error("❌ No se puede actualizar estado - folio_id es None")
            return False
            
        id_weighing = self.folio_id
        conn = self.db_manager.connect_db()
        
        if not conn:
            self.logger.error("❌ No se pudo conectar a la base de datos")
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute('''
                    UPDATE weighing_records
                    SET saved_in_Odoo = ?
                    WHERE id_weighing = ?;
                ''', (status, id_weighing))
            
            conn.commit()  # Guardar los cambios en la base de datos
            
            # Verificar si se actualizó alguna fila
            if cursor.rowcount > 0:
                self.logger.info(f"✅ Estado Odoo actualizado en SQLite. ID: {id_weighing}, Estado: {status} ({status_text})")
                return True
            else:
                self.logger.warning(f"⚠️ No se encontró el registro para actualizar estado. ID: {id_weighing}")
                return False
                
        except Exception as e:
            error_msg = f"❌ Error al actualizar estado Odoo en base de datos: {e}"
            self.logger.error(error_msg, exc_info=True)
            return False
        finally:
            self.db_manager.close_db(conn)
            self.logger.debug("🔌 Conexión a base de datos cerrada")