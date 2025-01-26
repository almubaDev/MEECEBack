# content/management/commands/normalize_sections.py
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from content.models import Section, Publication

class Command(BaseCommand):
    help = 'Normaliza las secciones y corrige los slugs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='ID del usuario que se asignará como created_by',
            required=True
        )

    def handle(self, *args, **options):
        # Obtener el usuario
        User = get_user_model()
        try:
            user = User.objects.get(id=options['user_id'])
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'No se encontró un usuario con ID {options["user_id"]}')
            )
            return

        # Mapeo correcto de títulos a slugs
        SLUG_MAPPING = {
            'Revista': 'revista',
            'Congresos': 'congresos',
            'Media': 'media',
            'Presentación del Magíster': 'presentacion-del-magister',
            'Noticias': 'noticias'
        }

        self.stdout.write(self.style.SUCCESS('Corrigiendo slugs de secciones...'))
        
        for title, correct_slug in SLUG_MAPPING.items():
            section = Section.objects.filter(title__iexact=title).first()
            if section:
                old_slug = section.slug
                if old_slug != correct_slug:
                    section.slug = correct_slug
                    if not section.created_by:
                        section.created_by = user
                    Section.objects.filter(id=section.id).update(
                        slug=correct_slug,
                        created_by=section.created_by
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'Slug actualizado: {old_slug} -> {correct_slug}')
                    )

        # Mostrar resultado final
        self.stdout.write('\nSlugs finales:')
        for section in Section.objects.all():
            self.stdout.write(f'- {section.title}: {section.slug}')

        self.stdout.write(self.style.SUCCESS('\n¡Corrección de slugs completada!'))