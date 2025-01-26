# content/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db.models import Q
import os
from django.conf import settings
from urllib.parse import urlparse
from tinymce.models import HTMLField

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_created"
    )

    class Meta:
        abstract = True


class Publication(BaseModel):
    title = models.CharField(max_length=200, blank=False, null=False)
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived')
        ],
        default='draft'
    )
    layout = models.JSONField(default=list)
    section = models.ForeignKey('Section', on_delete=models.CASCADE)
    publish_date = models.DateTimeField(blank=False, null=False)
    featured_image = models.ImageField(upload_to='publications/', blank=False, null=False)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-publish_date']

    def delete(self, *args, **kwargs):
        try:
            # Guardar referencia a las imágenes antes de eliminar
            layout_images = []
            if self.layout:
                for row in self.layout:
                    for cell in row.get('cells', []):
                        if cell.get('type') == 'image' and cell.get('content'):
                            try:
                                # Convertir URL a ruta relativa
                                url_path = urlparse(cell['content']).path
                                # Remover MEDIA_URL del inicio
                                relative_path = url_path.replace(settings.MEDIA_URL, '', 1)
                                if relative_path:
                                    layout_images.append(relative_path)
                                    print(f"Imagen encontrada en layout: {relative_path}")
                            except Exception as e:
                                print(f"Error procesando ruta de imagen: {e}")

            # Eliminar el featured_image
            if self.featured_image:
                try:
                    featured_image_path = self.featured_image.path
                    if os.path.isfile(featured_image_path):
                        os.remove(featured_image_path)
                        print(f"Imagen destacada eliminada: {featured_image_path}")
                except Exception as e:
                    print(f"Error eliminando imagen destacada: {e}")

            # Eliminar las imágenes del layout
            for image_path in layout_images:
                try:
                    full_path = os.path.join(settings.MEDIA_ROOT, image_path)
                    if os.path.isfile(full_path):
                        os.remove(full_path)
                        print(f"Imagen de layout eliminada: {full_path}")
                    else:
                        print(f"Archivo no encontrado: {full_path}")
                except Exception as e:
                    print(f"Error eliminando imagen de layout: {e}")

        except Exception as e:
            print(f"Error general en delete: {e}")
        finally:
            # Llamar al método delete original
            super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_instance = Publication.objects.get(pk=self.pk)
                old_images = set()
                new_images = set()

                # Recolectar imágenes antiguas
                if old_instance.layout:
                    for row in old_instance.layout:
                        for cell in row.get('cells', []):
                            if cell.get('type') == 'image' and cell.get('content'):
                                url_path = urlparse(cell['content']).path
                                relative_path = url_path.replace(settings.MEDIA_URL, '', 1)
                                if relative_path:
                                    old_images.add(relative_path)

                # Recolectar imágenes nuevas
                if self.layout:
                    for row in self.layout:
                        for cell in row.get('cells', []):
                            if cell.get('type') == 'image' and cell.get('content'):
                                url_path = urlparse(cell['content']).path
                                relative_path = url_path.replace(settings.MEDIA_URL, '', 1)
                                if relative_path:
                                    new_images.add(relative_path)

                # Eliminar imágenes que ya no están en uso
                for image_path in old_images - new_images:
                    try:
                        full_path = os.path.join(settings.MEDIA_ROOT, image_path)
                        if os.path.isfile(full_path):
                            os.remove(full_path)
                            print(f"Imagen eliminada durante actualización: {full_path}")
                    except Exception as e:
                        print(f"Error eliminando imagen durante actualización: {e}")

            except Publication.DoesNotExist:
                pass

        super().save(*args, **kwargs)
        

class Section(BaseModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        # Añadir índice único case-insensitive para title
        constraints = [
            models.UniqueConstraint(
                fields=['title'],
                name='unique_title_case_insensitive',
                violation_error_message="Ya existe una sección con este nombre (sin importar mayúsculas/minúsculas)."
            )
        ]

    def clean(self):
        if self.title:
            # Verificar si existe una sección con el mismo título (case-insensitive)
            exists = Section.objects.filter(
                Q(title__iexact=self.title)
            ).exclude(pk=self.pk).exists()
            
            if exists:
                raise ValidationError({
                    'title': 'Ya existe una sección con este nombre (sin importar mayúsculas/minúsculas).'
                })

    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecutar validaciones
        self.slug = slugify(self.title)  # Siempre normalizar el slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    

class Biography(BaseModel):
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=150)
    biography = models.TextField(max_length=500)
    photo = models.ImageField(upload_to='biographys/', blank=True, null=True)
    email = models.EmailField(blank=True)
    linkedin = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']