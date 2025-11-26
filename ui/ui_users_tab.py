# ui_user_tab.py

import tkinter as tk
from tkinter import ttk, messagebox 
import datetime
from db_operations.db_save_folio import WeighingDBManager
from logic.logic_tables_users import UsersTable
from ui.ui_dialog_windows import  DialogWindows 

class UsersTab:
    def __init__(self, notebook, styles, user_id=None, user_access_level=None):
        self.styles = styles
        self.frame = ttk.Frame(notebook, style="TFrame")
        notebook.add(self.frame, text="Usuarios")
        self.user_id = user_id
        self.user_table_id = None
        self.user_access_level = int(user_access_level)
        self.data_closed_weighing = None         
        self.db_manager = WeighingDBManager()
        self._create_ui()
        self.menu_handlers = DialogWindows(self.frame.winfo_toplevel())
        self.users_table = UsersTable(self.table_container)
        self._setup_managers()      
    
    
    def _create_ui(self):
        """Solo creación de widgets visuales"""
        # Obtener fecha actual para el título
        fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y")
        
        # Frame principal con fecha en el título
        entrada_frame = ttk.LabelFrame(
            self.frame, text="Usuarios", 
            style="TFrame",padding=10)
        
        entrada_frame.pack(fill=tk.X, padx=5, pady=5)
               

        # User_name
        ttk.Label(entrada_frame, text="Nombre de usuario:", style="TLabel").grid(row=1, column=0, sticky=tk.W, padx=5, pady=10)
        self.entry_user_name = tk.Entry(entrada_frame,font=("Helvetica", 10), borderwidth=0, width=30,   state="readonly")
        self.entry_user_name.grid(row=1, column=1, padx=5, pady=10, sticky='ew')
        
        # User_email
        #ttk.Label(entrada_frame, text="Vehículo:", style="TLabel").grid(row=1, column=0, sticky=tk.W, padx=5, pady=10)
        ttk.Label(entrada_frame, text="Correo de usuario:", style="TLabel").grid(row=2, column=0, sticky=tk.W, padx=5, pady=10)
        self.entry_user_email = tk.Entry(entrada_frame,font=("Helvetica", 10), borderwidth=0, width=30, state="readonly")
        self.entry_user_email.grid(row=2, column=1, padx=5, pady=10, sticky='ew')
        #creation_date
        ttk.Label(entrada_frame, text="Fecha creación:", style="TLabel").grid(row=3, column=0, sticky=tk.W, padx=5, pady=10)
        self.entry_creation_date = tk.Entry(entrada_frame,font=("Helvetica", 10), borderwidth=0, width=30, state="readonly")
        self.entry_creation_date.grid(row=3, column=1, padx=5, pady=10, sticky='ew')
        
        
        #access_level
        ttk.Label(entrada_frame, text="Tipo de usuario:", style="TLabel").grid(row=4, column=0, sticky=tk.W, padx=5, pady=10)
        self.combo_access_level = ttk.Combobox(entrada_frame, values=["1 - Báscula", "2 - Odoo", "3 - Administrador"], state="readonly")
        self.combo_access_level.set("1 - Báscula")
        self.combo_access_level.grid(row=4, column=1, pady=5, sticky="ew")
        self.active_use = tk.BooleanVar(value=False)
        self.check_active =ttk.Checkbutton(entrada_frame, text="Desactivado", variable=self.active_use, style="Orange.TCheckbutton", command=self._on_user_changed)
        self.check_active.grid(row=5, column=1, pady=5, sticky="ew")
        
        
        
        self._create_action_buttons()
        self._create_users_table_section()
        
    
    def _create_action_buttons(self):
        """Botones de acción del pesaje"""
        action_frame = ttk.Frame(self.frame, style="TFrame", padding=5)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Guardar referencias a los botones state="disabled
        self.entrada_button = ttk.Button(action_frame, text="Registrar usuario", cursor="hand2", 
                command=self._add_user, 
                style="TButton")
        self.entrada_button.pack(side=tk.LEFT, padx=5)
        
        self.btn_update_user = ttk.Button(action_frame, text="Modificar usuario", cursor="hand2", 
                command= self._update_user, 
                style="Primary.TButton")
        self.btn_update_user.pack(side=tk.LEFT, padx=5)
        
        self.btn_reset = ttk.Button(action_frame, text="Restablecer contraseña", cursor="hand2",
                command=self._reset_password,
                style="Warning.TButton")
        self.btn_reset.pack(side=tk.LEFT, padx=5)

    
    def _setup_managers(self):
        self.users_table.set_row_select_callback(self.on_table_user_selected)
        

    def _add_user(self):
        self.menu_handlers.add_user(self.user_id)    
        
    def _on_user_changed(self):
        """Callback cuando cambia el estado del checkbox del usuario"""
        user_status_value = self.active_use.get()        
        if user_status_value:
            self.check_active.config(text="Usuario activado", style="Green.TCheckbutton")
        else:
            self.check_active.config(text="Usuario desactivado", style="Orange.TCheckbutton")
        
    def on_table_user_selected(self, user_data):
        """Manejar selección de folio desde la tabla"""
        print(f"los datos en on_table_user_selected: {user_data}")
        if user_data is None:
            self.clean_form_fields(confirm=False)
            return

        try:
            if isinstance(user_data, dict) and 'id_user' in user_data:
                
                self.load_user_data(user_data)
            else: 
                print(f"--- DEBUG ERROR: Datos de tabla no tienen el formato esperado. {user_data}")
        except Exception as e:
            print(f"--- DEBUG ERROR: Excepción al cargar datos desde tabla: {e}")
            #self.lock_form_fields()

    def set_entry_value(self, entry_widget, value):
        """Función auxiliar para establecer valor en Entry normal o CustomAutocompleteEntry."""
        # Los CustomAutocompleteEntry tienen un método .set()
        self.unlock_form_fields()
        
        if hasattr(entry_widget, 'set'):
            entry_widget.set(value)
        elif isinstance(entry_widget, tk.Text): 
            entry_widget.config(state="normal")
            entry_widget.delete('1.0', tk.END)
            entry_widget.insert('1.0', value)
        elif isinstance(entry_widget, ttk.Combobox):
            # Para Combobox, simplemente establecer el valor
            entry_widget.set(value if value is not None else "")
        elif hasattr(entry_widget, 'delete'): 
            entry_widget.config(state="normal")
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, value if value is not None else "")
            entry_widget.config(state="readonly")

    def load_user_data(self, user_data):
        """Cargar todos los datos de un usuario seleccionado en la UI."""       
        self.set_entry_value(self.entry_user_name, user_data.get('user_name', ''))        
        self.set_entry_value(self.entry_user_email, user_data.get('user_email', ''))
        self.set_entry_value(self.entry_creation_date, user_data.get('creation_date', ''))
        
        # Manejar el nivel de acceso (combobox)
        access_level = user_data.get('access_level', '1')
        self.user_table_id = user_data.get('id_user')
        
        # Convertir a string si es necesario y mapear al valor del combobox
        if isinstance(access_level, int):
            access_level = str(access_level)
        
        # Mapear el valor numérico al texto del combobox
        access_level_map = {
            '1': "1 - Báscula",
            '2': "2 - Odoo", 
            '3': "3 - Administrador"
        }
        
        combo_value = access_level_map.get(access_level, "1 - Báscula")
        self.combo_access_level.set(combo_value)        
        # Manejar el estado activo/inactivo
        user_status = user_data.get('active_user', '0')        
        # Convertir a entero si es string
        if isinstance(user_status, str):
            try:
                user_status = int(user_status)
            except ValueError:
                user_status = 0
        
        # Establecer el valor del checkbox
        if user_status == 1:
            self.active_use.set(True)
        else:
            self.active_use.set(False)
        
        # Actualizar la apariencia del checkbox
        self._on_user_changed()
        
        self.lock_form_fields()    

    
    def update_date_title(self):
        """Método para actualizar la fecha en el título (puede ser llamado periódicamente)"""
        fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    

    
    def _get_value_entry(self, campo):
        """Obtener valor de un campo del formulario"""
        entry_map = {
            'user_name': self.entry_user_name,
            'user_email': self.entry_user_email,
            'creation_date':  self.entry_creation_date
        }
        
        if campo in entry_map:
            entry = entry_map[campo]
            if hasattr(entry, 'get'):
                return entry.get().strip()
        return ""
    

    def _update_user(self):
        user_table_id = self.user_table_id
        user_name = self.entry_user_name.get()
        user_email = self.entry_user_email.get()
        user_status_value = self.active_use.get()
        #password = self.entry_password.get()
        password =f"{user_name}123"
        selected_level_str = self.combo_access_level.get()
        access_level = int(selected_level_str.split(' ')[0])
        user_id =self.user_id
        active_user = 1 if user_status_value else 0
        if user_table_id and user_name and user_email:
            self.users_table.update_user(user_table_id, user_name, user_email, access_level, active_user, user_id)
        else:
            messagebox.showerror("Error", "Todos los campos son obligatorios.") 



    def _reset_password(self):
        user_table_id = self.user_table_id
        user_name = self.entry_user_name.get()
        user_id =self.user_id
        if user_table_id and user_name and user_id:
            self.users_table.reset_password(user_table_id, user_name, user_id)
        else:
            messagebox.showerror("Error", "No se selecciono usuario") 
        
    
    def _create_users_table_section(self):
        """Crear sección para la tabla de pesajes pendientes"""
        # Frame contenedor para la tabla
        self.table_container = ttk.Frame(self.frame, style="TFrame", padding=5)
        self.table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def refresh_folio_list(self):
        """Refrescar la lista de folios pendientes"""
        if hasattr(self, 'folio_selector'):
            self.folio_selector.refresh_folios()
        
        if hasattr(self, 'users_table'):
            self.users_table.refresh_table()
        
        # Actualizar también el folio actual
        self.clear_form_automatic()
    
    
        
    def clear_form_automatic(self):
        """Limpiar formulario automáticamente sin confirmación"""
        # Desbloquear campos primero
        self.unlock_form_fields()
        
        # Limpiar campos
        clear_fields = [
            self.entry_user_name,
            self.entry_user_email,
            self.entry_creation_date
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
        self.entrada_button.config(state="normal")
        self.salida_button.config(state="normal")
        self.close_folio_button.config(state="disabled")
        if self.user_access_level >=3:
            self.close_tara_button.config(state="disabled")   



    def lock_form_fields(self):
        """Bloquear todos los campos para prevenir manipulación"""
        lock_list = [
            #self.entry_user_name, 
            #self.entry_user_email, 
            self.entry_creation_date,
            self.combo_access_level  # Añadir el combobox a la lista
        ]
        for field in lock_list:
            # Llama al helper para establecer el estado "readonly"
            self.set_entry_state(field, "readonly")  


    def set_entry_state(self, widget, state):
        """Establecer el estado de un widget (normal, readonly, disabled)"""
        if isinstance(widget, ttk.Combobox):
            widget.config(state=state)
        elif hasattr(widget, 'config'):
            widget.config(state=state)          

    
    def unlock_form_fields(self):
        """Desbloquear todos los campos del formulario"""
        # Desbloquear campos de entrada
        self.entry_user_name.config(state="normal", background="white")
        self.entry_user_email.config(state="normal", background="white")
        self.entry_creation_date.config(state="normal", background="white")
        
        
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
                self.entry_user_name,
                self.entry_user_email,
                self.entry_creation_date,
            ]

        for campo in clear_fields:
            campo.delete(0, tk.END) 
            
            
            
    def get_frame(self):
        return self.frame
    


    def clean_form_fields(self, confirm=True):
        """Limpia el formulario, bloquea los campos,
        y restablece el estado de los botones.
        
        Args:
            confirm (bool): Si es True, muestra una ventana de confirmación antes de limpiar.
                            Se usa 'False' cuando se llama internamente (ej: deselección de tabla).
        """
        
        # 1. Confirmación (si es necesaria)
        if confirm:
            respuesta = messagebox.askyesno(
                "Confirmación",
                "¿Desea limpiar todos los campos del formulario?",
                parent=self.frame
            )
            if not respuesta:
                return 
        """
        # 2. Desbloquear campos
        self.unlock_form_fields()
        
        # 3. Limpiar campos
        clear_fields = [
            self.placa_entry,
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
    """
    