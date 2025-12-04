# logic_scale_reader.py

import serial
import threading
import time
import re
from datetime import datetime
from db_operations.db_config import get_company_config
from utils.logger_config import app_logger, scale_logger

class ScaleReader:
    def __init__(self, port='COM4', baudrate=9600, update_callback=None):       
        self.logger = app_logger.getChild('ScaleReader')
        #self.scale_logger = scale_logger
        COMPANY_DATA = get_company_config()
        company_port = COMPANY_DATA.get('company_port_scale')

        if company_port:
            port = company_port 

        self.logger.info(f"🚀 Inicializando ScaleReader en puerto: {port}, baudrate: {baudrate}")
        
        self.port = port
        self.baudrate = baudrate
        self.update_callback = update_callback
        self.serial_conn = None
        self.reading = False
        self.current_weight = "0"
        self.current_unit = "kg"
        self.thread = None
        self.last_raw_data = ""
        self.bytes_received = 0
        self.read_attempts = 0
        self.consecutive_errors = 0
        self.max_consecutive_errors = 3
        
    def _update_display_with_error(self, error_message, error_type="error"):
        """Actualizar la pantalla con mensaje de error"""
        display_text = f"0 {error_type}"
        color = "red"
        
        self.logger.warning(f"Mostrando error en display: {error_message}")
        
        if self.update_callback:
            try:
                self.update_callback(display_text, color)
            except Exception as callback_error:
                self.logger.error(f"Error en callback de actualización: {callback_error}")
    
    def _update_display_with_weight(self, weight, unit="kg"):
        """Actualizar la pantalla con peso válido"""
        display_text = f"{weight} {unit}"
        color = "green"
        
        self.logger.debug(f"Actualizando display con peso: {display_text}")
        
        if self.update_callback:
            try:
                self.update_callback(display_text, color)
            except Exception as callback_error:
                self.logger.error(f"Error en callback de actualización: {callback_error}")
    
    def connect(self):
        """Establecer conexión con la báscula"""
        self.logger.info(f"🔧 Intentando conectar a {self.port} con baudrate {self.baudrate}")
        
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1,
                write_timeout=1
            )
            
            # Esperar a que la conexión se estabilice
            time.sleep(2)
            
            if self.serial_conn.is_open:
                self.logger.info(f"✅ Conectado a báscula en {self.port}")
                self.logger.info(f"📊 Configuración: {self.baudrate} baud, 8N1")
                self.consecutive_errors = 0  # Resetear contador de errores
                return True
            else:
                error_msg = f"❌ Puerto {self.port} no se pudo abrir"
                self.logger.error(error_msg)
                self._update_display_with_error("No Conect")
                return False
                
        except serial.SerialException as e:
            error_msg = f"❌ Error de serial: {e}"
            self.logger.error(error_msg)
            self._update_display_with_error("Err COM")
            return False
        except Exception as e:
            error_msg = f"❌ Error inesperado en conexión: {e}"
            self.logger.error(error_msg)
            self._update_display_with_error("Err Con")
            return False
    
    def start_reading(self):
        """Iniciar la lectura continua de peso"""
        self.logger.info("🔃 Iniciando lectura de báscula")
        
        if not self.serial_conn or not self.serial_conn.is_open:
            self.logger.warning("🔄 Conexión no establecida, intentando reconectar...")
            if not self.connect():
                self.logger.error("❌ No se pudo conectar a la báscula")
                self._update_display_with_error("No Conect")
                return False
        
        self.reading = True
        self.thread = threading.Thread(target=self._read_loop, name="ScaleReaderThread")
        self.thread.daemon = True
        self.thread.start()
        self.logger.info("✅ Lectura de báscula iniciada")
        return True
    
    def stop_reading(self):
        """Detener la lectura"""
        display_text = "0 desc"
        self.logger.info("⏹️ Deteniendo lectura de báscula...")
        self.reading = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.update_callback(display_text, "red")
            self.logger.info("✅ Conexión serial cerrada")
        self.logger.info("✅ Lectura de báscula detenida")
    
    def _read_loop(self):
        """Loop principal de lectura - VERSIÓN MEJORADA"""
        self.logger.info(f"🔄 Iniciando loop de lectura en puerto {self.port}")
        buffer = ""  # Buffer para datos incompletos
        
        while self.reading:
            try:
                if not self.serial_conn or not self.serial_conn.is_open:
                    self.logger.warning("⚠️ Conexión perdida, intentando reconectar...")
                    if not self.connect():
                        self._update_display_with_error("No Conect")
                        time.sleep(2)
                        continue
                
                # Leer todos los datos disponibles
                if self.serial_conn.in_waiting > 0:
                    raw_data = self.serial_conn.read(self.serial_conn.in_waiting)
                    self.bytes_received += len(raw_data)
                    self.read_attempts += 1
                    
                    try:
                        # Decodificar y agregar al buffer
                        new_data = raw_data.decode('utf-8', errors='ignore')
                        buffer += new_data
                        
                        # Procesar líneas completas (separadas por \r o \n)
                        lines = buffer.split('\r')
                        if len(lines) > 1:
                            # Mantener última línea incompleta en buffer
                            buffer = lines[-1]
                            
                            # Procesar líneas completas
                            for line in lines[:-1]:
                                line = line.replace('\n', '').strip()
                                if line and len(line) > 3:  # Ignorar líneas muy cortas
                                    self._process_scale_data(line)
                        
                        self.logger.debug(f"📥 Buffer actual: '{buffer}' - Bytes recibidos: {self.bytes_received}")
                        
                    except UnicodeDecodeError as ude:
                        self.logger.warning(f"📥 Datos binarios recibidos: {raw_data.hex()}")
                        self._update_display_with_error("Err Dat")
                
                time.sleep(3)  # Reducir frecuencia de lectura
                    
            except Exception as e:
                error_msg = f"❌ Error en loop de lectura: {e}"
                self.logger.error(error_msg)
                self.consecutive_errors += 1
                
                if self.consecutive_errors >= self.max_consecutive_errors:
                    self.logger.error("🔴 Múltiples errores consecutivos, mostrando error en display")
                    self._update_display_with_error("Err Sis")
                
                time.sleep(1)

    def _process_scale_data(self, data):
        """Procesar datos recibidos de la báscula - VERSIÓN MEJORADA CON DETECCIÓN DE NEGATIVOS"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.last_raw_data = data
        
        #self.logger.debug(f"[{timestamp}] 📟 Datos crudos: '{data}'")
        
        # LIMPIEZA DE DATOS - más agresiva
        # Remover espacios extra y caracteres no deseados
        cleaned_data = re.sub(r'\s+', ' ', data.strip())  # Normalizar espacios
        cleaned_data = re.sub(r'[^a-zA-Z0-9\s\-+]', '', cleaned_data)  # Permitir signos negativo/positivo
        
        self.logger.debug(f"[{timestamp}] 🧹 Datos limpios: '{cleaned_data}'")
        
        # Buscar el patrón de peso más reciente (último número en los datos)
        weight_patterns = [
            r'([-+]?\d+)\s*KG',           # 65 KG o -65 KG
            r'([-+]?\d+)\s*KGS',          # 65 KGS o -65 KGS  
            r'([-+]?\d+)\s*KILO',         # 65 KILO o -65 KILO
            r'([-+]?\d+)\s*G',            # 65 G (asumimos kg) o -65 G
            r'\b([-+]?\d+)\b',            # Solo número con posible signo
        ]
        
        for pattern in weight_patterns:
            matches = re.findall(pattern, cleaned_data, re.IGNORECASE)
            if matches:
                # Tomar el ÚLTIMO peso encontrado (más reciente)
                last_weight = matches[-1]
                try:
                    weight_int = int(last_weight)
                    
                    # 🔴 DETECCIÓN DE PESO NEGATIVO
                    if weight_int < 0:
                        error_msg = f"🚫 Peso negativo detectado: {weight_int} kg"
                        self.logger.error(error_msg)
                        self._update_display_with_error("Err Neg", "red")
                        self.consecutive_errors += 1
                        return
                    
                    # ✅ PESO VÁLIDO (positivo o cero)
                    self.consecutive_errors = 0  # Resetear contador de errores
                    
                    # FILTRO: Redondear a múltiplo de 5
                    weight_rounded = self._round_to_5_kg(weight_int)
                    
                    # FILTRO: Evitar fluctuaciones rápidas
                    current_display_weight = int(self.current_weight) if self.current_weight.isdigit() else 0
                    weight_diff = abs(weight_rounded - current_display_weight)
                    
                    # Solo actualizar si hay cambio significativo (más de 5kg diferencia)
                    if weight_diff >= 5:
                        weight_rounded_str = str(weight_rounded)
                        
                        # Actualizar estado
                        self.current_weight = weight_rounded_str
                        self.current_unit = "kg"
                        
                        # Llamar al callback
                        self.logger.info(f"[{timestamp}] ✅ Peso estable: {weight_rounded_str} kg")
                        self._update_display_with_weight(weight_rounded_str, "kg")
                    else:
                        self.logger.debug(f"🔍 Cambio pequeño ignorado: {weight_rounded} kg (diff: {weight_diff})")
                        
                    return
                    
                except ValueError as ve:
                    error_msg = f"❌ Error convirtiendo peso '{last_weight}': {ve}"
                    self.logger.error(error_msg)
                    self._update_display_with_error("Err Val")
                    continue
        
        # Si llegamos aquí, no se pudo extraer un peso válido
        error_msg = f"❌ No se pudo extraer peso válido de: '{data}'"
        self.logger.warning(error_msg)
        self._update_display_with_error("Err For")

    def _round_to_5_kg(self, weight):
        """Redondea un peso al múltiplo de 5 kg más cercano - VERSIÓN MEJORADA"""
        if weight is None or weight < 0:
            return 0
        
        # Para pesos pequeños, no redondear tan agresivamente
        if weight <= 20:
            return weight
        
        # Para pesos mayores, redondear a múltiplo de 5
        return int(round(weight / 5.0) * 5.0)
    
    def _parse_weight_data(self, data):
        """Parsear datos de peso con múltiples patrones"""
        self.logger.debug(f"🔍 Analizando datos: '{data}'")
        
        try:
            # Patrón 1: Número con unidades ej: "150 kg"
            pattern1 = r'([-+]?\d+)\s*([a-zA-Z]*)'
            match1 = re.search(pattern1, data)
            if match1:
                weight_int = int(match1.group(1))
                unit = match1.group(2).strip().lower() if match1.group(2) else "kg"
                normalized_unit = self._normalize_unit(unit)
                self.logger.debug(f"✅ Parseado (patrón 1): {weight_int} {normalized_unit}")
                return weight_int, normalized_unit
            
            # Patrón 2: Solo número ej: "150"
            pattern2 = r'([-+]?\d+)'
            match2 = re.search(pattern2, data)
            if match2:
                weight_int = int(match2.group(1))
                self.logger.debug(f"✅ Parseado (patrón 2): {weight_int} kg")
                return weight_int, "kg"
            
            # Patrón 3: Datos con caracteres especiales
            pattern3 = r'[^\d]*(\d+)[^\d]*'
            match3 = re.search(pattern3, data)
            if match3:
                weight_int = int(match3.group(1))
                self.logger.debug(f"✅ Parseado (patrón 3): {weight_int} kg")
                return weight_int, "kg"
                
        except ValueError as ve:
            self.logger.error(f"❌ Error de valor parseando datos: {ve}")
        except Exception as e:
            self.logger.error(f"❌ Error parseando datos: {e}")
        
        return None
    
    def _normalize_unit(self, unit):
        """Normalizar las unidades a formato estándar"""
        unit = unit.lower().strip()
        
        unit_mapping = {
            'kg': 'kg', 'kgs': 'kg', 'kilogramo': 'kg', 'kilogramos': 'kg',
            'lb': 'lb', 'lbs': 'lb', 'libra': 'lb', 'libras': 'lb',
            'g': 'g', 'gr': 'g', 'gramo': 'g', 'gramos': 'g',
            'tn': 't', 'ton': 't', 'tonelada': 't', 'toneladas': 't',
            '': 'kg'  # Unidad vacía por defecto kg
        }
        
        return unit_mapping.get(unit, unit)
    
    def send_test_command(self):
        """Enviar comando de prueba a la báscula"""
        self.logger.info("📤 Enviando comandos de prueba a la báscula")
        
        try:
            if self.serial_conn and self.serial_conn.is_open:
                # Comando común para solicitar peso (depende del modelo de báscula)
                test_commands = [
                    b'P',           # Comando simple
                    b'\r',          # Enter
                    b'\n',          # Nueva línea
                    b'?',           # Interrogación
                    b'WEIGHT\r\n',  # Comando weight
                ]
                
                for cmd in test_commands:
                    self.logger.debug(f"📤 Enviando comando: {cmd}")
                    self.serial_conn.write(cmd)
                    self.serial_conn.flush()
                    time.sleep(0.5)
                    
        except Exception as e:
            error_msg = f"❌ Error enviando comando de prueba: {e}"
            self.logger.error(error_msg)
    
    def get_current_weight(self):
        """Obtener el peso actual con unidad"""
        return f"{self.current_weight} {self.current_unit}"
    
    def get_weight_data(self):
        """Obtener peso y unidad por separado"""
        try:
            weight_value = float(self.current_weight) if self.current_weight and self.current_weight != "" else 0
        except ValueError:
            weight_value = 0
            
        return {
            'weight': weight_value,
            'unit': self.current_unit,
            'display_text': f"{self.current_weight} {self.current_unit}",
            'raw_data': self.last_raw_data
        }

    def get_debug_info(self):
        """Información de debug"""
        return {
            'port': self.port,
            'baudrate': self.baudrate,
            'reading': self.reading,
            'connected': self.serial_conn.is_open if self.serial_conn else False,
            'bytes_received': self.bytes_received,
            'read_attempts': self.read_attempts,
            'last_raw_data': self.last_raw_data,
            'current_weight': self.current_weight,
            'current_unit': self.current_unit,
            'has_callback': self.update_callback is not None,
            'consecutive_errors': self.consecutive_errors
        }


# Simulador mejorado con unidades (SIN CAMBIOS EN EL SIMULADOR)
class ScaleSimulator:
    def __init__(self, update_callback=None):
        self.update_callback = update_callback
        self.reading = False
        self.current_weight = "0"
        self.current_unit = "kg"
        self.thread = None
        self.simulated_weight = 23550  # Peso inicial más realista
        self.units = ['kg']
        self.current_unit_index = 0
        self.iteration_count = 0
        
    def connect(self):
        print("Simulador de báscula iniciado")
        return True
    
    def start_reading(self):
        self.reading = True
        self.thread = threading.Thread(target=self._simulate_loop)
        self.thread.daemon = True
        self.thread.start()
        print("Simulador de báscula: lectura iniciada")
        return True
    
    def stop_reading(self):
        self.reading = False
        if self.thread:
            self.thread.join(timeout=1)
        self.update_callback("0 desc", "red")
        print("Simulador de báscula: lectura detenida")
    
    def _simulate_loop(self):
        """Simular cambios de peso para testing"""
        import random
        
        print("Simulador de báscula: loop de simulación iniciado")
        
        while self.reading:
            try:
                self.iteration_count += 1
                
                # Simular pequeñas variaciones de peso
                variation = random.uniform(-10, 10)
                self.simulated_weight = max(500, self.simulated_weight + variation)  # Mínimo 500 kg
                
                # Formatear peso según la unidad
                def round_to_5_kg(weight):
                    if weight is None: return 0
                    return int(round(weight / 5.0) * 5.0) 

                # Valor base redondeado a 5 kg y como INT
                weight_int_rounded = round_to_5_kg(self.simulated_weight)
                
                # Formatear peso según la unidad (usando el valor redondeado INT)
                
                if self.units[self.current_unit_index] == 'lb':
                    # Si se convierte a otras unidades, aún se pueden introducir decimales.
                    formatted_weight = f"{weight_int_rounded * 2.20462:.0f}" 
                elif self.units[self.current_unit_index] == 't':
                    # Si se convierte a toneladas, no se puede garantizar que sea un entero.
                    formatted_weight = f"{weight_int_rounded / 1000:.0f}"
                else:  # kg
                    # En kg, usamos el entero directo
                    formatted_weight = str(weight_int_rounded)
                
                self.current_weight = formatted_weight
                self.current_unit = self.units[self.current_unit_index]
                
                #print(f"Simulador: {self.current_weight} {self.current_unit} (iteración {self.iteration_count})")
                
                if self.update_callback:
                    display_text = f"{self.current_weight} {self.current_unit}"
                    self.update_callback(display_text, "green")
                
                time.sleep(2)  # Actualizar cada 1 segundo (más lento para debugging)
                
            except Exception as e:
                print(f"Error en simulador: {e}")
                time.sleep(1)
    
    def get_current_weight(self):
        return f"{self.current_weight} {self.current_unit}"
    
    def get_weight_data(self):
        try:
            weight_value = self.current_weight if self.current_weight != "" else 0
        except ValueError:
            weight_value = 0
            
        return {
            'weight': weight_value,
            'unit': self.current_unit,
            'display_text': f"{self.current_weight} {self.current_unit}"
        }

# Factory para seleccionar reader real o simulado
def create_scale_reader(use_simulator=False, **kwargs):
    print(f"🔧 create_scale_reader: use_simulator = {use_simulator}")

    global current_use_simulator
    current_use_simulator = use_simulator

    if use_simulator:
        return ScaleSimulator(**kwargs)
    else:
        return ScaleReader(**kwargs)