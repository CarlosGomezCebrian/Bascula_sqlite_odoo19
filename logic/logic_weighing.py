#   

import datetime
from dataclasses import dataclass
from typing import Optional
import tkinter as tk
from utils.logger_config import app_logger

@dataclass
class DataWeighing:
    """Clase para almacenar los datos del pesaje"""
    #id_weighing: int
    folio: str
    date_start: str
    gross_weight: int
    tare_weight: int
    date_end: str
    peso_neto: float
    id_changes: int
    notes: str
    id_customer: Optional[int]
    id_vehicle: Optional[int]
    id_trailer: Optional[int]
    id_driver: Optional[int]
    id_material: Optional[int]
    id_usuario: Optional[int]
    tipo_pesaje: str  # 'entrada' o 'salida'
    folio_ALM2: str = ""
    weight_original: Optional[int] = None
    id_alm2_discont: Optional[int] = None
    id_alm2: Optional[int] = None

class WeighingLogic:
    def __init__(self, user_id: int = None):
        # Inicializar logger
        
        self.logger = app_logger.getChild('WeighingLogic')
        self.logger.info(f"Inicializando WeighingLogic para usuario: {user_id}")
        
        self.user_id = user_id
        self.input_weighing = None
        self.output_weighing = None
        self.closing_weighing = None
        self.scale_manager = None
        self.ui_references = {}  # Referencias a los widgets de UI
        self.autocomplete_handler = None  # Referencia al autocomplete handler
        self.use_simulator_var = None  # Referencia al BooleanVar del checkbox
        self.use_simulator = False  # Valor por defecto

    def set_simulator_checkbox(self, simulator_var):
        """Establecer referencia al BooleanVar del checkbox"""
        self.logger.info("🔧 Configurando checkbox del simulador")
        self.use_simulator_var = simulator_var
        # Actualizar el valor inicial
        self.use_simulator = simulator_var.get()
        self.logger.info(f"✅ Checkbox conectado, valor = {self.use_simulator}")
    
    def update_use_simulator(self, value):
        """Actualizar el valor del simulador"""
        self.logger.info(f"🔄 Actualizando use_simulator a: {value}")
        self.use_simulator = value
        self.logger.debug(f"use_simulator actualizado = {self.use_simulator}")
    
    def _get_use_simulator(self):
        """Obtener el estado actual del simulador"""
        # Si tenemos referencia al checkbox, obtener el valor actual
        if self.use_simulator_var is not None:
            self.use_simulator = self.use_simulator_var.get()
        self.logger.debug(f"Estado del simulador obtenido: {self.use_simulator}")
        return self.use_simulator
      
    def set_scale_manager(self, scale_manager):
        """Inyectar el ScaleManager"""
        self.logger.info("🔧 Configurando ScaleManager")
        self.scale_manager = scale_manager
    
    def set_ui_references(self, ui_references):
        """Establecer referencias a los widgets de UI"""
        self.logger.info("🔧 Configurando referencias de UI")
        self.ui_references = ui_references
        self.logger.debug(f"Referencias de UI establecidas: {list(ui_references.keys())}")
    
    def set_autocomplete_handler(self, autocomplete_handler):
        """Establecer referencia al autocomplete handler"""
        self.logger.info("🔧 Configurando autocomplete handler")
        self.autocomplete_handler = autocomplete_handler
    
    def _get_form_data(self, tipo_pesaje):
        """Obtener datos reales del formulario"""
        self.logger.debug(f"📋 Obteniendo datos del formulario para {tipo_pesaje}")
        
        current_weight = self._get_current_weight()
        fecha_hora_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        
        datos = {
            'folio': folio,
            'weight': current_weight,
            'fecha_hora': fecha_hora_actual,
            'tipo_pesaje': tipo_pesaje,
            'vehicle_name': vehicle_name,
            'vehicle_id': vehicle_id,
            'trailer_name': trailer_name,
            'trailer_id': trailer_id,
            'driver_name': driver_name,
            'driver_id': driver_id,
            'customer_nombre': customer_name,
            'customer_id': customer_id,
            'customer_discount': customer_discount,
            'customer_id_alm2': customer_id_alm2,
            'material_name': material_name,
            'material_id': material_id,
            'id_usuario': self.user_id, 
            'notes': notes,
            'folio_alm2': "",
            'weight_original': None,
            'material_spd': material_spd
        }
        
        self.logger.debug(f"📦 Datos del formulario obtenidos: {datos}")
        return datos
    
    def _get_current_weight(self):
        """Obtener el peso actual del label (no directamente de la báscula)"""
        self.logger.debug("⚖️ Obteniendo peso actual del label")
        
        if 'weight_label' in self.ui_references:
            weight_label = self.ui_references['weight_label']
            if hasattr(weight_label, 'cget'):
                weight_text = weight_label.cget('text')
                # Extraer el número del texto "0.00 kg"
                try:
                    # Remover "kg" y espacios, luego convertir a float
                    weight_str = weight_text.replace('kg', '').strip()
                    weight_value = int(weight_str)
                    self.logger.debug(f"✅ Peso obtenido del label: {weight_value}")
                    return weight_value
                except (ValueError, AttributeError) as e:
                    self.logger.warning(f"⚠️ Error obteniendo peso del label: {e}")
                    return 0
        self.logger.warning("⚠️ No se pudo obtener peso del label")
        return 0
    
    def _validate_required_fields(self, tipo_pesaje):
        """Validar campos obligatorios (solo lógica, sin UI)"""
        self.logger.debug(f"🔍 Validando campos obligatorios para {tipo_pesaje}")
        
        campos_obligatorios = ['vehicle', 'trailer', 'driver', 'customer', 'material']
        
        for campo in campos_obligatorios:
            valor = self._get_value_entry(campo)
            if not valor:
                self.logger.warning(f"❌ Campo obligatorio vacío: {campo}")
                return False
        
        self.logger.debug("✅ Todos los campos obligatorios están completos")
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
        
        if campo in self.ui_references:
            entry = self.ui_references[campo]
            if isinstance(entry, tk.Text):
                # Obtener todo el contenido excepto el salto de línea final
                value = entry.get('1.0', tk.END).strip()
                import re
                value = re.sub(r'\n{3,}', '\n\n', value)
                self.logger.debug(f"✅ Valor obtenido (Text): {value}")
                return value
            
            elif hasattr(entry, 'get'):
                value = entry.get().strip()
                self.logger.debug(f"✅ Valor obtenido (Entry): {value}")
                return value
                
        self.logger.warning(f"⚠️ Campo no encontrado en UI references: {campo}")
        return ""
    
    def _get_id_mapped(self, campo):
        """Obtener el id mapeado de un campo autocomplete"""
        self.logger.debug(f"🆔 Obteniendo ID mapeado para: {campo}")
        
        if campo in self.ui_references:
            entry = self.ui_references[campo]
            if hasattr(entry, 'get_mapped_value'):
                mapped_value = entry.get_mapped_value()
                self.logger.debug(f"✅ ID mapeado obtenido: {mapped_value}")
                return mapped_value if mapped_value else None
                
        self.logger.warning(f"⚠️ No se pudo obtener ID mapeado para: {campo}")
        return None
    
    def calculate_net_weight(self, gross_weight, tare_weight):
        """Calcular el peso neto"""
        net_weight = max(0, gross_weight - tare_weight)
        self.logger.debug(f"🧮 Cálculo neto: {gross_weight} - {tare_weight} = {net_weight}")
        return net_weight
    
    def register_weighing(self, tipo_pesaje, db_manager):
        """Registrar un pesaje (entrada, salida o salida c/peso)"""
        self.logger.info(f"📝 Iniciando registro de pesaje: {tipo_pesaje}")
        
        
        if not self._validate_required_fields(tipo_pesaje):
            self.logger.error("❌ Registro fallido - Campos obligatorios incompletos")
            return None, None
        
        datos = self._get_form_data(tipo_pesaje)
        customer_discount = datos['customer_discount'] 
        material_spd = datos['material_spd']
        
        self.logger.info(f"📊 Datos procesados - Cliente: {datos['customer_nombre']}, Material: {datos['material_name']}, Peso: {datos['weight']}")
        
        if tipo_pesaje == 'Entrada':
            weighing_type = tipo_pesaje
            self.input_weighing = datos
            if customer_discount > 0 and material_spd == 1:
                self.logger.info("🔔 Aplicando descuento ALM2")
                new_datos, weighing_data_alm2 = self._create_weighing_input_alm2(datos, weighing_type)
                db_manager.save_weighing_record(weighing_data_alm2)
                datos = new_datos

            weighing_data = self._create_weighing_input(datos, weighing_type)
        elif tipo_pesaje == 'Salida':
            weighing_type = tipo_pesaje
            self.output_weighing = datos
            weighing_data = self._create_weighing_output(datos, weighing_type)
        else:
            weighing_type = tipo_pesaje
            weighing_data = self._create_weighing_input(datos, weighing_type)
        
        self.logger.info(f"💾 Guardando registro en base de datos - Folio: {datos['folio']}")
        exito, siguiente_folio = db_manager.save_weighing_record(weighing_data)
        
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
        
    def _round_to_5_kg(self, weight):
        """Redondear peso a múltiplo de 5 kg"""
        if weight is None: 
            self.logger.debug("⚠️ Peso None, retornando 0")
            return 0
            
        rounded = int(round(weight / 5.0) * 5.0)
        self.logger.debug(f"🔢 Redondeo: {weight} -> {rounded}")
        return rounded
    
    def _create_weighing_input_alm2(self, datos, weighing_type):
        """Crear objeto de pesaje para entrada (peso bruto) al ALM2""" 
        self.logger.info("🔄 Creando pesaje ALM2 con descuento")
        
        discount_alm2 = int(datos['customer_discount'])
        weight = int(datos['weight'])
        porsentage_dicount = (discount_alm2 / 100)
        weight_with_discount = (weight * porsentage_dicount)
        weight_minus_discount = (weight - weight_with_discount)

        weight_round_original = self._round_to_5_kg(weight_minus_discount)
        weight_alm2_folio = weight - weight_round_original
        
        self.logger.debug(f"🧮 Cálculos ALM2 - Original: {weight}, Con descuento: {weight_round_original}, ALM2: {weight_alm2_folio}")
        
        new_datos = {
            'folio': datos['folio'],
            'weight': weight_round_original,
            'fecha_hora': datos['fecha_hora'],
            'tipo_pesaje': weighing_type,
            'vehicle_id': datos['vehicle_id'],
            'trailer_id': datos['trailer_id'],
            'driver_id': datos['driver_id'],
            'customer_id': datos['customer_id'],
            'customer_discount': datos['customer_discount'],
            'folio_alm2': (f"{datos['folio']}A"),
            'material_id': datos['material_id'],
            'id_usuario': self.user_id, 
            'notes': datos['notes'],
            'weight_original': datos['weight']
        }

        weighing_data_alm2 = DataWeighing(
            folio=(f"{datos['folio']}A"),
            date_start=datos['fecha_hora'],
            gross_weight=weight_alm2_folio,
            tare_weight=0,
            date_end="",
            peso_neto=0,
            id_changes=0,
            notes=datos['notes'],
            weight_original=datos['weight'],
            id_customer=datos['customer_id_alm2'],
            id_alm2=datos['customer_id_alm2'],
            id_alm2_discont=datos['customer_discount'],
            id_vehicle=datos['vehicle_id'],
            id_trailer=datos['trailer_id'],
            id_driver=datos['driver_id'],
            id_material=datos['material_id'],
            id_usuario=datos['id_usuario'],
            tipo_pesaje= weighing_type
        )
        
        self.logger.info(f"✅ Pesaje ALM2 creado - Folio: {weighing_data_alm2.folio}")
        return new_datos, weighing_data_alm2
    
    def _create_weighing_input(self, datos, weighing_type):
        """Crear objeto de pesaje para entrada (peso bruto)"""
        self.logger.info("🔄 Creando pesaje de entrada")

        folio_ALM2_datos = datos['folio_alm2'] if datos['folio_alm2'] else None       
        weight_original_datos = datos['weight_original'] if datos['weight_original'] else datos['weight']

        weighing_data = DataWeighing(
            folio=datos['folio'],
            date_start=datos['fecha_hora'],
            gross_weight=datos['weight'], 
            tare_weight=0,
            date_end="",  # Se calculará en la salida
            peso_neto=0,
            id_changes=0,
            notes=datos['notes'],
            weight_original=weight_original_datos,
            folio_ALM2=folio_ALM2_datos,
            id_customer=datos['customer_id'] or 0,
            id_vehicle=datos['vehicle_id'],
            id_trailer=datos['trailer_id'],
            id_driver=datos['driver_id'],
            id_material=datos['material_id'],
            id_usuario=datos['id_usuario'],
            tipo_pesaje=weighing_type
        )
        
        self.logger.info(f"✅ Pesaje entrada creado - Folio: {weighing_data.folio}, Peso: {weighing_data.gross_weight}")
        return weighing_data
    
    def _create_weighing_output(self, datos, weighing_type):
        """Crear objeto de pesaje para salida (peso tara)"""
        self.logger.info("🔄 Creando pesaje de salida")
        
        fecha_hora_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")               
        gross_weight = 0
        current_simulator_state = self._get_use_simulator()
        peso_descuento = datos['weight'] if current_simulator_state == False else datos['weight'] - 19000
        tare_weight = int(peso_descuento)
        peso_neto = self.calculate_net_weight(gross_weight, tare_weight)
        
        weighing_data = DataWeighing(
            folio=datos['folio'],
            date_start=fecha_hora_actual,
            gross_weight=gross_weight,
            tare_weight=tare_weight,
            date_end="",
            peso_neto=peso_neto,
            id_changes=0,
            id_customer=datos['customer_id'] or 0,
            id_alm2=datos['customer_id_alm2'],
            id_alm2_discont=datos['customer_discount'],
            id_vehicle=datos['vehicle_id'],
            id_trailer=datos['trailer_id'],
            id_driver=datos['driver_id'],
            id_material=datos['material_id'],
            id_usuario=datos['id_usuario'],
            notes=datos['notes'],
            tipo_pesaje=weighing_type
        )
        
        self.logger.info(f"✅ Pesaje {weighing_type} creado - Folio: {weighing_data.folio}, Tara: {weighing_data.tare_weight}")
        return weighing_data

    def calculate_weight_alm2(self, gross_weight, tare_weight, customer_name):
        """Calcular peso para ALM2 con descuento"""
        self.logger.info(f"🧮 Calculando peso ALM2 para cliente: {customer_name}")
        
        original_grooss_weight = int(gross_weight)
        original_tare_weight = int(tare_weight)
        original_net_weight = original_grooss_weight - original_tare_weight

        if self.autocomplete_handler:
            mappings = self.autocomplete_handler.mappings          
            customer_discount_map = mappings.get('customers_discount', {})
            customer_discount_alm2 = customer_discount_map.get(customer_name, 0)

            customer_discount = (100 - customer_discount_alm2)
            customer_discount_porcent = (customer_discount / 100)
            new_net_weight = original_net_weight * customer_discount_porcent
            new_net_weight_round = self._round_to_5_kg(new_net_weight)
            new_gross_weight = original_tare_weight + new_net_weight_round
            new_net_weight_ALM2 = original_net_weight - new_net_weight_round
            new_gross_weight_ALM2 = original_tare_weight + new_net_weight_ALM2
        
        result = {
            'new_gross_weight_ALM2': new_gross_weight_ALM2,
            'new_net_weight_ALM2': new_net_weight_ALM2,
            'new_gross_weight': new_gross_weight,
            'new_net_weight': new_net_weight_round,
        }
        
        self.logger.debug(f"📊 Resultados cálculo ALM2: {result}")
        return result
    
    def register_closed_weighing(self, data, id_user_closed, db_manager):
        """Registrar pesaje cerrado"""
        self.logger.info(f"🔒 Cerrando pesaje - ID: {data.get('id_weighing')}, Tipo: {data.get('weighing_type')}")
        
        exito = False
        weighing_type = data.get('weighing_type')    
        current_weight = self._get_current_weight()
        current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_simulator_state = self._get_use_simulator()

        if weighing_type == 'Entrada':
            folio_alm2_closed = data.get('folio_ALM2')
            if folio_alm2_closed is not None and str(folio_alm2_closed).upper() != 'NONE' and folio_alm2_closed != '':
                self.logger.info("🔔 Cerrando pesaje ALM2")
                
                gross_weight = int(data.get('weight_original'))
                customer_name = data.get('customer_name')
                tare_weight = int(current_weight) if current_simulator_state == False else int(current_weight) - 19000
                
                data_new_weight = self.calculate_weight_alm2(gross_weight, tare_weight, customer_name)

                new_gross_weight_ALM2 = data_new_weight['new_gross_weight_ALM2']
                new_net_weight_ALM2 = data_new_weight['new_net_weight_ALM2']
                new_gross_weight = data_new_weight['new_gross_weight']
                new_net_weight = data_new_weight['new_net_weight']
                
                weighing_closed_data_alm2 = {
                    'id_weighing': int(data.get('id_weighing')) - 1,
                    'folio_number': (f"{data.get('folio_number')}A"),
                    'gross_weight': new_gross_weight_ALM2,
                    'tare_weight': tare_weight,
                    'id_changes': 0,
                    'date_end': current_date_time,
                    'net_weight': new_net_weight_ALM2,
                    'scale_record_status': "Cerrado",
                    'id_user_closed': id_user_closed,
                    'notes': data.get('notes')
                }
                
                self.logger.info(f"💾 Guardando cierre ALM2 - Folio: {weighing_closed_data_alm2['folio_number']}")
                result = db_manager.close_weighing_input_alm2(weighing_closed_data_alm2)
                self.logger.info(f"✅ Respuesta BD ALM2: {result}, exito={result['exito']}")
                exito =  result['exito']
                if exito:
                    weighing_closed_data = {
                        'id_weighing': data.get('id_weighing'),
                        'folio_number': data.get('folio_number'),
                        'gross_weight': new_gross_weight,
                        'tare_weight': tare_weight,
                        'date_end': current_date_time,
                        'net_weight': new_net_weight,
                        'id_changes': 0,
                        'scale_record_status': "Cerrado",
                        'id_user_closed': id_user_closed,
                        'notes': data.get('notes')
                    }
                    self.logger.info(f"💾 Guardando cierre principal - Folio: {weighing_closed_data['folio_number']}")
                    result = db_manager.close_weighing_input_alm2(weighing_closed_data)
                    self.logger.info(f"✅ Cierre principal completado: {result}")
            else:
                self.logger.info("🔔 Cerrando pesaje entrada normal")
                gross_weight = data.get('gross_weight')
                tare_weight = int(current_weight) if current_simulator_state == False else int(current_weight) - 19000
                net_weight = self.calculate_net_weight(int(gross_weight), int(tare_weight))

                weighing_closed_data = {
                    'id_weighing': data.get('id_weighing'),
                    'folio_number': data.get('folio_number'),
                    'tare_weight': tare_weight,
                    'date_end': current_date_time,
                    'net_weight': net_weight,
                    'id_changes': 0,
                    'scale_record_status': "Cerrado",
                    'id_user_closed': id_user_closed,
                    'notes': data.get('notes')
                }
                self.logger.info(f"💾 Guardando cierre entrada - Folio: {weighing_closed_data['folio_number']}")
                result = db_manager.close_weighing_input(weighing_closed_data)
                self.logger.info(f"✅ Cierre entrada completado: {result}")
                
        elif weighing_type == 'Salida' :
            self.logger.info("🔔 Cerrando pesaje salida")
            #weighing_type == 'Salida'            
            gross_weight = int(current_weight)
            tare_weight = int(data.get('tare_weight'))
            net_weight = self.calculate_net_weight(gross_weight, tare_weight)

            weighing_closed_data = {
                'id_weighing': data.get('id_weighing'),
                'folio_number': data.get('folio_number'),
                'gross_weight': gross_weight,
                'date_end': current_date_time,
                'net_weight': net_weight,
                'id_changes': 0,
                'scale_record_status': "Cerrado",
                'id_user_closed': id_user_closed,
                'notes': data.get('notes')
            } 
            self.logger.info(f"💾 Guardando cierre salida - Folio: {weighing_closed_data['folio_number']}")
            result = db_manager.close_weighing_output(weighing_closed_data)
            self.logger.info(f"✅ Cierre salida completado: {result}")
        else:
                self.logger.info("🔔 Cerrando pesaje entrada normal")
                gross_weight = data.get('gross_weight')
                tare_weight = int(current_weight) if current_simulator_state == False else int(current_weight) - 19000
                net_weight = self.calculate_net_weight(int(gross_weight), int(tare_weight))

                weighing_closed_data = {
                    'id_weighing': data.get('id_weighing'),
                    'folio_number': data.get('folio_number'),
                    'tare_weight': tare_weight,
                    'date_end': current_date_time,
                    'net_weight': net_weight,
                    'id_changes': 0,
                    'scale_record_status': "Cerrado",
                    'id_user_closed': id_user_closed,
                    'notes': data.get('notes')
                }
                self.logger.info(f"💾 Guardando cierre entrada - Folio: {weighing_closed_data['folio_number']}")
                result = db_manager.close_weighing_input(weighing_closed_data)
                self.logger.info(f"✅ Cierre entrada completado: {result}")                                       
        return result