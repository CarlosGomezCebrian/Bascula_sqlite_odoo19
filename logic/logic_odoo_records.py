# logic_odoo_records.py

import requests
import json
from datetime import datetime, timedelta
from db_operations.db_odoo_config import OdooConfig
from tkinter import messagebox
from db_operations.db_odoo_save_folio import OdooDBManager
from utils.logger_config import app_logger  
import socket
import urllib.parse

class OdooAPI:
    def __init__(self, folio_id):
        self.logger = app_logger.getChild('OdooAPI')
        self.logger.info(f"🚀 Inicializando OdooAPI para folio_id: {folio_id}")
        
        self.folio_id = folio_id
        self.odoo_id = None
        self.db_manager = OdooDBManager(self.folio_id)
        self.odoo_config = OdooConfig()
        
        config = self.odoo_config.get_odoo_config()
        if not config:
            error_msg = "Faltan datos de configuración de la API de Odoo."
            self.logger.error(error_msg)
            status = 0
            self.db_manager.saved_in_Odoo_status(status)
            messagebox.showerror("Error de Configuración", error_msg)
            return False
        
        self.url = config['odoo_url']
        self.db_name = config['odoo_db_name']
        self.email = config['odoo_api_user_email']
        self.api_key = config['odoo_api_key']
        
        self.logger.debug("Configuración de Odoo cargada correctamente")
    
    def _test_internet_connection(self, timeout=5):
        """
        Verifica si hay conexión a internet
        """
        self.logger.debug("Probando conexión a internet")
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=timeout)
            self.logger.debug("✅ Conexión a internet disponible")
            return True
        except OSError:
            self.logger.error("❌ Sin conexión a internet")
            return False
    
    def _test_odoo_server_connection(self, timeout=5):
        """
        Verifica si el servidor Odoo está accesible
        """
        self.logger.debug(f"Probando conexión al servidor Odoo: {self.url}")
        try:
            parsed_url = urllib.parse.urlparse(self.url)
            hostname = parsed_url.hostname
            
            if not hostname:
                self.logger.error("❌ URL de Odoo inválida")
                return False
            
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            socket.create_connection((hostname, port), timeout=timeout)
            self.logger.debug("✅ Servidor Odoo accesible")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Servidor Odoo inaccesible: {e}")
            return False
    
    def _make_odoo_json_request(self, model, method, params=None):
        """
        Realiza una petición a Odoo 19+ usando el endpoint /json/2/
        """
        endpoint_url = f"{self.url}/json/2/{model}/{method}"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # PREPARAR PAYLOAD SEGÚN EL MÉTODO
        if method == 'create':
            payload = {
                "vals_list": [params] if params else [{}]
            }
        elif method == 'write':
            if 'id' in params:
                record_id = params.pop('id')
                payload = {
                    "ids": [record_id],
                    "vals": params
                }
            else:
                self.logger.error("❌ Falta 'id' para operación write")
                return None
        elif method == 'search_read':
            payload = params or {}
        else:
            payload = params or {}
        
        self.logger.debug(f"Enviando {method} a {model} con payload: {payload}")
        
        try:
            response = requests.post(
                endpoint_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            self.logger.debug(f"Status Code: {response.status_code}")
            
            response.raise_for_status()
            
            data = response.json()
            self.logger.debug(f"✅ Respuesta cruda de Odoo: {data}")
            
            return data
            
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"❌ Error HTTP {response.status_code} en {model}.{method}: {e}")
            try:
                error_content = response.json()
                self.logger.error(f"❌ Detalles del error: {error_content}")
            except:
                self.logger.error(f"❌ Contenido del error: {response.text}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Error de conexión en {model}.{method}: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Error decodificando JSON en {model}.{method}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error inesperado en {model}.{method}: {e}")
            return None
    
    def _analyze_auth_error(self, error):
        """
        Analiza el error de autenticación para determinar la causa
        """
        error_str = str(error).lower()
        
        # Errores de conexión/red
        connection_errors = [
            'connection refused',
            'cannot connect',
            'timeout',
            'network is unreachable',
            'name or service not known',
            'no route to host',
            'temporary failure in name resolution'
        ]
        
        for conn_error in connection_errors:
            if conn_error in error_str:
                return "internet"
        
        # Errores de credenciales
        credential_errors = [
            'wrong login/password',
            'authentication failed',
            'invalid credentials',
            'access denied',
            'unauthorized',
            '401',
            '403'
        ]
        
        for cred_error in credential_errors:
            if cred_error in error_str:
                return "credentials"
        
        # Error desconocido
        return "unknown"
    
    def authenticate(self) -> bool:
        """
        Verifica que la conexión y autenticación con Odoo funcionen
        """
        self.logger.info("🔐 Verificando conexión con Odoo")
        
        # Primero verificar conexión a internet
        if not self._test_internet_connection():
            error_msg = "No hay conexión a internet. Verifique su conexión de red."
            self.logger.error(error_msg)
            status = 0
            self.db_manager.saved_in_Odoo_status(status)
            messagebox.showerror("Error de Conexión", error_msg)
            return False
        
        # Verificar si el servidor Odoo está accesible
        if not self._test_odoo_server_connection():
            error_msg = f"No se puede conectar al servidor Odoo: {self.url}. Verifique la URL y que el servidor esté en línea."
            self.logger.error(error_msg)
            status = 0
            self.db_manager.saved_in_Odoo_status(status)
            messagebox.showerror("Error de Conexión", error_msg)
            return False
        
        # Probar autenticación con una consulta simple
        try:
            result = self._make_odoo_json_request(
                'res.users',
                'search_read',
                {
                    'domain': [['id', '=', 1]],
                    'fields': ['name'],
                    'limit': 1
                }
            )
            
            if result is not None:
                self.logger.info("✅ Autenticación y conexión exitosas")
                return True
            else:
                error_msg = "Autenticación fallida - API Key incorrecta o sin permisos"
                self.logger.warning(error_msg)
                status = 0
                self.db_manager.saved_in_Odoo_status(status)
                messagebox.showerror("Error de Autenticación", 
                                   "Credenciales incorrectas. Verifique:\n"
                                   "- API Key\n"
                                   "- Usuario tiene permisos API\n"
                                   "- API Key está activa")
                return False
                
        except Exception as e:
            error_type = self._analyze_auth_error(e)
            
            if error_type == "credentials":
                error_msg = f"Error de credenciales: {e}"
                self.logger.error(error_msg)
                status = 0
                self.db_manager.saved_in_Odoo_status(status)
                messagebox.showerror("Error de Credenciales", 
                                   "Credenciales incorrectas. Verifique:\n"
                                   "- API Key\n"
                                   "- Permisos de usuario")
            elif error_type == "internet":
                error_msg = f"Error de conexión: {e}"
                self.logger.error(error_msg)
                status = 0
                self.db_manager.saved_in_Odoo_status(status)
                messagebox.showerror("Error de Conexión", 
                                   "No se puede conectar al servidor Odoo.\n"
                                   "Verifique:\n"
                                   "- Su conexión a internet\n"
                                   "- La URL del servidor\n"
                                   "- Que el servidor esté en línea")
            else:
                error_msg = f"Error inesperado durante autenticación: {e}"
                self.logger.error(error_msg, exc_info=True)
                status = 0
                self.db_manager.saved_in_Odoo_status(status)
                messagebox.showerror("Error de Autenticación", error_msg)
            
            return False
    
    def _stage_id(self, status):
        self.logger.debug(f"Obteniendo stage_id para estado: {status}")
        
        status_references = {
            'Pendiente': 1,
            'Cerrado': 2,
            'Capturado': 3
        }
        result = status_references[status]
        self.logger.debug(f"stage_id obtenido: {result} para estado: {status}")
        return result
    
    def _adjust_single_date(self, date_str):
        """
        Convierte hora de México (UTC-6) a UTC para Odoo
        """
        self.logger.debug(f"Ajustando fecha: {date_str}")
        
        if not date_str or date_str in ["", None, "None", "null"]:
            self.logger.warning("Fecha vacía o nula recibida, retornando False")
            return False
            
        try:
            # Parsear la fecha/hora original (hora de México UTC-6)
            dt_mexico = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            
            # Convertir a UTC: México (UTC-6) → UTC (sumar 6 horas)
            dt_utc = dt_mexico + timedelta(hours=6)
            
            # Formatear para Odoo
            result = dt_utc.strftime('%Y-%m-%d %H:%M:%S')
            
            self.logger.debug(f"🕒 Conversión MX->UTC exitosa: {date_str} -> {result}")
            return result
            
        except Exception as e:
            error_msg = f"Error convirtiendo timezone: {e}"
            self.logger.error(error_msg, exc_info=True)
            return date_str  # Mantener original si hay error
            
    def _adjust_dateTime(self, date_str):
        """
        Recibe una cadena de fecha y hora en formato 'DD/MM/AAAA HH:MM' 
        y devuelve solo la parte de la fecha 'DD/MM/AAAA'.
        """
        self.logger.debug(f"Extrayendo fecha de: {date_str}")
        
        date_only = date_str.split(' ')[0]
        self.logger.debug(f"Fecha extraída: {date_only}")
        return date_only

    def create_record_scale(self):
        self.logger.info(f"📝 Iniciando creación/actualización de registro para folio: {self.folio_id}")
        
        # Verificar autenticación primero
        if not self.authenticate():
            self.logger.error("No se puede proceder sin autenticación válida")
            return None
        
        weighing_data = self.db_manager.get_folios_weighings()
        if not weighing_data:
            self.logger.warning("No se encontraron datos de pesaje para el folio")
            return None
            
        self.logger.debug(f"Datos de pesaje obtenidos: {len(weighing_data)} registros")
        
        for record in weighing_data:
            self.logger.debug(f"Procesando registro: {record}")

            date_start_adjusted = self._adjust_single_date(record['date_start'])
            date_end_adjusted = self._adjust_single_date(record['date_end'])
            date_adjustedTime = self._adjust_single_date(record['date_start'])
            date_adjusted = self._adjust_dateTime(date_adjustedTime)

            odoo_data = {
                'x_studio_weighing_type': record['weighing_type'],
                'x_studio_folio_number': record['folio_number'],
                'x_studio_partner_id': record['external_id_customer'],
                'x_studio_scale_record_status': record['scale_record_status'],
                'x_studio_stage_id': self._stage_id(record['scale_record_status']),
                'x_studio_id_vehicle': record['external_id_vehicle'],
                'x_studio_id_trailer': record['external_id_trailer'] or "",
                'x_studio_id_material': record['external_id_material'],
                'x_studio_date': date_adjusted,
                'x_studio_date_start': date_start_adjusted,
                'x_studio_gross_weight': record['gross_weight'],
                'x_studio_tare_weight': record['tare_weight'],
                'x_studio_net_weight': record['net_weight'],
                'x_studio_date_end': date_end_adjusted,
                'x_studio_days_open_folio': record['days_open_folio'],
                'x_studio_id_driver': record['external_id_driver'],
                'x_studio_company_id': 1,
                'x_studio_scale_user_start': record['user_name_open'],
                'x_studio_scale_user_end': record['user_name_closed'] or "",
                'x_studio_notas': record['notes'],
                'x_studio_weight_original': record['weight_original'] or 0
            }
            
            self.logger.debug(f"Datos preparados para Odoo: {odoo_data}")
            
            odoo_weighing_id = record['id_status_odoo']
            self.logger.debug(f"ID de Odoo encontrado: {odoo_weighing_id}")
            
            if odoo_weighing_id is None or odoo_weighing_id == "":
                self.logger.info("Creando nuevo registro en Odoo")
                self.odoo_id = self._create_new_record_scale_odoo(odoo_data)
                return self.odoo_id
            else:
                self.logger.info(f"Actualizando registro existente en Odoo: {odoo_weighing_id}")
                self._update_record_scale_odoo(odoo_weighing_id, odoo_data)


    

    def _create_new_record_scale_odoo(self, odoo_data):
        self.logger.info("🆕 Iniciando creación de nuevo registro en Odoo")
        self.logger.debug(f"Datos para creación: {odoo_data}")

        try:
            registro_id = self._make_odoo_json_request(
                'x_scale_records',
                'create',
                odoo_data
            )
            
            if registro_id:
                # ✅ CORRECCIÓN: Odoo devuelve el ID como lista, extraemos el primer elemento
                if isinstance(registro_id, list) and len(registro_id) > 0:
                    odoo_id_value = registro_id[0]  # Extraer el ID de la lista [2] -> 2
                    self.logger.info(f"✅ Registro creado exitosamente. ID extraído: {odoo_id_value} (de respuesta: {registro_id})")
                else:
                    odoo_id_value = registro_id  # Si ya es un entero, usarlo directamente
                    self.logger.info(f"✅ Registro creado exitosamente. ID: {odoo_id_value}")
                
                # Guardar ID en base de datos local
                exito = self.db_manager.save_odoo_id_weighings(odoo_id_value)
                if exito:
                    status = 1
                    self.db_manager.saved_in_Odoo_status(status)
                    self.logger.info(f"Campo id_status_odoo actualizado exitosamente con valor: {odoo_id_value}")
                    return (True, odoo_id_value)
                else:
                    status = 0
                    self.db_manager.saved_in_Odoo_status(status)
                    self.logger.error(f"❌ No se pudo actualizar campo id_status_odoo con valor: {odoo_id_value}")
                    return None
            else:
                status = 0
                self.db_manager.saved_in_Odoo_status(status)
                self.logger.error("❌ No se pudo crear el registro en Odoo")
                return None
                
        except Exception as e:
            status = 0
            self.db_manager.saved_in_Odoo_status(status)
            error_msg = f"Error al crear registro en Odoo: {e}"
            self.logger.error(error_msg, exc_info=True)
            return None
         
    def _update_record_scale_odoo(self, odoo_weighing_id, odoo_data):
        self.logger.info(f"🔄 Iniciando actualización de registro en Odoo. ID: {odoo_weighing_id}")
        self.logger.debug(f"Datos para actualización: {odoo_data}")
        
        try:
            # Para WRITE, necesitamos incluir el ID en los parámetros
            update_data = odoo_data.copy()
            update_data['id'] = odoo_weighing_id  # Agregar el ID aquí
            
            resultado = self._make_odoo_json_request(
                'x_scale_records',
                'write',
                update_data
            )
            
            if resultado is not None:
                status = 1
                self.db_manager.saved_in_Odoo_status(status)
                self.logger.info(f"✅ Registro actualizado exitosamente. ID: {odoo_weighing_id}")
            else:
                status = 0
                self.db_manager.saved_in_Odoo_status(status)
                self.logger.warning(f"⚠️ No se pudo actualizar el registro ID: {odoo_weighing_id}")
                
            return resultado
        
        except Exception as e:
            status = 0
            self.db_manager.saved_in_Odoo_status(status)
            error_msg = f"Error al actualizar registro en Odoo: {e}"
            self.logger.error(error_msg, exc_info=True)
            return False

"""
if __name__ == "__main__":
    FOLIO_TO_FIND = 8
    folio_id = FOLIO_TO_FIND 
    odoo = OdooAPI(folio_id)

    result_main = odoo.create_record_scale()

    print(f'El resultado en el test es {result_main}')
"""