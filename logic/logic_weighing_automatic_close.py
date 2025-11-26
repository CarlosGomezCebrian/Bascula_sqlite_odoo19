import datetime
import tkinter as tk
from db_operations.db_folio_history  import FolioHistory

class AutomaticClose:
    def __init__(self, user_id: int =None):
        self.user_id = user_id
        self.db_history =  FolioHistory()

        self.id_history = None
        self.hitory_data ={}

    def register_weighing_automatically_closed(self, data, id_user_closed, db_manager,weighing_logic):
        exito = False
        weighing_type = data.get('weighing_type')
        vehicle_tara = int(data.get('vehicle_tara'))
        equipo_tara = int(data.get('equipo_tara'))   
        current_weight = vehicle_tara+equipo_tara
        current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if weighing_type == 'Entrada':
            self.id_history = self.db_history.get_last_hitory_id()
            folio_alm2_closed = data.get('folio_ALM2')
            if  folio_alm2_closed is not None and str(folio_alm2_closed).upper() != 'NONE' and folio_alm2_closed != '':
                #print(f"En el if folio_alm2_closed: {folio_alm2_closed}, de tipo: {type(folio_alm2_closed)}")
                gross_weight = int(data.get('weight_original'))
                customer_name = data.get('customer_name')
                tare_weight = int(current_weight)
                
                data_new_weight = weighing_logic.calculate_weight_alm2(gross_weight, tare_weight, customer_name )

                new_gross_weight_ALM2 = data_new_weight['new_gross_weight_ALM2']
                new_net_weight_ALM2  = data_new_weight['new_net_weight_ALM2']
                new_gross_weight =  data_new_weight['new_gross_weight']
                new_net_weight = data_new_weight['new_net_weight']
                
                weighing_closed_data_alm2 ={

                    'id_weighing': int(data.get('id_weighing'))-1,
                    'folio_number': (f"{data.get('folio_number')}A"),
                    'gross_weight': new_gross_weight_ALM2,
                    'tare_weight': tare_weight,
                    'date_end':current_date_time,
                    'net_weight': new_net_weight_ALM2,
                    'id_changes': self.id_history,
                    'scale_record_status':"Cerrado",
                    'id_user_closed': id_user_closed,
                    'notes':data.get('notes')
                }

                self.history_data ={                    
                    'id_weighing': data.get('id_weighing'),
                    'folio_number': (f"{data.get('folio_number')}A"),
                    'previous_value':"0",
                    'new_value': current_weight,
                    'datetime_modification':current_date_time,
                    'id_user_modificacion':id_user_closed

                 }
                
                exito = db_manager.close_weighing_input_alm2(weighing_closed_data_alm2)
                print(f"La rspuesta de la BD en logic entrada es: {exito}")

                if exito:
                    self.id_history = self.db_history.get_last_hitory_id()
                    self.db_history.incert_change(self.history_data)
                    weighing_closed_data ={
                        'id_weighing': data.get('id_weighing'),
                        'folio_number': {data.get('folio_number')},
                        'gross_weight': new_gross_weight,
                        'tare_weight': tare_weight,
                        'date_end':   current_date_time,
                        'net_weight': new_net_weight,
                        'id_changes': self.id_history,
                        'scale_record_status':"Cerrado",
                        'id_user_closed': id_user_closed,
                        'notes':data.get('notes')
                    }
                    result = db_manager.close_weighing_input(weighing_closed_data)
                    self.history_data ={                    
                        'id_weighing': data.get('id_weighing'),
                        'folio_number': data.get('folio_number'),
                        'previous_value':"0",
                        'new_value': current_weight,
                        'datetime_modification':current_date_time,
                        'id_user_modificacion':id_user_closed,
                        'history_notes':'Cerrado automaticamente'

                    }
                    self.db_history.incert_change(self.history_data)
                    #print_weighing_ticket(result['updated_row'])
            else:
                gross_weight = data.get('gross_weight')
                tare_weight = int(current_weight) 
                net_weight = weighing_logic.calculate_net_weight(int(gross_weight), int(tare_weight))
                self.id_history = self.db_history.get_last_hitory_id()
                weighing_closed_data ={
                    'id_weighing': data.get('id_weighing'),
                    'folio_number': data.get('folio_number'),
                    'tare_weight': tare_weight,
                    'date_end':current_date_time,
                    'net_weight': net_weight,
                    'id_changes': self.id_history,
                    'scale_record_status':"Cerrado",
                    'id_user_closed': id_user_closed,
                    'notes':data.get('notes')
                }
                result = db_manager.close_weighing_input(weighing_closed_data)

                self.history_data ={                    
                        'id_weighing': data.get('id_weighing'),
                        'folio_number': data.get('folio_number'),
                        'previous_value':"0",
                        'new_value': current_weight,
                        'datetime_modification':current_date_time,
                        'id_user_modificacion':id_user_closed,
                        'history_notes':'Cerrado automaticamente'

                    }
                self.db_history.incert_change(self.history_data)
                
                
        else:         
            result['exito'] = True                              
        return result