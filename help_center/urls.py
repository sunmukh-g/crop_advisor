from django.urls import path
from . import views

urlpatterns = [
    path('', views.help_center_view, name='help_center'),
    path('api/schemes/', views.fetch_schemes_api, name='api_schemes'),
]
