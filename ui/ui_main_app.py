# ui_main_app.py

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from db_operations.db_config import load_logo, set_window_icon
from db_operations.db_config import get_company_config
from ui.ui_menu_handlers import MenuHandlers
from ui.ui_tab_creators import TabCreators
from logic.logic_autocomplete import AutocompleteHandler  # Nuevo import
from logic.logic_sync_operations import SyncOperations  # Nuevo import


class AppStyles:
    def __init__(self):
        self.primary_color = "#714B67"
        self.secondary_color = "#F2F2F2"
        self.accent_color = "#00A09D"
        self.warning_color = "#F5B027"
        self.login_bg = "#FDFAFD"
        self.login_text = "#714B67"
        self.entry_second_color = "#7E7F80"
        self.font_base = ("Helvetica", 10)
        self.font_title = ("Helvetica", 12)
        self.font_heading = ("Helvetica", 14)

        

class MainApp:
    def __init__(self, root, user_access_level, user_id, user_name):
        self.root = root
        self.user_access_level = user_access_level
        self.user_id = user_id
        self.user_name = user_name 
        self.styles = AppStyles()
        
        set_window_icon(self.root, "icono_app.svg")
        
        self.setup_odoo_style()

        # PRIMERO: Crear autocomplete_handler (para SyncOperations)
        self.autocomplete_handler = AutocompleteHandler()
        
        # SEGUNDO: Crear tab_creator con autocomplete_handler
        self.tab_creator = TabCreators(self.styles, self.autocomplete_handler, user_id = self.user_id, user_access_level=self.user_access_level)
        
        # TERCERO: Crear los widgets básicos
        self.create_basic_widgets()
        
        # CUARTO: Crear sync_operations con autocomplete_handler
        self.sync_ops = SyncOperations(root, self.status_label, self.autocomplete_handler)
        
        # QUINTO: Crear menu_handlers con todos los componentes
        self.menu_handlers = MenuHandlers(
            root, 
            user_access_level, 
            self.status_label, 
            self.tab_creator,
            self.sync_ops,  # Pasar sync_operations actualizado   
            user_id = self.user_id,
            user_name = self.user_name        
        )
        
        # SEXTO: Crear las pestañas
        self.create_tabs()
        
        # SÉPTIMO: Crear el menú
        self.create_menu_bar()

        
        
        self.root.update_idletasks()

    def setup_odoo_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TFrame", background=self.styles.secondary_color)
        style.configure("Header.TFrame", background=self.styles.primary_color)
        style.configure("TLabel", background=self.styles.secondary_color, font=self.styles.font_base)
        style.configure("Header.TLabel", background=self.styles.primary_color, foreground="white", font=self.styles.font_title)
        style.configure("Orange.TCheckbutton", foreground="orange", background=self.styles.secondary_color,)
        style.configure("Green.TCheckbutton", foreground="green" )
        style.configure("TButton", font=self.styles.font_base, background=self.styles.accent_color)
        style.configure("Warning.TButton", font=self.styles.font_base, background=self.styles.warning_color)
        style.configure("Primary.TButton", background=self.styles.primary_color, foreground="white")
        style.configure("TNotebook", background=self.styles.secondary_color)
        style.configure("TNotebook.Tab", font=self.styles.font_base, padding=[10, 5])
        style.configure("Treeview", 
            font=self.styles.font_base, 
            rowheight=25, 
            borderwidth=0,
            fieldbackground="white" # Fondo blanco para las celdas
        )
        style.configure("Treeview.Heading", 
            font=self.styles.font_title, 
            background=self.styles.primary_color, # Color primario en el encabezado
            foreground="white"
        )
        # ESTILO DE SELECCIÓN DE FILA (Crucial)
        style.map('Treeview', 
            background=[('selected', self.styles.accent_color)], # Usar color de acento para la selección
            foreground=[('selected', 'white')]
        )
        
        # Estilos para el Scrollbar (TScrollbar)
        # Usa Vertical.TScrollbar para asegurar que se aplica al vertical
        style.configure("Vertical.TScrollbar", 
            troughcolor=self.styles.secondary_color,
            background=self.styles.secondary_color,
            bordercolor=self.styles.secondary_color,
            arrowcolor=self.styles.secondary_color,
            relief="flat",
            troughrelief="flat")
        
        style.map("Vertical.TScrollbar",
            background=[('active', self.styles.primary_color)] # Color al pasar el mouse
        )
        
        # Asegúrate de que los scrollbars del Treeview usen el estilo
        style.configure("TScrollbar",
            troughcolor=self.styles.secondary_color,
            background=self.styles.secondary_color,
            bordercolor=self.styles.secondary_color,
            arrowcolor=self.styles.secondary_color,
            relief="flat",
            troughrelief="flat")

        style.map("TScrollbar",
            background=[('active', self.styles.primary_color)] # Color al pasar el mouse
        )
    
    def create_basic_widgets(self):
        """Crea solo los widgets básicos sin las pestañas"""
        # Header y estructura principal
        header_frame = ttk.Frame(self.root, style="Header.TFrame", height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        COMPANY_DATA = get_company_config()
        COMPANY_NAME = COMPANY_DATA.get('company_name').upper()
        
        logo_width=70
        Logo_height=50
        logo = load_logo(logo_width, Logo_height)
        if logo:
            logo_label = ttk.Label(header_frame, image=logo, style="Header.TLabel")
            logo_label.image = logo
            logo_label.pack(side=tk.LEFT, padx=20)
        else:
            logo_label = ttk.Label(header_frame, text="App", style="Header.TLabel")
            logo_label.pack(side=tk.LEFT, padx=20)
        
        title_label = ttk.Label(header_frame, text="Sistema de Báscula", style="Header.TLabel")
        title_label.pack(side=tk.LEFT, padx=20)

        company_name = ttk.Label(header_frame, text=COMPANY_NAME, style="Header.TLabel")
        company_name.pack(side=tk.LEFT, padx=80)

        user_name_label = ttk.Label(header_frame, text=f"Hola  {self.user_name}", style="Header.TLabel")
        user_name_label.pack(side=tk.LEFT, padx=50)
        
        self.status_label = ttk.Label(header_frame, text="", style="Header.TLabel")
        self.status_label.pack(side=tk.RIGHT, padx=20)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
    
    def create_tabs(self):
        """Crea las pestañas ahora que todo está disponible"""
        # Crear pestañas usando el tab creator
        self.tab_creator.create_pesaje_tab(self.notebook)
        # Aquí puedes agregar más pestañas si las tienes:
        self.tab_creator.create_folios_tab(self.notebook)
        self.tab_creator.create_users_tab(self.notebook)

    
    def create_menu_bar(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        change_password = tk.Menu(self.menu_bar, tearoff=0)
        change_password.add_command(label='Cambiar contraseña', command=self.menu_handlers.change_password)        
        self.menu_bar.add_cascade(label="Usuario", menu=change_password)

        # Menú Agregar/Modificar
        add_edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        
        # Submenú Vehículos
        vehicles_menu = tk.Menu(add_edit_menu, tearoff=0)
        vehicles_menu.add_command(label="Sincronizar Vehículos de Odoo", command=self.menu_handlers.sync_vehicles)
        """
        if self.user_access_level == 3:
            vehicles_menu.add_command(label="Gestionar Vehículos", command=self.menu_handlers.manage_vehicles)
        """
        add_edit_menu.add_cascade(label="Vehículos", menu=vehicles_menu)
        
        # Submenú Remolques
        trailers_menu = tk.Menu(add_edit_menu, tearoff=0)
        trailers_menu.add_command(label="Sincronizar Remolques de Odoo", command=self.menu_handlers.sync_trailers)
        """
        if self.user_access_level == 3:
            trailers_menu.add_command(label="Gestionar Remolques", command=self.menu_handlers.manage_vehicles)
        """
        add_edit_menu.add_cascade(label="Remolques", menu=trailers_menu)
        
        # Submenú Choferes
        drivers_menu = tk.Menu(add_edit_menu, tearoff=0)
        drivers_menu.add_command(label="Sincronizar Choferes de Odoo", command=self.menu_handlers.sync_drivers)
        """
        if self.user_access_level == 3:
            drivers_menu.add_command(label="Gestionar Choferes", command=self.menu_handlers.manage_drivers)
        """
        add_edit_menu.add_cascade(label="Choferes", menu=drivers_menu)
        
        # Submenú Clientes
        customers_menu = tk.Menu(add_edit_menu, tearoff=0)
        customers_menu.add_command(label="Sincronizar Clientes de Odoo", command=self.menu_handlers.sync_customers)
        """
        if self.user_access_level == 3:
            customers_menu.add_command(label="Gestionar Clientes", command=self.menu_handlers.manage_customers)
        """
        add_edit_menu.add_cascade(label="Clientes", menu=customers_menu)

        # Submenú Materiales
        materials_menu = tk.Menu(add_edit_menu, tearoff=0)
        materials_menu.add_command(label="Sincronizar Materiales de Odoo", command=self.menu_handlers.sync_materials)
        """
        if self.user_access_level == 3:
            materials_menu.add_command(label="Gestionar Materiales", command=self.menu_handlers.manage_materials)
        """
        add_edit_menu.add_cascade(label="Materiales", menu=materials_menu)
        
        # Opción Folios (solo para nivel 3)
        """
        if self.user_access_level == 3:
            add_edit_menu.add_command(label="Folios", command=self.menu_handlers.add_edit_folios)
        """
        if self.user_access_level >= 2:
            self.menu_bar.add_cascade(label="Agregar/Modificar", menu=add_edit_menu)
        
        # Menú Configuración (solo para nivel 3)
        if self.user_access_level >= 3:
            config_menu = tk.Menu(self.menu_bar, tearoff=0)
            
            # Opciones generales de configuración

            company_menu = tk.Menu(config_menu, tearoff=0)
            company_menu.add_command(label="Nombre, dirección, puerto báscula", command=self.menu_handlers.add_company_data)
            company_menu.add_command(label="Agregar logotipos", command=self.menu_handlers.add_company_logo)
            #config_menu.add_command(label="Agregar logotipos", command=self.menu_handlers.add_logo)

            config_menu.add_cascade(label="Agregar datos de la compañía", menu=company_menu)
            """
            config_menu.add_command(label="Agregar parametros de impresora", command=self.menu_handlers.add_print)
            """
            # Submenú Usuarios
            users_menu = tk.Menu(config_menu, tearoff=0)
            users_menu.add_command(label="Agregar usuario", command=self.menu_handlers.add_user)
            config_menu.add_cascade(label="Usuarios", menu=users_menu)
            
            # Submenú API Odoo
            odoo_menu = tk.Menu(config_menu, tearoff=0)
            odoo_menu.add_command(label="Configuración de conexión", command=self.menu_handlers.configure_odoo_api)
            odoo_menu.add_command(label="Probar conexión", command=self.menu_handlers.test_odoo_connection)
            config_menu.add_cascade(label="API Odoo", menu=odoo_menu)
            
            self.menu_bar.add_cascade(label="Configuración", menu=config_menu)