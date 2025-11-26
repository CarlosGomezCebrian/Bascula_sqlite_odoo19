# ui_weighing_tab.py

import tkinter as tk
import datetime
from tkinter import ttk, messagebox  
from logic.logic_scale_manager import ScaleManager
from logic.logic_autocomplete import AutocompleteHandler
from logic.logic_weighing import WeighingLogic
from logic.logic_weighing_automatic_close import AutomaticClose
from logic.logic_print_folios import print_weighing_ticket
from db_operations.db_save_folio import WeighingDBManager
from logic.logic_tables_weighings import PendingWeighingsTable 

class PesajeTab:
    def __init__(self, notebook, styles, autocomplete_handler=None, user_id=None, user_access_level=None):
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

        
        # Primero definir el método de callback antes de crear ScaleManager
        self.update_weight_display = self._create_weight_display_callback()
        
        # Inyectar dependencias
        self.scale_manager = ScaleManager(update_callback=self.update_weight_display)
        self.weighing_logic = WeighingLogic(user_id=user_id)
        self.automatic_close = AutomaticClose(user_id=user_id)
        self._create_ui()
        self.pending_table = PendingWeighingsTable(self.table_container)
        self._setup_managers()
        self._update_date_title()
    
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
                    print(f"El peso sin texto:{weight_int}")
                    if weight_int <=0:
                        self.weight_status = False
                        self.entrada_button.config(state="disabled")
                        self.salida_button.config(state="disabled")
                        self.close_folio_button.config(state="disabled")
                        self._clear_form_automatic()
                    else:
                        print(f"El peso en else sin texto:{weight_int}")
                        self.weight_status = True
                        print(f"self.btn_status:{self.btn_status}")
                        if self.btn_status:
                            self.entrada_button.config(state="normal")
                            self.salida_button.config(state="normal")
                        #self._clear_form_automatic()
                        
                    print(f"[{timestamp}] ✅ UI Actualizada: {weight_text}")
                except Exception as e:
                    messagebox.showerror(
                        "Error Inesperado",
                        f"❌ BSC-Error actualizando UI:\n{str(e)}")
                    print(f"❌ BSC-Error actualizando UI: {e}")
            else:
                print(f"⚠️ Label de peso no disponible o destruido")
        
        return update_callback
    
    def _create_ui(self):
        """Solo creación de widgets visuales"""
        # Obtener fecha actual para el título
        self.fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.date_label = ttk.Label(
            self.frame, 
            text=f"Fecha y Hora Actual: {self.fecha_actual}", 
            font=("Helvetica", 10, "bold"),
            style="TLabel"
        )
        # Empaquetar en la parte superior del frame principal
        self.date_label.pack(fill=tk.X, padx=5, pady=(5, 0)) 
        
        self.entrada_frame = ttk.LabelFrame(
            self.frame, 
            text="Registro de Pesaje", # Título estático
            style="TFrame",
            padding=10
        )
        
        self.entrada_frame.pack(fill=tk.X, padx=5, pady=(5, 5))
        
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
        self.notes_entry = tk.Text(self.entrada_frame, font=("Helvetica", 10), borderwidth=0, width=40, height=4)
        self.notes_entry.grid(row=6, column=1, padx=5, pady=10)
        
        # Peso actual
        ttk.Label(self.entrada_frame, text="Peso actual:", style="TLabel").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
        self.weight_label = ttk.Label(self.entrada_frame, text="0 kg",  font=("Helvetica",30 , "bold"), foreground="green")
        self.weight_label.grid(row=7, column=1, padx=5, pady=5)
        
        # Controles de báscula
        self._create_scale_controls(self.entrada_frame)
        
        # Botones de acción
        self._create_action_buttons()

        # Contenedor para la tabla de pesajes pendientes
        self._create_pending_table_section()
    
    def _create_folio_section(self, parent):
        """Crear sección de folio dentro del LabelFrame"""
        folio_frame = ttk.Frame(parent, style="TFrame")
        folio_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        # Folio alineado a la izquierda
        ttk.Label(folio_frame, text="Folio:", style="TLabel",font=("Helvetica", 10, "bold")
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.folio_entry = tk.Entry(
            folio_frame, font=("Helvetica", 10), borderwidth=0,width=15,relief="solid", state="readonly", background="#f0f0f0")
        self.folio_entry.pack(side=tk.LEFT)
        # Botón para refrescar
        ttk.Button(folio_frame,text="Limpiar", width=10, cursor="hand2", command=self.refresh_folio_list
        ).pack(side=tk.RIGHT, padx=(5, 0))

        self.folio_entry.insert(0, "Pendiente")  # Valor inicial
    
    def _create_scale_controls(self, parent):
        """Controles específicos de la báscula"""
        scale_control_frame = ttk.Frame(parent, style="TFrame")
        scale_control_frame.grid(row=7, column=2, columnspan=2, pady=10)

        self.btn_scale_control = ttk.Button(scale_control_frame, text="▶ Conectar", style="Warning.TButton",
                                    cursor="hand2",  width=15, command=self._connect_disconnect)
        self.btn_scale_control.pack(side=tk.LEFT, padx=5) 

        self.scale_status_label = ttk.Label(scale_control_frame, text="Desconectada", style="TLabel")
        self.use_simulator_var = tk.BooleanVar(value=False)
        self.check_active = ttk.Checkbutton(scale_control_frame, text="Simulador de desactivado",  
                                   variable=self.use_simulator_var,  style="Orange.TCheckbutton",  command=self._on_simulator_changed)
    
        self.scale_status_label.pack(side=tk.LEFT, padx=10)
        if  self.user_access_level > 3:
            self.check_active.pack(side=tk.LEFT, padx=10)

    def _connect_disconnect(self):
        """Conectar  y desconectar la bascula"""
        current_text = self.btn_scale_control.cget('text')
        if current_text == "⏹ Desconectar":            
            self.scale_manager.disconnect()
            
        else: 
            self.scale_manager.connect()

    def _on_simulator_changed(self):
        """Callback cuando cambia el estado del checkbox del simulador"""
        use_simulator = self.use_simulator_var.get()
        self.scale_manager.set_use_simulator(use_simulator)
        self.weighing_logic.update_use_simulator(use_simulator)
        if use_simulator:
            self.check_active.config(text="Simulador de activado", style="Green.TCheckbutton" )
        else:
            self.check_active.config(text="Simulador de desactivado", style="Orange.TCheckbutton" )        

        
    def _create_action_buttons(self):
        """Botones de acción del pesaje"""
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
        
        self.cancel_button = ttk.Button(action_frame, text="Cancelar", cursor="hand2",
                command=self.clear_form,
                style="Warning.TButton")
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        self.close_folio_button = ttk.Button(action_frame, text="Cerrar folio", cursor="hand2",
                command=lambda:self.closed_weighing_wrapper(), 
                style="TButton",state="disabled")
        self.close_folio_button.pack(side=tk.LEFT, padx=5)

        if self.user_access_level >=3:
            self.close_tara_button = ttk.Button(action_frame, text="Cerrar c/tara", cursor="hand2",
                command=lambda:self.closed_weighing_wrapper_automatic(), 
                style="Warning.TButton",state="disabled")
            self.close_tara_button.pack(side=tk.RIGHT, padx=5)

            

    def _handle_autocomplete_selection(self, selected_value, entry_type):
        """
        Callback ejecutado al seleccionar un valor en los campos Chofer, Cliente, Material o Vehículo.
        Si el valor es '... externo', inserta una etiqueta en el campo Notas.
        """
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
            notes_text_widget.config(state="normal")
            
            # Obtener todo el texto actual
            current_text = notes_text_widget.get('1.0', tk.END).strip()
            
            # Verificar si la etiqueta ya existe en alguna parte del texto
            # Usamos un marcador fácil de encontrar para verificar existencia
            if INSERT_TEXT_LABEL.strip() not in current_text:
                
                # Prepara el nuevo texto con el marcador y un salto de línea
                new_text = INSERT_TEXT_LABEL + "\n"
                
                # Limpiar el campo
                notes_text_widget.delete('1.0', tk.END) 
                
                # 1. Insertar la nueva etiqueta al inicio
                notes_text_widget.insert('1.0', new_text)
                
                # 2. Reinsertar el texto que ya existía si no está vacío
                if current_text:
                    # Insertamos a partir de la línea 2, posición 0 ('2.0')
                    # Nota: Si el texto actual ya tenía una de las otras etiquetas, se mantendrá.
                    notes_text_widget.insert('2.0', current_text + "\n")

            # Colocar el cursor de inserción al inicio del texto (posición 1.X, donde X es el final de la etiqueta)
            # Primero nos aseguramos de que haya foco en el widget para obtener la posición.
            notes_text_widget.focus_set()
            
            # Buscar dónde debería ir el cursor (al final de la etiqueta recién insertada o ya existente)
            # Usamos search para encontrar la posición
            insert_pos = notes_text_widget.search(INSERT_TEXT_LABEL, "1.0", tk.END, nocase=True)
            
            if insert_pos:
                # Mueve el cursor al final de la etiqueta encontrada
                end_pos = f"{insert_pos}+{len(INSERT_TEXT_LABEL)}c"
                notes_text_widget.mark_set(tk.INSERT, end_pos)
            else:
                 # Si no se encontró, solo lo ponemos al final del campo
                 notes_text_widget.mark_set(tk.INSERT, tk.END)
                
        # Si no es un valor externo, no se hace nada para no modificar las notas.


    def _setup_managers(self):
        """Configurar los managers después de crear la UI"""
        
        self.scale_manager.set_status_label(self.scale_status_label,  self.btn_scale_control)

        use_simulator = self.use_simulator_var.get()
        self.scale_manager.set_use_simulator(use_simulator)


        self.weighing_logic.set_simulator_checkbox(self.use_simulator_var)
        self.weighing_logic.set_scale_manager(self.scale_manager)

        # Pasar referencia al autocomplete handler
        self.weighing_logic.set_autocomplete_handler(self.autocomplete_handler)
        self._set_initial_folio()

        if hasattr(self.vehicle_entry, 'set_select_callback'):
             # Usamos lambda para pasar 'vehicle' como tipo
             self.vehicle_entry.set_select_callback(lambda val: self._handle_autocomplete_selection(val, 'vehicle')) 

        # DRIVER (Chofer externo)
        if hasattr(self.driver_entry, 'set_select_callback'):
             # Usamos lambda para pasar 'driver' como tipo
             self.driver_entry.set_select_callback(lambda val: self._handle_autocomplete_selection(val, 'driver'))

        # CUSTOMER (Cliente externo)
        if hasattr(self.customer_entry, 'set_select_callback'):
             # Usamos lambda para pasar 'customer' como tipo
             self.customer_entry.set_select_callback(lambda val: self._handle_autocomplete_selection(val, 'customer'))

        # MATERIAL (Material externo)
        if hasattr(self.material_entry, 'set_select_callback'):
             # Usamos lambda para pasar 'material' como tipo
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

    def set_entry_state(self, entry_widget, state):
        """Helper para establecer el estado (normal/readonly/disabled) en Entry estándar o CustomAutocompleteEntry.

        Args:
            entry_widget: El widget de entrada (tk.Entry, ttk.Entry o CustomAutocompleteEntry).
            state (str): El estado deseado ('normal', 'readonly' o 'disabled').
        """
        # Si tiene el atributo 'entry', es un CustomAutocompleteEntry
        if hasattr(entry_widget, 'entry'):
            entry_widget.entry.config(state=state)
        # Si es un Entry estándar (tk.Entry o ttk.Entry)
        elif hasattr(entry_widget, 'config'):
            entry_widget.config(state=state)       

    
    def on_table_folio_selected(self, folio_data):
        """Manejar selección de folio desde la tabla"""
        if folio_data is None:
            self.clean_form_fields_for_new_folio(confirm=False)
            self.update_buttons_state(None) # Opcional: Asegurar que los botones vuelvan a 'normal'
            return

        try:

            if isinstance(folio_data, dict) and 'folio_number' in folio_data:
                
                self.load_folio_data(folio_data)
            else: 
                print(f"--- DEBUG ERROR: Datos de tabla no tienen el formato esperado. {folio_data}")
        except Exception as e:
            print(f"--- DEBUG ERROR: Excepción al cargar datos desde tabla: {e}")
            self.lock_form_fields()

    def set_entry_value(self, entry_widget, value):
        """Función auxiliar para establecer valor en Entry normal o CustomAutocompleteEntry."""
        # Los CustomAutocompleteEntry tienen un método .set()
        self.unlock_form_fields()
        if hasattr(entry_widget, 'set'):
            entry_widget.set(value)
        # Para Entry normales (como placa_entry), deshabilitamos/habilitamos para escribir

        elif isinstance(entry_widget, tk.Text): 
            entry_widget.config(state="normal")
            entry_widget.delete('1.0', tk.END) # 👈 Importante: Usar '1.0' y tk.END
            entry_widget.insert('1.0', value)

        elif hasattr(entry_widget, 'delete'): 
            entry_widget.config(state="normal")
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, value if value is not None else "")
            entry_widget.config(state="readonly")

    def lock_form_fields(self):
        """Bloquear todos los campos para prevenir manipulación"""
        lock_list = [
            self.folio_entry,
            self.vehicle_entry,
            self.trailer_entry, 
            self.driver_entry, 
            self.customer_entry, 
            self.material_entry
        ]
        for field in lock_list:
            # Llama al helper para establecer el estado "readonly"
            self.set_entry_state(field, "readonly")    


    def load_folio_data(self, folio_data):
        """Cargar todos los datos de un folio seleccionado en la UI."""       
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
        self.folio_entry.config(state="normal")
        self.folio_entry.delete(0, tk.END)
        self.folio_entry.insert(0, str(folio))
        self.folio_entry.config(state="readonly")
    
    def _validate_required_fields(self, tipo_pesaje):
        """Validar campos obligatorios con messagebox"""
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
            messagebox.showerror(
                "Campos Obligatorios",
                f"Los siguientes campos son obligatorios y están vacíos:\n{campos_texto}\n\nPor favor, complete todos los campos antes de registrar el pesaje de {tipo_pesaje}.",
                parent=self.frame
            )
            return False
        
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
        # Frame contenedor para la tabla
        self.table_container = ttk.Frame(self.frame, style="TFrame", padding=5)
        self.table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def refresh_folio_list(self):
        """Refrescar la lista de folios pendientes"""
        if hasattr(self, 'folio_selector'):
            self.folio_selector.refresh_folios()
        
        if hasattr(self, 'pending_table'):
            self.pending_table.refresh_table()
        
        # Actualizar también el folio actual
        self._clear_form_automatic()
        self._set_initial_folio()
    
    def register_weighing_wrapper(self, tipo_pesaje):
        """Método wrapper para registrar pesaje con db_manager"""
        # Validar campos obligatorios primero
        if not self._validate_required_fields(tipo_pesaje):
            return None
        
        try:
            # Registrar el pesaje
            exito, weighing_data = self.weighing_logic.register_weighing(tipo_pesaje, self.db_manager)
            
            if exito and weighing_data:
                messagebox.showinfo(
                    "Pesaje Registrado",
                    f"✅ Pesaje de {tipo_pesaje} registrado exitosamente\n\nFolio: {weighing_data.folio}",
                    parent=self.frame
                )
                self._clear_form_automatic()
                self.refresh_folio_list()
                return weighing_data
            else:
                messagebox.showerror(
                    "Error",
                    f"❌ Error al registrar pesaje de {tipo_pesaje}",
                    parent=self.frame
                )
                return None
                
        except Exception as e:
            messagebox.showerror(
                "Error Inesperado",
                f"❌ ui_Ocurrió un error inesperado:\n{str(e)}",
                parent=self.frame
            )
            print(f"❌ ui_Ocurrió un error inesperado:\n{str(e)}")
            return None
        
    def _clear_form_automatic(self):
        """Limpiar formulario automáticamente sin confirmación"""
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
        # 1. Lógica para CustomAutocompleteEntry (usando .set(""))
            if hasattr(campo, 'set'):
                campo.set("")
            
            # 2. Lógica para tk.Text (usando delete('1.0', tk.END))
            #    Necesitamos importar 'tk' para usar isinstance(campo, tk.Text)
            elif isinstance(campo, tk.Text):
                campo.delete('1.0', tk.END) # <--- CORRECCIÓN CLAVE para tk.Text
            
            # 3. Lógica para tk.Entry y ttk.Entry estándar (usando delete(0, tk.END))
            elif hasattr(campo, 'delete') and hasattr(campo, 'insert'):
                campo.delete(0, tk.END) # <--- CORRECCIÓN CLAVE para tk.Entry
            
        # Obtener nuevo folio
        nuevo_folio = self.db_manager.get_next_folio()
        self.set_folio(nuevo_folio)
        
        # Restablecer botones a estado normal
        if  self.weight_status:
            self.btn_status = True
            self.entrada_button.config(state="normal")
            self.salida_button.config(state="normal")
            self.close_folio_button.config(state="disabled")
            if self.user_access_level >=3:
                self.close_tara_button.config(state="disabled")   
        

    
    def unlock_form_fields(self):
        """Desbloquear todos los campos del formulario"""        
        # Desbloquear autocomplete entries
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
        # Confirmar con el usuario
        respuesta = messagebox.askyesno(
            "Limpiar Formulario",
            "¿Está seguro de que desea limpiar todos los campos del formulario?",
            parent=self.frame
        )
        
        if respuesta:
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
        # 1. Lógica para CustomAutocompleteEntry (usando .set(""))
            if hasattr(campo, 'set'):
                campo.set("")
            
            # 2. Lógica para tk.Text (usando delete('1.0', tk.END))
            #    Necesitamos importar 'tk' para usar isinstance(campo, tk.Text)
            elif isinstance(campo, tk.Text):
                campo.delete('1.0', tk.END) # <--- CORRECCIÓN CLAVE para tk.Text
            
            # 3. Lógica para tk.Entry y ttk.Entry estándar (usando delete(0, tk.END))
            elif hasattr(campo, 'delete') and hasattr(campo, 'insert'):
                campo.delete(0, tk.END) # <--- CORRECCIÓN CLAVE para tk.Entry
            
            # Obtener nuevo folio
            nuevo_folio = self.db_manager.get_next_folio()
            self.set_folio(nuevo_folio)
            
            # Restablecer botones
            if self.weight_status:
                self.btn_status = True
                self.entrada_button.config(state="normal")
                self.salida_button.config(state="normal")
                self.close_folio_button.config(state="disabled")
                if self.user_access_level >=3:
                    self.close_tara_button.config(state="disabled")
            

    def update_buttons_state(self, weighing_type):
        """Actualizar estado de los botones según el tipo de pesada"""
        if self.weight_status:
            self.btn_status = False
            self.entrada_button.config(state="disabled")
            self.salida_button.config(state="disabled")
            self.close_folio_button.config(state="normal")
            if weighing_type == "Entrada" and self.user_access_level >=3:            
                self.close_tara_button.config(state="normal")
            elif weighing_type != "Entrada" and self.user_access_level >=3:
                self.close_tara_button.config(state="disabled")
        
    def get_frame(self):
        return self.frame
    


    def clean_form_fields_for_new_folio(self, confirm=True):
        """Limpia el formulario, desbloquea los campos, establece un nuevo folio 
        y restablece el estado de los botones.
        
        Args:
            confirm (bool): Si es True, muestra una ventana de confirmación antes de limpiar.
                            Se usa 'False' cuando se llama internamente (ej: deselección de tabla).
        """
        
        # 1. Confirmación (si es necesaria)
        if confirm:
            respuesta = messagebox.askyesno(
                "Confirmación",
                "¿Desea limpiar todos los campos del formulario para iniciar un nuevo pesaje?",
                parent=self.frame
            )
            if not respuesta:
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
        # 1. Lógica para CustomAutocompleteEntry (usando .set(""))
            if hasattr(campo, 'set'):
                campo.set("")
            
            # 2. Lógica para tk.Text (usando delete('1.0', tk.END))
            #    Necesitamos importar 'tk' para usar isinstance(campo, tk.Text)
            elif isinstance(campo, tk.Text):
                campo.delete('1.0', tk.END) # <--- CORRECCIÓN CLAVE para tk.Text
            
            # 3. Lógica para tk.Entry y ttk.Entry estándar (usando delete(0, tk.END))
            elif hasattr(campo, 'delete') and hasattr(campo, 'insert'):
                campo.delete(0, tk.END) # <--- CORRECCIÓN CLAVE para tk.Entry

        nuevo_folio = self.db_manager.get_next_folio()
        self.set_folio(nuevo_folio)
        
        # 5. Restablecer botones (Estado Normal: Ambos habilitados, Cerrar deshabilitado)
        self.update_buttons_state(None) # Pasa None para indicar el estado por defecto
        
        # 6. Mostrar mensaje de éxito (si se pasó la confirmación)
        if confirm:
            messagebox.showinfo(
                "Formulario Limpio",
                "✅ Todos los campos han sido limpiados y el folio ha sido actualizado.",
                parent=self.frame
            )

    def closed_weighing_wrapper(self):
        """Método datos para cerrar folio"""
        
        data = self.data_closed_weighing
        second_user_id = self.user_id 
        
        try:
            # Registrar el pesaje
            result = self.weighing_logic.register_closed_weighing(data,second_user_id, self.db_manager)
            
            
            if result['exito']:
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
                messagebox.showerror(
                    "Error",
                    f"⚠️ No se encontró el registro con Folio  {data['folio_number']} para cerrar.",
                    parent=self.frame
                )
                return None
                
        except Exception as e:
            messagebox.showerror(
                "Error Inesperado",
                f"❌ CSW-Ocurrió un error inesperado:\n{str(e)}",
                parent=self.frame
            )
            print(f"❌ CSW-Ocurrió un error inesperado:\n{str(e)}")
        return None

    def closed_weighing_wrapper_automatic(self):
        """Método datos para cerrar folio con tara"""
                
        data = self.data_closed_weighing
        folio_number =  data.get('folio_number')
        vehicle_name = data.get('vehicle_name')
        vehicle_tara = int(data.get('vehicle_tara'))
        trailer_name = data.get('trailer_name')
        equipo_tara = int(data.get('equipo_tara'))

        if vehicle_tara >0 and equipo_tara >0:
            print(f"Los datos para cerrar son:{data}")
            self.execute_closed_weighing_wrapper_automatic(data)
        elif vehicle_name =="SLRMQ-Solo remolque" and equipo_tara >0:
            print(f"Los datos para cerrar son:{data}")
            self.execute_closed_weighing_wrapper_automatic(data)
        elif vehicle_tara >0 and trailer_name =="Sin remolque":
            print(f"Los datos para cerrar son:{data}")
            self.execute_closed_weighing_wrapper_automatic(data)

        else:
            messagebox.showerror(
                "Error en tara",
                 f"El folio {folio_number}.\nNo se puede cerrar de manera automatica\nLa tara del vehículo: {vehicle_name} es {vehicle_tara}\nLa tara del remolque: {trailer_name} es {equipo_tara}")
            self._clear_form_automatic()        
        
    def execute_closed_weighing_wrapper_automatic(self,data):
        try:
            # Registrar el pesaje
            second_user_id = self.user_id 
            result = self.automatic_close.register_weighing_automatically_closed(data,second_user_id, self.db_manager, self.weighing_logic)
            
            
            if result['exito']:
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
                messagebox.showerror(
                    "Error CWWA",
                    f"⚠️ CWWA-No se encontró el registro con Folio  {data['folio_number']} para cerrar.",
                    parent=self.frame
                )
                return None
                
        except Exception as e:
            messagebox.showerror(
                "Error Inesperado CWWA",
                f"❌ CWWA-Ocurrió un error inesperado:\n{str(e)}",
                parent=self.frame
            )
            print(f"❌ CWWA-Ocurrió un error inesperado:\n{str(e)}")
        return None
           

def Send_to_print(data):
    if data:                    
            try:
               exito, e = print_weighing_ticket(data)              
               
               if exito:
                  data ={}

                  return None
               else:
                  #mensaje_text= "not found or cable not plugged in"
                  mensaje_text="Impresora no conectada"
                  mensaje = str(e)
                  if mensaje_text in mensaje:
                      mensaje_en_pantalla = "La impresora no se encuentra\n o el cable no esta conectado"
                  messagebox.showerror(
                     "Error",
                     # parent=self.frame
                     f"⚠️ Problemas para imprimir el folio  {data['folio_number']}\n{mensaje_en_pantalla}",
                  )
                  return None
                  
            except Exception as e:
                  messagebox.showerror(
                  "Error Inesperado",
                  f"❌ Ocurrió un error inesperado:\n{str(e)}",
                  #parent=self.frame
               )
                  print("Error Inesperado",
                  f"❌ Ocurrió un error inesperado:\n{str(e)}",)            