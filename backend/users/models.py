from django.contrib.auth.models import AbstractUser
from django.db import models

class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('responsable', 'Responsable'),
        ('technicien', 'Technicien'),
        ('utilisateur', 'Utilisateur'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='utilisateur')
    telephone = models.CharField(max_length=20, blank=True)
    service = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.username


class OTPCode(models.Model):
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='otp_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def is_valid(self):
        from django.utils import timezone
        return not self.is_used and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"OTP pour {self.user.username} - {self.code}"
