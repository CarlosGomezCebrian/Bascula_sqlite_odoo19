# logic_weighing_video.py
import tkinter as tk


class WeighingVideo:
    def __init__(self):
        self.camera_frames ={}

    def resize_camera_feed(self, camera_id, camera_frames):
        """Redimensionar el feed de cámara manteniendo la relación de aspecto"""
        self.camera_frames = camera_frames
        if camera_id not in self.camera_frames:
            return
        
        camera_data = self.camera_frames[camera_id]
        canvas = camera_data['canvas']
        container = camera_data['canvas_container']
        
        # Obtener dimensiones del contenedor
        container_width = container.winfo_width()
        container_height = container.winfo_height()
        
        if container_width <= 5 or container_height <= 5:
            return
        
        # Calcular tamaño máximo disponible por cámara (2x2 grid)
        available_width = container_width
        available_height = container_height
        
        # Calcular nuevas dimensiones manteniendo relación de aspecto
        target_ratio = camera_data['aspect_ratio']
        available_ratio = available_width / available_height
        
        if available_ratio > target_ratio:
            # Contenedor más ancho que la relación objetivo
            # Usar toda la altura disponible
            display_height = available_height
            display_width = int(display_height * target_ratio)
        else:
            # Contenedor más alto que la relación objetivo  
            # Usar todo el ancho disponible
            display_width = available_width
            display_height = int(display_width / target_ratio)
        
        # Centrar en el contenedor
        x_offset = (available_width - display_width) // 2
        y_offset = (available_height - display_height) // 2
        
        # Configurar el canvas para que ocupe el espacio calculado
        canvas.place(
            x=x_offset, 
            y=y_offset, 
            width=display_width, 
            height=display_height
        )
        
        # Actualizar la imagen si existe
        if camera_data['current_image'] and camera_data['original_image']:
            try:
                from PIL import Image, ImageTk
                
                original_image = camera_data['original_image']
                
                # Redimensionar imagen manteniendo relación de aspecto
                resized_image = original_image.resize(
                    (display_width, display_height), 
                    Image.Resampling.LANCZOS
                )
                
                photo = ImageTk.PhotoImage(resized_image)
                canvas.delete("all")  # Limpiar canvas
                
                # Crear imagen centrada (ahora el canvas ya está centrado)
                canvas.create_image(
                    display_width // 2,
                    display_height // 2,
                    image=photo,
                    anchor=tk.CENTER
                )
                canvas.image = photo  # Mantener referencia
                
                # Ocultar label de estado cuando hay imagen
                camera_data['status_label'].place_forget()
                
            except Exception as e:
                self.logger.error(f"Error redimensionando imagen para {camera_id}: {str(e)}")
                # Mostrar label de error
                camera_data['status_label'].place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        else:
            # Mostrar label de estado centrado
            camera_data['status_label'].place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            
        def update_camera_feed(self, camera_id, image=None, status="connected", message=None):
            """
            Placeholder para actualizar el feed de cámara
            Esta función será implementada en otro archivo con la lógica de video
            """
            self.logger.debug(f"Llamada a update_camera_feed para {camera_id} - Estado: {status}")
            
            # Aquí solo registramos la llamada, la implementación estará en otro módulo
            if camera_id in self.camera_frames:
                camera_data = self.camera_frames[camera_id]
                
                # Solo actualizamos el texto de estado por ahora
                status_messages = {
                    'connected': '✅ Conectada',
                    'disconnected': '❌ Desconectada', 
                    'error': '⚠️ Error'
                }
                status_text = status_messages.get(status, '❓ Estado desconocido')
                display_text = f"📷 {camera_id.replace('_', ' ').title()}\n{status_text}"
                if message:
                    display_text += f"\n{message}"
                
                camera_data['status_label'].configure(text=display_text)
                camera_data['status'] = status
                
            else:
                self.logger.warning(f"Cámara {camera_id} no encontrada")      


    def set_camera_aspect_ratio(self, camera_id, aspect_ratio):
        """
        Establecer la relación de aspecto para una cámara específica
        
        Args:
            camera_id (str): 'camera_1', 'camera_2', etc.
            aspect_ratio (float): Relación de aspecto (ancho/alto), ej: 16/9, 4/3
        """
        if camera_id in self.camera_frames:
            self.camera_frames[camera_id]['aspect_ratio'] = aspect_ratio
            self.logger.debug(f"Relación de aspecto establecida para {camera_id}: {aspect_ratio}")
            # Forzar redimensionamiento
            self._resize_camera_feed(camera_id)