# content/urls_public.py

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views_public import PublicPublicationViewSet, PublicPublicationDetailView

router = DefaultRouter()
router.register(r'publications', PublicPublicationViewSet, basename='public-publication')

urlpatterns = [
    path('publication/<int:id>/', PublicPublicationDetailView.as_view(), name='public-publication-detail'),
] + router.urls