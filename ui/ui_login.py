#ui_login.py

import tkinter as tk
from tkinter import messagebox, ttk
from db_operations.db_config import load_logo, set_window_icon
from PIL import Image, ImageTk
from ui.ui_main_app import AppStyles, MainApp
from db_operations.db_operations import verify_login, log_login_attempt

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.styles = AppStyles()
        self.root.title("Login - Aplicación Báscula")
        self.root.geometry("350x500")

        set_window_icon(self.root, "icono_app.svg")

        self.root.config(bg=self.styles.login_bg)

        screen_width = self.root.winfo_screenwidth()
        x_coordinate = int((screen_width / 2) - (350 / 2))
        self.root.geometry(f"350x500+{x_coordinate}+100")

        self.app_font = (self.styles.font_heading)
        
        # Frame principal para contener todo
        self.main_frame = tk.Frame(root, bg=self.styles.login_bg)
        self.main_frame.pack(expand=True, fill="both")
        
        self.create_login_widgets()

    def create_login_widgets(self):
        frame = tk.Frame(self.main_frame, padx=10, pady=10, bg=self.styles.login_bg)
        frame.pack(expand=True)
        
        self.logo_space = tk.Frame(frame, height=150, bg=self.styles.login_bg)
        self.logo_space.pack(pady=20)
        self.logo_label = tk.Label(self.logo_space, bg=self.styles.login_bg)
        self.logo_label.pack()
        self.display_logo()
        
        self.label_username = tk.Label(frame, text="Nombre de usuario:", bg=self.styles.login_bg, font=self.app_font,  fg=self.styles.login_text)
        self.label_username.pack(pady=(10, 0))
        
        self.entry_username = tk.Entry(frame, font=self.app_font, bg="#FFFFFF",fg=self.styles.entry_second_color )
        self.entry_username.pack(pady=(0, 10))

        self.label_password = tk.Label(frame, text="Contraseña:", bg=self.styles.login_bg, font=self.app_font, fg=self.styles.login_text)
        self.label_password.pack(pady=(10, 0))
        
        self.entry_password = tk.Entry(frame, show="*", font=self.app_font, bg="#FFFFFF",fg=self.styles.entry_second_color)
        self.entry_password.pack(pady=(0, 10))

        # Botón de login con mejoras de UX
        self.login_button = tk.Button(
            frame, 
            text="Iniciar Sesión", 
            command=self.handle_login,
            bg=self.styles.login_text, 
            fg="white", 
            relief="flat", 
            font=self.app_font,
            activebackground=self.styles.login_text,  # Mismo color al hacer clic
            activeforeground="white",  # Texto blanco al hacer clic
            cursor="hand2"  # Cursor de mano al pasar por encima
        )
        self.login_button.pack(pady=10)
        self.entry_username.focus()
        # Configurar eventos de teclado
        self.setup_keyboard_events()

    def setup_keyboard_events(self):
        """Configurar navegación con teclado"""
        # Enter en campos de texto ejecuta login
        self.entry_username.bind('<Return>', lambda e: self.entry_password.focus())
        self.entry_password.bind('<Return>', lambda e: self.handle_login())
        
        # Enter en el botón ejecuta login
        self.login_button.bind('<Return>', lambda e: self.handle_login())
        
        # Tabulación entre campos
        self.entry_username.bind('<Tab>', lambda e: self.entry_password.focus())
        self.entry_password.bind('<Tab>', lambda e: self.login_button.focus())
        self.login_button.bind('<Tab>', lambda e: self.entry_username.focus())

    def display_logo(self):
        logo = load_logo(200, 150)
        if logo:
            self.logo_label.config(image=logo)
            self.logo_label.image = logo
        else:
            self.logo_label.config(text="Logo no encontrado", font=self.app_font, fg="red")
            self.logo_label.image = None

    def handle_login(self, event=None):
        """Manejar login (acepta evento para bindings de teclado)"""
        user_name = self.entry_username.get()
        password = self.entry_password.get()
        user_id = None
        login_successful = False

        user_access_level, user_id = verify_login(user_name, password)
        
        if user_access_level is not None:
            #messagebox.showinfo("Éxito", "¡Inicio de sesión exitoso!")
            self.transition_to_main_app(user_access_level, user_id, user_name)
            login_successful = True
        else:
            messagebox.showerror("Error", "Credenciales inválidas")
        
        log_login_attempt(user_id, user_name,  1 if login_successful else 0)

    def transition_to_main_app(self, user_access_level, user_id, user_name):
        """Maneja la transición limpia a la aplicación principal"""
        # Ocultar la ventana completamente
        self.root.withdraw()        
        # Destruir widgets de login
        self.main_frame.destroy()        
        # Limpiar completamente la ventana
        for widget in self.root.winfo_children():
            widget.destroy()        
        # Configurar ventana principal
        self.root.title("Aplicación de báscula")        
        # Calcular posición centrada
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (1200 / 2))
        y_coordinate = int((screen_height / 2) - (800 / 2))
        
        # Aplicar geometría mientras está oculta
        self.root.geometry(f"1200x800+{x_coordinate}+{y_coordinate}")
        
        # Crear MainApp mientras está oculta
        MainApp(self.root, user_access_level, user_id, user_name)
        self.root.geometry("1200x800")
        
        # Forzar actualización y mostrar en la posición correcta
        self.root.update_idletasks()
        self.root.deiconify()
        self.root.focus_force()