from django.db import models
from django.conf import settings


class Incident(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
        ('reouvert', 'Réouvert'),
        ('ferme', 'Fermé'),
    ]
    PRIORITE_CHOICES = [
        ('basse', 'Basse'),
        ('moyenne', 'Moyenne'),
        ('haute', 'Haute'),
        ('critique', 'Critique'),
    ]
    CATEGORIE_CHOICES = [
        ('Reseau', 'Réseau'),
        ('Application', 'Application Bancaire'),
        ('Securite', 'Sécurité'),
        ('Email', 'Messagerie'),
        ('Telephonie', 'Téléphonie IP'),
        ('Materiel', 'Matériel'),
        ('Non_classifie', 'Non classifié'),
    ]

    # ===== INFORMATIONS DE BASE =====
    titre = models.CharField(max_length=200)
    description = models.TextField()
    categorie = models.CharField(
        max_length=50,
        choices=CATEGORIE_CHOICES,
        default='Non_classifie'
    )
    priorite = models.CharField(
        max_length=20,
        choices=PRIORITE_CHOICES,
        default='moyenne'
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente'
    )

    # ===== DATES =====
    date_creation = models.DateTimeField(auto_now_add=True)
    date_derniere_modification = models.DateTimeField(auto_now=True)
    date_resolution = models.DateTimeField(null=True, blank=True)
    date_confirmation = models.DateTimeField(null=True, blank=True)

    # ===== RELATIONS =====
    createur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='incidents_crees'
    )
    technicien_assigne = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidents_assignes'
    )

    # ===== INTELLIGENCE ARTIFICIELLE =====
    classification_ia = models.BooleanField(default=False)
    confidence_score = models.FloatField(null=True, blank=True)

    # ===== PHOTO DE L'INCIDENT (Supabase Storage) =====
    photo = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL publique de la photo stockée sur Supabase"
    )
    photo_nom = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Nom du fichier dans Supabase Storage"
    )

    # ===== WORKFLOW DE VALIDATION =====
    resolution_commentaire = models.TextField(
        blank=True,
        help_text="Résumé simple de la résolution (visible par l'utilisateur)"
    )
    commentaire_interne = models.TextField(
        blank=True,
        help_text="Commentaire technique interne (visible par le technicien et le responsable)"
    )
    confirme_par_utilisateur = models.BooleanField(
        default=False,
        help_text="L'utilisateur a confirmé la résolution"
    )

    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Incident'
        verbose_name_plural = 'Incidents'

    def __str__(self):
        return f"#{self.id} - {self.titre} [{self.get_statut_display()}]"