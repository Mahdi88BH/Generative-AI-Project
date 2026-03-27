from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.upload_view, name='upload'),
    path('exam/<int:pk>/', views.exam_detail_view, name='exam_detail'),
    path('exam/<int:pk>/delete/', views.delete_exam_view, name='delete_exam'),
   
   ]