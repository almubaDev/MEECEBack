# utils/image_handler.py
from PIL import Image
import os
from django.conf import settings
from datetime import datetime
import uuid
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ImageHandler:
    def __init__(self, image_file, directory='uploads', max_size=(1920, 1080)):
        self.image_file = image_file
        self.directory = directory
        self.max_size = max_size
        self.upload_path = os.path.join(settings.MEDIA_ROOT, directory)
        Path(self.upload_path).mkdir(parents=True, exist_ok=True)

    def process_image(self):
        """Procesa la imagen: optimiza, redimensiona y guarda"""
        try:
            # Asegurarse de que el puntero del archivo esté al inicio
            self.image_file.seek(0)
            
            # Abrir la imagen
            image = Image.open(self.image_file)
            
            # Convertir a RGB si es necesario
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Redimensionar si excede el tamaño máximo
            if image.size[0] > self.max_size[0] or image.size[1] > self.max_size[1]:
                image.thumbnail(self.max_size, Image.LANCZOS)
            
            # Generar nombre único usando timestamp y uuid
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = uuid.uuid4().hex[:8]
            original_name = os.path.splitext(self.image_file.name)[0]
            ext = os.path.splitext(self.image_file.name)[1].lower()
            
            # Sanitizar el nombre original
            safe_name = "".join(c for c in original_name if c.isalnum() or c in ('-', '_'))[:30]
            
            # Construir nombre final
            filename = f"{timestamp}_{safe_name}_{unique_id}{ext}"
            filepath = os.path.join(self.upload_path, filename)
            
            # Guardar imagen optimizada
            image.save(
                filepath, 
                quality=85, 
                optimize=True,
                progressive=True
            )
            
            # Retornar path relativo para la URL
            return os.path.join(self.directory, filename)
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise ValueError(f"Error procesando imagen: {str(e)}")

    @staticmethod
    def validate_image(image_file):
        """Valida el archivo de imagen"""
        try:
            # Verificar tamaño máximo (5MB)
            if image_file.size > settings.IMAGE_UPLOAD_MAX_SIZE:
                raise ValueError("La imagen no debe superar los 5MB")
                
            # Verificar tipo de archivo
            if image_file.content_type not in settings.IMAGE_UPLOAD_ALLOWED_TYPES:
                raise ValueError("Tipo de archivo no permitido")
                
            # Verificar que sea una imagen válida
            try:
                image_file.seek(0)
                img = Image.open(image_file)
                img.verify()
                image_file.seek(0)
                
                # Abrir de nuevo para verificar dimensiones
                img = Image.open(image_file)
                
                # Verificar dimensiones mínimas
                if img.size[0] < 200 or img.size[1] < 200:
                    raise ValueError("La imagen es demasiado pequeña (mínimo 200x200)")
                
                image_file.seek(0)
                
            except Exception as e:
                raise ValueError(f"Archivo de imagen inválido: {str(e)}")
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating image: {str(e)}")
            raise ValueError(str(e))