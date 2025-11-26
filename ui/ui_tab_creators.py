# ui_tab_creators.py

import tkinter as tk
from tkinter import ttk
from ui.ui_weighing_tab import PesajeTab
from ui.ui_folios_tab import FoliosTab
from ui.ui_users_tab import UsersTab


class TabCreators:
    def __init__(self, styles, autocomplete_handler=None, user_id=None, user_access_level= None):
        self.styles = styles
        self.autocomplete_handler = autocomplete_handler
        self.user_id = user_id
        self.user_access_level= user_access_level
        self.folios_tab_instance = None  # Guardar referencia a la instancia

    
    def create_pesaje_tab(self, notebook):
        """Crear pestaña de pesaje"""
        pesaje_tab = PesajeTab(notebook, self.styles, self.autocomplete_handler, self.user_id, self.user_access_level)
        return pesaje_tab.get_frame()
    
    def create_folios_tab(self, notebook):
        """Crear pestaña de folios con evento de cambio de pestaña"""
        self.folios_tab_instance = FoliosTab(notebook, self.styles)        
        # Configurar el evento de cambio de pestaña
        notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)        
        return self.folios_tab_instance   
     

    def create_users_tab(self, notebook):
        """Crear pestaña de pesaje"""
        if self.user_access_level >=3:
            users_tab = UsersTab(notebook, self.styles, self.user_id, self.user_access_level)
            return users_tab.get_frame()
    
    def _on_tab_changed(self, event):
        """Manejar cambio de pestaña"""
        notebook = event.widget
        selected_tab = notebook.select()
        
        if selected_tab:
            tab_text = notebook.tab(selected_tab, "text")
            
            # Si la pestaña seleccionada es "Folios", cargar los datos
            if tab_text == "Folios" and self.folios_tab_instance:
                self.folios_tab_instance.folio_table.load_folios()