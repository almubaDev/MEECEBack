# content/admin.py
from django.contrib import admin
from .models import Section, Publication, Biography

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order']

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'status', 'publish_date', 'is_featured']
    list_filter = ['status', 'section', 'is_featured']
    search_fields = ['title']
    date_hierarchy = 'publish_date'
    ordering = ['-publish_date']
    raw_id_fields = ['created_by']

@admin.register(Biography)
class BiographyAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'email', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'position', 'email']
    ordering = ['order', 'name']