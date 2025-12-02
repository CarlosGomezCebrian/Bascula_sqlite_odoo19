# create_db.py

import sqlite3

def create_database():
    """
    Crea la base de datos y las tablas para la aplicación de pesaje de vehiculos.
    """
    conn = None
    try:
        conn = sqlite3.connect('scale_app_DB.db')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id_user INTEGER PRIMARY KEY,
                user_name TEXT NOT NULL UNIQUE,
                creation_date TEXT NOT NULL,
                user_email TEXT NOT NULL UNIQUE, 
                password_hash TEXT NOT NULL,
                access_level INTEGER NOT NULL,
                active_user INTEGER NOT NULL,
                change_password_date TEXT,
                user_create	INTEGER,
                user_changes  INTEGER,
                user_change_password INTEGER,
                user_level_change INTEGER,
                date_last_change TEXT,
                FOREIGN KEY("user_change_password") REFERENCES "users"("id_user"),
                FOREIGN KEY("user_create") REFERENCES "users"("id_user"),
                FOREIGN KEY("user_level_change") REFERENCES "users"("id_user")
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id_customer INTEGER PRIMARY KEY,
                external_id_customer INTEGER,
                customer_name TEXT NOT NULL,
                environment_code INTEGER NOT NULL DEFAULT 0,
                customer_discount INTEGER NOT NULL DEFAULT 0,
                id_alm2 INTEGER NOT NULL DEFAULT 0,
                company_name TEXT NOT NULL,
                active_customer INTEGER NOT NULL
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id_vehicle INTEGER PRIMARY KEY,
                external_id_vehicle INTEGER,
                plates TEXT NOT NULL UNIQUE,
                vehicle_type TEXT NOT NULL,
                vehicle_tara INTEGER NOT NULL DEFAULT 0, 
                active_vehicle INTEGER NOT NULL
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trailers (
                id_trailer INTEGER PRIMARY KEY,
                external_id_trailer INTEGER NOT NULL,
                trailer_name TEXT NOT NULL UNIQUE,
                category_trailer TEXT NOT NULL,
                equipo_tara	INTEGER NOT NULL DEFAULT 0,
                active_trailer INTEGER NOT NULL
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drivers (
                id_driver INTEGER PRIMARY KEY,
                external_id_driver INTEGER,
                driver_name TEXT NOT NULL,
                license_number TEXT,
                active_driver INTEGER NOT NULL
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS materials (
                id_material INTEGER PRIMARY KEY,
                external_id_material INTEGER NOT NULL,
                material_name TEXT NOT NULL UNIQUE,
                udm TEXT NOT NULL,
                category TEXT,
                spd INTEGER NOT NULL,
                active_material INTEGER NOT NULL
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS folio_history (
                id_history INTEGER PRIMARY KEY,
                id_weighing INTEGER,
                folio_number TEXT NOT NULL,
                previous_value TEXT,
                new_value TEXT,
                datetime_modification TEXT NOT NULL,
                id_user_modificacion INTEGER,
                history_notes TEXT,
                FOREIGN KEY (id_weighing) REFERENCES weighing_records(id_weighing),
                FOREIGN KEY (id_user_modificacion) REFERENCES users(id_user)
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weighing_records (
                    id_weighing INTEGER PRIMARY KEY,
                    folio_number TEXT UNIQUE NOT NULL,
                    date_start TEXT,
                    days_open_folio INTEGER DEFAULT 0,
                    gross_weight INTEGER,
                    tare_weight INTEGER,
                    date_end TEXT,
                    net_weight INTEGER,
                    id_changes INTEGER NOT NULL DEFAULT 1,
                    weighing_type TEXT NOT NULL DEFAULT 'Pendiente', 
                    scale_record_status TEXT NOT NULL DEFAULT 'Pendiente',
                    id_status_odoo INTEGER,
                    saved_in_Odoo INTEGER DEFAULT 0,                   
                    notes TEXT,
                    weight_original INTEGER DEFAULT 0,
                    folio_ALM2 TEXT,
                    id_customer INTEGER,
                    id_vehicle INTEGER,
                    id_trailer  INTEGER,                    
                    id_driver INTEGER,
                    id_material INTEGER,
                    id_user INTEGER,
                    id_user_closed INTEGER,
                    FOREIGN KEY("id_changes") REFERENCES "folio_history"("id_history"),
                    -- FOREIGN KEY (id_customer) REFERENCES customers(id_customer),
                    FOREIGN KEY (id_customer) REFERENCES customers(external_id_customer),
                    FOREIGN KEY (id_vehicle) REFERENCES vehicles(id_vehicle),
                    FOREIGN KEY (id_trailer) REFERENCES trailers(id_trailer), 
                    FOREIGN KEY (id_driver) REFERENCES drivers(id_driver),
                    FOREIGN KEY (id_material) REFERENCES materials(id_material),
                    FOREIGN KEY (id_user) REFERENCES users(id_user), 
                    FOREIGN KEY (id_user_closed) REFERENCES users(id_user)
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logins (
                id_login_history INTEGER PRIMARY KEY,
                id_user INTEGER,
                user_text TEXT,
                datetime TEXT NOT NULL,
                successful_authentication INTEGER NOT NULL,
                FOREIGN KEY (id_user) REFERENCES users(id_user)
            );
        ''')

        # Nueva tabla para la configuración de la aplicación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL
            );
        ''')

        _insert_default_external_records(cursor)
        _insert_default_settings(cursor)
        conn.commit()
        print("Base de datos y tablas creadas exitosamente.")
        return True

    except sqlite3.Error as e:
        print(f"Error al crear la base de datos: {e}")
        return False

    finally:
        if conn:
            conn.close()


def _insert_default_external_records(cursor):   
    """Insertar registros externos por defecto"""
    
    # Insertar cliente externo
    cursor.execute('''
        INSERT OR IGNORE INTO customers (
            external_id_customer, customer_name, environment_code, 
            customer_discount, id_alm2, company_name, active_customer
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (0, 'Cliente externo', 0, 0, 0, 'Externo', 1))
    
    # Insertar vehículo externo
    cursor.execute('''
        INSERT OR IGNORE INTO vehicles (
            external_id_vehicle, plates, vehicle_type, vehicle_tara, active_vehicle
        ) VALUES (?, ?, ?, ?, ?)
    ''', (0, 'VEHEXT', 'Vehículo externo', 0, 1))

    cursor.execute('''
        INSERT OR IGNORE INTO trailers (
            external_id_trailer, trailer_name, category_trailer, equipo_tara, active_trailer
        ) VALUES (?, ?, ?, ?, ?)
    ''', (0, 'Sin remolque', 'Externa', 0, 1))  # Corregido: Extena -> Externa

    cursor.execute('''
        INSERT OR IGNORE INTO vehicles (
            external_id_vehicle, plates, vehicle_type, vehicle_tara, active_vehicle
        ) VALUES (?, ?, ?, ?, ?)
    ''', (0, 'SLRMQ', 'Solo remolque', 0, 1))
    
    # Insertar chofer externo
    cursor.execute('''
        INSERT OR IGNORE INTO drivers (
            external_id_driver, driver_name, license_number, active_driver
        ) VALUES (?, ?, ?, ?)
    ''', (0, 'Chofer externo', 'Licencia externa', 1))
    
    # Insertar material externo
    cursor.execute('''
        INSERT OR IGNORE INTO materials (
            external_id_material, material_name, udm, category, spd, active_material
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (0, 'Material externo', 'kg', 'Externo', 0, 1))


def _insert_default_settings(cursor):
    """Insertar configuraciones por defecto"""
    default_settings = [
        ('company_name', 'Mi Empresa'),
        ('company_address', 'Dirección de la empresa')
    ]
    
    for key, value in default_settings:
        cursor.execute('''
            INSERT OR IGNORE INTO app_settings (setting_key, setting_value)
            VALUES (?, ?)
        ''', (key, value))


if __name__ == '__main__':
    create_database()