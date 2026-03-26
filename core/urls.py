from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('results/<int:query_id>/', views.results_view, name='results'),
    path('download-report/<int:query_id>/', views.download_report_view, name='download_report'),
    path('view-report/<int:query_id>/', views.view_report_view, name='view_report'),
    path('api/weather/', views.api_weather_view, name='api_weather'),
    path('api/recommendations/', views.api_crop_recommendation_create_view, name='api_crop_recommendations_create'),
    path('api/recommendations/<int:query_id>/', views.api_crop_recommendation_detail_view, name='api_crop_recommendations_detail'),
    path('api/recommendations/<int:query_id>/report/', views.api_crop_recommendation_report_view, name='api_crop_recommendations_report'),
]
