from rest_framework import serializers
from .models import Section, Publication, Biography

class SectionSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'title', 'slug', 'is_active', 'order', 'created_at']
        read_only_fields = ['created_at', 'slug']

class PublicationSerializer(serializers.ModelSerializer):
    section = SectionSerializer(read_only=True)
    section_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'status', 'layout', 
            'section', 'section_id', 'publish_date',
            'featured_image', 'is_featured', 'created_at'
        ]
        read_only_fields = ['created_at']
        
        
class BiographySerializer(serializers.ModelSerializer):
    class Meta:
        model = Biography
        fields = [
            'id', 'name', 'position', 'biography',
            'photo', 'email', 'linkedin', 
            'is_active', 'order', 'created_at'
        ]
        read_only_fields = ['created_at']
        
        
class PublicPublicationSerializer(serializers.ModelSerializer):
    section_slug = serializers.CharField(source='section.slug', read_only=True)
    section_title = serializers.CharField(source='section.title', read_only=True)

    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'layout', 'section_slug', 
            'section_title', 'publish_date', 'featured_image'
        ]

# Nuevo serializador para biografías públicas
class PublicBiographySerializer(serializers.ModelSerializer):
    class Meta:
        model = Biography
        fields = [
            'id', 'name', 'position', 'biography',
            'photo', 'email', 'linkedin', 'order'
        ]