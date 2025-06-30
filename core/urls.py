from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HomeView

app_name = 'core'

# Router para APIs
router = DefaultRouter()

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('api/', include(router.urls)),
]