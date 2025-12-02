# logic_pending_weighings.py 

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from db_operations.db_save_folio import WeighingDBManager

class PendingWeighingsTable:
    def __init__(self, parent_frame, styles=None):
        self.parent_frame = parent_frame
        self.styles = styles
        self.tree = None
        self.row_select_callback = None
        self.db_manager = WeighingDBManager()
        self.create_table()
        self.load_pending_weighings()


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
            text="Pesajes pendientes",
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
            'id', 'folio', 'date_start', 'days_open_folio', 'user', 'weighing_type', 'gross_weight', 'net_weight', 
            'tare_weight', 'plate', 'vehicle', 'trailer', 'driver', 'customer', 'material', 'notes', 'folio_ALM2', 'weight_original', 'vehicle_tara', 'equipo_tara'
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
            'folio': ('Folio', 50, 'center'),
            'date_start': ('Fecha', 120, 'center'),
            'days_open_folio':('Días abierto',90, 'center'),
            'user': ('Usuario',90 , 'center'),
            'weighing_type': ('Tipo Pesada', 90, 'center'),
            'gross_weight': ('P. Bruto (kg)', 0, 'center'),
            'net_weight': ('P. Neto (kg)', 0, 'center'),
            'tare_weight': ('P. Tara (kg)', 0, 'center'),
            'plate': ('Placas', 90, 'center'),
            'vehicle': ('Vehículo', 180, 'w'),
            'trailer': ('Remolque', 180, 'w'),
            'driver': ('Chofer', 150, 'w'),
            'customer': ('Cliente', 180, 'w'),
            'material': ('Material', 150, 'w'),
            'notes': ('Notas', 160, 'w'),
            'folio_ALM2': ('Folio ALM2', 0, 'center'),
            'weight_original':('-', 0, 'w'),
            'vehicle_tara':('-', 0, 'w'),
            'equipo_tara':('-', 0, 'w')
        }
        
        
        for col, (heading, width, anchor) in column_config.items():
            self.tree.heading(col, text=heading)
        
        # Si width es 0, ocultar la columna completamente
            if width == 0:
                self.tree.column(col, width=0, minwidth=0, stretch=False)
            else:
                self.tree.column(col, width=width, minwidth=width, anchor=anchor, stretch=True)
            
        
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
            self.load_pending_weighings() 
            

    
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
    
    def load_pending_weighings(self):
        """Cargar pesajes pendientes desde la base de datos"""
        if not self.tree:
            return
        
        # Limpiar tabla existente
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        weighings = self.db_manager.get_pending_weighings()
        # Alternar colores de filas para mejor legibilidad
        tags = ('evenrow', 'oddrow')
        
        for i, weighing in enumerate(weighings):
            tag = tags[i % 2]
            days_open_folio = self.create_open_folio_days(weighing['date_start'])
            self.tree.insert('', tk.END, values=(
                weighing['id_weighing'],
                weighing['folio_number'],
                self.format_date(weighing['date_start']),
                days_open_folio,
                weighing['user_name'],
                weighing['weighing_type'],
                weighing['gross_weight'],
                weighing['net_weight'],
                weighing['tare_weight'],
                weighing['plates'] or "-",
                weighing['vehicle_name'] or "-",
                weighing['trailer_name'] or "-",
                weighing['driver_name'] or "-",
                weighing['customer_name'] or "-",
                weighing['material_name'] or "-",
                weighing['notes'],
                weighing['folio_ALM2'],
                weighing['weight_original'],
                weighing['vehicle_tara'],
                weighing['equipo_tara']
            ), tags=(tag,))
        
        # Configurar colores alternados
        self.tree.tag_configure('evenrow', background="#dfdfdf")
        self.tree.tag_configure('oddrow', background='#ffffff')
        
        # Actualizar contador
        self.update_count_label(len(weighings))
    
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
            self.count_label.config(text="✅ No hay registros pendientes", foreground="#27ae60")
        elif count == 1:
            self.count_label.config(text="1 registro pendiente", foreground="#f4871b")
        else:
            self.count_label.config(text=f"{count} registros pendientes", foreground="#e74c3c")
    
    
    def on_row_select(self, event):
     """Manejar selección de fila click"""
     selection = self.tree.selection()
     if selection:
         item = selection[0]
         values = self.tree.item(item, 'values')
         if values and len(values) > 0:
             folio_number = values[1]  # Folio está en la primera columna
             print(f"📋 Folio seleccionado: {folio_number}")
             
             # Emitir evento personalizado con todos los datos
             selected_data = {
                    'id_weighing': values[0],
                    'folio_number': folio_number,
                    'plates': values[9],
                    'vehicle_name': values[10],
                    'trailer_name': values[11],
                    'driver_name': values[12],
                    'customer_name': values[13],
                    'material_name': values[14],
                    'weighing_type': values[5],
                    'gross_weight': values[6],
                    'tare_weight': values[8],
                    'notes':values[15],
                    'folio_ALM2': values[16],
                    'weight_original': values[17],
                    'vehicle_tara': values[18],
                    'equipo_tara': values[19]
                     
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
                folio_number = values[1]                 
                # Crear un diccionario con los datos, usando las claves de tu consulta:
                selected_data = {
                    'id_weighing': values[0],
                    'folio_number': folio_number,
                    'plates': values[9],
                    'vehicle_name': values[10],
                    'trailer_name': values[11],
                    'driver_name': values[12],
                    'customer_name': values[13],
                    'material_name': values[14],
                    'weighing_type': values[5],
                    'gross_weight': values[6],
                    'tare_weight': values[8],
                    'notes':values[15],
                    'folio_ALM2': values[16],
                    'weight_original': values[17],
                    'vehicle_tara': values[18],
                    'equipo_tara': values[19] 
                }
                # Llamar al callback en PesajeTab
                #print(f"DEBUG: selected data:{selected_data}")
                self.row_select_callback(selected_data)
    
    def refresh_table(self):
        """Refrescar la tabla"""
        self.load_pending_weighings()
        print("🔄 Tabla de pesajes pendientes actualizada")    

    def create_open_folio_days(self, date_start, date_end=None):
        try:
            if not date_end or date_end in ['', '-', 'None']:
                date_end = datetime.now()
            
            # Convertir a objetos datetime
            if isinstance(date_start, str):
                date_start = datetime.strptime(date_start, "%Y-%m-%d %H:%M:%S")
        
            if isinstance(date_end, str):
                date_end = datetime.strptime(date_end, "%Y-%m-%d %H:%M:%S")
            
            # Usar solo la parte de fecha (ignorar hora, minutos, segundos)
            fecha_inicio = date_start.date()
            fecha_fin = date_end.date()
            
            # Calcular diferencia en días naturales
            diferencia = fecha_fin - fecha_inicio
            dias = diferencia.days
            
            return dias
            
        except Exception as e:
            print(f"Error calculando días: {e}")
            return 0