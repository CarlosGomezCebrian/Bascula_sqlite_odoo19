# logic_scale_manager.py

from logic.logic_scale_reader import create_scale_reader

class ScaleManager:
    def __init__(self, update_callback=None):
        self.update_callback = update_callback
        self.scale_reader = None
        self.use_simulator = False
        self.status_label = None
        self.scale_reader = create_scale_reader(use_simulator=self.use_simulator, update_callback=self.update_callback)
    
    def set_status_label(self, status_label, btn_scale_control):
        self.status_label = status_label
        self.btn_scale_control = btn_scale_control

    def set_use_simulator(self, use_simulator):
        """Actualizar el estado del simulador"""
        self.use_simulator = use_simulator
        # Si ya existe un scale_reader, detenerlo y crear uno nuevo
        if self.scale_reader:
            self.scale_reader.stop_reading()
            self.scale_reader = create_scale_reader(
                use_simulator=self.use_simulator, 
                update_callback=self.update_callback
            )

    
    def connect(self):
        if self.scale_reader.start_reading():
            self._update_status("Conectada ✓", "green", "⏹ Desconectar", "Warning.TButton")
        else:
            self._update_status("Error de conexión", "red",  "▶ Conectar",  "TButton" )
    
    def disconnect(self):
        self.scale_reader.stop_reading()
        self._update_status("Desconectada", "orange", "▶ Conectar",  "TButton" )
    
    def _update_status(self, text, color,  btn_text, btn_style):
        if self.status_label:
            self.status_label.config(text=text, foreground=color)
            self.btn_scale_control.configure(text=btn_text, style=btn_style,)

    def get_current_weight_data(self):
        return self.scale_reader.get_weight_data()