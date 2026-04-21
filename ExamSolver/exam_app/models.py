from django.db import models
from django.contrib.auth.models import User

class Exam(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'En attente'),
        ('Processing', 'En cours...'),
        ('Completed', 'Terminé'),
        ('Error', 'Erreur'),
    ]

    MODE_CHOICES = [
        ('solve', 'Résolution simple'),
        ('grade', 'Correction (Professeur)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exams")
    
    # 1. FICHIERS
    image = models.ImageField(upload_to='exams/enonces/', help_text="L'énoncé de l'examen")
    corrige_file = models.ImageField(upload_to='exams/corriges/', null=True, blank=True, help_text="Le corrigé type")
    copie_file = models.FileField(upload_to='exams/copies/', null=True, blank=True, help_text="La copie étudiant (Image ou PDF)")

    # 2. MÉTADONNÉES
    uploaded_at = models.DateTimeField(auto_now_add=True)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='solve')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # 3. RÉSULTATS
    result_text = models.TextField(null=True, blank=True) # Contiendra soit la Solution, soit le Rapport de correction

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        mode_display = "Correction" if self.mode == "grade" else "Résolution"
        return f"{mode_display} #{self.id} - {self.user.username}"