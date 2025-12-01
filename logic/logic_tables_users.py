# logic_tables_users.py
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from db_operations.db_users import Users

class UsersTable:
    def __init__(self, parent_frame, styles=None):
        self.parent_frame = parent_frame
        self.styles = styles
        self.tree = None
        self.row_select_callback = None
        self.db_user = Users()
        self.create_table()
        self.load_users()


    def set_row_select_callback(self, callback):
        """Permite que PesajeTab inyecte la función para cargar el folio."""
        self.row_select_callback = callback
    
    def create_table(self):
        """Crear la tabla Treeview para mostrar pesajes pendientes con estilos mejorados"""
        # Frame principal para la tabla
        main_frame = ttk.Frame(self.parent_frame, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame para el título y controles
        header_frame = ttk.Frame(main_frame, style="TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Label de título con estilo mejorado
        title_label = ttk.Label(
            header_frame, 
            text="Usuarios",
            font=("Helvetica", 12),
            style="TLabel"
        )
        title_label.pack(side=tk.LEFT)
        
        # Botón de refresh
        refresh_btn = ttk.Button(
            header_frame,
            text="Actualizar",
            cursor="hand2",
            command=self.refresh_table,
            width=12
        )
        refresh_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Contador de registros
        self.count_label = ttk.Label(
            header_frame,
            text="Cargando...",
            font=("Helvetica", 12),
            foreground="#7f8c8d"
        )
        self.count_label.pack(side=tk.RIGHT, padx=10)
        
        # Frame para la tabla y scrollbars
        table_container = ttk.Frame(main_frame, style="TFrame")
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Configurar columnas
        columns = (
            'id', 'user_name', 'creation_date', 'user_email', 'access_level', 'active_user', 'user_create'
        )
        
        # Crear Treeview con estilo mejorado
        self.tree = ttk.Treeview(
            table_container, 
            columns=columns,
            show='headings',
            height=10,
            selectmode='browse'
        )
        
        # Configurar estilos para el Treeview
        self.configure_treeview_styles()
        
        # Configurar columnas con anchos optimizados
        column_config = {
            'id': ('Id',0, 'center'),
            'user_name': ('Nombre',70 , 'w'),            
            'creation_date':('Fecha de creación',50, 'w'),
            'user_email': ('Correo', 50, 'w'),
            'access_level':('Tipo de usuario',30, 'w'),
            'active_user': ('Esta activo',30 , 'w'),
            'user_create': ('Creado por', 50, 'w')
        }

        for col, (heading, width, anchor) in column_config.items():
            # CONFIGURACIÓN DEL ENCABEZADO: Usar el mismo 'anchor' ('w' para izquierda)
            self.tree.heading(col, text=heading, anchor=anchor)             
            # CONFIGURACIÓN DE LOS DATOS DE LA COLUMNA
            if col == 'id':
                 # Ocultar 'id'
                 self.tree.column(col, width=0, minwidth=0, anchor=anchor, stretch=tk.NO)
            else:
                 self.tree.column(col, width=width, minwidth=width, anchor=anchor)
        """
        for col, (heading, width, anchor) in column_config.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, minwidth=width, anchor=anchor)
        """
        # Scrollbar vertical
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Scrollbar horizontal
        h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Empaquetar usando grid para mejor control
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configurar weights para expansión
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Vincular eventos
        #self.tree.bind('<Double-1>', self.on_row_select)
        self.tree.bind('<<TreeviewSelect>>', self._on_selection_change)
        self.tree.winfo_toplevel().bind_all('<Button-1>', self.check_click_outside_table, add='+')
        
        # Tooltip para items largos
        self.setup_tooltip()

    def check_click_outside_table(self, event):
        """Verifica si un clic ocurrió fuera de la tabla Treeview y deselecciona."""        
        # Obtener coordenadas de la tabla Treeview
        tx, ty = self.tree.winfo_rootx(), self.tree.winfo_rooty()
        tw, th = self.tree.winfo_width(), self.tree.winfo_height()
        
        # Comprobar si el clic está fuera de la tabla
        is_outside = not (tx <= event.x_root < tx + tw and ty <= event.y_root < ty + th)
        
        if is_outside:
            self.load_users() 
            

    
    def configure_treeview_styles(self):
        """Configurar estilos visuales para el Treeview"""
        style = ttk.Style()
        
        # Estilo para el Treeview
        style.configure(
            "Custom.Treeview",
            background="#ffffff",
            foreground="#2c3e50",
            rowheight=25,
            font=("Helvetica", 10),
            fieldbackground="#ffffff",
            bordercolor="#333333",
            borderwidth=1
        )
        
        style.configure(
            "Custom.Treeview.Heading",
            background="#714B67",
            foreground="#ecf0f1",
            relief="flat",
            font=("Helvetica", 10, "bold")
        )
        
        style.map(
            "Custom.Treeview.Heading",
            background=[('active', '#714B67'), ('pressed', '#714B67')]
        )
        
        style.map(
            "Custom.Treeview",
            background=[('selected', '#3498db')],
            foreground=[('selected', 'white')]
        )
        
        # Aplicar el estilo
        self.tree.configure(style="Custom.Treeview")
    
    def setup_tooltip(self):
        """Configurar tooltip para mostrar texto completo en celdas largas"""
        self.tooltip = tk.Toplevel(self.parent_frame)
        self.tooltip.withdraw()
        self.tooltip.overrideredirect(True)
        self.tooltip.configure(bg='#ffffe0', relief='solid', bd=1)
        
        self.tooltip_label = tk.Label(
            self.tooltip, 
            text="", 
            bg='#ffffe0', 
            fg='#2c3e50',
            font=("Helvetica", 9),
            justify='left'
        )
        self.tooltip_label.pack(padx=2, pady=1)
        
        self.tree.bind('<Motion>', self.on_motion)
        self.tree.bind('<Leave>', self.on_leave)
    
    def on_motion(self, event):
     """Manejar movimiento del mouse para tooltip"""
     try:
         item = self.tree.identify_row(event.y)
         col = self.tree.identify_column(event.x)
         
         # Verificar que col sea válido (no vacío y no la columna #0)
         if item and col and col != '#0' and col.startswith('#'):
             col_index = int(col[1:]) - 1
             values = self.tree.item(item, 'values')
             
             # Verificar que el índice sea válido
             if col_index < len(values):
                 value = values[col_index]
                 
                 # Mostrar tooltip solo para textos largos
                 if len(str(value)) > 20:
                     x, y, _, _ = self.tree.bbox(item, col)
                     if x < event.x < x + self.tree.column(col, 'width'):
                         self.tooltip.deiconify()
                         self.tooltip_label.config(text=value)
                         self.tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
                         return
         
         self.tooltip.withdraw()
     except (ValueError, IndexError, AttributeError) as e:
         # Silenciar errores del tooltip
         self.tooltip.withdraw()
     
    def on_leave(self, event):
        """Ocultar tooltip al salir del treeview"""
        self.tooltip.withdraw()
    
    def load_users(self):
        """Cargar pesajes pendientes desde la base de datos"""
        if not self.tree:
            return
        
        # Limpiar tabla existente
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        users = self.db_user.get_active_users()
        # Alternar colores de filas para mejor legibilidad
        tags = ('evenrow', 'oddrow')                
        for i, users in enumerate(users):
            tag = tags[i % 2]
            self.tree.insert('', tk.END, values=(
                users['id_user'],
                users['user_name'],
                self.format_date(users['creation_date']),
                users['user_email'],
                users['access_level'],
                users['active_user'],
                users['user_create']
            ), tags=(tag,))
        
        # Configurar colores alternados
        self.tree.tag_configure('evenrow', background="#dfdfdf")
        self.tree.tag_configure('oddrow', background='#ffffff')
        
        # Actualizar contador
        self.update_count_label(len(users))
    
    def format_date(self, date_string):
        """Formatear fecha para mejor visualización"""
        if not date_string:
            return "-"
        
        try:
            # Convertir de YYYY-MM-DD HH:MM:SS a DD/MM/YYYY HH:MM
            if ' ' in date_string:
                date_part, time_part = date_string.split(' ')
                year, month, day = date_part.split('-')
                return f"{day}/{month}/{year} {time_part[:5]}"
            return date_string
        except:
            return date_string
                
    def update_count_label(self, count):
        """Actualizar el label del contador"""
        if count == 0:
            self.count_label.config(text="❌ No hay usuarios", foreground="#e74c3c")
        else:
            self.count_label.config(text=f"{count} Usuarios", foreground="#27ae60")
    
    
    def on_row_select(self, event):
     """Manejar selección de fila click"""
     selection = self.tree.selection()
     if selection:
         item = selection[0]
         values = self.tree.item(item, 'values')
         if values and len(values) > 0:
             """
            'id', 'user_name', 'creation_date', 'user_email', 'access_level', 'active_user', 'user_create'
            """

             # Emitir evento personalizado con todos los datos
             selected_data = {
                    'id_user': values[0],
                    'user_name': values[1],
                    'creation_date': values[2],
                    'user_email': values[3],
                    'access_level': values[4],
                    'active_user': values[5],
                    'user_create': values[6]
                }
             # Emitir evento con los datos
             #print(f"Selected_data en on_row_select {selected_data}")
             self.tree.event_generate('<<FolioSelected>>', data=selected_data)
     
    def _on_selection_change(self, event):
        """Manejar cambio de selección (un solo clic)"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')          
            if values and self.row_select_callback:
                # El folio está en la segunda columna (índice 1)
                              
                # Crear un diccionario con los datos, usando las claves de tu consulta:
                selected_data = {
                    'id_user': values[0],
                    'user_name': values[1],
                    'creation_date': values[2],
                    'user_email': values[3],
                    'access_level': values[4],
                    'active_user': values[5],
                    'user_create': values[6] 
                }
                # Llamar al callback en PesajeTab
                #print(f"DEBUG: selected data:{selected_data}")
                self.row_select_callback(selected_data)
    
    def refresh_table(self):
        """Refrescar la tabla"""
        self.load_users()
        print("🔄 Tabla de usuarios actualizada")   

                   
    def update_user(self,user_table_id, user_name, user_email, access_level, active_user, user_id):   
        
        if self.db_user.update_user(user_table_id, user_name, user_email, access_level, active_user, user_id):    
            messagebox.showinfo("Éxito", f"Usuario '{user_name}' actualizado correctamente con el nivel {access_level}.")
        else:
             messagebox.showerror("Error", "El nombre de usuario o correo ya existen.")

    def reset_password(self,user_table_id, user_name, user_id):  
          
            password = f"{user_name}123"
        
            if self.db_user.change_password(user_table_id, password, user_id):    
                messagebox.showinfo("Éxito", f"La contraseña del usuario '{user_name}' se restableció")
            else:
                messagebox.showerror("Error", "El nombre de usuario o correo ya existen.")
      

    