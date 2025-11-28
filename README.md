📄 README: Sistema de Pesaje para Vehículos (Báscula)
Este proyecto implementa una aplicación de báscula de pesaje diseñada para registrar el peso de tráilers y camionetas. Se encarga de la comunicación con el dispositivo de pesaje, la gestión de datos en una base de datos local SQLite, y la sincronización con un sistema Odoo ERP para la gestión centralizada de la información de pesaje.

✨ Características Principales
Captura de Peso: Interfaz de comunicación con la báscula para la lectura en tiempo real de los pesos.

Base de Datos Local (SQLite): Almacenamiento rápido y local de todos los registros de pesaje.

Generación de Pesos: Cálculo del peso Neto a partir de los pesos Tara y Bruto.

Integración con Odoo:

Actualización de datos (clientes, productos, vehículos) desde Odoo.

Guardado de los registros de pesaje (Tara, Bruto, Neto) en un modelo específico dentro de Odoo.

📄 README: Sistema de Pesaje para Vehículos (Báscula)
Este proyecto implementa una aplicación de báscula de pesaje diseñada para registrar el peso de tráilers y camionetas. Se encarga de la comunicación con el dispositivo de pesaje, la gestión de datos en una base de datos local SQLite, y la sincronización con un sistema Odoo ERP para la gestión centralizada de la información de pesaje.

✨ Características Principales
Captura de Peso: Interfaz de comunicación con la báscula para la lectura en tiempo real de los pesos.

Base de Datos Local (SQLite): Almacenamiento rápido y local de todos los registros de pesaje.

Generación de Pesos: Cálculo del peso Neto a partir de los pesos Tara y Bruto.

Integración con Odoo:

Actualización de datos (clientes, productos, vehículos) desde Odoo.

Guardado de los registros de pesaje (Tara, Bruto, Neto) en un modelo específico dentro de Odoo.

🛠️ Requisitos del Sistema
Para ejecutar esta aplicación, necesitarás:

Python 3.x

Dispositivo de Báscula: Un dispositivo de pesaje compatible (generalmente a través de un puerto serial/USB).

Acceso a la Base de Datos Odoo: Credenciales de conexión válidas para la base de datos PostgreSQL de Odoo.

⚙️ Instalación

1. Clonar el Repositorio
   git clone [URL_DEL_REPOSITORIO]
   cd [NOMBRE_DEL_DIRECTORIO]
2. Instalar Dependencias de Python
   Todas las dependencias necesarias se encuentran en el archivo
   requirements.txt
   pip install -r requirements.txt
   Nota: Las dependencias incluyen librerías esenciales como psycopg2 (para PostgreSQL/Odoo)
   pyserial o pyusb (para la báscula)
   zeep (para servicios web, si se usa la API XML-RPC de Odoo)
   y las librerías de generación de reportes (reportlab, openpyxl, etc.)
3. Configuración de ConexionesDebe configurar los parámetros de  
    conexión para la Báscula, la base de datos SQLite (ruta del archivo) y la base de datos Odoo (host, puerto, base de datos, usuario y contraseña).
   Estos parámetros se configuran una vez abierta la aplicacion en el menu de configuracion,

   dbname = odoo_database_name
   user = odoo_user
   password = odoo_password

   [WEIGHBRIDGE]
   port = COM4 ; o /dev/ttyUSB0, dependiendo del sistema
   baudrate = 9600
   timeout = 1

   🚀 Uso
   1.Iniciar la Aplicación:
   python main.py
   2.Proceso de Pesaje:
   La aplicación se conecta a Odoo para obtener datos maestros (ej. vehículos, clientes).
   Registrar un peso Tara (vehículo vacío).
   Registrar un peso Bruto (vehículo cargado).
   La aplicación calcula automáticamente el peso Neto ($Neto = Bruto - Tara$).
   3.Guardado de Datos:
   Todos los registros de pesaje se guardan inmediatamente en la base de datos local SQLite.
   Una vez confirmado, el registro de pesaje completo (Tara, Bruto, Neto) se sincroniza con el modelo de datos correspondiente en Odoo.
   🧑‍💻 Tecnologías Utilizadas
   Backend:
   Python
   Base de Datos Local:
   SQLite
   Integración ERP:
   PostgreSQL (a través de psycopg2) y API de Odoo
   Dependencias Clave (Basadas en requirements.txt):
   psycopg2: Conexión a la base de datos Odoo/PostgreSQL
   pyserial/pyusb: Comunicación con el hardware de la báscula
   zeep: Comunicación con servicios web (posiblemente Odoo)
   reportlab, PyPDF2: Funcionalidades de generación de pdf.
