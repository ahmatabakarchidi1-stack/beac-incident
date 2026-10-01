from django.contrib import admin
from .models import Incident


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'categorie', 'priorite', 'statut', 'createur', 'technicien_assigne', 'date_creation')
    list_filter = ('categorie', 'priorite', 'statut', 'classification_ia')
    search_fields = ('titre', 'description')
    readonly_fields = ('date_creation', 'date_derniere_modification')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('titre', 'description', 'categorie', 'priorite', 'statut')
        }),
        ('Relations', {
            'fields': ('createur', 'technicien_assigne')
        }),
        ('Intelligence Artificielle', {
            'fields': ('classification_ia', 'confidence_score')
        }),
        ('Résolution', {
            'fields': ('resolution_commentaire', 'commentaire_interne', 'confirme_par_utilisateur', 'date_resolution', 'date_confirmation')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_derniere_modification')
        }),
    )