# logic_sync_operations.py

import tkinter as tk
from tkinter import messagebox, ttk
import threading
from db_operations.db_materials import Materials
from db_operations.db_customers import Customers
from db_operations.db_vehicles import Vehicles
from db_operations.db_trailers import Trailers
from db_operations.db_drivers import Drivers
from logic.logic_odoo_api import get_odoo_customers, get_odoo_materials, get_odoo_drivers, get_odoo_vehicles, get_odoo_trailers

class SyncOperations:
    def __init__(self, root, status_label, autocomplete_handler):
        """
        Args:
            root: Ventana principal
            status_label: Etiqueta para mostrar estado
            autocomplete_handler: Instancia de AutocompleteHandler
        """
        self.root = root
        self.status_label = status_label
        self.autocomplete_handler = autocomplete_handler
        self.materials_class = Materials()
        self.customers_class = Customers()
        self.vehicles_class = Vehicles()
        self.trailers_class = Trailers()
        self.drivers_class = Drivers()


    def _sync_type_entry_name(self,sync_type):
        
        sync_type_references={
            'vehicles': 'Vehículos',
            'trailers': 'Remolques',
            'drivers': 'Choferes',
            'customers': 'Clientes',
            'materials': 'Materiales'
        }
        return sync_type_references[sync_type]
    
    def start_sync_thread(self, sync_type):
        """Iniciar sincronización en hilo separado"""
        self.status_label.config(text=f"Sincronizando {self._sync_type_entry_name(sync_type)}...")
        self.root.update_idletasks()
        
        sync_thread = threading.Thread(target=self.run_sync, args=(sync_type,))
        sync_thread.daemon = True
        sync_thread.start()
    
    def run_sync(self, sync_type):
        """Ejecutar sincronización (en hilo secundario)"""
        result = None
        
        # Usar autocomplete_handler en lugar de tab_creator
        custom_entry = self.autocomplete_handler.entries.get(sync_type)
        
        try:
            if sync_type == 'vehicles':
                result = self._sync_vehicles(custom_entry)
            elif sync_type == 'trailers':
                result = self._sync_trailers(custom_entry)
            elif sync_type == 'drivers':
                result = self._sync_drivers(custom_entry)
            elif sync_type == 'materials':
                result = self._sync_materials(custom_entry)
            elif sync_type == 'customers':
                result = self._sync_customers(custom_entry)
        except Exception as e:
            print(f"Error en sincronización de {self._sync_type_entry_name(sync_type)}: {e}")
            result = -1
        
        # Mostrar resultado en el hilo principal
        self.root.after(0, self.show_sync_result, sync_type, result)

    def _sync_vehicles(self, custom_entry):
        """Sincronizar vehículos"""
        vehicles = get_odoo_vehicles()
        if vehicles is not None:
            result = self.vehicles_class.save_vehicles_from_odoo(vehicles)
            if result >= 0:
                self._update_autocomplete_data('vehicles', custom_entry)
            return result
        return -1
    
    def _sync_trailers(self, custom_entry):
        """Sincronizar remolques"""
        trailers = get_odoo_trailers()
        if trailers is not None:
            result = self.trailers_class.save_trailers_from_odoo(trailers)
            if result >= 0:
                self._update_autocomplete_data('trailers', custom_entry)
            return result
        return -1

    def _sync_drivers(self, custom_entry):
        """Sincronizar choferes"""
        drivers = get_odoo_drivers()
        if drivers is not None:
            result = self.drivers_class.save_drivers_from_odoo(drivers)
            if result >= 0:
                self._update_autocomplete_data('drivers', custom_entry)
            return result
        return -1

    def _sync_materials(self, custom_entry):
        """Sincronizar materiales"""
        materials = get_odoo_materials()
        if materials is not None:
            result = self.materials_class.save_materials_from_odoo(materials)            
            if result >= 0:
                self._update_autocomplete_data('materials', custom_entry)
            return result
        return -1

    def _sync_customers(self, custom_entry):
        """Sincronizar clientes"""
        customers = get_odoo_customers()
        if customers is not None:
            result = self.customers_class.save_customers_from_odoo(customers)            
            if result >= 0:
                self._update_autocomplete_data('customers', custom_entry)
            return result
        return -1

    def _update_autocomplete_data(self, data_type, custom_entry=None):
        """Actualizar datos en autocomplete_handler después de sincronizar"""
        data_getters = {
            'vehicles': (lambda: self.vehicles_class.get_active_vehicles(), lambda v: f"{v[2]}-{v[3]}", lambda v: f"{v[2]}-{v[3]}"),
            'trailers': (lambda: self.trailers_class.get_active_trailers(), lambda t: t[2], lambda t: t[2]),
            'drivers': (lambda: self.drivers_class.get_active_drivers(), lambda d: d[2], lambda d: d[2]),
            'customers': (lambda: self.customers_class.get_active_customers(), lambda c: c[2], lambda c: c[2]),
            'materials': (lambda: self.materials_class.get_active_materials(), lambda m: m[2], lambda m: m[2]) 
        }
        
        getter, name_formatter, key_formatter = data_getters.get(data_type) 
        if not getter:
            return 

        data_tupla = getter()
        
        if data_tupla:
            names = [name_formatter(item) for item in data_tupla]
            mapping = {key_formatter(item): item[0] for item in data_tupla} 
            
            if data_type == 'customers':
                mapping = {key_formatter(item): item[1] for item in data_tupla}
                customers_discount = {item[2]: item[3] for item in data_tupla} 
                customers_id_alm2 = {item[2]: item[4] for item in data_tupla}             
                
                self.autocomplete_handler.mappings['customers'] = mapping
                self.autocomplete_handler.mappings['customers_discount'] = customers_discount
                self.autocomplete_handler.mappings['customers_id_alm2'] = customers_id_alm2
            
            elif data_type == 'materials':
                mapping = {key_formatter(item): item[0] for item in data_tupla}
                material_spd = {item[2]: item[3] for item in data_tupla}

                self.autocomplete_handler.mappings['materials'] = mapping
                self.autocomplete_handler.mappings['material_spd'] = material_spd

            # 2. Actualizar TODAS las entradas relacionadas (normales y manuales)
            # Actualizar la entrada normal si existe
            if data_type in self.autocomplete_handler.entries:
                entry = self.autocomplete_handler.entries[data_type]
                entry.items = names
                entry.mapping_dict = mapping
            
            # ✅ NUEVO: Actualizar la entrada MANUAL si existe
            manual_key = f"{data_type}_manual"
            if manual_key in self.autocomplete_handler.entries:
                manual_entry = self.autocomplete_handler.entries[manual_key]
                manual_entry.items = names
                manual_entry.mapping_dict = mapping
            
            # 3. Actualizar mappings GENERALES en autocomplete_handler
            self.autocomplete_handler.mappings[data_type] = mapping
            self.autocomplete_handler.mappings[f'{data_type}_names'] = names
            
        # Si no hay datos, limpiar ambas entradas
        elif not data_tupla:
            print(f"No hay datos activos para {data_type}. Limpiando mappings.")
            
            # Limpiar entrada normal
            if data_type in self.autocomplete_handler.entries:
                self.autocomplete_handler.entries[data_type].items = []
                self.autocomplete_handler.entries[data_type].mapping_dict = {}
            
            # ✅ NUEVO: Limpiar entrada manual
            manual_key = f"{data_type}_manual"
            if manual_key in self.autocomplete_handler.entries:
                self.autocomplete_handler.entries[manual_key].items = []
                self.autocomplete_handler.entries[manual_key].mapping_dict = {}
            
            # Limpiar mappings
            self.autocomplete_handler.mappings[data_type] = {}
            self.autocomplete_handler.mappings[f'{data_type}_names'] = []
            
            if data_type == 'customers':
                self.autocomplete_handler.mappings['customers_discount'] = {}
                self.autocomplete_handler.mappings['customers_id_alm2'] = {}
            elif data_type == 'materials':
                self.autocomplete_handler.mappings['material_spd'] = {}
                
    def show_sync_result(self, sync_type, records_processed):
        """Mostrar resultado de la sincronización"""
        self.status_label.config(text="Sincronización completa.")
        
        if records_processed is not None and records_processed > 0:
            messagebox.showinfo(
                "Sincronización Exitosa", 
                f"Se procesaron {records_processed} registros de {self._sync_type_entry_name(sync_type)}.", 
                parent=self.root
            )
        elif records_processed is not None and records_processed == 0:
            messagebox.showinfo(
                "Sincronización Completa", 
                f"No se encontraron nuevos registros de {sync_type} para procesar.", 
                parent=self.root
            )
        else:
            messagebox.showerror(
                "Error", 
                f"Ocurrió un error al sincronizar {self._sync_type_entry_name(sync_type)}.", 
                parent=self.root
            )