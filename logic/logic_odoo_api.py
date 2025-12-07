# logic_odoo_api.py

import json
import requests
import socket
import urllib.error
import urllib.parse
from db_operations.db_odoo_config import OdooConfig
from tkinter import messagebox
from utils.logger_config import app_logger

# Crear un logger específico para Odoo
odoo_logger = app_logger.getChild('odoo_api')
odoo_config = OdooConfig()
trebol_company_id = 1

def get_odoo_connection_config():
    """
    Obtiene y valida la configuración de conexión a Odoo.
    
    Returns:
        dict: Configuración de conexión o None si hay error
    """
    config = odoo_config.get_odoo_config()
    
    if not config:
        odoo_logger.error("No se encontró configuración de Odoo en la base de datos")
        return None
    
    required_fields = ['odoo_url', 'odoo_db_name', 'odoo_api_user_email', 'odoo_api_key']
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        odoo_logger.error(f"Configuración de Odoo incompleta. Faltan: {missing_fields}")
        return None
    
    return config

def make_odoo_json_request(model, method="search_read", domain=None, fields=None, limit=1000):
    """
    Realiza una petición a Odoo 19+ usando el endpoint /json/2/
    
    Args:
        model (str): Modelo de Odoo (ej: 'fleet.vehicle')
        method (str): Método a ejecutar (por defecto 'search_read')
        domain (list): Dominio para filtrar
        fields (list): Campos a retornar
        limit (int): Límite de registros
    
    Returns:
        list/dict: Respuesta de Odoo o None en caso de error
    """
    config = get_odoo_connection_config()
    if not config:
        return None
    
    url = f"{config['odoo_url']}/json/2/{model}/{method}"
    api_key = config['odoo_api_key']
    
    # Preparar payload
    payload = {
        "domain": domain or [],
        "fields": fields or [],
        "limit": limit
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
        # "X-Odoo-Database": config['odoo_db_name']  # Opcional según documentación
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        odoo_logger.info(f"✅ Petición {model}.{method} exitosa: {len(data) if isinstance(data, list) else 1} registros")
        return data
        
    except requests.exceptions.RequestException as e:
        odoo_logger.error(f"❌ Error de conexión en {model}.{method}: {e}")
        return None
    except json.JSONDecodeError as e:
        odoo_logger.error(f"❌ Error decodificando JSON en {model}.{method}: {e}")
        return None
    except Exception as e:
        odoo_logger.error(f"❌ Error inesperado en {model}.{method}: {e}")
        return None

def test_odoo_connection():
    """
    Prueba la conexión con Odoo 19+ usando el endpoint /json/2/
    """
    odoo_logger.info("Probando conexión con Odoo 19+ (/json/2/ endpoint)...")
    
    config = get_odoo_connection_config()
    odoo_db_name= config['odoo_db_name']
    if not config:
        messagebox.showerror(
            "Error de Configuración", 
            "No se encontró configuración de Odoo en la base de datos."
        )
        return False
    
    # Probar con una consulta simple de usuarios
    result = make_odoo_json_request(
        'res.users',
        domain=[['id', '=', 1]],
        fields=['name', 'login']
    )
    
    if result is not None:
        odoo_logger.info("✅ Conexión Odoo 19+ exitosa")
        messagebox.showinfo(
            "Conexión Exitosa", 
            f"✅ Conexión con {odoo_db_name} exitosa\nUsando endpoint /json/2/"
        )
        return True
    else:
        odoo_logger.error("❌ Conexión Odoo 19+ fallida")
        messagebox.showerror(
            "Error de Conexión",
            "❌ No se pudo conectar a Odoo\n\n"
            "Verifica:\n"
            "• URL del servidor\n"
            "• API Key y permisos\n"
            "• Usuario tiene acceso API\n"
        )
        return False

# FUNCIONES MIGRADAS AL NUEVO ENDPOINT

def get_odoo_vehicles():
    """
    Recupera los registros de vehículos (fleet.vehicle) de Odoo.
    """
    odoo_logger.info("Solicitando vehículos desde Odoo...")
    
    domain_filter_vehicles = [["company_id", "=", trebol_company_id]]
    fields = ['model_id', 'license_plate', 'x_studio_tara', 'active']
    
    vehicles = make_odoo_json_request(
        'fleet.vehicle',
        domain=domain_filter_vehicles,
        fields=fields
    )
    
    return vehicles

def get_odoo_trailers():
    """
    Recupera los registros de remolques (maintenance.equipment) de Odoo.
    """
    odoo_logger.info("Solicitando remolques desde Odoo...")
    
    domain_filter_trailers = [
        ["company_id", "=", 1],
        ["category_id", "in", [10, 9, 15]]
    ]
    fields = ['name', 'category_id', 'x_studio_equipo_tara', 'active']
    
    trailers = make_odoo_json_request(
        'maintenance.equipment',
        domain=domain_filter_trailers,
        fields=fields
    )
    
    return trailers

def get_odoo_drivers():
    """
    Recupera los registros de choferes (hr.employee) de Odoo.
    """
    odoo_logger.info("Solicitando choferes desde Odoo...")
    
    domain_filter_drivers = [
        ["department_id", "=", 20],
        ["company_id", "=", 1]
    ]
    fields = ['name', 'job_title', 'active']
    
    drivers = make_odoo_json_request(
        'hr.employee',
        domain=domain_filter_drivers,
        fields=fields
    )
    
    return drivers

def get_odoo_materials():
    """
    Recupera los registros de materiales (product.template) de Odoo.
    """
    odoo_logger.info("Solicitando materiales desde Odoo...")
    
    domain_filter_product = [
        ['uom_name', '=', 'kg'],
        ["type", "=", "consu"], 
        ['company_id', '=', trebol_company_id]
    ]
    fields = ['id', 'display_name', 'active', 'uom_name', 'categ_id', 'company_id', 'x_studio_spd']
    
    materials = make_odoo_json_request(
        'product.template',
        domain=domain_filter_product,
        fields=fields
    )
    
    return materials

def get_odoo_customers():
    """
    Recupera los registros de clientes (res.partner) de Odoo.
    """
    odoo_logger.info("Solicitando clientes desde Odoo...")
    
    domain_filter_contact = [
        ['is_company', '=', True], 
        ['company_id', '=', trebol_company_id],
        ['x_studio_use_scale', '=', True]
    ]
    fields = ['id', 'name', 'active', 'x_studio_referencia_ambiente', 'company_id']
    
    partners = make_odoo_json_request(
        'res.partner',
        domain=domain_filter_contact,
        fields=fields
    )
    
    return partners

# Eliminar funciones obsoletas de XML-RPC
def get_odoo_authenticated_connection():
    """
    ⚠️ OBSOLETO en Odoo 19+ - Usar make_odoo_json_request en su lugar
    """
    odoo_logger.warning("Función obsoleta llamada - usar JSON endpoint en su lugar")
    return None, None, get_odoo_connection_config()

# Mantener la función de diagnóstico si la necesitas
def diagnose_odoo_connection():
    """
    Función de diagnóstico actualizada para Odoo 19+
    """
    odoo_logger.info("Ejecutando diagnóstico de conexión Odoo 19+...")
    
    config = get_odoo_connection_config()
    if not config:
        return "❌ No hay configuración de Odoo en la base de datos"
    
    diagnostic_messages = []
    
    # Test de conexión básica
    result = make_odoo_json_request(
        'res.users',
        domain=[['id', '=', 1]],
        fields=['name'],
        limit=1
    )
    
    if result is not None:
        diagnostic_messages.append("✅ Conexión JSON API exitosa")
        diagnostic_messages.append(f"✅ Autenticación con API Key válida")
        diagnostic_messages.append(f"✅ Modelos accesibles")
    else:
        diagnostic_messages.append("❌ Error en conexión JSON API")
    
    return "\n".join(diagnostic_messages)

"""
if __name__ == "__main__":
    # Probar todas las funciones
    test_odoo_connection()
    
    vehiculos = get_odoo_vehicles()
    remolques = get_odoo_trailers()
    choferes = get_odoo_drivers()
    materiales = get_odoo_materials()
    clientes = get_odoo_customers()
    
    print(f"Vehículos: {len(vehiculos) if vehiculos else 0}")
    print(f"Remolques: {len(remolques) if remolques else 0}")
    print(f"Choferes: {len(choferes) if choferes else 0}")
    print(f"Materiales: {len(materiales) if materiales else 0}")
    print(f"Clientes: {len(clientes) if clientes else 0}")
"""