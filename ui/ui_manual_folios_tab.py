# ui_manual_folios_tab.py

import tkinter as tk
import datetime
from tkinter import ttk, messagebox  
from logic.logic_print_folios import print_weighing_ticket
from db_operations.db_save_folio import WeighingDBManager
from logic.logic_tables_all_folios import FoliosWeighingsTable
from logic.logic_weighing_manual import WeighingManualLogic
from utils.logger_config import app_logger

class ManualFoliosTab:
    def __init__(self, notebook, styles, autocomplete_handler=None, user_id=None, user_access_level=None):
        # Configurar logger para esta clase
        self.logger = app_logger.getChild('ManualFoliosTab')
        self.logger.info(f"Inicializando pestaña de foliod manuales para usuario ID: {user_id}, Nivel de acceso: {user_access_level}")
        
        self.styles = styles
        self.frame = ttk.Frame(notebook, style="TFrame")
        notebook.add(self.frame, text="Generar folio manual")
        self.user_id = user_id
        self.user_access_level = int(user_access_level)
        self.data_closed_weighing = None
        self.weight_status = False
        self.btn_status = True 
        self.search_folio_entry = None
        self._validate_number_cmd = None
        self.id_folio_selected = None 
        
        if autocomplete_handler:
            self.autocomplete_handler = autocomplete_handler
        else:
            from logic.logic_autocomplete import AutocompleteHandler
            self.autocomplete_handler = AutocompleteHandler()
        
        # Inicializar el manager de base de datos
        self.db_manager = WeighingDBManager()    
        self.weighing_manual_logic = WeighingManualLogic(user_id=user_id)    
        self._create_ui()
        self.table_all_folios = FoliosWeighingsTable(self.table_container,  self.search_folio_entry)
        self._setup_managers()
        self._update_date_title()        
        self.logger.info("Pestaña de folio manual inicializada correctamente")    
    
    def _create_ui(self):
        """Solo creación de widgets visuales"""
        self.logger.debug("Creando interfaz de usuario")
        
        # Obtener fecha actual para el título
        self.fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.date_label = ttk.Label(
            self.frame, 
            text=f"Fecha y Hora Actual: {self.fecha_actual}", 
            font=("bold"),
            style="TLabel"
        )
        # Empaquetar en la parte superior del frame principal
        self.date_label.pack(fill=tk.X, padx=5, pady=(5, 0)) 
        
        # CREAR FRAME CONTENEDOR PARA LOS DOS LABELFRAMES
        self.horizontal_container = ttk.Frame(self.frame, style="TFrame")
        self.horizontal_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.entrada_frame = ttk.LabelFrame(
            self.horizontal_container,  # ¡CAMBIAR: usar el contenedor horizontal!
            text="Registro de Pesaje",
            style="TFrame",
            padding=10
        )
        
        self.entrada_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.horizontal_container.columnconfigure(1, weight=1)
        self.horizontal_container.rowconfigure(0, weight=1)
        self._create_folio_section(self.entrada_frame)
                    
        # Vehículo
        ttk.Label(self.entrada_frame, text="Vehículo:", style="TLabel").grid(row=1, column=0, sticky=tk.W, padx=5, pady=10)
        self.vehicle_entry = self.autocomplete_handler.create_vehicle_entry_manual(self.entrada_frame)
        self.vehicle_entry.grid(row=1, column=1, padx=5, pady=10, sticky='ew')        
        
        # Remolque
        ttk.Label(self.entrada_frame, text="Remolque:", style="TLabel").grid(row=2, column=0, sticky=tk.W, padx=5, pady=10)
        self.trailer_entry = self.autocomplete_handler.create_trailer_entry_manual(self.entrada_frame)
        self.trailer_entry.grid(row=2, column=1, padx=5, pady=10, sticky='ew')
        
        # Chofer
        ttk.Label(self.entrada_frame, text="Chofer:", style="TLabel").grid(row=3, column=0, sticky=tk.W, padx=5, pady=10)
        self.driver_entry = self.autocomplete_handler.create_driver_entry_manual(self.entrada_frame)
        self.driver_entry.grid(row=3, column=1, padx=5, pady=10, sticky='ew')
        
        # Cliente
        ttk.Label(self.entrada_frame, text="Cliente:", style="TLabel").grid(row=4, column=0, sticky=tk.W, padx=5, pady=10)
        self.customer_entry = self.autocomplete_handler.create_customer_entry_manual(self.entrada_frame)
        self.customer_entry.grid(row=4, column=1, padx=5, pady=10, sticky='ew')
        
        # Material
        ttk.Label(self.entrada_frame, text="Material:", style="TLabel").grid(row=5, column=0, sticky=tk.W, padx=5, pady=10)
        self.material_entry = self.autocomplete_handler.create_material_entry_manual(self.entrada_frame)
        self.material_entry.grid(row=5, column=1, padx=5, pady=10, sticky='ew')
        
        # Campos simples notas
        ttk.Label(self.entrada_frame, text="Notas:\n(Datos externos)", style="TLabel").grid(row=6, column=0, sticky=tk.W, padx=5, pady=10)
        self.notes_entry_manual = tk.Text(self.entrada_frame, font=("Helvetica", 12), borderwidth=0, width=40, height=4)
        self.notes_entry_manual.grid(row=6, column=1, padx=5, pady=10)       
        
                
        # Botones de acción
        self._create_action_buttons()

        self._validate_number_cmd = (self.frame.register(self._validate_number), '%P')

        #Crear columna de datos de pesaje
        ttk.Label(self.entrada_frame, style="TLabel", text="Datos de pesaje").grid(row=0, column=3, padx=10, pady=10, sticky='ew')

        self.folio_label_weighing_type = ttk.Label(self.entrada_frame, style="TLabel", text="Tipo de pesaje")
        self.folio_label_weighing_type.grid(row=1, column=3, padx=10, pady=10, sticky='ew')

        self.folio_combo_weighing_type = ttk.Combobox(self.entrada_frame, values=["Entrada", "Salida", "Salida c/peso"], state="readonly")
        self.folio_combo_weighing_type.set("Entrada")
        self.folio_combo_weighing_type.grid(row=1, column=4, padx=5, pady=10, sticky='ew')
        
        self.folio_label_date_start = ttk.Label(self.entrada_frame, style="TLabel", text="Fecha inicio")
        self.folio_label_date_start.grid(row=2, column=3, padx=10, pady=10, sticky='ew')

        self.folio_entry_date_start = tk.Entry(self.entrada_frame,font=("Helvetica", 12), borderwidth=0)
        self.folio_entry_date_start.grid(row=2, column=4, padx=5, pady=10, sticky='ew')
        self.folio_entry_date_start.insert(0, self.fecha_actual)

        #Peso bruto
        self.folio_label_gross_weight = ttk.Label(self.entrada_frame, style="TLabel", text="Peso bruto")
        self.folio_label_gross_weight.grid(row=3, column=3, padx=10, pady=10, sticky='ew')

        self.folio_entry_gross_weight = tk.Entry(self.entrada_frame,font=("Helvetica", 12), borderwidth=0,state="readonly")
        self.folio_entry_gross_weight.grid(row=3, column=4, padx=5, pady=10, sticky='ew')

        #Peso tara
        self.folio_label_tare_weight = ttk.Label(self.entrada_frame, style="TLabel", text="Peso tara")
        self.folio_label_tare_weight.grid(row=4, column=3, padx=10, pady=10, sticky='ew')

        self.folio_entry_tare_weight = tk.Entry(
            self.entrada_frame,font=("Helvetica", 12),
            borderwidth=0,
            validate="key",
            validatecommand=self._validate_number_cmd)
        self.folio_entry_tare_weight.grid(row=4, column=4, padx=5, pady=10, sticky='ew')
        self.folio_entry_tare_weight.bind('<KeyRelease>', self._update_gross_weight)


        #Peso neto
        self.folio_label_net_weight = ttk.Label(self.entrada_frame, style="TLabel", text="Peso neto")
        self.folio_label_net_weight.grid(row=5, column=3, padx=10, pady=10, sticky='ew')

        self.folio_entry_net_weight = tk.Entry(
            self.entrada_frame,font=("Helvetica", 12),
            borderwidth=0,
            validate="key",
            validatecommand=self._validate_number_cmd)
        self.folio_entry_net_weight.grid(row=5, column=4, padx=5, pady=10, sticky='ew')
        self.folio_entry_net_weight.bind('<KeyRelease>', self._update_gross_weight)


        #crear tercera columna
        self.search_folio_label = ttk.Label(self.entrada_frame, style="TLabel", text="Buscar folio:")
        self.search_folio_label.grid(row=1, column=5, padx=5, pady=10, sticky='ew')
        self.search_folio_entry = ttk.Entry(self.entrada_frame)
        self.search_folio_entry.grid(row=1, column=6, padx=5, pady=10, sticky='ew')
        self.search_folio_entry.focus()
        self.search_folio_entry.bind('<KeyRelease>', self.search_folio)

        #Fecha fin
        self.folio_label_date_end = ttk.Label(self.entrada_frame, style="TLabel", text="Fecha fin")
        self.folio_label_date_end.grid(row=2, column=5, padx=10, pady=10, sticky='ew')

        self.folio_entry_date_end = tk.Entry(self.entrada_frame,font=("Helvetica", 12), borderwidth=0)
        self.folio_entry_date_end.grid(row=2, column=6, padx=5, pady=10, sticky='ew')
        self.folio_entry_date_end.insert(0, self.fecha_actual)


        #ALM2
        self.folio_label_alm2 = ttk.Label(self.entrada_frame, style="TLabel", text="Folio alm2")
        self.folio_label_alm2.grid(row=3, column=5, padx=10, pady=10, sticky='ew')

        self.folio_entry_alm2 = tk.Entry(self.entrada_frame,font=("Helvetica", 12),  state="readonly", borderwidth=0)
        self.folio_entry_alm2.grid(row=3, column=6, padx=5, pady=10, sticky='ew')
        
        self._create_table_all_folios_section()
    
    def _create_folio_section(self, parent):
        """Crear sección de folio dentro del LabelFrame"""
        
        folio_frame = ttk.Frame(parent, style="TFrame")
        folio_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        # Folio alineado a la izquierda
        ttk.Label(folio_frame, text="Folio:", style="TLabel",font=("bold")
        ).pack(side=tk.LEFT, padx=(5, 20))
        
        self.folio_entry = tk.Entry(
            folio_frame, font=("Helvetica", 14, "bold"), borderwidth=0,width=20,relief="solid", state="readonly", background="#f0f0f0")
        self.folio_entry.pack(side=tk.LEFT)
        # Botón para refrescar
        ttk.Button(folio_frame,text="Limpiar", width=10, cursor="hand2", command=self.refresh_folio_list
        ).pack(side=tk.RIGHT, padx=(5, 0))

        self.folio_entry.insert(0, "Pendiente")  # Valor inicial    
        
    
    def _create_action_buttons(self):
        """Botones de acción del pesaje"""        
        action_frame = ttk.Frame(self.frame, style="TFrame", padding=5)
        action_frame.pack(fill=tk.X, padx=5, pady=5)       
                
        self.close_folio_button = ttk.Button(action_frame, text="Cerrar / actualizar folio", cursor="hand2",
                command=lambda:self._register_weighing_wrapper(), 
                style="TButton",state="normal")
        self.close_folio_button.pack(side=tk.LEFT, padx=10)


    def _handle_autocomplete_selection(self, selected_value, entry_type):
        """
        Callback ejecutado al seleccionar un valor en los campos Chofer, Cliente, Material o Vehículo.
        Si el valor es '... externo', inserta una etiqueta en el campo Notas.
        """
        self.logger.debug(f"Selección autocomplete: {entry_type} = {selected_value}")
        
        notes_text_widget = self.notes_entry_manual
        insert_text_map = {
            "vehicle": {"target": "VEHEXT-Vehículo externo", "label": "Placas: "},
            "driver": {"target": "Chofer externo", "label": "Nombre: "},
            "customer": {"target": "Cliente externo", "label": "Cliente ext.: "},
            "material": {"target": "Material externo", "label": "Mat. ext.: "}
        }
        
        config = insert_text_map.get(entry_type)
        if not config:
            return

        TARGET_VALUE = config["target"]
        INSERT_TEXT_LABEL = config["label"]

        if selected_value == TARGET_VALUE:
            self.logger.info(f"Insertando etiqueta para {entry_type} externo")
            notes_text_widget.config(state="normal")
            
            # Obtener todo el texto actual
            current_text = notes_text_widget.get('1.0', tk.END).strip()
            
            # Verificar si la etiqueta ya existe en alguna parte del texto
            if INSERT_TEXT_LABEL.strip() not in current_text:
                
                # Prepara el nuevo texto con el marcador y un salto de línea
                new_text = INSERT_TEXT_LABEL + "\n"
                
                # Limpiar el campo
                notes_text_widget.delete('1.0', tk.END) 
                
                # 1. Insertar la nueva etiqueta al inicio
                notes_text_widget.insert('1.0', new_text)
                
                # 2. Reinsertar el texto que ya existía si no está vacío
                if current_text:
                    notes_text_widget.insert('2.0', current_text + "\n")

            # Colocar el cursor de inserción al inicio del texto
            notes_text_widget.focus_set()
            
            # Buscar dónde debería ir el cursor
            insert_pos = notes_text_widget.search(INSERT_TEXT_LABEL, "1.0", tk.END, nocase=True)
            
            if insert_pos:
                end_pos = f"{insert_pos}+{len(INSERT_TEXT_LABEL)}c"
                notes_text_widget.mark_set(tk.INSERT, end_pos)
            else:
                 notes_text_widget.mark_set(tk.INSERT, tk.END)

    

    def _setup_managers(self):
        """Configurar los managers después de crear la UI"""
        self.logger.debug("Configurando managers")
        
        self._set_initial_folio()

        if hasattr(self.vehicle_entry, 'set_select_callback'):
             self.vehicle_entry.set_select_callback(lambda val: self._handle_autocomplete_selection(val, 'vehicle')) 

        # DRIVER (Chofer externo)
        if hasattr(self.driver_entry, 'set_select_callback'):
             self.driver_entry.set_select_callback(lambda val: self._handle_autocomplete_selection(val, 'driver'))

        # CUSTOMER (Cliente externo)
        if hasattr(self.customer_entry, 'set_select_callback'):
             self.customer_entry.set_select_callback(lambda val: self._handle_autocomplete_selection(val, 'customer'))

        # MATERIAL (Material externo)
        if hasattr(self.material_entry, 'set_select_callback'):
             self.material_entry.set_select_callback(lambda val: self._handle_autocomplete_selection(val, 'material'))        
             
        self.table_all_folios.set_row_select_callback(self.on_table_folio_selected)
    
        ui_references = {
            'folio': self.folio_entry,
            'vehicle': self.vehicle_entry,  
            'trailer': self.trailer_entry,  
            'driver': self.driver_entry,    
            'customer': self.customer_entry, 
            'material': self.material_entry, 
            'notes': self.notes_entry_manual,
            'star_date': self.folio_entry_date_start,
            'end_date': self.folio_entry_date_end,
            'gross_weight': self.folio_entry_gross_weight,
            'tare_weight': self.folio_entry_tare_weight,
            'net_weight': self.folio_entry_net_weight,
            'folio_ALM2': self.folio_entry_alm2
        }
        self.weighing_manual_logic.set_ui_references(ui_references)
        self.weighing_manual_logic.set_autocomplete_handler(self.autocomplete_handler)
        self._ensure_manual_entries_have_data()
    
        self.logger.debug("Managers configurados exitosamente")

    def _ensure_manual_entries_have_data(self):
        """Asegurar que las entradas manuales tengan los mismos datos que las normales"""
        self.logger.debug("Asegurando datos en entradas manuales")
        
        data_types = ['vehicles', 'trailers', 'drivers', 'customers', 'materials']
        
        for data_type in data_types:
            normal_key = data_type
            manual_key = f"{data_type}_manual"
            
            # Verificar si ambas entradas existen
            if (normal_key in self.autocomplete_handler.entries and 
                manual_key in self.autocomplete_handler.entries):
                
                normal_entry = self.autocomplete_handler.entries[normal_key]
                manual_entry = self.autocomplete_handler.entries[manual_key]
                
                # Si la entrada manual está vacía, copiar de la normal
                if not manual_entry.items and normal_entry.items:
                    manual_entry.items = normal_entry.items.copy()
                    manual_entry.mapping_dict = normal_entry.mapping_dict.copy()
                    self.logger.debug(f"Datos copiados de {normal_key} a {manual_key}")

    def set_entry_state(self, entry_widget, state):
        """Helper para establecer el estado (normal/readonly/disabled) en Entry estándar o CustomAutocompleteEntry."""
        self.logger.debug(f"Cambiando estado de entry a: {state}")
        
        # Si tiene el atributo 'entry', es un CustomAutocompleteEntry
        if hasattr(entry_widget, 'entry'):
            entry_widget.entry.config(state=state)
        # Si es un Entry estándar (tk.Entry o ttk.Entry)
        elif hasattr(entry_widget, 'config'):
            entry_widget.config(state=state)       
    
    def on_table_folio_selected(self, folio_data):
        """Manejar selección de folio desde la tabla"""
        self.logger.debug(f"Selección de tabla: {folio_data}")
        
        if folio_data is None:
            self.logger.debug("Deselección de tabla, limpiando formulario")
            self.clean_form_fields_for_new_folio(confirm=False) 
            self.id_folio_selected = None           
            return

        try:
            if isinstance(folio_data, dict) and 'folio_number' in folio_data and 'id_weighing' in folio_data:
                self.id_folio_selected = folio_data['id_weighing']
                self.logger.info(f"Cargando datos del folio: {folio_data['folio_number']}")
                self.load_folio_data(folio_data)
            else: 
                self.logger.error(f"Datos de tabla no tienen el formato esperado: {folio_data}")
        except Exception as e:
            self.logger.error(f"Excepción al cargar datos desde tabla: {e}", exc_info=True)
            

    def set_entry_value(self, entry_widget, value):
        """Función auxiliar para establecer valor en Entry normal o CustomAutocompleteEntry."""
        self.logger.debug(f"Estableciendo valor en entry: {value}")
        
        self.unlock_form_fields()
        if hasattr(entry_widget, 'set'):
            entry_widget.set(value)
        elif isinstance(entry_widget, tk.Text): 
            entry_widget.config(state="normal")
            entry_widget.delete('1.0', tk.END)
            entry_widget.insert('1.0', value)
        elif hasattr(entry_widget, 'delete'): 
            entry_widget.config(state="normal")
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, value if value is not None else "")
            self.folio_entry_gross_weight.config(state="readonly")
            self.folio_entry_alm2.config(state="readonly")
            #entry_widget.config(state="readonly")


    def _validate_number(self, new_value):
        """
        Valida que el nuevo valor sea un número entero o vacío.
        Retorna True si es válido, False si no.
        """
        if new_value == "":  # Permite campo vacío
            return True
        
        # Solo permite números enteros positivos (0-9)99999
        if new_value.isdigit():
            # Opcional: puedes limitar la longitud máxima si es necesario
            if len(new_value) <= 5:  # Máximo 10 dígitos
                return True
        return False

    
    def _update_gross_weight(self, event=None):
        """Calcula y actualiza el valor del peso bruto según la tara y peso neto"""
        try:
            # Obtener valores de los campos
            entry_tare_weight = self.folio_entry_tare_weight.get().strip()
            entry_net_weight = self.folio_entry_net_weight.get().strip()
            
            # Convertir a enteros, manejando campos vacíos
            tare = int(entry_tare_weight) if entry_tare_weight else 0
            net = int(entry_net_weight) if entry_net_weight else 0
            
            # Calcular peso bruto
            if tare > 0:
                gross_weight = tare + net
            else:
                gross_weight = 0
            
            # Actualizar el campo de peso bruto
            self.folio_entry_gross_weight.config(state="normal")
            self.folio_entry_gross_weight.delete(0, tk.END)
            self.folio_entry_gross_weight.insert(0, str(gross_weight))
            self.folio_entry_gross_weight.config(state="readonly")
            
            self.logger.debug(f"Cálculo de peso: Tara={tare}, Neto={net}, Bruto={gross_weight}")
            
        except ValueError as e:
            # Esto no debería ocurrir con la validación, pero es por seguridad
            self.logger.error(f"Error al convertir valores numéricos: {e}")
            self.folio_entry_gross_weight.config(state="normal")
            self.folio_entry_gross_weight.delete(0, tk.END)
            self.folio_entry_gross_weight.insert(0, "Error")
            self.folio_entry_gross_weight.config(state="readonly")
        
    def load_folio_data(self, folio_data):
        """Cargar todos los datos de un folio seleccionado en la UI."""
        self.logger.info(f"Cargando datos del folio: {folio_data.get('folio_number')}")
        entry_gross_weight = folio_data.get('gross_weight', '0')
        folio_entry_tare_weight = folio_data.get('tare_weight', '0')
        folio_entry_net_weight = folio_data.get('net_weight', '0')

        if int(folio_entry_tare_weight)> 0:
            entry_gross_weight = int(folio_entry_tare_weight) + int(folio_entry_net_weight)

        # 1. Establecer Folio (ReadOnly)
        self.set_folio(folio_data.get('folio_number', '')) 
        self.set_entry_value(self.vehicle_entry, folio_data.get('vehicle_name', ''))
        self.set_entry_value(self.trailer_entry, folio_data.get('trailer_name', ''))
        self.set_entry_value(self.driver_entry, folio_data.get('driver_name', ''))
        self.set_entry_value(self.customer_entry, folio_data.get('customer_name', ''))
        self.set_entry_value(self.material_entry, folio_data.get('material_name', ''))
        self.set_entry_value(self.notes_entry_manual, folio_data.get('notes', ''))         
        self.set_entry_value(self.folio_entry_date_start, folio_data.get('date_start', ''))
        self.folio_combo_weighing_type.set(folio_data.get('weighing_type'))
        self.set_entry_value(self.folio_entry_gross_weight, entry_gross_weight)
        self.set_entry_value(self.folio_entry_tare_weight, folio_entry_tare_weight)
        self.set_entry_value(self.folio_entry_net_weight, folio_entry_net_weight)
        self.set_entry_value(self.folio_entry_date_end, folio_data.get('date_end', ''))
        self.set_entry_value(self.folio_entry_alm2, folio_data.get('folio_ALM2'))        
        self.data_closed_weighing = folio_data
        
        
    def _set_initial_folio(self):
        """Establecer el folio inicial al cargar la pestaña"""
        folio = self.db_manager.get_next_folio()
        self.logger.debug(f"Estableciendo folio inicial: {folio}")
        self.set_folio(folio)
    
    def _update_date_title(self):
        """Método para actualizar la fecha en el título (llamado periódicamente)"""
        # 1. Calcular la nueva fecha
        self.fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # 2. Actualizar el texto del nuevo Label
        if hasattr(self, 'date_label'):
            self.date_label.config(text=f"Fecha y Hora Actual:    {self.fecha_actual}")

        # 3. Programar la próxima llamada
        self.frame.after(1000, self._update_date_title) 

    def set_folio(self, folio):
        """Establecer el número de folio"""
        self.logger.debug(f"Actualizando folio a: {folio}")
        
        self.folio_entry.config(state="normal")
        self.folio_entry.delete(0, tk.END)
        self.folio_entry.insert(0, str(folio))
        self.folio_entry.config(state="readonly")
    
    def _validate_required_fields(self):
        """Validar campos obligatorios con messagebox"""
        self.logger.debug(f"Validando campos obligatorios para")
        
        campos_obligatorios = [
            ('vehicle', 'Vehículo'),
            ('trailer', 'Remolque'),
            ('driver', 'Chofer'), 
            ('customer', 'Cliente'),
            ('material', 'Material'),
            ('star_date', 'Fecha inicio'),
            ('end_date', 'Fecha fin'),
            ('gross_weight', 'Peso bruto'),
            ('tare_weight', 'Peso tara'),            
            ('net_weight', 'Peso neto')
        ]
        
        campos_vacios = []
        
        for campo_key, campo_nombre in campos_obligatorios:
            valor = self._get_value_entry(campo_key)
            if not valor:
                campos_vacios.append(campo_nombre)
     
        if campos_vacios:
            campos_texto = "\n• " + "\n• ".join(campos_vacios)
            self.logger.warning(f"Campos obligatorios vacíos: {campos_vacios}")
            messagebox.showerror(
                "Campos Obligatorios",
                f"Los siguientes campos son obligatorios y están vacíos:\n{campos_texto}\n\nPor favor, complete todos los campos antes de registrar el pesaje.",
                parent=self.frame
            )
            return False
        
        self.logger.debug("Validación de campos obligatorios exitosa")
        return True
    
    def _get_value_entry(self, campo):
        """Obtener valor de un campo del formulario"""
        entry_map = {
            'vehicle': self.vehicle_entry,
            'trailer': self.trailer_entry,
            'driver': self.driver_entry,
            'customer': self.customer_entry,
            'material': self.material_entry,
            'star_date': self.folio_entry_date_start,
            'end_date': self.folio_entry_date_end,
            'gross_weight': self.folio_entry_gross_weight,
            'tare_weight': self.folio_entry_tare_weight,
            'net_weight': self.folio_entry_net_weight,
            'folio_ALM2': self.folio_entry_alm2

        }
        
        if campo in entry_map:
            entry = entry_map[campo]
            if hasattr(entry, 'get'):
                return entry.get().strip()
        return ""
    
    def _create_table_all_folios_section(self):
        """Crear sección para la tabla de pesajes pendientes"""
        self.logger.debug("Creando sección de tabla de pesajes pendientes")
        
        # Frame contenedor para la tabla
        self.table_container = ttk.Frame(self.frame, style="TFrame", padding=5)
        self.table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def refresh_folio_list(self):
        """Refrescar la lista de folios"""
        self.logger.info("Refrescando lista de folios")
        
        if hasattr(self, 'folio_selector'):
            self.folio_selector.refresh_folios()
        
        if hasattr(self, 'pending_table'):
            self.table_all_folios.refresh_table()
        
        # Actualizar también el folio actual
        self._clear_form_automatic()
        self._set_initial_folio()
    
    def _register_weighing_wrapper(self):
        """Método wrapper para registrar pesaje con db_manager"""
        self.logger.info(f"Iniciando registro de pesaje")
        weighing_type = self.folio_combo_weighing_type.get()
        data = self.data_closed_weighing
        second_user_id = self.user_id        
            
        if not self._validate_required_fields():
            self.logger.warning("Registro cancelado - Campos obligatorios incompletos")
            return None
        
        try:
            # Registrar el pesaje
            exito, weighing_data = self.weighing_manual_logic.register_weighing(self.db_manager, weighing_type,self.id_folio_selected)
            if exito and weighing_data:
                self.logger.info(f"Pesaje registrado exitosamente - Folio: {weighing_data.folio}")
                messagebox.showinfo(
                    "Pesaje Registrado",
                    f"✅ Pesaje registrado exitosamente\n\nFolio: {weighing_data.folio}",
                    parent=self.frame
                )
                self._clear_form_automatic()
                self.table_all_folios.refresh_table()
                self.refresh_folio_list()
                #return weighing_data
            else:
                self.logger.error(f"Error al registrar pesaje")
                messagebox.showerror(
                    "Error",
                    f"❌ Error al registrar pesaje",
                    parent=self.frame
                )
                return None
                
        except Exception as e:
            self.logger.error(f"Error inesperado al registrar pesaje: {str(e)}", exc_info=True)
            messagebox.showerror(
                "Error Inesperado",
                f"❌ ui_Ocurrió un error inesperado:\n{str(e)}",
                parent=self.frame
            )
            return None
        
    def _clear_form_automatic(self):
        """Limpiar formulario automáticamente sin confirmación"""
        self.logger.debug("Limpiando formulario automáticamente")
        self.data_closed_weighing ={}
        self.id_folio_selected = None
        # Desbloquear campos primero
        self.unlock_form_fields()
        
        # Limpiar campos
        clear_fields = [
            self.vehicle_entry,
            self.trailer_entry,
            self.driver_entry,
            self.customer_entry,
            self.material_entry,
            self.notes_entry_manual,
            self.folio_entry_date_start,
            self.folio_entry_date_end,
            self.folio_entry_tare_weight,
            self.folio_entry_net_weight
        ]

        clear_fields_readonly = [            
            self.folio_entry_gross_weight,            
            self.folio_entry_alm2,
        ]
        
        for campo in clear_fields:
            if hasattr(campo, 'set'):
                campo.set("")
            elif isinstance(campo, tk.Text):
                campo.delete('1.0', tk.END)
            elif hasattr(campo, 'delete') and hasattr(campo, 'insert'):
                campo.delete(0, tk.END)

        for campo in clear_fields_readonly:            
            if isinstance(campo, tk.Text):
                campo.delete('1.0', tk.END)
            elif hasattr(campo, 'delete') and hasattr(campo, 'insert'):
                campo.config(state='normal')
                campo.delete(0, tk.END)
                campo.config(state='readonly')

            
        # Obtener nuevo folio
        nuevo_folio = self.db_manager.get_next_folio()
        self.set_folio(nuevo_folio)
                
        self.logger.debug("Formulario limpiado automáticamente")
    
    def unlock_form_fields(self):
        """Desbloquear todos los campos del formulario"""
        self.logger.debug("Desbloqueando campos del formulario")
        
        autocomplete_entries = [
            self.vehicle_entry,
            self.trailer_entry,
            self.driver_entry, 
            self.customer_entry,
            self.material_entry            
        ]
        #self.folio_entry_date_start.config(state="normal", background="white")
        self.folio_entry_gross_weight.config(state="readonly")
        self.folio_entry_alm2.config(state="readonly")
        for entry in autocomplete_entries:
            if hasattr(entry, 'entry'):
                entry.entry.config(state="normal", background="white")

    
    def search_folio(self, event=None):
        """Buscar folios por texto"""
        search_text = self.search_folio_entry.get().strip()
        
        if search_text:
            self.table_all_folios.update_table(search_text)            
        else:
            self.table_all_folios.load_folios()
            
    def get_frame(self):
        return self.frame

    
    def closed_weighing_wrapper(self):
        """Método datos para cerrar folio"""
        self.logger.info("Iniciando cierre manual de folio")
        
        data = self.data_closed_weighing
        second_user_id = self.user_id 
        
        try:
            # Registrar el pesaje
            result = self.weighing_manual_logic.register_closed_weighing(data,second_user_id, self.db_manager)
            
            if result['exito']:
                self.logger.info(f"Folio cerrado exitosamente: {data['folio_number']}")
                self.Send_to_print(result['updated_row'])
                messagebox.showinfo(
                    "Pesaje Registrado",
                    f"✅ Pesaje Folio: {data['folio_number']} cerrado exitosamente.",
                    parent=self.frame
                )
                self._clear_form_automatic()
                self.refresh_folio_list()
                return None
            else:
                self.logger.warning(f"No se encontró el registro con Folio {data['folio_number']} para cerrar")
                messagebox.showerror(
                    "Error",
                    f"⚠️ No se encontró el registro con Folio  {data['folio_number']} para cerrar.",
                    parent=self.frame
                )
                return None
                
        except Exception as e:
            self.logger.error(f"Error inesperado al cerrar folio: {str(e)}", exc_info=True)
            messagebox.showerror(
                "Error Inesperado",
                f"❌ CSW-Ocurrió un error inesperado:\n{str(e)}",
                parent=self.frame
            )
        return None
           
    def Send_to_print(data):
        """Función para enviar a imprimir"""
        logger = app_logger.getChild('PrintFunction')
        
        if data:                    
            try:
                logger.info(f"Enviando a imprimir folio: {data.get('folio_number', 'N/A')}")
                exito, e = print_weighing_ticket(data)              
                
                if exito:
                    logger.info("Impresión exitosa")
                    data ={}
                    return None
                else:
                    mensaje_text="Impresora no conectada"
                    mensaje = str(e)
                    if mensaje_text in mensaje:
                        mensaje_en_pantalla = "La impresora no se encuentra\n o el cable no esta conectado"
                    logger.error(f"Error de impresión:{e}, {mensaje}")
                    messagebox.showerror(
                        "Error",
                        f"⚠️ Problemas para imprimir el folio  {data['folio_number']}\n{mensaje_en_pantalla}, {e}",
                    )
                    return None
                    
            except Exception as e:
                logger.error(f"Error inesperado en impresión: {str(e)}", exc_info=True)
                messagebox.showerror(
                    "Error Inesperado",
                    f"❌ Ocurrió un error inesperado:\n{str(e)}",
                )