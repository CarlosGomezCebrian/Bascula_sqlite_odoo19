# logic_autocomplete.py
from db_operations.db_materials import Materials
from db_operations.db_customers import Customers
from db_operations.db_vehicles import Vehicles
from db_operations.db_trailers import Trailers
from db_operations.db_drivers import Drivers
from logic.logic_autocomplete_widget import CustomAutocompleteEntry
from logic.logic_odoo_api import get_odoo_materials, get_odoo_customers, get_odoo_drivers, get_odoo_vehicles, get_odoo_trailers
class AutocompleteHandler:
    def __init__(self):
        self.entries = {}
        self.mappings = {}
        self.materials_class = Materials()
        self.customers_class = Customers()
        self.vehicles_class = Vehicles()
        self.trailers_class = Trailers()
        self.drivers_class = Drivers()
        self.load_initial_data()
    
    def load_initial_data(self):
        """Cargar datos para autocomplete"""
        # Vehículos
        #vehicles = get_odoo_vehicles()
        #if vehicles is not None:
        #    result = self.vehicles_class.save_vehicles_from_odoo(vehicles)
        #if result >= 0:
        vehicles_data = self.vehicles_class.get_active_vehicles()
        if vehicles_data:
            vehicles_name = [f"{v[2]}-{v[3]}" for v in vehicles_data]
            vehicles_mapping = {f"{v[2]}-{v[3]}": v[0] for v in vehicles_data}
            self.mappings['vehicles'] = vehicles_mapping
            self.mappings['vehicles_names'] = vehicles_name

    # Remolques
        #trailers = get_odoo_trailers()
        #if trailers is not None:
        #    result = self.trailers_class.save_trailers_from_odoo(trailers)
        #if result >= 0:
        trailers_data = self.trailers_class.get_active_trailers()
        if trailers_data:
            trailers_name = [trailer[2] for trailer in trailers_data]
            trailers_mapping = {trailer[2]: trailer[0] for trailer in trailers_data}
            self.mappings['trailers'] = trailers_mapping
            self.mappings['trailers_names'] = trailers_name
        
        # Choferes
        #drivers = get_odoo_drivers()
        #if drivers is not None:
         #   result = self.drivers_class.save_drivers_from_odoo(drivers)
        #if result >= 0:
        drivers_data = self.drivers_class.get_active_drivers()
        if drivers_data:
            drivers_name = [driver[2] for driver in drivers_data]
            drivers_mapping = {driver[2]: driver[0] for driver in drivers_data}
            self.mappings['drivers'] = drivers_mapping
            self.mappings['drivers_names'] = drivers_name
        
        # Clientes
        #customers = get_odoo_customers()
        #if customers is not None:
        #    result = self.customers_class.save_customers_from_odoo(customers)
        #if result >= 0:
        customers_data = self.customers_class.get_active_customers()
        if customers_data:
            customers_name = [customer[2] for customer in customers_data]
            customers_mapping = {customer[2]: customer[1] for customer in customers_data}
            customers_discount = {customer[2]: customer[3] for customer in customers_data}
            customers_id_alm2 = {customer[2]: customer[4] for customer in customers_data}
            self.mappings['customers'] = customers_mapping
            self.mappings['customers_names'] = customers_name
            self.mappings['customers_discount'] = customers_discount
            self.mappings['customers_id_alm2'] = customers_id_alm2

        # Materiales    
        #materials = get_odoo_materials()
        #if materials is not None:
        #    result = self.materials_class.save_materials_from_odoo(materials)
        #if result >= 0:
        materials_data = self.materials_class.get_active_materials()            
        if materials_data:
            materials_name = [material[2] for material in materials_data]
            materials_mapping = {material[2]: material[0] for material in materials_data}
            material_spd = {material[2]: material[3] for material in materials_data}
            self.mappings['materials'] = materials_mapping
            self.mappings['materials_names'] = materials_name
            self.mappings['material_spd'] = material_spd
        else: print("Sin coneccion a datos")
    
    
    def create_vehicle_entry(self, parent):
        entry = CustomAutocompleteEntry(
            parent, 
            items=self.mappings.get('vehicles_names', []),
            mapping_dict=self.mappings.get('vehicles', {}),
            width=35,
            height=12, 
            placeholder="Seleccione un vehículo..."
        )
        self.entries['vehicles'] = entry        
        return entry
    
    def create_trailer_entry(self, parent):
        entry = CustomAutocompleteEntry(
            parent, 
            items=self.mappings.get('trailers_names', []),
            mapping_dict=self.mappings.get('trailers', {}),
            width=35,
            height=12, 
            placeholder="Seleccione un remolque/contenedor..."
        )
        self.entries['trailers'] = entry
        return entry
    
    def create_driver_entry(self, parent):
        """Crear entry para choferes"""
        entry = CustomAutocompleteEntry(
            parent, 
            items=self.mappings.get('drivers_names', []),
            mapping_dict=self.mappings.get('drivers', {}),
            width=35,
            height=12, 
            placeholder="Seleccione un chofer..."
        )
        self.entries['drivers'] = entry
        return entry
    
    def create_customer_entry(self, parent):
        """Crear entry para clientes"""
        entry = CustomAutocompleteEntry(
            parent, 
            items=self.mappings.get('customers_names', []),
            mapping_dict=self.mappings.get('customers', {}),
            width=35,
            height=12, 
            placeholder="Seleccione un cliente..."
        )
        self.entries['customers'] = entry
        return entry
    
    def create_material_entry(self, parent):
        """Crear entry para materiales"""
        entry = CustomAutocompleteEntry(
            parent, 
            items=self.mappings.get('materials_names', []),
            mapping_dict=self.mappings.get('materials', {}),
            width=35, 
            placeholder="Seleccione un material..."
        )
        self.entries['materials'] = entry
        return entry

    # En la clase AutocompleteHandler, cambia los nombres de las claves:

    def create_vehicle_entry_manual(self, parent):
        entry = CustomAutocompleteEntry(
            parent, 
            items=self.mappings.get('vehicles_names', []),
            mapping_dict=self.mappings.get('vehicles', {}),
            width=35,
            height=12, 
            placeholder="Seleccione un vehículo..."
        )
        self.entries['vehicles_manual'] = entry  # Cambia la clave
        return entry

    def create_trailer_entry_manual(self, parent):
        entry = CustomAutocompleteEntry(
            parent, 
            items=self.mappings.get('trailers_names', []),
            mapping_dict=self.mappings.get('trailers', {}),
            width=35,
            height=12, 
            placeholder="Seleccione un remolque/contenedor..."
        )
        self.entries['trailers_manual'] = entry  # Cambia la clave
        return entry

    def create_driver_entry_manual(self, parent):
        entry = CustomAutocompleteEntry(
            parent, 
            items=self.mappings.get('drivers_names', []),
            mapping_dict=self.mappings.get('drivers', {}),
            width=35,
            height=12, 
            placeholder="Seleccione un chofer..."
        )
        self.entries['drivers_manual'] = entry  # Cambia la clave
        return entry

    def create_customer_entry_manual(self, parent):
        entry = CustomAutocompleteEntry(
            parent, 
            items=self.mappings.get('customers_names', []),
            mapping_dict=self.mappings.get('customers', {}),
            width=35,
            height=12, 
            placeholder="Seleccione un cliente..."
        )
        self.entries['customers_manual'] = entry  # Cambia la clave
        return entry

    def create_material_entry_manual(self, parent):
        entry = CustomAutocompleteEntry(
            parent, 
            items=self.mappings.get('materials_names', []),
            mapping_dict=self.mappings.get('materials', {}),
            width=35, 
            placeholder="Seleccione un material..."
        )
        self.entries['materials_manual'] = entry  # Cambia la clave
        return entry   
        