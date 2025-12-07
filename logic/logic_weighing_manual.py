# logic_weighing_manual.py

from datetime import datetime  # ✅ Importa datetime directamente
from dataclasses import dataclass
from typing import Optional
import tkinter as tk
from utils.logger_config import app_logger

@dataclass
class DataManualWeighing:
    """Clase para almacenar los datos del pesaje"""
    folio: str
    date_start: str
    gross_weight: int
    tare_weight: int
    date_end: str
    net_weight: int
    id_changes: int
    notes: str
    id_customer: Optional[int]
    id_vehicle: Optional[int]
    id_trailer: Optional[int]
    id_driver: Optional[int]
    id_material: Optional[int]
    id_usuario: Optional[int]
    weighing_type: str  # 'entrada' o 'salida'
    folio_ALM2: str = ""
    scale_record_status: str = ""
    weight_original: Optional[int] = None
    id_alm2_discont: Optional[int] = None
    id_alm2: Optional[int] = None
    id_weighing: Optional[int] = None
    saved_in_Odoo: int = 0

class WeighingManualLogic:
    def __init__(self, user_id: int = None):
        # Inicializar logger
        self.logger = app_logger.getChild('WeighingLogic')
        self.logger.info(f"Inicializando WeighingManualLogic para usuario: {user_id}")
        
        self.user_id = user_id
        self.output_weighing = None
        self.closing_weighing = None
        self.scale_manager = None
        self.ui_references = {}  # Referencias a los widgets de UI
        self.autocomplete_handler = None  # Referencia al autocomplete handler
        self.use_simulator_var = None  # Referencia al BooleanVar del checkbox
        self.use_simulator = False  # Valor por defecto

    
    def set_ui_references(self, ui_references):
        """Establecer referencias a los widgets de UI"""
        self.ui_references = ui_references
        self.logger.debug(f"Referencias de UI establecidas: {list(ui_references.keys())}")
        
        # DEPURACIÓN: Verificar tipos de widgets
        for key, widget in ui_references.items():
            self.logger.debug(f"  - {key}: {type(widget)}")
    
    def set_autocomplete_handler(self, autocomplete_handler):
        """Establecer referencia al autocomplete handler"""
        self.logger.info("🔧 Configurando autocomplete handler")
        self.autocomplete_handler = autocomplete_handler
            
    def _get_form_data(self, weighing_type):
        """Obtener datos reales del formulario"""
        self.logger.debug(f"📋 Obteniendo datos del formulario")
        
        # ✅ CORREGIDO: Usar datetime.now() directamente
        fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        material_data = self._get_material_data()
        
        # Obtener valores reales de los entry
        folio = self._get_value_entry('folio')        
        vehicle_name = self._get_value_entry('vehicle')
        vehicle_id = self._get_id_mapped('vehicle')
        trailer_name = self._get_value_entry('trailer')
        trailer_id = self._get_id_mapped('trailer')
        driver_name = self._get_value_entry('driver')
        driver_id = self._get_id_mapped('driver')
        customer_name, customer_id, customer_discount, customer_id_alm2 = self._get_customer_data()
        material_name = material_data['material_name']
        material_id = material_data['material_id']
        notes = self._get_value_entry('notes')
        material_spd = material_data['material_spd']
        start_date = self._get_value_entry('star_date')
        end_date = self._get_value_entry('end_date')
        gross_weight = self._get_value_entry('gross_weight')
        tare_weight = self._get_value_entry('tare_weight')
        net_weight = self._get_value_entry('net_weight')
        folio_ALM2 = self._get_value_entry('folio_ALM2')

        start_date_dt = datetime.strptime(start_date, "%d/%m/%Y %H:%M:%S")
        change_format_star_date = start_date_dt.strftime("%Y-%m-%d %H:%M:%S")

        end_date_dt = datetime.strptime(end_date, "%d/%m/%Y %H:%M:%S")
        change_format_end_date = end_date_dt.strftime("%Y-%m-%d %H:%M:%S")
        
        datos = {
            'folio': folio,
            'start_date': change_format_star_date,
            'end_date': change_format_end_date,
            'weighing_type': weighing_type,
            'gross_weight': gross_weight,
            'tare_weight': tare_weight,
            'net_weight': net_weight,
            'vehicle_name': vehicle_name,
            'vehicle_id': vehicle_id,
            'trailer_name': trailer_name,
            'trailer_id': trailer_id,
            'driver_name': driver_name,
            'driver_id': driver_id,
            'customer_name': customer_name,
            'customer_id': customer_id,
            'customer_discount': customer_discount,
            'customer_id_alm2': customer_id_alm2,
            'material_name': material_name,
            'material_id': material_id,
            'id_usuario': self.user_id, 
            'notes': notes,
            'weight_original': gross_weight,
            'material_spd': material_spd,
            'folio_ALM2': folio_ALM2
        }
        
        self.logger.debug(f"📦 Datos del formulario obtenidos: {datos}")
        return datos
    
    def _validate_required_fields(self):
        """Validar campos obligatorios (solo lógica, sin UI)"""
        self.logger.debug(f"🔍 Validando campos obligatorios")
        
        campos_obligatorios = [
            'vehicle', 
            'trailer', 
            'driver', 
            'customer', 
            'material',
            'star_date',
            'end_date',
            'gross_weight',
            'tare_weight', 
            'net_weight'
        ]
        
        for campo in campos_obligatorios:
            valor = self._get_value_entry(campo)
            if not valor:
                self.logger.warning(f"❌ Campo obligatorio vacío: {campo}")
                return False
        return True
        
    def _get_customer_data(self):
        """Obtener nombre, id y del cliente"""
        self.logger.debug("👤 Obteniendo datos del cliente")
        
        customer_name = self._get_value_entry('customer')
        customer_id = self._get_id_mapped('customer')
        customer_discount = 0
        customer_id_alm2 = 0

        if self.autocomplete_handler:
            mappings = self.autocomplete_handler.mappings            
            customer_discount_map = mappings.get('customers_discount', {})
            customer_discount = customer_discount_map.get(customer_name, 0)
            customer_id_alm2_map = mappings.get('customers_id_alm2', {})
            customer_id_alm2 = customer_id_alm2_map.get(customer_name, 0)
            
            self.logger.debug(f"📊 Datos cliente: {customer_name}, ID: {customer_id}, Descuento: {customer_discount}, ALM2: {customer_id_alm2}")
                    
        return customer_name, customer_id, customer_discount, customer_id_alm2

    def _get_material_data(self):
        """Obtener nombre, id y del cliente"""
        self.logger.debug("📦 Obteniendo datos del material")
        
        material_name = self._get_value_entry('material')
        material_id = self._get_id_mapped('material')
        material_spd = 0
        
        # 1. Verificar si el autocomplete_handler está disponible
        if self.autocomplete_handler:
            # 2. Obtener los mapeos de clientes del handler
            mappings = self.autocomplete_handler.mappings
            material_spd_map = mappings.get('material_spd', {})
            material_spd = material_spd_map.get(material_name, 0)
            
            self.logger.debug(f"📊 Datos material: {material_name}, ID: {material_id}, SPD: {material_spd}")
                    
        return {
            'material_name': material_name, 
            'material_id': material_id, 
            'material_spd': material_spd
        }

    def _get_value_entry(self, campo):
        """Obtener el valor textual de un campo"""
        self.logger.debug(f"📝 Obteniendo valor del campo: {campo}")
        
        # Primero intentar con la clave normal
        if campo in self.ui_references:
            entry = self.ui_references[campo]
            self.logger.debug(f"✅ Campo encontrado en UI references: {campo}")
            return self._get_entry_value(entry)
        
        self.logger.warning(f"⚠️ Campo no encontrado en UI references: {campo}")
        return ""

    def _get_entry_value(self, entry):
        """Obtener valor de un widget de entrada específico"""
        if isinstance(entry, tk.Text):
            # Obtener todo el contenido excepto el salto de línea final
            value = entry.get('1.0', tk.END).strip()
            import re
            value = re.sub(r'\n{3,}', '\n\n', value)
            self.logger.debug(f"✅ Valor obtenido (Text): {value}")
            return value
        
        elif hasattr(entry, 'get'):
            # Para CustomAutocompleteEntry y tk.Entry
            value = entry.get().strip()
            self.logger.debug(f"✅ Valor obtenido (Entry): {value}")
            return value
        
        self.logger.warning(f"⚠️ Tipo de widget no reconocido: {type(entry)}")
        return ""
    
    def _get_id_mapped(self, campo):
        """Obtener el id mapeado de un campo autocomplete"""
        self.logger.debug(f"🆔 Obteniendo ID mapeado para: {campo}")
        
        # Para campos manuales, usa el sufijo _manual
        if campo in ['vehicle', 'trailer', 'driver', 'customer', 'material']:
            campo_key = f"{campo}s_manual"  # ¡NOTA: 's' al final! (vehicles_manual, trailers_manual, etc.)
        else:
            campo_key = campo
        
        self.logger.debug(f"🔍 Buscando clave en entries: {campo_key}")
        
        if self.autocomplete_handler:
            # DEPURACIÓN: Mostrar todas las claves disponibles
            self.logger.debug(f"📋 Entradas disponibles: {list(self.autocomplete_handler.entries.keys())}")
        
        if self.autocomplete_handler and campo_key in self.autocomplete_handler.entries:
            entry = self.autocomplete_handler.entries[campo_key]
            self.logger.debug(f"✅ Entrada encontrada para: {campo_key}")
            if hasattr(entry, 'get_mapped_value'):
                mapped_value = entry.get_mapped_value()
                self.logger.debug(f"✅ ID mapeado obtenido: {mapped_value}")
                return mapped_value if mapped_value else None
                    
        self.logger.warning(f"⚠️ No se pudo obtener ID mapeado para: {campo} (clave buscada: {campo_key})")
        return None
        
    def register_weighing(self, db_manager, weighing_type, id_folio_selected):
        """Registrar un pesaje (entrada, salida o salida c/peso)"""
        self.logger.info(f"📝 Iniciando registro de pesaje")
        
        if not self._validate_required_fields():
            self.logger.error("❌ Registro fallido - Campos obligatorios incompletos")
            return None, None
        
        datos = self._get_form_data(weighing_type)

        customer_discount = datos['customer_discount'] 
        material_spd = datos['material_spd']
        
        self.logger.info(f"📊 Datos procesados - Cliente: {datos['customer_name']}, Material: {datos['material_name']}, ID del folio: {id_folio_selected}")     
        
        if id_folio_selected is None:
            self.logger.info(f"📊 Datos procesados - Descuento: {customer_discount}, se puede descontar material: {material_spd}, ID del folio: {id_folio_selected}")
            if customer_discount > 0 and material_spd == 1:
                self.logger.info("🔔 Aplicando descuento ALM2")
                new_datos, weighing_data_alm2 = self._create_weighing_input_alm2_manual(datos, weighing_type)
                db_manager.save_manual_weighing_record(weighing_data_alm2)
                datos = new_datos
                weighing_data = self._create_weighing_manual(datos, weighing_type)
            
            else:
                weighing_data = self._create_weighing_manual(datos, weighing_type)
            
            self.logger.info(f"💾 Guardando registro en base de datos - Folio: {datos['folio']}")
            exito, siguiente_folio = db_manager.save_manual_weighing_record(weighing_data)
            
            if exito and siguiente_folio:
                # Actualizar el campo folio en la UI con el siguiente folio
                if 'folio' in self.ui_references:
                    folio_entry = self.ui_references['folio']
                    if hasattr(folio_entry, 'delete') and hasattr(folio_entry, 'insert'):
                        folio_entry.delete(0, 'end')
                        folio_entry.insert(0, siguiente_folio)
                        self.logger.info(f"✅ Folio actualizado a: {siguiente_folio}")
                else:
                    self.logger.warning("⚠️ No se pudo actualizar folio en UI")
            else:
                self.logger.error("❌ Error al guardar registro en base de datos")
        
            return exito, weighing_data
        else:
            exito, weighing_update_data = self._update_manual_weighing(datos, db_manager, id_folio_selected)
            return exito, weighing_update_data

    def _round_to_5_kg(self, weight):
        """Redondear peso a múltiplo de 5 kg"""
        if weight is None: 
            self.logger.debug("⚠️ Peso None, retornando 0")
            return 0
            
        rounded = int(round(weight / 5.0) * 5.0)
        #self.logger.debug(f"🔢 Redondeo: {weight} -> {rounded}")
        return rounded
    
    def _create_weighing_input_alm2_manual(self, datos, weighing_type):
        """Crear objeto de pesaje para entrada (peso bruto) al ALM2""" 
        self.logger.info("🔄 Creando pesaje ALM2 con descuento")

        gross_weight = int(datos['gross_weight'])
        tare_weight = int(datos['tare_weight'])
        net_weight = int(datos['net_weight'])
        
        discount_alm2 = int(datos['customer_discount'])
        
        porsentage_dicount = (discount_alm2 / 100)
        weight_with_discount = (net_weight * porsentage_dicount)
        weight_minus_discount = (net_weight - weight_with_discount)

        new_net_weight_round_original = self._round_to_5_kg(weight_minus_discount)
        net_weight_folio_alm2 = net_weight - new_net_weight_round_original

        new_gross_weight = tare_weight + new_net_weight_round_original
        new_gross_weight_alm2 = tare_weight + net_weight_folio_alm2
        
        self.logger.debug(f"🧮 Cálculos ALM2 - Original: {net_weight}, Con descuento: {new_net_weight_round_original}, ALM2: {net_weight_folio_alm2}")
        folio_ALM2 = f"{datos['folio']}A"
        new_datos = {
            'folio': datos['folio'],
            'start_date': datos['start_date'],
            'end_date': datos['end_date'],
            'weighing_type': datos['weighing_type'],
            'gross_weight': new_gross_weight,
            'tare_weight': tare_weight,
            'net_weight': new_net_weight_round_original,
            'vehicle_id': datos['vehicle_id'],
            'trailer_id': datos['trailer_id'],
            'driver_id': datos['driver_id'],
            'customer_id': datos['customer_id'],
            'customer_discount': datos['customer_discount'],
            'customer_id_alm2': datos['customer_id_alm2'],
            'material_id': datos['material_id'],
            'id_usuario': self.user_id, 
            'notes': datos['notes'],
            'weight_original': gross_weight,
            'material_spd': datos['material_spd'],
            'folio_ALM2': folio_ALM2
        }

        weighing_data_alm2 = DataManualWeighing(
            folio=folio_ALM2,
            date_start=datos['start_date'],
            date_end=datos['end_date'],
            gross_weight= new_gross_weight_alm2,
            tare_weight=tare_weight,
            net_weight=net_weight_folio_alm2,
            id_changes=0,
            notes=datos['notes'],
            weight_original=gross_weight,
            id_customer=datos['customer_id_alm2'],
            id_alm2=datos['customer_id_alm2'],
            id_alm2_discont=datos['customer_discount'],
            id_vehicle=datos['vehicle_id'],
            id_trailer=datos['trailer_id'],
            id_driver=datos['driver_id'],
            id_material=datos['material_id'],
            id_usuario=self.user_id,
            weighing_type=weighing_type,
            scale_record_status="Cerrado",
            saved_in_Odoo=0,
            folio_ALM2=folio_ALM2
        )
        
        self.logger.info(f"✅ Pesaje ALM2 creado - Folio: {weighing_data_alm2.folio}")
        return new_datos, weighing_data_alm2
    
    def _create_weighing_manual(self, datos, weighing_type):
        """Crear objeto de pesaje para entrada (peso bruto)"""
        folio_ALM2_datos = datos.get('folio_alm2') if 'folio_alm2' in datos else None       
        self.logger.info(f"🔄 Creando pesaje de entrada valor en ALM2--{folio_ALM2_datos}")

        
        weighing_data = DataManualWeighing(
            folio=datos['folio'],
            date_start=datos['start_date'],
            date_end=datos['end_date'],
            gross_weight=datos['gross_weight'],
            tare_weight=datos['tare_weight'],
            net_weight=datos['net_weight'],
            id_changes=0,
            notes=datos['notes'],
            weight_original=datos['weight_original'],
            id_customer=datos['customer_id'],
            id_alm2=datos['customer_id_alm2'],
            id_alm2_discont=datos['customer_discount'],
            id_vehicle=datos['vehicle_id'],
            id_trailer=datos['trailer_id'],
            id_driver=datos['driver_id'],
            id_material=datos['material_id'],
            id_usuario=self.user_id,
            weighing_type=weighing_type,
            scale_record_status="Cerrado",
            folio_ALM2=datos['folio_ALM2'],
            saved_in_Odoo=0
        )
        
        self.logger.info(f"✅ Pesaje entrada creado - Folio: {weighing_data.folio}, Peso: {weighing_data.gross_weight},ALM2--{weighing_data.folio_ALM2}")
        return weighing_data
    
    
    def _update_manual_weighing(self, datos, db_manager, id_folio_selected):
        """Registrar pesaje cerrado"""
        folio_ALM2_datos = datos.get('folio_alm2') if 'folio_alm2' in datos else None       
        self.logger.info(f"🔒 Actualizando manualmente - ID: {datos.get('id_weighing')}, Tipo: {datos.get('weighing_type')}, Valor del ALM2--{folio_ALM2_datos}")
        
        exito = False
        weighing_type = datos.get('weighing_type')  
        current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
        weighing_update_data = DataManualWeighing(
            id_weighing=id_folio_selected,
            folio=datos['folio'],
            date_start=datos['start_date'],
            date_end=datos['end_date'],
            gross_weight=datos['gross_weight'],
            tare_weight=datos['tare_weight'],
            net_weight=datos['net_weight'],
            id_changes=0,
            notes=datos['notes'],
            weight_original=datos['gross_weight'],
            id_customer=datos['customer_id'],
            id_alm2=datos['customer_id_alm2'],
            id_alm2_discont=datos['customer_discount'],
            id_vehicle=datos['vehicle_id'],
            id_trailer=datos['trailer_id'],
            id_driver=datos['driver_id'],
            id_material=datos['material_id'],
            id_usuario=datos['id_usuario'],
            weighing_type=weighing_type,
            scale_record_status="Cerrado",
            saved_in_Odoo=0,
            folio_ALM2=datos['folio_ALM2']
        )
        
        self.logger.info(f"💾 Guardando cierre entrada - Folio: {weighing_update_data.folio}, ALM2--{weighing_update_data.folio_ALM2}")
        result = db_manager.update_weighing_manual(weighing_update_data)
        self.logger.info(f"✅ Cierre entrada completado: {result}")  
        exito = result['exito']
        updated_row = result['updated_row']

        print(f"Exito: {exito}")
        print(f"Updated row: {updated_row}")

        return exito, weighing_update_data
