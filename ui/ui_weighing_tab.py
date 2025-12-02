# ui_weighing_tab.py

import tkinter as tk
import datetime
from tkinter import ttk, messagebox  
from logic.logic_scale_manager import ScaleManager
from logic.logic_weighing import WeighingLogic
from logic.logic_weighing_video import WeighingVideo
from logic.logic_weighing_automatic_close import AutomaticClose
from logic.logic_print_folios import print_weighing_ticket
from db_operations.db_save_folio import WeighingDBManager
from logic.logic_tables_weighings import PendingWeighingsTable
from utils.logger_config import app_logger

class PesajeTab:
    def __init__(self, notebook, styles, autocomplete_handler=None, user_id=None, user_access_level=None):
        # Configurar logger para esta clase
        self.logger = app_logger.getChild('PesajeTab')
        self.logger.info(f"Inicializando pestaña de pesaje para usuario ID: {user_id}, Nivel de acceso: {user_access_level}")
        
        self.styles = styles
        self.frame = ttk.Frame(notebook, style="TFrame")
        notebook.add(self.frame, text="Registrar peso")
        self.user_id = user_id
        self.user_access_level = int(user_access_level)
        self.data_closed_weighing = None
        self.weight_status = False
        self.btn_status = True 
        
        if autocomplete_handler:
            self.autocomplete_handler = autocomplete_handler
        else:
            from logic.logic_autocomplete import AutocompleteHandler
            self.autocomplete_handler = AutocompleteHandler()
        
        # Inicializar el manager de base de datos
        self.db_manager = WeighingDBManager()
        self.video_manager = WeighingVideo()
        self.update_weight_display = self._create_weight_display_callback()
        
        # Inyectar dependencias
        self.scale_manager = ScaleManager(update_callback=self.update_weight_display)
        self.weighing_logic = WeighingLogic(user_id=user_id)
        self.automatic_close = AutomaticClose(user_id=user_id)
        self._create_ui()
        self.pending_table = PendingWeighingsTable(self.table_container)
        self._setup_managers()
        self._update_date_title()
        
        self.logger.info("Pestaña de pesaje inicializada correctamente")
    
    def _create_weight_display_callback(self):
        """Crear el callback para actualizar el display de peso"""
        def update_callback(weight_text, text_color):
            """Callback para actualizar la etiqueta de peso"""
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            
            # Actualizar la UI de forma segura desde el hilo principal
            if hasattr(self, 'weight_label') and self.weight_label.winfo_exists():
                try:
                    self.weight_label.after(0, lambda: self.weight_label.config(
                        text=weight_text,  foreground=text_color))
                    weight_int = int(weight_text.split()[0])
                    if weight_int <=0:
                        self.weight_status = False
                        self.entrada_button.config(state="disabled")
                        self.salida_button.config(state="disabled")#btn_exit_with_weight
                        self.btn_exit_with_weight.config(state="disabled")#btn_exit_with_weight
                        self.close_folio_button.config(state="disabled")
                        self._clear_form_automatic()
                    else:
                        self.weight_status = True
                        if self.btn_status:
                            self.entrada_button.config(state="normal")
                            self.salida_button.config(state="normal")
                            self.btn_exit_with_weight.config(state="normal")#btn_exit_with_weight
                        self.logger.debug(f"Peso actualizado: {weight_text}, Estado botones: {self.btn_status}")
                        
                except Exception as e:
                    self.logger.error(f"Error actualizando UI del peso: {str(e)}", exc_info=True)
                    messagebox.showerror(
                        "Error Inesperado",
                        f"❌ BSC-Error actualizando UI:\n{str(e)}")
            else:
                self.logger.warning("Label de peso no disponible o destruido")
        
        return update_callback
    
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
        
        self.video_frame = ttk.LabelFrame(
            self.horizontal_container,  # ¡CAMBIAR: usar el contenedor horizontal!
            text="Video/imagen",
            style="TFrame",
            padding=10
        )
        
        # Usar grid en el contenedor horizontal (que solo tiene estos dos frames)
        self.entrada_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.video_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Configurar expansión del contenedor horizontal
        #self.horizontal_container.columnconfigure(0, weight=1)
        self.horizontal_container.columnconfigure(1, weight=1)
        self.horizontal_container.rowconfigure(0, weight=1)
        self.video_frame.grid_propagate(False)  
        # Folio justo después del texto del LabelFrame
        self._create_folio_section(self.entrada_frame)
                    
        # Vehículo
        ttk.Label(self.entrada_frame, text="Vehículo:", style="TLabel").grid(row=1, column=0, sticky=tk.W, padx=5, pady=10)
        self.vehicle_entry = self.autocomplete_handler.create_vehicle_entry(self.entrada_frame)
        self.vehicle_entry.grid(row=1, column=1, padx=5, pady=10, sticky='ew')
        
        # Remolque
        ttk.Label(self.entrada_frame, text="Remolque:", style="TLabel").grid(row=2, column=0, sticky=tk.W, padx=5, pady=10)
        self.trailer_entry = self.autocomplete_handler.create_trailer_entry(self.entrada_frame)
        self.trailer_entry.grid(row=2, column=1, padx=5, pady=10, sticky='ew')
        
        # Chofer
        ttk.Label(self.entrada_frame, text="Chofer:", style="TLabel").grid(row=3, column=0, sticky=tk.W, padx=5, pady=10)
        self.driver_entry = self.autocomplete_handler.create_driver_entry(self.entrada_frame)
        self.driver_entry.grid(row=3, column=1, padx=5, pady=10, sticky='ew')
        
        # Cliente
        ttk.Label(self.entrada_frame, text="Cliente:", style="TLabel").grid(row=4, column=0, sticky=tk.W, padx=5, pady=10)
        self.customer_entry = self.autocomplete_handler.create_customer_entry(self.entrada_frame)
        self.customer_entry.grid(row=4, column=1, padx=5, pady=10, sticky='ew')
        
        # Material
        ttk.Label(self.entrada_frame, text="Material:", style="TLabel").grid(row=5, column=0, sticky=tk.W, padx=5, pady=10)
        self.material_entry = self.autocomplete_handler.create_material_entry(self.entrada_frame)
        self.material_entry.grid(row=5, column=1, padx=5, pady=10, sticky='ew')
        
        # Campos simples notas
        ttk.Label(self.entrada_frame, text="Notas:\n(Datos externos)", style="TLabel").grid(row=6, column=0, sticky=tk.W, padx=5, pady=10)
        self.notes_entry = tk.Text(self.entrada_frame, font=("Helvetica", 12), borderwidth=0, width=40, height=4)
        self.notes_entry.grid(row=6, column=1, padx=5, pady=10)
        
        
        
        # Controles de báscula
        self._create_scale_controls(self.frame)
        
        # Botones de acción
        self._create_action_buttons()

        # Crear sección de video con 4 cámaras
        #self._create_video_section()

        # Contenedor para la tabla de pesajes pendientes
        self._create_pending_table_section()
        
        self.logger.debug("Interfaz de usuario creada exitosamente")
    
    def _create_folio_section(self, parent):
        """Crear sección de folio dentro del LabelFrame"""
        self.logger.debug("Creando sección de folio")
        
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
        
        self.logger.debug("Sección de folio creada")
    
    def _create_scale_controls(self, parent):
        """Controles específicos de la báscula"""
        self.logger.debug("Creando controles de báscula")
        
        scale_control_frame = ttk.Frame(parent, style="TFrame")
        scale_control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Peso actual
        ttk.Label(scale_control_frame, text="Peso actual:", style="TLabel").pack(side=tk.LEFT, padx=20)
        self.weight_label = ttk.Label(scale_control_frame, text="0 kg",  font=("Helvetica",30 , "bold"), foreground="green")
        self.weight_label.pack(side=tk.LEFT, padx=100)

        
    def _connect_disconnect(self):
        """Conectar y desconectar la bascula"""
        current_text = self.btn_scale_control.cget('text')
        if current_text == "⏹ Desconectar":
            self.logger.info("Desconectando báscula")            
            self.scale_manager.disconnect()
        else: 
            self.logger.info("Conectando báscula")
            self.scale_manager.connect()

    def _on_simulator_changed(self):
        """Callback cuando cambia el estado del checkbox del simulador"""
        use_simulator = self.use_simulator_var.get()
        self.logger.info(f"Cambiando estado del simulador a: {use_simulator}")
        
        self.scale_manager.set_use_simulator(use_simulator)
        self.weighing_logic.update_use_simulator(use_simulator)
        if use_simulator:
            self.check_active.config(text="Simulador de activado", style="Green.TCheckbutton" )
        else:
            self.check_active.config(text="Simulador de desactivado", style="Orange.TCheckbutton" )        

    def _create_action_buttons(self):
        """Botones de acción del pesaje"""
        self.logger.debug("Creando botones de acción")
        
        action_frame = ttk.Frame(self.frame, style="TFrame", padding=5)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Guardar referencias a los botones state="disabled
        self.entrada_button = ttk.Button(action_frame, text="Registrar entrada", cursor="hand2", 
                command=lambda: self.register_weighing_wrapper('Entrada'), 
                style="Primary.TButton",state="disabled" )
        self.entrada_button.pack(side=tk.LEFT, padx=5)
        
        self.salida_button = ttk.Button(action_frame, text="Registrar salida", cursor="hand2", 
                command=lambda: self.register_weighing_wrapper('Salida'), 
                style="Primary.TButton",state="disabled")
        self.salida_button.pack(side=tk.LEFT, padx=5)

        self.btn_exit_with_weight = ttk.Button(action_frame, text="Registrar salida c/peso", cursor="hand2", 
                command=lambda: self.register_weighing_wrapper('Salida C/peso'), 
                style="Warning.TButton",state="disabled")
        self.btn_exit_with_weight.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(action_frame, text="Cancelar", cursor="hand2",
                command=self.clear_form,
                style="Warning.TButton")
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        self.close_folio_button = ttk.Button(action_frame, text="Cerrar folio", cursor="hand2",
                command=lambda:self.closed_weighing_wrapper(), 
                style="TButton",state="disabled")
        self.close_folio_button.pack(side=tk.LEFT, padx=5)

        self.btn_scale_control = ttk.Button(action_frame, text="▶ Conectar", style="Warning.TButton", cursor="hand2",  width=15, command=self._connect_disconnect)
        self.btn_scale_control.pack(side=tk.LEFT, padx=20) 

        self.scale_status_label = ttk.Label(action_frame, text="Desconectada", style="TLabel")
        self.use_simulator_var = tk.BooleanVar(value=False)
        self.check_active = ttk.Checkbutton(action_frame, text="Simulador de desactivado",  
        variable=self.use_simulator_var,  style="Orange.TCheckbutton",  command=self._on_simulator_changed)    
        self.scale_status_label.pack(side=tk.LEFT, padx=10)
        if  self.user_access_level > 3:
            self.check_active.pack(side=tk.LEFT, padx=10)
            
        self.logger.debug("Controles de báscula creados")


        if self.user_access_level >=3:
            self.close_tara_button = ttk.Button(action_frame, text="Cerrar c/tara", cursor="hand2",
                command=lambda:self.closed_weighing_wrapper_automatic(), 
                style="Warning.TButton",state="disabled")
            self.close_tara_button.pack(side=tk.RIGHT, padx=5)
            
        self.logger.debug("Botones de acción creados")

    def _handle_autocomplete_selection(self, selected_value, entry_type):
        """
        Callback ejecutado al seleccionar un valor en los campos Chofer, Cliente, Material o Vehículo.
        Si el valor es '... externo', inserta una etiqueta en el campo Notas.
        """
        self.logger.debug(f"Selección autocomplete: {entry_type} = {selected_value}")
        
        notes_text_widget = self.notes_entry
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

    def _create_video_section(self):
        """Crear sección de video con 4 cámaras en grid 2x2 manteniendo relación de aspecto"""
        self.logger.debug("Creando sección de video con 2 cámaras")
        
        # Configurar grid para el frame de video
        self.video_frame.columnconfigure(0, weight=1)
        self.video_frame.columnconfigure(1, weight=1)
        self.video_frame.rowconfigure(0, weight=1)
        self.video_frame.rowconfigure(1, weight=1)
        
        # Crear los 4 frames para las cámaras
        self.camera_frames = {}
        #camera_labels = ['Cámara 1', 'Cámara 2']
        camera_labels = ['Cámara frente', 'Cámara atras', 'Imagen inició frente', 'Imagen inició atras']

        
        for i, label in enumerate(camera_labels):
            row = i // 2  # 0, 0, 1, 1
            col = i % 2   # 0, 1, 0, 1
            
            # Frame individual para cada cámara
            cam_frame = ttk.LabelFrame(
                self.video_frame,
                text=label,
                style="TFrame",
                padding=3
            )
            cam_frame.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            
            # Configurar expansión del frame de cámara
            cam_frame.columnconfigure(0, weight=1)
            cam_frame.rowconfigure(0, weight=1)

            # Frame contenedor para el canvas (ayuda con el redimensionamiento)
            canvas_container = ttk.Frame(cam_frame, style="TFrame")
            canvas_container.grid(row=0, column=0, sticky="nsew")
            canvas_container.columnconfigure(0, weight=1)
            canvas_container.rowconfigure(0, weight=1)
            
            # Canvas para mantener relación de aspecto (en lugar de Label)
            video_canvas = tk.Canvas(
                cam_frame,
                bg="black",
                highlightthickness=1,
                highlightbackground="#555555",
                relief="solid"
            )
            video_canvas.grid(row=0, column=0, sticky="nsew")
            
            # Label para estado/texto (sobre el canvas)
            status_label = ttk.Label(
                video_canvas,
                text=f"📷 {label}\nConectando...",
                style="TLabel",
                background="black",
                foreground="white",
                anchor="center",
                font=("Helvetica", 10)
            )
            
            # Centrar el label en el canvas
            video_canvas.create_window(
                video_canvas.winfo_reqwidth() // 2, 
                video_canvas.winfo_reqheight() // 2,
                window=status_label
            )
            
            # Guardar referencia para futuras actualizaciones
            self.camera_frames[f'camera_{i+1}'] = {
                'frame': cam_frame,
                'canvas_container': canvas_container,
                'canvas': video_canvas,
                'status_label': status_label,
                'current_image': None,
                'original_image': None,
                'aspect_ratio': 16/9,  # Relación de aspecto por defecto (16:9)
                'status': 'disconnected'
            }
            camera_frames = self.camera_frames
            # Bind para redimensionar manteniendo relación de aspecto
            video_canvas.bind('<Configure>', lambda e, cam_id=f'camera_{i+1}': self.video_manager.resize_camera_feed(cam_id, camera_frames))
        
        self.logger.debug("Sección de video creada con 4 cámaras manteniendo relación de aspecto")

    def _setup_managers(self):
        """Configurar los managers después de crear la UI"""
        self.logger.debug("Configurando managers")
        
        self.scale_manager.set_status_label(self.scale_status_label,  self.btn_scale_control)

        use_simulator = self.use_simulator_var.get()
        self.scale_manager.set_use_simulator(use_simulator)

        self.weighing_logic.set_simulator_checkbox(self.use_simulator_var)
        self.weighing_logic.set_scale_manager(self.scale_manager)

        # Pasar referencia al autocomplete handler
        self.weighing_logic.set_autocomplete_handler(self.autocomplete_handler)
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
             self.material_entry.set_select_callback(lambda val: self._handle_autocomplete_selection(val, 'material'))        # NUEVA CONEXIÓN DE TABLA        
        self.pending_table.set_row_select_callback(self.on_table_folio_selected)
        
        # Pasar referencias de los widgets a la lógica
        ui_references = {
            'folio': self.folio_entry,
            'vehicle': self.vehicle_entry,
            'trailer': self.trailer_entry,
            'driver': self.driver_entry,
            'customer': self.customer_entry,
            'material': self.material_entry,
            'weight_label': self.weight_label,
            'folio_entry': self.folio_entry,
            'notes': self.notes_entry
        }
        self.weighing_logic.set_ui_references(ui_references)
        
        self.scale_manager.connect()  # Conectar automáticamente
        self.logger.debug("Managers configurados exitosamente")

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
            self.update_buttons_state(None)
            return

        try:
            if isinstance(folio_data, dict) and 'folio_number' in folio_data:
                self.logger.info(f"Cargando datos del folio: {folio_data['folio_number']}")
                self.load_folio_data(folio_data)
            else: 
                self.logger.error(f"Datos de tabla no tienen el formato esperado: {folio_data}")
        except Exception as e:
            self.logger.error(f"Excepción al cargar datos desde tabla: {e}", exc_info=True)
            self.lock_form_fields()

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
            entry_widget.config(state="readonly")

    def lock_form_fields(self):
        """Bloquear todos los campos para prevenir manipulación"""
        self.logger.debug("Bloqueando campos del formulario")
        
        lock_list = [
            self.folio_entry,
            self.vehicle_entry,
            self.trailer_entry, 
            self.driver_entry, 
            self.customer_entry, 
            self.material_entry
        ]
        for field in lock_list:
            self.set_entry_state(field, "readonly")    

    def load_folio_data(self, folio_data):
        """Cargar todos los datos de un folio seleccionado en la UI."""
        self.logger.info(f"Cargando datos del folio: {folio_data.get('folio_number', '')}")
           
        # 1. Establecer Folio (ReadOnly)
        self.set_folio(folio_data.get('folio_number', '')) 
        self.set_entry_value(self.vehicle_entry, folio_data.get('vehicle_name', ''))
        self.set_entry_value(self.trailer_entry, folio_data.get('trailer_name', ''))
        self.set_entry_value(self.driver_entry, folio_data.get('driver_name', ''))
        self.set_entry_value(self.customer_entry, folio_data.get('customer_name', ''))
        self.set_entry_value(self.material_entry, folio_data.get('material_name', ''))
        self.set_entry_value(self.notes_entry, folio_data.get('notes', ''))
        self.data_closed_weighing = folio_data
        
        self.lock_form_fields()
        self.update_buttons_state(folio_data.get('weighing_type', ''))
        
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
    
    def _validate_required_fields(self, tipo_pesaje):
        """Validar campos obligatorios con messagebox"""
        self.logger.debug(f"Validando campos obligatorios para {tipo_pesaje}")
        
        campos_obligatorios = [
            ('vehicle', 'Vehículo'),
            ('trailer', 'Remolque'),
            ('driver', 'Chofer'), 
            ('customer', 'Cliente'),
            ('material', 'Material')
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
                f"Los siguientes campos son obligatorios y están vacíos:\n{campos_texto}\n\nPor favor, complete todos los campos antes de registrar el pesaje de {tipo_pesaje}.",
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
            'material': self.material_entry
        }
        
        if campo in entry_map:
            entry = entry_map[campo]
            if hasattr(entry, 'get'):
                return entry.get().strip()
        return ""
    
    def _create_pending_table_section(self):
        """Crear sección para la tabla de pesajes pendientes"""
        self.logger.debug("Creando sección de tabla de pesajes pendientes")
        
        # Frame contenedor para la tabla
        self.table_container = ttk.Frame(self.frame, style="TFrame", padding=5)
        self.table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def refresh_folio_list(self):
        """Refrescar la lista de folios pendientes"""
        self.logger.info("Refrescando lista de folios pendientes")
        
        if hasattr(self, 'folio_selector'):
            self.folio_selector.refresh_folios()
        
        if hasattr(self, 'pending_table'):
            self.pending_table.refresh_table()
        
        # Actualizar también el folio actual
        self._clear_form_automatic()
        self._set_initial_folio()
    
    def register_weighing_wrapper(self, tipo_pesaje):
        """Método wrapper para registrar pesaje con db_manager"""
        self.logger.info(f"Iniciando registro de pesaje: {tipo_pesaje}")
        
        # Validar campos obligatorios primero
        if not self._validate_required_fields(tipo_pesaje):
            self.logger.warning("Registro cancelado - Campos obligatorios incompletos")
            return None
        
        try:
            # Registrar el pesaje
            exito, weighing_data = self.weighing_logic.register_weighing(tipo_pesaje, self.db_manager)
            
            if exito and weighing_data:
                self.logger.info(f"Pesaje registrado exitosamente - Folio: {weighing_data.folio}")
                messagebox.showinfo(
                    "Pesaje Registrado",
                    f"✅ Pesaje de {tipo_pesaje} registrado exitosamente\n\nFolio: {weighing_data.folio}",
                    parent=self.frame
                )
                self._clear_form_automatic()
                self.refresh_folio_list()
                return weighing_data
            else:
                self.logger.error(f"Error al registrar pesaje de {tipo_pesaje}")
                messagebox.showerror(
                    "Error",
                    f"❌ Error al registrar pesaje de {tipo_pesaje}",
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
        
        # Desbloquear campos primero
        self.unlock_form_fields()
        
        # Limpiar campos
        clear_fields = [
            self.vehicle_entry,
            self.trailer_entry,
            self.driver_entry,
            self.customer_entry,
            self.material_entry,
            self.notes_entry
        ]
        
        for campo in clear_fields:
            if hasattr(campo, 'set'):
                campo.set("")
            elif isinstance(campo, tk.Text):
                campo.delete('1.0', tk.END)
            elif hasattr(campo, 'delete') and hasattr(campo, 'insert'):
                campo.delete(0, tk.END)
            
        # Obtener nuevo folio
        nuevo_folio = self.db_manager.get_next_folio()
        self.set_folio(nuevo_folio)
        
        # Restablecer botones a estado normal
        if  self.weight_status:
            self.btn_status = True
            self.entrada_button.config(state="normal")
            self.salida_button.config(state="normal")
            self.btn_exit_with_weight.config(state="normal")#btn_exit_with_weight
            self.close_folio_button.config(state="disabled")
            if self.user_access_level >=3:
                self.close_tara_button.config(state="disabled")   
        
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
        
        for entry in autocomplete_entries:
            if hasattr(entry, 'entry'):
                entry.entry.config(state="normal", background="white")

    def clear_form(self):
        """Limpiar todos los campos del formulario"""
        self.logger.info("Solicitando limpieza de formulario")
        
        # Confirmar con el usuario
        respuesta = messagebox.askyesno(
            "Limpiar Formulario",
            "¿Está seguro de que desea limpiar todos los campos del formulario?",
            parent=self.frame
        )
        
        if respuesta:
            self.logger.debug("Usuario confirmó limpieza de formulario")
            
            # Desbloquear campos primero
            self.unlock_form_fields()
            
            # Limpiar campos
            clear_fields = [
                self.vehicle_entry,
                self.trailer_entry,
                self.driver_entry,
                self.customer_entry,
                self.material_entry,
                self.notes_entry
            ]

            for campo in clear_fields:
                if hasattr(campo, 'set'):
                    campo.set("")
                elif isinstance(campo, tk.Text):
                    campo.delete('1.0', tk.END)
                elif hasattr(campo, 'delete') and hasattr(campo, 'insert'):
                    campo.delete(0, tk.END)
                
                # Obtener nuevo folio
                nuevo_folio = self.db_manager.get_next_folio()
                self.set_folio(nuevo_folio)
                
                # Restablecer botones
                if self.weight_status:
                    self.btn_status = True
                    self.entrada_button.config(state="normal")
                    self.salida_button.config(state="normal")
                    self.btn_exit_with_weight.config(state="normal")#btn_exit_with_weight
                    self.close_folio_button.config(state="disabled")
                    if self.user_access_level >=3:
                        self.close_tara_button.config(state="disabled")
            
            self.logger.info("Formulario limpiado exitosamente")

    def update_buttons_state(self, weighing_type):
        """Actualizar estado de los botones según el tipo de pesada"""
        self.logger.debug(f"Actualizando estado de botones para tipo: {weighing_type}")
        
        if self.weight_status:
            self.btn_status = False
            self.entrada_button.config(state="disabled")
            self.salida_button.config(state="disabled")
            self.btn_exit_with_weight.config(state="disabled")#btn_exit_with_weight
            self.close_folio_button.config(state="normal")
            if weighing_type == "Entrada" and self.user_access_level >=3:            
                self.close_tara_button.config(state="normal")
            elif weighing_type != "Entrada" and self.user_access_level >=3:
                self.close_tara_button.config(state="disabled")
        
        self.logger.debug(f"Estado de botones actualizado - Entrada: {self.entrada_button['state']}, Salida: {self.salida_button['state']}, Salida c/peso: {self.btn_exit_with_weight['state']}")
        
    def get_frame(self):
        return self.frame

    def clean_form_fields_for_new_folio(self, confirm=True):
        """Limpia el formulario, desbloquea los campos, establece un nuevo folio 
        y restablece el estado de los botones."""
        self.logger.info(f"Solicitando limpieza de formulario para nuevo folio (confirmación: {confirm})")
        
        # 1. Confirmación (si es necesaria)
        if confirm:
            respuesta = messagebox.askyesno(
                "Confirmación",
                "¿Desea limpiar todos los campos del formulario para iniciar un nuevo pesaje?",
                parent=self.frame
            )
            if not respuesta:
                self.logger.debug("Usuario canceló la limpieza del formulario")
                return 

        # 2. Desbloquear campos
        self.unlock_form_fields()
        
        # 3. Limpiar campos
        clear_fields = [
            self.vehicle_entry,
            self.trailer_entry,
            self.driver_entry,
            self.customer_entry,
            self.material_entry,
            self.notes_entry
        ]

        for campo in clear_fields:
            if hasattr(campo, 'set'):
                campo.set("")
            elif isinstance(campo, tk.Text):
                campo.delete('1.0', tk.END)
            elif hasattr(campo, 'delete') and hasattr(campo, 'insert'):
                campo.delete(0, tk.END)

        nuevo_folio = self.db_manager.get_next_folio()
        self.set_folio(nuevo_folio)
        
        # 5. Restablecer botones (Estado Normal: Ambos habilitados, Cerrar deshabilitado)
        self.update_buttons_state(None)
        
        # 6. Mostrar mensaje de éxito (si se pasó la confirmación)
        if confirm:
            self.logger.info("Formulario limpiado exitosamente para nuevo folio")
            messagebox.showinfo(
                "Formulario Limpio",
                "✅ Todos los campos han sido limpiados y el folio ha sido actualizado.",
                parent=self.frame
            )

    def closed_weighing_wrapper(self):
        """Método datos para cerrar folio"""
        self.logger.info("Iniciando cierre manual de folio")
        
        data = self.data_closed_weighing
        second_user_id = self.user_id 
        
        try:
            # Registrar el pesaje
            result = self.weighing_logic.register_closed_weighing(data,second_user_id, self.db_manager)
            
            if result['exito']:
                self.logger.info(f"Folio cerrado exitosamente: {data['folio_number']}")
                Send_to_print(result['updated_row'])
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

    def closed_weighing_wrapper_automatic(self):
        """Método datos para cerrar folio con tara"""
        self.logger.info("Iniciando cierre automático de folio con tara")
                
        data = self.data_closed_weighing
        folio_number =  data.get('folio_number')
        vehicle_name = data.get('vehicle_name')
        vehicle_tara = int(data.get('vehicle_tara'))
        trailer_name = data.get('trailer_name')
        equipo_tara = int(data.get('equipo_tara'))

        if vehicle_tara >0 and equipo_tara >0:
            self.logger.info(f"Cerrando folio con tara completa: {folio_number}")
            self.execute_closed_weighing_wrapper_automatic(data)
        elif vehicle_name =="SLRMQ-Solo remolque" and equipo_tara >0:
            self.logger.info(f"Cerrando folio solo remolque: {folio_number}")
            self.execute_closed_weighing_wrapper_automatic(data)
        elif vehicle_tara >0 and trailer_name =="Sin remolque":
            self.logger.info(f"Cerrando folio solo vehículo: {folio_number}")
            self.execute_closed_weighing_wrapper_automatic(data)
        else:
            self.logger.warning(f"No se puede cerrar automáticamente - Tara insuficiente: V={vehicle_tara}, R={equipo_tara}")
            messagebox.showerror(
                "Error en tara",
                 f"El folio {folio_number}.\nNo se puede cerrar de manera automatica\nLa tara del vehículo: {vehicle_name} es {vehicle_tara}\nLa tara del remolque: {trailer_name} es {equipo_tara}")
            self._clear_form_automatic()        
        
    def execute_closed_weighing_wrapper_automatic(self,data):
        """Ejecutar cierre automático de folio"""
        self.logger.info(f"Ejecutando cierre automático para folio: {data['folio_number']}")
        
        try:
            second_user_id = self.user_id 
            result = self.automatic_close.register_weighing_automatically_closed(data,second_user_id, self.db_manager, self.weighing_logic)
            
            if result['exito']:
                self.logger.info(f"Cierre automático exitoso: {data['folio_number']}")
                Send_to_print(result['updated_row'])
                messagebox.showinfo(
                    "Pesaje Registrado CWWA",
                    f"✅ Pesaje Folio: {data['folio_number']} cerrado exitosamente.",
                    parent=self.frame
                )
                self._clear_form_automatic()
                self.refresh_folio_list()
                return None
            else:
                self.logger.error(f"Error en cierre automático: {data['folio_number']}")
                messagebox.showerror(
                    "Error CWWA",
                    f"⚠️ CWWA-No se encontró el registro con Folio  {data['folio_number']} para cerrar.",
                    parent=self.frame
                )
                return None
                
        except Exception as e:
            self.logger.error(f"Error inesperado en cierre automático: {str(e)}", exc_info=True)
            messagebox.showerror(
                "Error Inesperado CWWA",
                f"❌ CWWA-Ocurrió un error inesperado:\n{str(e)}",
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
                logger.error(f"Error de impresión: {mensaje}")
                messagebox.showerror(
                    "Error",
                    f"⚠️ Problemas para imprimir el folio  {data['folio_number']}\n{mensaje_en_pantalla}",
                )
                return None
                
        except Exception as e:
            logger.error(f"Error inesperado en impresión: {str(e)}", exc_info=True)
            messagebox.showerror(
                "Error Inesperado",
                f"❌ Ocurrió un error inesperado:\n{str(e)}",
            )