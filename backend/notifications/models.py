from django.db import models
from django.conf import settings

class Notification(models.Model):
    destinataire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    incident = models.ForeignKey('incidents.Incident', on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    est_lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
