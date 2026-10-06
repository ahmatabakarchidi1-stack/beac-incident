from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Incident
from .serializers import IncidentSerializer
from .ml.classifier import IncidentClassifier
from .services.supabase_storage import uploader_photo, supprimer_photo
from .notifications_ws import (
    notifier_nouvel_incident,
    notifier_incident_assigne,
    notifier_incident_resolu,
    notifier_incident_ferme,
    notifier_incident_reouvert,
)
from .services.fcm_service import (
    notifier_tous_les_admins,
    notifier_tous_les_responsables,
    notifier_technicien,
    envoyer_notification_push,
)

classifier = IncidentClassifier()


class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all().order_by('-date_creation')
    serializer_class = IncidentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # ============================================================
    # CRÉATION : seuls Utilisateur et Admin peuvent déclarer
    # ============================================================
    def perform_create(self, serializer):
        user = self.request.user
        
        if user.role not in ['utilisateur', 'admin']:
            raise PermissionDenied(
                "Seuls les utilisateurs et administrateurs peuvent déclarer un incident."
            )
        
        description = self.request.data.get('description', '')
        try:
            categorie = classifier.predict(description)
        except Exception:
            categorie = 'Non_classifie'
        
        # Récupérer la photo si elle existe
        photo_file = self.request.FILES.get('photo')
        photo_url = None
        photo_nom = None
        
        if photo_file:
            try:
                result = uploader_photo(photo_file, user.id)
                photo_url = result['url']
                photo_nom = result['nom']
            except Exception as e:
                print(f"❌ Erreur upload photo : {str(e)}")
        
        incident = serializer.save(
            createur=user,
            categorie=categorie,
            classification_ia=True,
            photo=photo_url,
            photo_nom=photo_nom
        )
        
        # ============================================================
        # NOTIFICATIONS : WebSocket + Push (FCM)
        # ============================================================
        
        # 1. Notification WebSocket (temps réel dans l'app web)
        notifier_nouvel_incident(incident)
        
        # 2. Notification Push (FCM) aux admins et responsables
        try:
            notifier_tous_les_admins(
                "🔔 Nouvel incident",
                f"#{incident.id} - {incident.titre}",
                {"incident_id": str(incident.id), "type": "nouvel_incident"}
            )
            notifier_tous_les_responsables(
                "🔔 Nouvel incident",
                f"#{incident.id} - {incident.titre}",
                {"incident_id": str(incident.id), "type": "nouvel_incident"}
            )
        except Exception as e:
            print(f"❌ Erreur notification FCM : {str(e)}")

    # ============================================================
    # FILTRAGE : chaque rôle voit ce qui le concerne
    # ============================================================
    def get_queryset(self):
        user = self.request.user
        if user.role == 'utilisateur':
            return Incident.objects.filter(createur=user)
        elif user.role == 'technicien':
            return Incident.objects.filter(technicien_assigne=user)
        elif user.role == 'responsable':
            return Incident.objects.all()
        elif user.role == 'admin':
            return Incident.objects.all()
        return Incident.objects.none()

    # ============================================================
    # AFFECTER : Responsable + Admin
    # ============================================================
    @action(detail=True, methods=['post'])
    def assigner(self, request, pk=None):
        if request.user.role not in ['responsable', 'admin']:
            raise PermissionDenied("Seul le responsable peut affecter un incident.")
        
        incident = self.get_object()
        technicien_id = request.data.get('technicien_id')
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            technicien = User.objects.get(id=technicien_id, role='technicien')
            incident.technicien_assigne = technicien
            incident.statut = 'en_cours'
            incident.save()
            
            # Notifications
            notifier_incident_assigne(incident)
            try:
                notifier_technicien(
                    technicien,
                    "🔧 Incident assigné",
                    f"#{incident.id} - {incident.titre}",
                    {"incident_id": str(incident.id), "type": "incident_assigne"}
                )
            except Exception as e:
                print(f"❌ Erreur notification FCM : {str(e)}")
            
            return Response({'status': 'Incident assigné avec succès'})
        except User.DoesNotExist:
            return Response(
                {'error': 'Technicien non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )

    # ============================================================
    # RÉSOUDRE : Technicien assigné + Admin
    # ============================================================
    @action(detail=True, methods=['post'])
    def resoudre(self, request, pk=None):
        incident = self.get_object()
        user = request.user
        
        if user.role == 'technicien' and incident.technicien_assigne != user:
            raise PermissionDenied("Vous n'êtes pas assigné à cet incident.")
        if user.role not in ['technicien', 'admin']:
            raise PermissionDenied("Seul un technicien peut résoudre un incident.")
        
        incident.statut = 'resolu'
        incident.date_resolution = timezone.now()
        incident.resolution_commentaire = request.data.get('resolution_commentaire', '')
        incident.commentaire_interne = request.data.get('commentaire_interne', '')
        incident.save()
        
        # Notifications
        notifier_incident_resolu(incident)
        try:
            envoyer_notification_push(
                incident.createur,
                "✅ Incident résolu",
                f"#{incident.id} - Merci de confirmer la résolution",
                {"incident_id": str(incident.id), "type": "incident_resolu"}
            )
        except Exception as e:
            print(f"❌ Erreur notification FCM : {str(e)}")
        
        return Response({'status': 'Incident marqué comme résolu'})

    # ============================================================
    # CONFIRMER : Utilisateur créateur + Admin
    # ============================================================
    @action(detail=True, methods=['post'])
    def confirmer(self, request, pk=None):
        incident = self.get_object()
        user = request.user
        
        if incident.createur != user and user.role != 'admin':
            raise PermissionDenied("Seul le créateur peut confirmer la résolution.")
        
        incident.confirme_par_utilisateur = True
        incident.statut = 'ferme'
        incident.date_confirmation = timezone.now()
        incident.save()
        
        # Notifications
        notifier_incident_ferme(incident)
        
        return Response({'status': 'Résolution confirmée'})

    # ============================================================
    # RÉOUVRIR : Utilisateur créateur + Admin
    # ============================================================
    @action(detail=True, methods=['post'])
    def reouvrir(self, request, pk=None):
        incident = self.get_object()
        user = request.user
        
        if incident.createur != user and user.role != 'admin':
            raise PermissionDenied("Seul le créateur peut réouvrir l'incident.")
        
        incident.confirme_par_utilisateur = False
        incident.statut = 'reouvert'
        raison = request.data.get('raison', '')
        incident.commentaire_interne += f"\n\n[REOUVERT par {user.username}] {raison}"
        incident.save()
        
        # Notifications
        notifier_incident_reouvert(incident)
        try:
            if incident.technicien_assigne:
                notifier_technicien(
                    incident.technicien_assigne,
                    "⚠️ Incident réouvert",
                    f"#{incident.id} - Retour au technicien",
                    {"incident_id": str(incident.id), "type": "incident_reouvert"}
                )
        except Exception as e:
            print(f"❌ Erreur notification FCM : {str(e)}")
        
        return Response({'status': 'Incident réouvert'})

    # ============================================================
    # SUPPRIMER LA PHOTO
    # ============================================================
    @action(detail=True, methods=['delete'])
    def supprimer_photo(self, request, pk=None):
        incident = self.get_object()
        
        if incident.createur != request.user and request.user.role != 'admin':
            raise PermissionDenied("Vous ne pouvez pas supprimer cette photo.")
        
        if incident.photo_nom:
            supprimer_photo(incident.photo_nom)
            incident.photo = None
            incident.photo_nom = None
            incident.save()
            return Response({'status': 'Photo supprimée'})
        return Response({'error': 'Aucune photo à supprimer'}, status=status.HTTP_400_BAD_REQUEST)