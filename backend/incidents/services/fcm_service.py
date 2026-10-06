from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
import logging

logger = logging.getLogger(__name__)


def envoyer_notification_push(user, titre, message, data=None):
    """
    Envoie une notification push à un utilisateur spécifique
    """
    try:
        devices = FCMDevice.objects.filter(user=user, active=True)
        
        if not devices.exists():
            logger.info(f"ℹ️ Aucun appareil pour {user.username}")
            return False
        
        fcm_message = Message(
            notification=Notification(title=titre, body=message),
            data=data or {}
        )
        
        response = devices.send_message(fcm_message)
        
        logger.info(f"✅ Notification envoyée à {user.username} : {titre}")
        print(f"✅ Notification envoyée à {user.username} : {titre}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Erreur envoi notification : {str(e)}")
        print(f"❌ Erreur envoi notification : {str(e)}")
        return False


def notifier_tous_les_admins(titre, message, data=None):
    """Notifie tous les administrateurs"""
    from users.models import Utilisateur
    admins = Utilisateur.objects.filter(role='admin', is_active=True)
    for admin in admins:
        envoyer_notification_push(admin, titre, message, data)


def notifier_tous_les_responsables(titre, message, data=None):
    """Notifie tous les responsables"""
    from users.models import Utilisateur
    responsables = Utilisateur.objects.filter(role='responsable', is_active=True)
    for resp in responsables:
        envoyer_notification_push(resp, titre, message, data)


def notifier_technicien(technicien, titre, message, data=None):
    """Notifie un technicien spécifique"""
    envoyer_notification_push(technicien, titre, message, data)