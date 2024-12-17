from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('add-snippet/', views.add_snippet, name='add_snippet'),
    path('ai_view/', views.ai_view, name='ai_view'),
]
