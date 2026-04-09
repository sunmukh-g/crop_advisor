from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_page, name='chat_page'),
    path('api/', views.chatbot_view, name='chatbot_api'), 
]