from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import SectionViewSet, PublicationViewSet, BiographyViewSet, ImageUploadView

router = DefaultRouter()
router.register(r'sections', SectionViewSet)
router.register(r'publications', PublicationViewSet, basename='publication')
router.register(r'biographies', BiographyViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('upload-image/', ImageUploadView.as_view(), name='upload-image'),
]

# Asegurar que los archivos media sean servidos en desarrollo
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
