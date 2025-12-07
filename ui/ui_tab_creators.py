# ui_tab_creators.py

import tkinter as tk
from tkinter import ttk
from ui.ui_weighing_tab import PesajeTab
from ui.ui_folios_tab import FoliosTab
from ui.ui_users_tab import UsersTab
from ui.ui_manual_folios_tab import ManualFoliosTab


class TabCreators:
    def __init__(self, styles, autocomplete_handler=None, user_id=None, user_access_level= None):
        self.styles = styles
        self.autocomplete_handler = autocomplete_handler
        self.user_id = user_id
        self.user_access_level= user_access_level
        self.folios_tab_instance = None  # Guardar referencia a la instancia set_initial_folio(self)
        self.create_pesaje_tab_instance = None
        self.manual_folios_instance = None

    
    def create_pesaje_tab(self, notebook):
        """Crear pestaña de pesaje"""
        self.create_pesaje_tab_instance = PesajeTab(notebook, self.styles, self.autocomplete_handler, self.user_id, self.user_access_level)
        notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed) 
        #return pesaje_tab.get_frame()
        return self.create_pesaje_tab_instance
    
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
            self.manual_folios_instance = ManualFoliosTab(notebook, self.styles, self.autocomplete_handler, self.user_id, self.user_access_level)
            #return users_tab.get_frame(), manual_folios_tab.get_frame()
            return users_tab.get_frame(), self.manual_folios_instance
        
        
    
    def _on_tab_changed(self, event):
        """Manejar cambio de pestaña"""
        notebook = event.widget
        selected_tab = notebook.select()
        
        if selected_tab:
            tab_text = notebook.tab(selected_tab, "text")
            
            # Si la pestaña seleccionada es "Folios", cargar los datos
            if tab_text == "Folios" and self.folios_tab_instance:
                self.folios_tab_instance.folio_table.load_folios()

            if tab_text == "Registrar peso" and self.create_pesaje_tab_instance:
                self.create_pesaje_tab_instance.set_initial_folio()

            if tab_text == "Generar folio manual" and self.manual_folios_instance:
                self.manual_folios_instance._set_initial_folio()
                self.manual_folios_instance.table_all_folios.refresh_table()