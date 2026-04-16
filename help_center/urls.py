from django.urls import path
from . import views

urlpatterns = [
    path('', views.help_center_view, name='help_center'),
    path('api/schemes/', views.fetch_schemes_api, name='api_schemes'),
    path('api/scheme-detail/', views.scheme_detail_api, name='api_scheme_detail'),
    path('api/chat/', views.scheme_chat_api, name='api_scheme_chat'),
]
