from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Section, Publication, Biography
from .serializers import SectionSerializer, PublicationSerializer, BiographySerializer
from rest_framework.views import APIView
from django.conf import settings
from .utils.image_handler import ImageHandler
from django.utils.text import slugify


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    parser_classes = (JSONParser,)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Asignamos manualmente created_by
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                detail = e.message_dict
            else:
                detail = {'non_field_errors': [str(e)]}
            return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            print("Error creating section:", str(e))
            print(traceback.format_exc())
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # Aseguramos que created_by sea el usuario actual
        serializer.save(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            
            # No sobrescribir created_by en actualizaciones
            self.perform_update(serializer)
            
            return Response(serializer.data)
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                detail = e.message_dict
            else:
                detail = {'non_field_errors': [str(e)]}
            return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            print("Error updating section:", str(e))
            print(traceback.format_exc())
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=['patch'])
    def reorder(self, request):
        try:
            for item in request.data:
                Section.objects.filter(id=item['id']).update(order=item['order'])
            return Response({'status': 'ok'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PublicationViewSet(viewsets.ModelViewSet):
   queryset = Publication.objects.all()
   serializer_class = PublicationSerializer
   parser_classes = (MultiPartParser, FormParser, JSONParser)

   def perform_create(self, serializer):
       serializer.save(created_by=self.request.user)

   def get_queryset(self):
       queryset = Publication.objects.all()
       section = self.request.query_params.get('section', None)
       if section is not None:
           queryset = queryset.filter(section_id=section)
       return queryset

   @action(detail=False, methods=['get'])
   def featured(self, request):
       featured = self.get_queryset().filter(is_featured=True)
       serializer = self.get_serializer(featured, many=True)
       return Response(serializer.data)

   @action(detail=True, methods=['post'])
   def upload_cell_image(self, request, pk=None):
       try:
           image_file = request.FILES.get('image')
           if not image_file:
               return Response({
                   'error': 'No se proporcionó ninguna imagen',
                   'success': 0
               }, status=400)

           try:
               # Validar imagen
               ImageHandler.validate_image(image_file)
               
               # Procesar imagen
               handler = ImageHandler(
                   image_file,
                   directory=settings.UPLOAD_PATHS['editor_uploads']
               )
               relative_path = handler.process_image()
               
               # Construir URL completa con el dominio
               image_url = request.build_absolute_uri(settings.MEDIA_URL + relative_path)
               
               return Response({
                   'url': image_url,
                   'uploaded': 1
               })
               
           except ValueError as e:
               return Response({
                   'error': str(e),
                   'uploaded': 0
               }, status=400)
           
       except Exception as e:
           import traceback
           print("Error al procesar imagen:", str(e))
           print(traceback.format_exc())
           return Response({
               'error': 'Error procesando la imagen',
               'uploaded': 0
           }, status=500)

   @action(detail=True, methods=['patch'])
   def update_layout(self, request, pk=None):
       publication = self.get_object()
       layout = request.data.get('layout')
       
       if not layout:
           return Response({
               'error': 'No se proporcionó el layout'
           }, status=400)

       # Validar estructura del layout
       try:
           for row in layout:
               if not isinstance(row.get('cells', []), list):
                   raise ValueError('Cada fila debe tener una lista de celdas')
               for cell in row['cells']:
                   if 'type' not in cell or 'content' not in cell:
                       raise ValueError('Cada celda debe tener tipo y contenido')
                   if cell['type'] not in ['text', 'image', 'video']:
                       raise ValueError('Tipo de celda no válido')
       except (TypeError, ValueError) as e:
           return Response({
               'error': str(e)
           }, status=400)

       publication.layout = layout
       publication.save()
       
       serializer = self.get_serializer(publication)
       return Response(serializer.data)

class BiographyViewSet(viewsets.ModelViewSet):
   queryset = Biography.objects.all()
   serializer_class = BiographySerializer
   parser_classes = (MultiPartParser, FormParser, JSONParser)

   def get_queryset(self):
       queryset = Biography.objects.all()
       if not self.request.user.is_staff:
           queryset = queryset.filter(is_active=True)
       return queryset

   @action(detail=False, methods=['patch'])
   def reorder(self, request):
       for item in request.data:
           Biography.objects.filter(id=item['id']).update(order=item['order'])
       return Response({'status': 'ok'})


class ImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            image_file = request.FILES.get('image')
            if not image_file:
                return Response({
                    'error': 'No se proporcionó ninguna imagen'
                }, status=400)

            try:
                # Validar imagen
                ImageHandler.validate_image(image_file)
                
                # Procesar imagen
                handler = ImageHandler(
                    image_file,
                    directory=settings.UPLOAD_PATHS['temp_uploads']  # Usar el path desde settings
                )
                relative_path = handler.process_image()
                
                # Construir URL completa con el dominio
                image_url = request.build_absolute_uri(settings.MEDIA_URL + relative_path)
                
                return Response({
                    'url': image_url
                })
                
            except ValueError as e:
                return Response({
                    'error': str(e)
                }, status=400)
            
        except Exception as e:
            import traceback
            print("Error al procesar imagen:", str(e))
            print(traceback.format_exc())
            return Response({
                'error': 'Error procesando la imagen'
            }, status=500)