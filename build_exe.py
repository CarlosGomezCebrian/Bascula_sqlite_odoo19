# build_exe.py
import os
import subprocess
import sys
import shutil
from pathlib import Path

def install_bcrypt_wheels():
    """Instala bcrypt con wheels compilados para Windows"""
    print("🔧 Instalando bcrypt con wheels...")
    
    # Forzar la instalación de wheels precompilados
    packages = [
        "bcrypt==4.1.2",  # Versión estable con wheels
        "python-escpos",
        "pillow",
        "requests",
        "cffi"  # Dependencia crítica para bcrypt
    ]
    
    for package in packages:
        try:
            # Forzar instalación con wheel
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "--force-reinstall", "--no-cache-dir",
                "--only-binary=all", package
            ], check=True, capture_output=True)
            print(f"  ✅ {package} instalado con wheel")
        except subprocess.CalledProcessError:
            print(f"  ⚠️  Problema con {package}, intentando instalación normal...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

def find_and_collect_bcrypt():
    """Encuentra y recolecta archivos de bcrypt"""
    try:
        import bcrypt
        bcrypt_path = os.path.dirname(bcrypt.__file__)
        print(f"📁 Ruta de bcrypt: {bcrypt_path}")
        
        # Buscar archivos .pyd (DLLs de Python)
        bcrypt_files = []
        for file in os.listdir(bcrypt_path):
            if file.endswith('.pyd') or '_bcrypt' in file:
                full_path = os.path.join(bcrypt_path, file)
                bcrypt_files.append(full_path)
                print(f"  ✅ {file}")
        
        return bcrypt_files
    except ImportError as e:
        print(f"❌ Error importando bcrypt: {e}")
        return []

def find_sqlite_dll():
    """Encuentra el DLL de SQLite3"""
    python_path = sys.base_prefix
    possible_paths = [
        os.path.join(python_path, 'DLLs', '_sqlite3.pyd'),
        os.path.join(python_path, 'DLLs', 'sqlite3.dll'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ SQLite3 encontrado: {path}")
            return path
    
    return None

def find_escpos_files():
    """Encuentra archivos JSON de escpos"""
    try:
        import escpos
        escpos_path = os.path.dirname(escpos.__file__)
        
        json_files = []
        capabilities_dir = os.path.join(escpos_path, 'capabilities')
        
        if os.path.exists(capabilities_dir):
            for root, dirs, files in os.walk(capabilities_dir):
                for file in files:
                    if file.endswith('.json'):
                        full_path = os.path.join(root, file)
                        json_files.append(full_path)
        
        main_json = os.path.join(escpos_path, 'capabilities.json')
        if os.path.exists(main_json):
            json_files.append(main_json)
        
        return escpos_path, json_files
    except ImportError:
        return None, []

def build_executable():
    """Empaqueta la aplicación con todos los fixes"""
    
    print("🚀 Iniciando empaquetado DEFINITIVO...")
    
    # Verificar archivos esenciales
    if not os.path.exists('main.py'):
        print("❌ main.py no encontrado")
        return False
    
    if not os.path.exists('icono_app.ico'):
        print("❌ icono_app.ico no encontrado")
        return False
    
    # Instalar paquetes críticos
    install_bcrypt_wheels()
    
    # Recolectar archivos de bcrypt ESPECÍFICAMENTE
    bcrypt_files = find_bcrypt_binary()
    
    # Si no se encuentran los archivos, forzar la recolección
    if not bcrypt_files:
        print("⚠️  No se encontraron archivos _bcrypt, buscando alternativas...")
        bcrypt_files = force_find_bcrypt()
    
    # Buscar SQLite3
    sqlite_dll = find_sqlite_dll()
    
    # Buscar escpos
    escpos_path, json_files = find_escpos_files()
    
    # Verificar estructura de la app
    required_items = ['db_operations', 'logic', 'ui', 'utils', 'img', 'scale_app_DB.db', 'sqlite3.exe']
    print("🔍 Verificando estructura...")
    for item in required_items:
        if not os.path.exists(item):
            print(f"  ❌ {item} faltante")
            return False
        print(f"  ✅ {item}")
    
    # Construir comando PyInstaller
    cmd = [
        'pyinstaller',
        '--name=BasculaSQLiteOdoo',
        '--onefile',
        '--windowed',
        '--clean',
        '--noconfirm',
    ]
    
    # AGREGAR ESTAS LÍNEAS CRÍTICAS PARA BCRYPT
    cmd.extend([
        '--collect-all=bcrypt',
        '--collect-all=cffi',
    ])
    
    # Agregar datos de la aplicación - INCLUYENDO IMG
    current_dir = os.getcwd()
    cmd.extend([
        f'--add-data={os.path.join(current_dir, "db_operations")};db_operations',
        f'--add-data={os.path.join(current_dir, "logic")};logic',
        f'--add-data={os.path.join(current_dir, "ui")};ui',
        f'--add-data={os.path.join(current_dir, "utils")};utils',
        f'--add-data={os.path.join(current_dir, "img")};img',  # ¡AGREGADO!
        f'--add-data={os.path.join(current_dir, "scale_app_DB.db")};.',
        f'--add-data={os.path.join(current_dir, "icono_app.ico")};.',
    ])
    
    # Agregar archivos binarios críticos de bcrypt
    for bcrypt_file in bcrypt_files:
        target_dir = 'bcrypt'
        cmd.append(f'--add-binary={bcrypt_file};{target_dir}')
    
    if sqlite_dll:
        cmd.append(f'--add-binary={sqlite_dll};.')
    
    # Agregar escpos
    if json_files:
        for json_file in json_files:
            relative_path = os.path.relpath(json_file, escpos_path)
            target_dir = os.path.dirname(relative_path)
            if target_dir == '.':
                cmd.append(f'--add-data={json_file};escpos')
            else:
                cmd.append(f'--add-data={json_file};escpos/{target_dir}')
    
    # Hidden imports CRÍTICOS - ACTUALIZADOS
    hidden_imports = [
        # Módulos del sistema
        'sqlite3', '_sqlite3', 'tkinter', 'os', 'sys', 'logging',
        
        # Módulos de terceros - ESPECÍFICOS PARA BCRYPT
        'bcrypt', 'bcrypt._bcrypt', 'cffi', 'cffi._cffi_backend',
        '_cffi_backend',  # ¡IMPORTANTE!
        
        'escpos', 'escpos.printer', 'escpos.escpos',
        'requests', 'PIL', 'PIL.Image', 'PIL.ImageTk',
        
        # Módulos de la aplicación
        'db_operations.db_create_db', 'db_operations.db_operations',
        'db_operations.db_users', 'db_operations.db_odoo_config',
        'ui.ui_login', 'ui.ui_dialog_windows', 'utils.logger_config',
        'logic.logic_odoo_api',
    ]
    
    for imp in hidden_imports:
        cmd.append(f'--hidden-import={imp}')
    
    # Icono y script principal
    cmd.extend(['--icon=icono_app.ico', 'main.py'])
    
    try:
        print("\n📦 Ejecutando PyInstaller...")
        print("⏳ Esto puede tomar varios minutos...")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completado")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en PyInstaller: {e}")
        if e.stderr:
            print(f"Detalles: {e.stderr}")
        return False

def create_complete_distribution():
    """Crea una distribución completa lista para usar"""
    dist_folder = "Distribucion_BasculaSQLiteOdoo"
    exe_source = os.path.join('dist', 'BasculaSQLiteOdoo.exe')
    
    if not os.path.exists(exe_source):
        print("❌ No se encontró el ejecutable")
        return False
    
    print(f"\n📦 Creando distribución completa: {dist_folder}")
    
    try:
        # Limpiar distribución anterior
        if os.path.exists(dist_folder):
            shutil.rmtree(dist_folder)
        
        # Crear estructura
        os.makedirs(dist_folder)
        os.makedirs(os.path.join(dist_folder, 'logs'))
        os.makedirs(os.path.join(dist_folder, 'temp'))
        
        # Copiar ejecutable
        shutil.copy2(exe_source, os.path.join(dist_folder, 'BasculaSQLiteOdoo.exe'))
        
        # Copiar archivos esenciales
        files_to_copy = ['icono_app.ico', 'scale_app_DB.db', 'README.md', 'sqlite3.exe']
        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy2(file, dist_folder)
                print(f"  ✅ {file}")
        
        # ¡COPIAR CARPETA IMG COMPLETA!
        if os.path.exists('img'):
            img_dest = os.path.join(dist_folder, 'img')
            if os.path.exists(img_dest):
                shutil.rmtree(img_dest)
            shutil.copytree('img', img_dest)
            print(f"  ✅ Carpeta 'img' copiada completa")
        
        # Crear archivos de configuración
        create_config_files(dist_folder)
        
        exe_size = os.path.getsize(exe_source) / (1024 * 1024)
        print(f"\n🎉 DISTRIBUCIÓN COMPLETADA")
        print(f"📁 Carpeta: {dist_folder}")
        print(f"📊 Tamaño ejecutable: {exe_size:.2f} MB")
        print(f"🔧 Lista para distribuir")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando distribución: {e}")
        return False

def create_config_files(dist_folder):
    """Crea archivos de configuración y ayuda"""
    
    # Archivo de instrucciones
    instructions = """INSTRUCCIONES - BÁSCULA SQLITE ODOO

🚀 INICIO RÁPIDO:
1. Ejecutar 'BasculaSQLiteOdoo.exe'
2. La aplicación creará automáticamente:
   - Base de datos (si no existe)
   - Usuario administrador
   - Estructura de carpetas

👤 PRIMER USO:
- Usuario: Admin
- Contraseña: Admin123
- Cambiar la contraseña después del primer login

⚙️ CONFIGURACIÓN ODOO:
1. Ir a: Menú → Configuración → Configuración Odoo
2. Ingresar:
   - URL de Odoo (ej: https://tudominio.odoo.com)
   - Nombre de la base de datos
   - Email de usuario
   - API Key

🖨️ CONFIGURACIÓN IMPRESORA:
- Compatible con impresoras térmicas ESC/POS

📊 FUNCIONALIDADES:
- Registro de pesajes (entrada/salida)
- Sincronización automática con Odoo
- Gestión de vehículos, remolques, materiales

🆘 SOPORTE:
- Logs: carpeta 'logs/'
- Imágenes: carpeta 'img/'
- Base de datos: 'scale_app_DB.db'

© 2025 - Sistema Integrado de Báscula
"""
    
    with open(os.path.join(dist_folder, 'INSTRUCCIONES.txt'), 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    # Archivo de requisitos (información)
    requirements_info = """REQUISITOS DEL SISTEMA:

Sistema Operativo:
- Windows 11 o superior
- Windows Server 2016 o superior

Requisitos Mínimos:
- 2 GB RAM
- 100 MB espacio libre
- Conexión a internet (para Odoo)

Requisitos Recomendados:
- 8 GB RAM  
- 500 MB espacio libre
- Windows 11 64-bit

Red:
- Acceso a servidor Odoo (puerto 443)
- Firewall configurado para la aplicación

Impresora:
- Compatible con ESC/POS
- USB, red o puerto serie
"""
    
    with open(os.path.join(dist_folder, 'REQUISITOS.txt'), 'w', encoding='utf-8') as f:
        f.write(requirements_info)

def clean_previous_builds():
    """Limpia builds anteriores"""
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🧹 Limpiado: {folder}")
    
    for file in ['BasculaSQLiteOdoo.spec']:
        if os.path.exists(file):
            os.remove(file)

def find_bcrypt_binary():
    """Encuentra el archivo binario _bcrypt específicamente"""
    try:
        import bcrypt
        bcrypt_path = os.path.dirname(bcrypt.__file__)
        
        # Buscar específicamente _bcrypt
        bcrypt_files = []
        for file in os.listdir(bcrypt_path):
            if file.endswith('.pyd') and '_bcrypt' in file:
                full_path = os.path.join(bcrypt_path, file)
                bcrypt_files.append(full_path)
                print(f"  ✅ Encontrado: {file}")
        
        # Si no se encuentra en el directorio principal, buscar en subdirectorios
        if not bcrypt_files:
            for root, dirs, files in os.walk(bcrypt_path):
                for file in files:
                    if file.endswith('.pyd') and '_bcrypt' in file:
                        full_path = os.path.join(root, file)
                        bcrypt_files.append(full_path)
                        print(f"  ✅ Encontrado en subdirectorio: {file}")
        
        return bcrypt_files
    except ImportError as e:
        print(f"❌ Error importando bcrypt: {e}")
        return []
    

def force_find_bcrypt():
    """Búsqueda forzada de archivos bcFrypt en el sistema"""
    import site
    bcrypt_files = []
    
    # Buscar en todos los sitios de Python
    for site_package in site.getsitepackages():
        bcrypt_pattern = os.path.join(site_package, 'bcrypt', '**', '*_bcrypt*')
        import glob
        for file in glob.glob(bcrypt_pattern, recursive=True):
            if file.endswith('.pyd'):
                bcrypt_files.append(file)
                print(f"  ✅ Encontrado por fuerza: {file}")
    
    # Buscar en directorio de usuario
    user_site = site.getusersitepackages()
    if user_site:
        bcrypt_pattern = os.path.join(user_site, 'bcrypt', '**', '*_bcrypt*')
        for file in glob.glob(bcrypt_pattern, recursive=True):
            if file.endswith('.pyd'):
                bcrypt_files.append(file)
                print(f"  ✅ Encontrado en user site: {file}")
    
    return bcrypt_files

if __name__ == "__main__":
    print("=" * 70)
    print("           EMPAQUETADOR - BÁSCULA SQLITE ODOO")
    print("=" * 70)
    
    # Limpiar builds anteriores
    clean_previous_builds()
    
    # Ejecutar build
    if build_executable():
        # Crear distribución completa
        create_complete_distribution()
        
        print("\n" + "=" * 70)
        print("🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
        print("=" * 70)
        print("\n📦 DISTRIBUCIÓN CREADA EN:")
        print(f"   📁 Distribucion_BasculaSQLiteOdoo/")
        print("\n🚀 PARA USAR:")
        print("   1. Comparte la carpeta 'Distribucion_BasculaSQLiteOdoo'")
        print("   2. El usuario ejecuta 'BasculaSQLiteOdoo.exe'")
        print("   3. ¡No requiere Python instalado!")
        print("\n🔧 INCLUYE:")
        print("   ✅ bcrypt._bcrypt (FIX aplicado)")
        print("   ✅ SQLite3 completo")
        print("   ✅ Icono personalizado")
        print("   ✅ Impresión ESC/POS")
        print("   ✅ Carpeta 'img' con todas las imágenes")
        print("   ✅ Documentación completa")
    else:
        print("\n💥 Error en el proceso de empaquetado")
    
    input("\nPresiona Enter para salir...")