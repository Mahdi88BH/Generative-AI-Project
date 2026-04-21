from django.db import models
from django.contrib.auth.models import User

class Exam(models.Model):
    # Correction ici : on_delete au lieu de on_get
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exams")
    image = models.ImageField(upload_to='exams/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    result_text = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending') 
    mode = models.CharField(max_length=20, default="solve")
    user_prompt = models.TextField(blank=True, null=True)

    def __str__(self):
        # Utilisation de self.user.username pour un affichage clair dans l'admin
        return f"Exam {self.id} by {self.user.username}"