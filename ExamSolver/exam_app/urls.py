from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # 1. Page d'accueil (Landing Page) - Accessible à tous
    path('', views.index_view, name='index'),
    
    # 2. Interface de résolution d'examen (Dashboard)
    path('dashboard/', views.upload_view, name='upload'),
    
    # 3. Gestion des examens
    path('exam/<int:pk>/', views.exam_detail_view, name='exam_detail'),
    path('exam/<int:pk>/delete/', views.delete_exam_view, name='delete_exam'),
    
    # 4. Authentification
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'), # Redirige vers l'accueil après déconnexion
]