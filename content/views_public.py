# content/views_public.py

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Publication
from .serializers import PublicPublicationSerializer
from django.shortcuts import get_object_or_404

class PublicPublicationViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = PublicPublicationSerializer
    
    def get_queryset(self):
        queryset = Publication.objects.filter(
            status='published'
        ).select_related('section').order_by('-publish_date')
        
        section_slug = self.request.query_params.get('section_slug', None)
        if section_slug:
            queryset = queryset.filter(section__slug=section_slug)
        
        return queryset

class PublicPublicationDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, id):
        publication = get_object_or_404(
            Publication.objects.select_related('section'),
            id=id,
            status='published'
        )
        serializer = PublicPublicationSerializer(
            publication,
            context={'request': request}  # Añadimos el contexto
        )
        return Response(serializer.data)