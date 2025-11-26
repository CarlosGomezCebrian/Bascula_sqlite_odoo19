# ui_folios_tab.py

import tkinter as tk
from tkinter import ttk, messagebox
from logic.logic_tables_folios import FoliosWeighingsTable
from logic.logic_print_folios import   print_weighing_ticket

class FoliosTab:
   def __init__(self, notebook, styles):
         self.styles = styles
         self.frame = ttk.Frame(notebook, style="TFrame")
         notebook.add(self.frame, text="Folios")
         self.search_folio_entry = None
        
         self._create_ui()        
         self.folio_table = FoliosWeighingsTable(self.table_container,  self.search_folio_entry)


   def _create_ui(self):
        self._create_accion_buttons()
        self._create_folios_table_section()

   def _create_accion_buttons(self):
         
         action_frame = ttk.LabelFrame(
            self.frame, text="Folios", 
            style="TFrame",padding=10)
         action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Guardar referencias a los botones state="disabled
         self.print_button = ttk.Button(action_frame, text="Imprimir", cursor="hand2",
                command=lambda: self._print_folio(), 
                style="TButton")
         self.print_button.pack(side=tk.LEFT, padx=5)

         self.search_folio_entry = ttk.Entry(action_frame)
         self.search_folio_entry.pack(side=tk.RIGHT, padx=5)
         self.search_folio_entry.bind('<KeyRelease>', self.search_folio)

         self.search_folio_label = ttk.Label(action_frame, style="TLabel", text="Buscar folio:", font=("Helvetica", 12))
         self.search_folio_label.pack(side=tk.RIGHT, padx=5)
         self.search_folio_entry.focus()
         

   def _create_folios_table_section(self):
        """Crear sección para la tabla de pesajes pendientes"""
        # Frame contenedor para la tabla
        self.table_container = ttk.Frame(self.frame, style="TFrame", padding=5)
        self.table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


   def _print_folio(self):
         data = self.folio_table.get_selected_folio_data() 
         #print(f"Data en print folio{data}")
         if data:                    
            try:
               exito, e = print_weighing_ticket(data)              
               
               if exito:
                  messagebox.showinfo(
                     "Impreso",
                     f"✅ Pesaje Folio: {data['folio_number']} impreso exitosamente.",
                     parent=self.frame
                  )
                  data ={}
                  return None
               else:
                  #mensaje_text= "not found or cable not plugged in"
                  mensaje_text="Impresora no conectada"
                  mensaje = str(e)
                  print(f"Mensaje del folio_tab: {mensaje}")
                  if mensaje_text in mensaje:
                      mensaje_en_pantalla = "La impresora no se encuentra\n o el cable no esta conectado"
                  messagebox.showerror(
                     "Error",
                     # parent=self.frame
                     f"⚠️ Problemas para imprimir el folio  {data['folio_number']}\n{mensaje_en_pantalla}",
                  )
                  return None
                  
            except Exception as e:
                  messagebox.showerror(
                  "Error Inesperado",
                  f"❌ Ocurrió un error inesperado:\n{e}",
                  #parent=self.frame
               )
                  print("Error Inesperado",
                  f"❌ Ocurrió un error inesperado:\n{e}",)
         else:
               messagebox.showerror(
                     "Error",
                     f"⚠️ No se selecciono ningun folio")
               

               
   def search_folio(self, event=None):
    """Buscar folios por texto"""
    search_text = self.search_folio_entry.get().strip()
    
    if search_text:
        self.folio_table.update_table(search_text)            
    else:
        self.folio_table.load_folios()