# menu_handlers.py

from tkinter import messagebox
from logic.logic_sync_operations import SyncOperations
from ui.ui_dialog_windows import DialogWindows


class MenuHandlers:
    def __init__(self, root, user_access_level, status_label, tab_creator, sync_ops=None, user_id =None,  user_name=None):
                
        self.root = root
        self.user_access_level = user_access_level
        self.status_label = status_label
        self.tab_creator = tab_creator
        self.user_id = user_id
        self.user_name = user_name
        
        # Usar sync_ops si se proporciona, de lo contrario crear uno nuevo
        if sync_ops:
            self.sync_ops = sync_ops
        else:
            # Fallback para compatibilidad
            self.sync_ops = SyncOperations(root, status_label, tab_creator)
        
        self.dialogs = DialogWindows(root)    
    
    # Handlers de reportes
    """
    def show_not_closed_folios(self):
        messagebox.showinfo("Reportes", "Mostrar reportes de folios no cerrados")
    
    def show_all_folios(self):
        messagebox.showinfo("Reportes", "Mostrar lista de todos los folios")
    
    def show_modified_folios(self):
        messagebox.showinfo("Reportes", "Mostrar lista de folios modificados")
    
    def show_access_list(self):
        messagebox.showinfo("Reportes", "Mostrar lista de accesos")
    """
    def change_password(self):
        if self.user_id:
            print(f"User name: {self.user_name}")
            self.dialogs.change_password(self.user_name, self.user_id)

    # Handlers de sincronización
    def sync_vehicles(self):
        if self.status_label and self.sync_ops:
            self.sync_ops.start_sync_thread('vehicles')
        else:
            messagebox.showerror("Error", "Sync operations no disponible")
    
    def sync_trailers(self):
        if self.status_label and self.sync_ops:
            self.sync_ops.start_sync_thread('trailers')
        else:
            messagebox.showerror("Error", "Sync operations no disponible")
    
    def sync_drivers(self):
        if self.status_label and self.sync_ops:
            self.sync_ops.start_sync_thread('drivers')
        else:
            messagebox.showerror("Error", "Sync operations no disponible")
    
    def sync_materials(self):
        if self.status_label and self.sync_ops:
            self.sync_ops.start_sync_thread('materials')
        else:
            messagebox.showerror("Error", "Sync operations no disponible")
    
    def sync_customers(self):
        if self.status_label and self.sync_ops:
            self.sync_ops.start_sync_thread('customers')
        else:
            messagebox.showerror("Error", "Sync operations no disponible")
    
    # Handlers de gestión
    """
    def manage_vehicles(self):
        messagebox.showinfo("Gestión", "Abrir gestión de vehículos")

    def manage_trailers(self):
        messagebox.showinfo("Gestión", "Abrir gestión de remolques")
    
    def manage_drivers(self):
        messagebox.showinfo("Gestión", "Abrir gestión de choferes")
    
    def manage_materials(self):
        messagebox.showinfo("Gestión", "Abrir gestión de materiales")
    
    def manage_customers(self):
        messagebox.showinfo("Gestión", "Abrir gestión de clientes")
    def add_edit_folios(self):
        messagebox.showinfo("Gestión", "Abrir gestión de folios")
    """    
    
    # Handlers de configuración
    def add_company_logo(self):
        self.dialogs.add_company_logo()

    def add_company_data(self):
        self.dialogs.add_company_data()
    """
    def add_print(self):
        self.dialogs.add_print()
    """  
    
    def add_user(self):
        self.dialogs.add_user(self.user_id)
    
    def configure_odoo_api(self):
        self.dialogs.configure_odoo_api()
    
    def test_odoo_connection(self):
        self.dialogs.test_odoo_connection()