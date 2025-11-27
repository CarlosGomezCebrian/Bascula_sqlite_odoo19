# dialog_windows.py

from tkinter import messagebox, ttk
import tkinter as tk
from  db_operations.db_users import Users
from  db_operations.db_odoo_config import OdooConfig
from logic.logic_odoo_api import test_odoo_connection
from db_operations.db_config import get_logo_path, get_logo_path_print, save_company_data_settings

class AppStylesMenu:
    def __init__(self):
        self.primary_color = "#714B67"
        self.secondary_color = "#F2F2F2"
        self.accent_color = "#00A09D"
        self.login_bg = "#FDFAFD"
        self.login_text = "#714B67"
        self.entry_second_color = "#7E7F80"
        self.font_base = ("Helvetica", 10)
        self.font_title = ("Helvetica", 12, "bold")
        self.font_heading = ("Helvetica", 14)


class DialogWindows:
    def __init__(self, root):
        self.root = root
        self.user_id =None
        self.user_name_cpw = None 
        self.user_id_cpw = None
        self.styles = AppStylesMenu()
        self.db_users = Users()
        self.db_odoo_config = OdooConfig()
     
        
    def add_company_logo(self):
        self.add_logo_window = tk.Toplevel(self.root)
        self.add_logo_window.title("Agregar logotipos")
        self.add_logo_window.geometry("700x300")
        self.add_logo_window.config(bg=self.styles.secondary_color)
        frame_logo = tk.Frame(self.add_logo_window, bg=self.styles.secondary_color, padx=20, pady=20)
        frame_logo.pack(expand=True)
        frame_logo.focus()

        tk.Label(frame_logo, text="El logotipo principal\nes el que se presentará dentro de la aplicación.\nLos formatos permitidos son .png, .jpg, .jpeg", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.primary_color, justify="left").grid(row=0, column=0, pady=10, sticky="w", padx=10)

        self.btn_logo_principal = tk.Button(frame_logo, text="Guardar logotipo principal", bg=self.styles.primary_color, fg="white", cursor="hand2", command=self.add_logo_principal).grid(row=0, column=1, pady=20, sticky="ew") 
               

        tk.Label(frame_logo, text="EL logotipo para impresión\nes el que se usara en la cabecera del ticket.\nDebe ser en blanco y negro.\nLos formatos permitidos son .png, .jpg, .jpeg", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.primary_color, justify="left").grid(row=2, column=0, pady=10, sticky="w", padx=10)        

        self.btn_logo_print =tk.Button(frame_logo, text="Guardar logotipo para impresión", bg=self.styles.primary_color, fg="white", cursor="hand2", command=self.add_logo_print).grid(row=2, column=1, pady=20,sticky="ew")
        

    def add_company_data(self):
        self.add_data_window = tk.Toplevel(self.root)
        self.add_data_window.title("Agregar datos")
        self.add_data_window.geometry("500x300")
        self.add_data_window.config(bg=self.styles.secondary_color)
        frame_logo = tk.Frame(self.add_data_window, bg=self.styles.secondary_color, padx=20, pady=20)
        frame_logo.pack(expand=True)
        
        tk.Label(frame_logo, text="Nombre\nde la compañía:", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.primary_color, justify="left").grid(row=1, column=0, pady=10, sticky="w")
        self.entry_company_name = tk.Entry(frame_logo, font=self.styles.font_title, bg="#FFFFFF", fg=self.styles.entry_second_color, width=50)
        self.entry_company_name.grid(row=1, column=1, pady=10, sticky="ew")
        self.entry_company_name.focus()

        company_name_value = "Trébol Gestor de Residuos Industriales, S.A. de C.V."
        self.entry_company_name.insert(0, company_name_value)

        tk.Label(frame_logo, text="Dirección:", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.primary_color).grid(row=2, column=0, pady=10, sticky="w")
        self.entry_address = tk.Entry(frame_logo, font=self.styles.font_title, bg="#FFFFFF", fg=self.styles.entry_second_color)
        self.entry_address.grid(row=2, column=1, pady=10, sticky="ew")

        address_value = "Carretera a El Salto 28200, Colonia El Muelle, C.P. 45683, El Salto, Jalisco"
        self.entry_address.insert(0, address_value)

        tk.Label(frame_logo, text="Puerto báscula:", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.primary_color).grid(row=3, column=0, pady=10, sticky="w")
        self.entry_port_scale = tk.Entry(frame_logo, font=self.styles.font_title, bg="#FFFFFF", fg=self.styles.entry_second_color)
        self.entry_port_scale.grid(row=3, column=1, pady=10, sticky="ew")

        port_scale_value = "COM4"
        self.entry_port_scale.insert(0, port_scale_value)

        self.btn_company_data=tk.Button(frame_logo, text="Guardar configuración", bg=self.styles.primary_color, fg="white", cursor="hand2", command=self.save_company_settings)
        self.btn_company_data.grid(row=4, column=1, pady=20, sticky="e")
        frame_logo.columnconfigure(1, weight=1)
        self.setup_keyboard_events_data()
    

    def add_logo_principal(self):
        logo_path = get_logo_path()
        if logo_path:
            messagebox.showinfo("Éxito", "Logotipo guardado correctamente.")
        else:
            messagebox.showerror("Error", "No se pudo guardar el logotipo. Asegúrate de seleccionar un archivo .png o .jpeg.")
    def add_logo_print(self):
        logo_path_print = get_logo_path_print()
        if logo_path_print:
            messagebox.showinfo("Éxito", "Logotipo guardado correctamente.")
        else:
            messagebox.showerror("Error", "No se pudo guardar el logotipo. Asegúrate de seleccionar un archivo .png o .jpeg.")

    def save_company_settings(self):
        address = self.entry_address.get()
        company_name = self.entry_company_name.get()
        port_scale =  self.entry_port_scale.get()
        if address and company_name:
            if save_company_data_settings(address, company_name, port_scale):
                messagebox.showinfo("Éxito", "Configuración de la empresa guardada correctamente.", parent=self.add_data_window)
                self.add_data_window.destroy()
            else:
                messagebox.showerror("Error", "Ocurrió un error al guardar la configuración.", parent=self.add_data_window)
        else:
            messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=self.add_data_window)       

    def add_print(self):
        messagebox.showinfo("Gestión", "Abrir gestion de impresora")
    
    def add_user(self,user_id):
        self.user_id = user_id

        self.add_user_window = tk.Toplevel(self.root)
        self.add_user_window.title("Agregar Usuario")
        self.add_user_window.geometry("400x350")
        self.add_user_window.config(bg=self.styles.secondary_color)

        frame = tk.Frame(self.add_user_window, bg=self.styles.secondary_color, padx=20, pady=20)
        frame.pack(expand=True)

        tk.Label(frame, text="Nombre de usuario:", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.primary_color).grid(row=0, column=0, pady=5, sticky="w")
        self.entry_user_name = tk.Entry(frame, font=self.styles.font_title, bg="#FFFFFF", fg=self.styles.entry_second_color)
        self.entry_user_name.grid(row=0, column=1, pady=5, sticky="ew")

        tk.Label(frame, text="Correo de usuario:", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.primary_color).grid(row=1, column=0, pady=5, sticky="w")
        self.entry_user_email = tk.Entry(frame, font=self.styles.font_title, bg="#FFFFFF", fg=self.styles.entry_second_color)
        self.entry_user_email.grid(row=1, column=1, pady=5, sticky="ew")
        """"
        tk.Label(frame, text="Contraseña:", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.primary_color).grid(row=2, column=0, pady=5, sticky="w")
        self.entry_password = tk.Entry(frame, show="*", font=self.styles.font_title, bg="#FFFFFF", fg=self.styles.entry_second_color)
        self.entry_password.grid(row=2, column=1, pady=5, sticky="ew")
        """
        tk.Label(frame, text="Tipo de usuario:", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.primary_color).grid(row=3, column=0, pady=5, sticky="w")
        self.combo_access_level = ttk.Combobox(frame, values=["1 - Báscula", "2 - Odoo", "3 - Administrador"], state="readonly", font=self.styles.font_title)
        self.combo_access_level.set("1 - Báscula")
        self.combo_access_level.grid(row=3, column=1, pady=5, sticky="ew")
        
        tk.Button(frame, text="Guardar usuario", bg=self.styles.primary_color, fg="white", cursor="hand2", command=self.save_user).grid(row=4, columnspan=2, pady=20)
        frame.columnconfigure(1, weight=1)

    def save_user(self):
        user_name = self.entry_user_name.get()
        user_email = self.entry_user_email.get()
        #password = self.entry_password.get()
        password =f"{user_name}123"
        selected_level_str = self.combo_access_level.get()
        access_level = int(selected_level_str.split(' ')[0])
        user_id =self.user_id
        if user_name and user_email and password:
            if self.db_users.create_new_user(user_name, user_email, password, access_level, user_id):
                messagebox.showinfo("Éxito", f"Usuario '{user_name}' creado correctamente con el nivel {access_level}.", parent=self.add_user_window)
                self.add_user_window.destroy()
            else:
                messagebox.showerror("Error", "El nombre de usuario o correo ya existen.", parent=self.add_user_window)
        else:
            messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=self.add_user_window)
    
    def configure_odoo_api(self):
        self.odoo_config_window = tk.Toplevel(self.root)
        self.odoo_config_window.title("Configuración de Conexión a Odoo")
        self.odoo_config_window.geometry("550x300")
        self.odoo_config_window.config(bg=self.styles.secondary_color)

        frame = tk.Frame(self.odoo_config_window, bg=self.styles.secondary_color, padx=20, pady=20)
        frame.pack(expand=True)

        tk.Label(frame, text="URL de Odoo:", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.primary_color).grid(row=0, column=0, pady=5, sticky="w")        
        self.entry_odoo_url = tk.Entry(frame, font=self.styles.font_title, bg="#FFFFFF", fg=self.styles.entry_second_color)
        self.entry_odoo_url.grid(row=0, column=1, pady=5, sticky="ew")

        odoo_url_value = "https://grupotrebol.odoo.com"
        self.entry_odoo_url.insert(0, odoo_url_value)

        tk.Label(frame, text="Nombre de la Base de Datos:", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.primary_color).grid(row=1, column=0, pady=5, sticky="w")
        self.entry_db_name = tk.Entry(frame, font=self.styles.font_title, bg="#FFFFFF", fg=self.styles.entry_second_color)
        self.entry_db_name.grid(row=1, column=1, pady=5, sticky="ew")

        db_name_value = "grupotrebol"
        self.entry_db_name.insert(0, db_name_value)

        tk.Label(frame, text="Correo de Usuario API:", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.primary_color).grid(row=2, column=0, pady=5, sticky="w")
        self.entry_api_user_email = tk.Entry(frame, font=self.styles.font_title, bg="#FFFFFF", fg=self.styles.entry_second_color)
        self.entry_api_user_email.grid(row=2, column=1, pady=5, sticky="ew")

        api_user_email_value = "general@grupotrebol.net"
        self.entry_api_user_email.insert(0, api_user_email_value)

        tk.Label(frame, text="API Key:", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.primary_color).grid(row=3, column=0, pady=5, sticky="w")
        self.entry_api_key = tk.Entry(frame, show="*", font=self.styles.font_title, bg="#FFFFFF", fg=self.styles.entry_second_color)
        self.entry_api_key.grid(row=3, column=1, pady=5, sticky="ew")

        tk.Button(frame, text="Guardar configuración", bg=self.styles.primary_color, fg="white", cursor="hand2", command=self.save_odoo_settings).grid(row=4, columnspan=2, pady=20)
        frame.columnconfigure(1, weight=1)

    def save_odoo_settings(self):
        url = self.entry_odoo_url.get()
        db_name = self.entry_db_name.get()
        email = self.entry_api_user_email.get()
        api_key = self.entry_api_key.get()

        if url and db_name and email and api_key:
            if self.db_odoo_config.save_odoo_api_settings(url, db_name, email, api_key):
                messagebox.showinfo("Éxito", "Configuración de Odoo guardada correctamente.", parent=self.odoo_config_window)
                self.odoo_config_window.destroy()
            else:
                messagebox.showerror("Error", "Ocurrió un error al guardar la configuración.", parent=self.odoo_config_window)
        else:
            messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=self.odoo_config_window)
    
    def test_odoo_connection(self):
        is_successful = test_odoo_connection()
        if is_successful:
            messagebox.showinfo("Prueba de Conexión", "Prueba de Conexión exitosa")
        else:
            messagebox.showerror("Prueba de Conexión", "Prueba de Conexión fallida")

    def change_password(self, user_name, user_id):
        self.user_name_cpw = user_name
        self.user_id_cpw =  user_id 

        self.add_change_password_window = tk.Toplevel(self.root)
        self.add_change_password_window.title("cambiar la contraseña")
        self.add_change_password_window.geometry("400x350")
        self.add_change_password_window.config(bg=self.styles.secondary_color)
        frame = tk.Frame(self.add_change_password_window, bg=self.styles.secondary_color, padx=20, pady=20)
        frame.pack(expand=True)

        tk.Label(frame, text="¡ADVERTENCIA!", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.primary_color).grid(row=0, columnspan=2, pady=5)

        tk.Label(frame, text="Esta acción cerrara la aplicación\npara ingresar con la nueva contraseña", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.entry_second_color).grid(row=1, columnspan=2, pady=5)


        tk.Label(frame, text="Nombre de usuario:", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.entry_second_color).grid(row=2, column=0, pady=5, sticky="w")
        self.label_user_name = tk.Label(frame, text=f"{self.user_name_cpw}", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.entry_second_color)
        self.label_user_name.grid(row=2, column=1, pady=5, sticky="ew")

        tk.Label(frame, text="Nueva contraseña:", bg=self.styles.secondary_color, font=self.styles.font_title, fg=self.styles.primary_color).grid(row=3, column=0, pady=5, sticky="w")
        self.entry_new_password = tk.Entry(frame, show="*", font=self.styles.font_title, bg="#FFFFFF", fg=self.styles.entry_second_color)
        self.entry_new_password.grid(row=3, column=1, pady=5, sticky="ew")
        self.entry_new_password.focus()

        self.button_cancel = tk.Button(frame, text="Cancelar", bg=self.styles.primary_color, fg="white", command=self.cancel_change_password, cursor="hand2")
        self.button_cancel.grid(row=5, column=0, pady=20, sticky="w")
        
        self.button_change_password=tk.Button(frame, text="Cambiar contraseña", bg=self.styles.primary_color, fg="white", command=self.save_change_password,  cursor="hand2")
        self.button_change_password.grid(row=5, column=1, pady=10, sticky="ew")
        self.setup_keyboard_events_password()

    def save_change_password(self):
        new_password = self.entry_new_password.get()

        if new_password and self.user_id_cpw:
            if  self.db_users.change_password(self.user_id_cpw, new_password, self.user_id_cpw):
                messagebox.showinfo("Éxito", f"El usuario '{self.user_name_cpw}' cambio  correctamente  la  contraseña.", parent=self.add_change_password_window)
                self.add_change_password_window.destroy()
                import os
                os.environ['RESTART_APP'] = '1'
                
                self.root.destroy()

            else:
                messagebox.showerror("Error", "Error al guardar la contraseña.", parent=self.add_change_password_window)
        else:
            messagebox.showerror("Error", "El campo contraseña está vacío.", parent=self.add_change_password_window)

    def cancel_change_password(self):
        self.add_change_password_window.destroy()

        
        
    def setup_keyboard_events_password(self):      

        self.button_cancel.bind('<Return>', lambda e: self.cancel_change_password())
        self.button_change_password.bind('<Return>', lambda e: self.save_change_password())

    def setup_keyboard_events_data(self):       

        self.btn_company_data.bind('<Return>', lambda e: self.save_company_settings())
