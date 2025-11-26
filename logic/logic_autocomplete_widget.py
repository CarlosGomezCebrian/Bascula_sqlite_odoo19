# custom_autocomplete.py

import tkinter as tk
from tkinter import ttk
import unicodedata

class CustomAutocompleteEntry:
    
    def __init__(self, parent, items, mapping_dict=None, width=30, height=8, placeholder=""):  
        self.parent = parent
        self.items = items
        self.mapping_dict = mapping_dict or {}
        self.filtered_items = items.copy()
        self.placeholder = placeholder
        self.is_placeholder = bool(placeholder)     
        
        # Frame principal
        self.frame = ttk.Frame(parent)
        
        # Entry
        self.entry = tk.Entry(self.frame, width=width, font=("Helvetica", 10), borderwidth=0)
        self.entry.pack(side=tk.TOP, fill=tk.X)
        
        # Configurar placeholder si existe
        if self.placeholder:
            self.setup_placeholder()
        
        # Listbox en una ventana Toplevel para posición absoluta
        self.listbox_window = tk.Toplevel(parent)
        self.listbox_window.withdraw()
        self.listbox_window.overrideredirect(True)
        self.listbox_window.configure(bg='white', relief='flat', bd=0)
        
        # Frame para listbox y scrollbar
        listbox_frame = ttk.Frame(self.listbox_window)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.listbox = tk.Listbox(
            listbox_frame, 
            width=width, 
            height=height, 
            font=("Arial", 10),
            relief='flat',           
            bd=0,                    
            highlightthickness=0,    
            selectbackground='#0078d4',  # Color de selección moderno
            selectforeground='white'
        )
        self.scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        
        # Configurar scrollbar
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)
        
        # Empaquetar listbox y scrollbar
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox_visible = False
        self._select_callback = None
        
        # Configurar eventos
        self.setup_events()
        self.update_listbox()


    def set_select_callback(self, callback):
        """Permite establecer una función callback que se ejecutará al seleccionar un item."""
        self._select_callback = callback
    
    def setup_placeholder(self):
        """Configurar placeholder"""
        self.entry.insert(0, self.placeholder)
        self.entry.configure(foreground='gray')
        
        def on_focus_in(event):
            if self.is_placeholder:
                self.entry.delete(0, tk.END)
                self.entry.configure(foreground='black')
                self.is_placeholder = False
        
        def on_focus_out(event):
            if not self.entry.get():
                self.entry.insert(0, self.placeholder)
                self.entry.configure(foreground='gray')
                self.is_placeholder = True
        
        self.entry.bind('<FocusIn>', on_focus_in)
        self.entry.bind('<FocusOut>', on_focus_out)
    
    def remove_accents(self, text):
        """Convierte texto quitando acentos y a minúsculas"""
        if not text:
            return ""
        text_normalized = unicodedata.normalize('NFD', text)
        text_without_accents = ''.join(
            c for c in text_normalized 
            if unicodedata.category(c) != 'Mn'
        )
        return text_without_accents.lower()
    
    def setup_events(self):
        """Configurar eventos de teclado y ratón"""
        
        def on_keyrelease(event):
            if event.keysym not in ['Down', 'Up', 'Return', 'Escape']:
                # Si hay placeholder y se empieza a escribir, limpiarlo
                if self.is_placeholder and event.keysym not in ['Control_L', 'Control_R']:
                    self.entry.delete(0, tk.END)
                    self.entry.configure(foreground='black')
                    self.is_placeholder = False
                
                self.filter_items()
                if self.entry.get() and self.filtered_items:
                    self.show_listbox()
                else:
                    self.hide_listbox()
            
            if event.keysym == 'Escape':
                self.hide_listbox()
                return
            
            if event.keysym == 'Return':
                self.select_item()
                return "break"
        
        def on_keypress(event):
            if event.keysym == 'Down':
                if not self.listbox_visible and self.filtered_items:
                    self.show_listbox()
                if self.filtered_items:
                    self.listbox.focus_set()
                    self.listbox.selection_set(0)
                    self.listbox.see(0)
                return "break"
            
            if event.keysym == 'Up' and self.listbox_visible:
                self.listbox.focus_set()
                if not self.listbox.curselection():
                    self.listbox.selection_set(tk.END)
                    self.listbox.see(tk.END)
                return "break"
        
        def on_listbox_key(event):
            if event.keysym == 'Return':
                self.select_item()
                return "break"
            
            if event.keysym == 'Escape':
                self.hide_listbox()
                self.entry.focus_set()
                return "break"
            
            if event.keysym == 'Up':
                selection = self.listbox.curselection()
                if selection and selection[0] > 0:
                    new_index = selection[0] - 1
                    self.listbox.selection_clear(0, tk.END)
                    self.listbox.selection_set(new_index)
                    self.listbox.see(new_index)
                return "break"
            
            if event.keysym == 'Down':
                selection = self.listbox.curselection()
                if selection and selection[0] < len(self.filtered_items) - 1:
                    new_index = selection[0] + 1
                    self.listbox.selection_clear(0, tk.END)
                    self.listbox.selection_set(new_index)
                    self.listbox.see(new_index)
                return "break"
        
        def on_listbox_click(event):
            self.select_item()
        
        def on_entry_click(event):
            # Si hay placeholder, limpiarlo al hacer clic
            if self.is_placeholder:
                self.entry.delete(0, tk.END)
                self.entry.configure(foreground='black')
                self.is_placeholder = False
            
            if self.filtered_items:
                self.show_listbox()
        
        def on_entry_focus_in(event):
            if self.entry.get() and self.filtered_items:
                self.show_listbox()
            elif not self.entry.get():
                self.filtered_items = self.items.copy()
                self.update_listbox()
                if self.filtered_items:
                    self.show_listbox()
        
        def on_focus_out(event):
            self.frame.after(150, self.check_focus)
        
        # Vincular eventos
        self.entry.bind('<KeyRelease>', on_keyrelease)
        self.entry.bind('<KeyPress>', on_keypress)
        self.entry.bind('<Button-1>', on_entry_click)
        self.entry.bind('<FocusIn>', on_entry_focus_in)
        self.entry.bind('<FocusOut>', on_focus_out)
        
        self.listbox.bind('<KeyPress>', on_listbox_key)
        self.listbox.bind('<Button-1>', on_listbox_click)
        self.listbox.bind('<Double-Button-1>', on_listbox_click)
        
        self.parent.bind('<Configure>', lambda e: self.position_listbox())
    
    def position_listbox(self):
        """Método de posicionamiento"""
        if self.listbox_window and self.listbox_visible:
            x = self.entry.winfo_rootx()
            y = self.entry.winfo_rooty() + self.entry.winfo_height()
            width = self.entry.winfo_width()
            
            item_count = len(self.filtered_items)
            max_height = 8
            visible_height = min(item_count, max_height)
            height_pixels = visible_height * 20
            
            self.listbox_window.wm_geometry(f"{width}x{height_pixels}+{x}+{y}")
            self.listbox.config(height=visible_height)
    
    def filter_items(self):
        """Filtrar items ignorando acentos"""
        typed = self.entry.get()
        typed_normalized = self.remove_accents(typed)
        
        if typed_normalized:
            self.filtered_items = [
                item for item in self.items 
                if typed_normalized in self.remove_accents(item)
            ]
        else:
            self.filtered_items = self.items.copy()
        
        self.update_listbox()
    
    def update_listbox(self):
        """Actualizar el contenido del Listbox"""
        self.listbox.delete(0, tk.END)
        for item in self.filtered_items:
            self.listbox.insert(tk.END, item)
    
    def show_listbox(self):
        """Mostrar el Listbox en posición absoluta"""
        if self.entry.cget('state') in ('readonly', 'disabled'):
            return
        if not self.listbox_visible and self.filtered_items:
            self.listbox_window.deiconify()
            self.listbox_visible = True
            self.position_listbox()
            self.listbox_window.lift()
        # *** NUEVO: Capturar el clic en cualquier parte de la aplicación ***
        self.entry.winfo_toplevel().bind_all('<Button-1>', self.check_click_outside)
    
    def hide_listbox(self):
        """Ocultar el Listbox"""
        if self.listbox_window.winfo_exists() and self.listbox_window.winfo_viewable():
            self.listbox_window.withdraw()
            self.listbox_visible = False

        # *** NUEVO: Liberar el enlace de clic ***
            self.entry.winfo_toplevel().unbind_all('<Button-1>')

    def check_click_outside(self, event):
        if not self.listbox_window.winfo_exists() or not self.listbox_window.winfo_viewable():
            return
            
        # Coordenadas del listbox y entry/frame
        lx, ly = self.listbox_window.winfo_rootx(), self.listbox_window.winfo_rooty()
        lw, lh = self.listbox_window.winfo_width(), self.listbox_window.winfo_height()
        ex, ey = self.frame.winfo_rootx(), self.frame.winfo_rooty()
        ew, eh = self.frame.winfo_width(), self.frame.winfo_height()

        # Comprobar si el clic está fuera de ambos
        is_inside_listbox = (lx <= event.x_root < lx + lw and ly <= event.y_root < ly + lh)
        is_inside_entry = (ex <= event.x_root < ex + ew and ey <= event.y_root < ey + eh)
        
        if not is_inside_listbox and not is_inside_entry:
            self.hide_listbox()

        # Si el clic NO está en el listbox O en el entry
        is_outside_listbox = not (lx <= event.x_root < lx + lw and ly <= event.y_root < ly + lh)
        is_outside_entry = not (ex <= event.x_root < ex + ew and ey <= event.y_root < ey + eh)
        
        # Si el clic no está ni en la lista ni en el entry, ocúltala
        if is_outside_listbox and is_outside_entry:
            self.hide_listbox()
    
    def check_focus(self):
        """Verificar si aún tenemos el foco"""
        focused_widget = self.parent.focus_get()
        if focused_widget not in [self.entry, self.listbox]:
            self.hide_listbox()
    
    def select_item(self):
        """Seleccionar item del Listbox"""
        selection = self.listbox.curselection()
        if selection:
            selected_text = self.listbox.get(selection[0])
            self.entry.delete(0, tk.END)
            self.entry.insert(0, selected_text)
            self.entry.configure(foreground='black')
            self.is_placeholder = False
            self.hide_listbox()
            self.entry.focus_set()

            if self._select_callback:
                self._select_callback(selected_text)
    
    def get(self):
        """Obtener texto actual"""
        if self.is_placeholder:
            return ""
        return self.entry.get()
    
    def get_mapped_value(self):
        """Obtener valor del mapping_dict basado en el texto actual"""
        current_text = self.get()
        return self.mapping_dict.get(current_text, "")
    
    def set(self, value):
        """Establecer valor en el entry"""
        self.entry.delete(0, tk.END)
        if value:
            self.entry.insert(0, value)
            self.entry.configure(foreground='black')
            self.is_placeholder = False
        else:
            if self.placeholder:
                self.entry.insert(0, self.placeholder)
                self.entry.configure(foreground='gray')
                self.is_placeholder = True
        self.hide_listbox()
    
    def clear(self):
        """Limpiar el entry"""
        self.set("")
    
    def pack(self, **kwargs):
        """Empaquetar el frame principal"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Colocar en grid el frame principal"""
        self.frame.grid(**kwargs)
    
    def focus_set(self):
        """Establecer foco en el entry"""
        self.entry.focus_set()
    
    def destroy(self):
        """Destruir la ventana del listbox al cerrar"""
        if self.listbox_window:
            self.listbox_window.destroy()