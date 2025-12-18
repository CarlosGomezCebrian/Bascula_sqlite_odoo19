# logic_tables_folios.py

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from db_operations.db_search import SearchOperations
from logic.logic_odoo_records import OdooAPI

class FoliosWeighingsTable:
    def __init__(self, parent_frame, search_folio_entry=None, styles=None):
        self.parent_frame = parent_frame
        #self.db_path = db_path
        self.styles = styles
        self.folioTree = None
        self.folio_id = None
        self.row_select_callback = None
        self.selected_data = {} 
        self.search_folio_entry = search_folio_entry
        self.db_manager = SearchOperations()        
        self.create_table()
        self.load_folios()


    def set_row_select_callback(self, callback):
        """Permite que inyecte la función para cargar el folio."""
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
            text="Pesajes",
            font=("Helvetica", 12),
            style="TLabel"
        )
        title_label.pack(side=tk.LEFT)

        all_foliios_btn = ttk.Button(
            header_frame,
            text="Todos los folios",
            cursor="hand2",
            style="Primary.TButton",
            command=self._load_all_folios,
            width=12
        )
        all_foliios_btn.pack(side=tk.LEFT, padx=(5, 0))
                
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
            'id', 'folio', 'date_start', 'date_end', 'days_open_folio', 'user', 'weighing_type', 'gross_weight','net_weight',
            'tare_weight', 'plate', 'vehicle', 'trailer', 'driver', 'customer', 'material', 'scale_record_status','id_status_odoo', 'user_closed', 'notes', 'folio_ALM2','weight_original'
        )
        
        # Crear Treeview con estilo mejorado - CAMBIO IMPORTANTE: 
        self.folioTree = ttk.Treeview(
            table_container, 
            columns=columns,
            show='headings',
            height=5,
            selectmode='browse'  
        )
        
        # Configurar estilos para el Treeview
        self.configure_treeview_styles()
        
        # Configurar columnas con anchos optimizados
        column_config = {
            'id': ('Id',0, 'center'),
            'folio': ('Folio', 70, 'center'),
            'date_start': ('Fecha inició', 110, 'center'),
            'date_end': ('Fecha fin', 110, 'center'),
            'days_open_folio':('Días abierto',90, 'center'),
            'user': ('Usuario',90 , 'center'),
            'weighing_type': ('Tipo Pesada', 90, 'center'),
            'gross_weight': ('P. Bruto (kg)', 90, 'center'),
            'net_weight': ('P. Neto (kg)', 90, 'center'),
            'tare_weight': ('P. Tara (kg)', 90, 'center'),
            'plate': ('Placas', 90, 'center'),
            'vehicle': ('Vehículo', 180, 'w'),
            'trailer': ('Remolque', 150, 'w'),
            'driver': ('Chofer', 150, 'w'),
            'customer': ('Cliente', 180, 'w'),
            'material': ('Material', 150, 'w'),
            'scale_record_status': ('Estado', 90, 'w'),
            'id_status_odoo': ('Estado Odoo', 90, 'w'),
            'user_closed': ('Usuario cierre', 90, 'w'),
            'notes':('Notas',150,'w'),
            'folio_ALM2':('F-alm2',0,'center'),
            'weight_original':('P-Original',10,'center')
        }
        
        for col, (heading, width, anchor) in column_config.items():
            self.folioTree.heading(col, text=heading)
        
            if width == 0:
                self.folioTree.column(col, width=0, minwidth=0, stretch=False)
            else:
                self.folioTree.column(col, width=width, minwidth=width, anchor=anchor, stretch=False)
        
        # Scrollbar vertical
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.folioTree.yview)
        self.folioTree.configure(yscrollcommand=v_scrollbar.set)
        
        # Scrollbar horizontal
        h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.folioTree.xview)
        self.folioTree.configure(xscrollcommand=h_scrollbar.set)
        
        # Empaquetar usando grid para mejor control
        self.folioTree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configurar weights para expansión
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Vincular eventos - SIMPLIFICADO
        self.folioTree.bind('<<TreeviewSelect>>', self.on_selection_change)
        self.folioTree.bind('<Button-1>', self.check_treeview_click, add='+')
        self.folioTree.bind('<Shift-MouseWheel>', self.on_mousewheel_h)
        self.folioTree.bind('<Right>', lambda e: self.folioTree.xview_scroll(1, "units"))
        self.folioTree.bind('<Left>', lambda e: self.folioTree.xview_scroll(-1, "units"))
        
        # Tooltip para items largos
        self.setup_tooltip()

    def check_treeview_click(self, event):
        """Deselecciona y limpia los datos solo si el clic cae en un área vacía del Treeview."""
        # Intenta identificar la fila donde ocurrió el clic
        item = self.folioTree.identify_row(event.y)
        
        # Si item es vacío (''), significa que el clic fue en un área vacía
        if item == '':
            selection = self.folioTree.selection()
            if selection:
                # 1. Deseleccionar la fila activa
                self.folioTree.selection_remove(selection)
                self.selected_data = {}

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
        self.folioTree.configure(style="Custom.Treeview")
    
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
        
        self.folioTree.bind('<Motion>', self.on_motion)
        self.folioTree.bind('<Leave>', self.on_leave)
    
    def on_motion(self, event):
        """Manejar movimiento del mouse para tooltip"""
        try:
            item = self.folioTree.identify_row(event.y)
            col = self.folioTree.identify_column(event.x)
            
            # Verificar que col sea válido (no vacío y no la columna #0)
            if item and col and col != '#0' and col.startswith('#'):
                col_index = int(col[1:]) - 1
                values = self.folioTree.item(item, 'values')
                
                # Verificar que el índice sea válido
                if col_index < len(values):
                    value = values[col_index]
                    
                    # Mostrar tooltip solo para textos largos
                    if len(str(value)) > 20:
                        x, y, _, _ = self.folioTree.bbox(item, col)
                        if x < event.x < x + self.folioTree.column(col, 'width'):
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
    
    def load_folios(self):
        """Cargar pesajes pendientes desde la base de datos"""        
        if not self.folioTree:
            return
        
        # Limpiar tabla existente
        for item in self.folioTree.get_children():
            self.folioTree.delete(item)
        
        folios = self.db_manager.get_last_folios_weighings_manual()
        # Alternar colores de filas para mejor legibilidad
        tags = ('evenrow', 'oddrow')
        
        for i, weighing in enumerate(folios):
            
            self.folio_id = weighing['id_weighing']
            saved_in_odoo = weighing['saved_in_Odoo']            
            if saved_in_odoo != 1:
                self.odoo_records = OdooAPI(self.folio_id)
                self.odoo_records.create_record_scale()
            
            tag = tags[i % 2]
            days_open_folio = self.create_open_folio_days(weighing['date_start'], weighing['date_end'])
            self.folioTree.insert('', tk.END, values=(
                weighing['id_weighing'],
                weighing['folio_number'],
                self._format_date(weighing['date_start']),
                self._format_date(weighing['date_end']),
                days_open_folio,
                weighing['user_name'],
                weighing['weighing_type'],
                weighing['gross_weight'],
                weighing['net_weight'],
                weighing['tare_weight'],
                weighing['plates'],
                weighing['vehicle_name'],
                weighing['trailer_name'],
                weighing['driver_name'],
                weighing['customer_name'],
                weighing['material_name'],
                weighing['scale_record_status'],
                weighing['id_status_odoo'],                
                weighing['user_name_closed'],
                weighing['notes'],
                weighing['folio_ALM2'],
                weighing['weight_original']
            ), tags=(tag,))
        
        # Configurar colores alternados
        self.folioTree.tag_configure('evenrow', background="#dfdfdf")
        self.folioTree.tag_configure('oddrow', background='#ffffff')
        self.search_folio_entry.delete(0, tk.END)
        # Actualizar contador
        self.update_count_label(len(folios))

    def _load_all_folios(self):
        """Cargar pesajes pendientes desde la base de datos"""        
        if not self.folioTree:
            return
        
        # Limpiar tabla existente
        for item in self.folioTree.get_children():
            self.folioTree.delete(item)
        
        folios = self.db_manager.get_all_folios_weighings_closed()
        # Alternar colores de filas para mejor legibilidad
        tags = ('evenrow', 'oddrow')
        
        for i, weighing in enumerate(folios):
            
            self.folio_id = weighing['id_weighing']
            saved_in_odoo = weighing['saved_in_Odoo']            
            if saved_in_odoo != 1:
                self.odoo_records = OdooAPI(self.folio_id)
                print(f"Folio id en if: {self.folio_id}\nsaved_in_odoo:{saved_in_odoo}")
                self.odoo_records.create_record_scale()
            
            tag = tags[i % 2]
            days_open_folio = self.create_open_folio_days(weighing['date_start'], weighing['date_end'])
            weighing_type_value = weighing['weighing_type']
            self.folioTree.insert('', tk.END, values=(
                weighing['id_weighing'],
                weighing['folio_number'],
                self._format_date(weighing['date_start']),
                self._format_date(weighing['date_end']),
                days_open_folio,
                weighing['user_name'],
                weighing['weighing_type'],
                weighing['gross_weight'],
                weighing['net_weight'],
                weighing['tare_weight'],
                weighing['plates'],
                weighing['vehicle_name'],
                weighing['trailer_name'],
                weighing['driver_name'],
                weighing['customer_name'],
                weighing['material_name'],
                weighing['scale_record_status'],
                weighing['id_status_odoo'],                
                weighing['user_name_closed'],
                weighing['notes'],
                weighing['folio_ALM2'],
                weighing['weight_original']
            ), tags=(tag,))
        
        # Configurar colores alternados
        self.folioTree.tag_configure('evenrow', background="#dfdfdf")
        self.folioTree.tag_configure('oddrow', background='#ffffff')
        self.search_folio_entry.delete(0, tk.END)
        # Actualizar contador
        self.update_count_label(len(folios))

        
    def _format_date(self, date_string):
        """Formatear fecha para mejor visualización"""  
        if not date_string:
            return ""
        
        try:
            # Convertir de YYYY-MM-DD HH:MM:SS a DD/MM/YYYY HH:MM
            if ' ' in date_string:
                date_part, time_part = date_string.split(' ')
                year, month, day = date_part.split('-')
                return f"{day}/{month}/{year} {time_part[:8]}"
            return date_string
        except:
            return date_string
        
    def create_open_folio_days(self, date_start, date_end):
        try:
            if not date_end or date_end in ['', '-', 'None']:
                date_end = datetime.now()
            
            # Convertir a objetos datetime
            if isinstance(date_start, str):
                date_start = datetime.strptime(date_start, "%Y-%m-%d %H:%M:%S")
        
            if isinstance(date_end, str):
                date_end = datetime.strptime(date_end, "%Y-%m-%d %H:%M:%S")
            
            # Usar solo la parte de fecha (ignorar hora, minutos, segundos)
            fecha_inicio = date_start.date()  # date_start.date() Solo año, mes, día
            fecha_fin = date_end.date()       # date_end.date() Solo año, mes, día
            
            # Calcular diferencia en días naturales
            diferencia = fecha_fin - fecha_inicio
            dias = diferencia.days
            
            return dias
            
        except Exception as e:
            print(f"Error calculando días: {e}")
            return 0

        

    def update_count_label(self, count):
        """Actualizar el label del contador"""
        if count == 0:
            self.count_label.config(text="❌ No hay registros", foreground="#f4871b")
        elif count == 1:
            self.count_label.config(text="1 registro", foreground="#27ae60")
        else:
            self.count_label.config(text=f"{count} registros", foreground="#27ae60")

    
    def on_selection_change(self, event):
        """Manejar cambio de selección (un solo clic)"""
        selection = self.folioTree.selection()
        if not selection:
            self.selected_data = {}
            return
        item = selection[0]
        values = self.folioTree.item(item, 'values')   
        if values:
            folio_number = values[1]
            self.selected_data = {
                    'id_weighing': values[0],
                    'folio_number': folio_number,
                    'date_start': values[2],
                    'date_end': values[3],
                    'user_name': values[4],
                    'plates': values[10],
                    'vehicle_name': values[11],
                    'trailer_name': values[12],
                    'driver_name': values[13],
                    'customer_name': values[14],
                    'material_name': values[15],
                    'weighing_type': values[6],                    
                    'gross_weight' : values[7],
                    'net_weight': values[8],
                    'tare_weight': values[9],
                    'user_name': values[5],
                    'user_name_closed': values[18],
                    'notes': values[19],
                    'folio_ALM2': values[20]
                }

            #print(f"📋 Datos seleccionados: {self.selected_data}")
            self.row_select_callback(self.selected_data)
        else:
            self.selected_data = {}  

    def get_selected_folio_data(self):
        """Devuelve el diccionario del folio actualmente seleccionado y almacenado."""
        return self.selected_data  
        
               
                
    def check_click_outside_table(self, event):
        """Verifica si un clic ocurrió fuera de la tabla Treeview y deselecciona."""        
        # Obtener coordenadas de la tabla Treeview
        tx, ty = self.folioTree.winfo_rootx(), self.folioTree.winfo_rooty()
        tw, th = self.folioTree.winfo_width(), self.folioTree.winfo_height()
        
        # Comprobar si el clic está fuera de la tabla
        is_outside = not (tx <= event.x_root < tx + tw and ty <= event.y_root < ty + th)
        
        if is_outside:
            # 1. Deseleccionar todas las filas actualmente seleccionadas
            if self.folioTree.selection():
                self.folioTree.selection_remove(self.folioTree.selection())
                
            
            self.selected_data = {}

    def refresh_table(self):
        """Refrescar la tabla"""
        self.load_folios()

    
    def update_table(self, text):
        """Cargar pesajes desde la base de datos filtrados por texto"""
        if not self.folioTree:
            return
        
        for item in self.folioTree.get_children():
            self.folioTree.delete(item)
        
        folios = self.db_manager.search_folio_for_text_manual(text)
        
        # Alternar colores de filas para mejor legibilidad
        tags = ('evenrow', 'oddrow')
        
        for i, weighing in enumerate(folios):
            tag = tags[i % 2]
            days_open_folio = self.create_open_folio_days(weighing['date_start'], weighing['date_end'])
            
            self.folioTree.insert('', tk.END, values=(
                weighing['id_weighing'],
                weighing['folio_number'],
                self._format_date(weighing['date_start']),
                self._format_date(weighing['date_end']),
                days_open_folio,
                weighing['user_name'],
                weighing['weighing_type'],
                weighing['gross_weight'],
                weighing['net_weight'],
                weighing['tare_weight'],
                weighing['plates'],
                weighing['vehicle_name'],
                weighing['trailer_name'],
                weighing['driver_name'],
                weighing['customer_name'],
                weighing['material_name'],
                weighing['scale_record_status'],
                weighing['id_status_odoo'],                
                weighing['user_name_closed'],
                weighing['notes'],
                weighing['folio_ALM2']
            ), tags=(tag,))
        
        # Configurar colores alternados
        self.folioTree.tag_configure('evenrow', background="#dfdfdf")
        self.folioTree.tag_configure('oddrow', background='#ffffff')
            
            # Actualizar contador
        self.update_count_label(len(folios))

    def on_mousewheel_h(self, event):
        """Maneja el desplazamiento horizontal con la rueda del ratón (Shift+Scroll)"""
        # Utiliza el scrollbar horizontal (h_scrollbar) para desplazar
        self.folioTree.xview_scroll(int(-1*(event.delta/200)), "units")