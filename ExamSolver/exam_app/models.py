from django.db import models
from django.contrib.auth.models import User

class Exam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exams")
    image = models.ImageField(upload_to='exams/enonces/') # L'épreuve
    copie_file = models.FileField(upload_to='exams/copies/', null=True, blank=True) # La copie (PDF/Image)
    mode = models.CharField(max_length=20, default='solve') # 'solve' ou 'grade'
    result_text = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')
    uploaded_at = models.DateTimeField(auto_now_add=True)