# config.py


from tkinter import filedialog
import os
import sqlite3
from PIL import Image, ImageTk
from db_operations.db_connect import  DatabaseManager

db_manager = DatabaseManager()

def set_logo_path(logo_path):
    """
    Guarda la ruta del logotipo en la base de datos.
    """
    conn = None
    try:
        conn = sqlite3.connect('scale_app_DB.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO app_settings (setting_key, setting_value)
            VALUES (?, ?)
            ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value;
        ''', ('logo_path', logo_path))
        
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        if conn:
            conn.close()

def get_logo_path():
    """
    Abre un cuadro de diálogo para que el usuario seleccione un archivo de imagen.
    Solo acepta archivos .jpeg y .png, los valida, guarda la ruta y la retorna.
    """
    filetypes = [
        ("Archivos de imagen", "*.png *.jpg *.jpeg"),
        ("Todos los archivos", "*.*")
    ]
    
    logo_path = filedialog.askopenfilename(
        title="Selecciona un archivo de logotipo",
        filetypes=filetypes
    )
    
    if logo_path:
        file_extension = os.path.splitext(logo_path)[1].lower()
        if file_extension in ['.jpeg', '.png', '.jpg']:
            if set_logo_path(logo_path):
                return logo_path
            else:
                return None
        else:
            return None
    
    return None

def load_logo(width, height):
    """
    Carga la imagen del logotipo desde la base de datos y la prepara para Tkinter.
    """
    conn = None
    logo_path = None
    try:
        conn = sqlite3.connect('scale_app_DB.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT setting_value FROM app_settings WHERE setting_key = 'logo_path'")
        result = cursor.fetchone()
        
        if result and result[0]:
            logo_path = result[0]
            if os.path.exists(logo_path):
                original_image = Image.open(logo_path)
                resized_image = original_image.resize((width, height), Image.Resampling.LANCZOS)
                tk_image = ImageTk.PhotoImage(resized_image)
                return tk_image
            else:
                print("Error: La ruta del logotipo no es válida.")
                return None
        return None
        
    except sqlite3.Error as e:
        print(f"Error al cargar la ruta del logo: {e}")
        return None
    except Exception as e:
        print(f"Error al procesar la imagen del logo: {e}")
        return None
    finally:
        if conn:
            conn.close()


def set_logo_path_print(company_logo_path_print):
    """
    Guarda la ruta del logotipo en la base de datos.
    """
    conn = None
    try:
        conn = sqlite3.connect('scale_app_DB.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO app_settings (setting_key, setting_value)
            VALUES (?, ?)
            ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value;
        ''', ('company_logo_path_print', company_logo_path_print))
        
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        if conn:
            conn.close()

def get_logo_path_print():
    """
    Abre un cuadro de diálogo para que el usuario seleccione un archivo de imagen.
    Solo acepta archivos .jpeg y .png, los valida, guarda la ruta y la retorna.
    """
    filetypes = [
        ("Archivos de imagen", "*.png *.jpg *.jpeg"),
        ("Todos los archivos", "*.*")
    ]
    
    company_logo_path_print = filedialog.askopenfilename(
        title="selecciona un archivo de logotipo para impresora termica",
        filetypes=filetypes
    )
    
    if company_logo_path_print:
        file_extension = os.path.splitext(company_logo_path_print)[1].lower()
        if file_extension in ['.jpeg', '.png', '.jpg']:
            if set_logo_path_print(company_logo_path_print):
                return company_logo_path_print
            else:
                return None
        else:
            return None
    
    return None


 # config.py - CORREGIR INDENTACIÓN
def set_window_icon(root, icon_path):
    icon_path  = os.path.join("img","icono.png")
    """
    Configura el icono de la ventana
    Args:
        root: La ventana de Tkinter
        icon_path: Ruta al archivo de icono (png o ico)
    """
    try:
        from PIL import Image, ImageTk
        # Intentar con PNG primero
        icon_image = Image.open(icon_path)
        icon_photo = ImageTk.PhotoImage(icon_image)
        root.iconphoto(True, icon_photo)
        return True
    except:
        try:
            # Fallback a ICO
            root.iconbitmap(icon_path)
            return True
        except:
            print(f"No se pudo cargar el icono: {icon_path}")
            return False
        
def save_company_data_settings(company_address, company_name, port_scale):
    """ port
    Guarda el nombre y dirección de la compañía en la base de datos.
    """
    print(f"company_address:{company_address}\ncompany_name:{company_name}\nport_scale:{port_scale}")
    conn = None
    try:
        conn = db_manager.connect_db()
        cursor = conn.cursor()
        
        settings = {
            'company_address': company_address,
            'company_name': company_name,
            'company_port_scale': port_scale
        }
        print(f"settings: {settings}")
        for key, value in settings.items():
            cursor.execute('''
                INSERT INTO app_settings (setting_key, setting_value)
                VALUES (?, ?)
                ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value;
            ''', (key, value))
            
        conn.commit()
        print(f"Nombre de la  compania: {company_name}.\nDireccion de la compañia: {company_address}. ")
        return True
    except sqlite3.Error as e:
        print(f"Error al guardar la configuración de Odoo: {e}")
        return False
    finally:
        if conn:
            db_manager.close_db(conn)


def get_company_config():
    """
    Obtiene la configuración de la compañia desde la base de datos.
    """
    conn = None
    try:
        conn = sqlite3.connect('scale_app_DB.db')
        cursor = conn.cursor()
        
        config = {}
        cursor.execute("SELECT setting_key, setting_value FROM app_settings WHERE setting_key LIKE 'company_%'")
        results = cursor.fetchall()
        for key, value in results:
            config[key] = value
        
        required_keys = ['company_logo_path_print', 'company_address', 'company_name', 'company_port_scale']
        if all(key in config and config[key] for key in required_keys):
            return config
        else:
            return {}
            
    except sqlite3.Error as e:
        print(f"Error al obtener la configuración de Odoo: {e}")
        return {}
    finally:
        if conn:
            conn.close()

