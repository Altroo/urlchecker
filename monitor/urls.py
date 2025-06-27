from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import URLViewSet, dashboard

router = DefaultRouter()
router.register(r'urls', URLViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', dashboard, name='dashboard'),
]