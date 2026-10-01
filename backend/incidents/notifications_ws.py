from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def envoyer_notification(groupe, type_message, incident_data, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        groupe,
        {
            'type': type_message,
            'incident': incident_data,
            'message': message,
        }
    )
    print(f"📢 Notification envoyée à {groupe} : {message}")


def notifier_nouvel_incident(incident):
    incident_data = {
        'id': incident.id,
        'titre': incident.titre,
        'categorie': incident.categorie,
        'priorite': incident.priorite,
        'statut': incident.statut,
        'createur': incident.createur.username if incident.createur else 'Inconnu',
    }
    message = f"Nouvel incident #{incident.id} : {incident.titre}"
    envoyer_notification('incidents_global', 'nouvel_incident', incident_data, message)


def notifier_incident_assigne(incident):
    incident_data = {
        'id': incident.id,
        'titre': incident.titre,
        'categorie': incident.categorie,
        'priorite': incident.priorite,
        'statut': incident.statut,
        'technicien': incident.technicien_assigne.username if incident.technicien_assigne else None,
    }
    message = f"Incident #{incident.id} vous a été assigné"
    envoyer_notification('incidents_global', 'incident_assigne', incident_data, message)


def notifier_incident_resolu(incident):
    incident_data = {
        'id': incident.id,
        'titre': incident.titre,
        'statut': incident.statut,
    }
    message = f"Incident #{incident.id} résolu. Merci de confirmer."
    envoyer_notification('incidents_global', 'incident_resolu', incident_data, message)


def notifier_incident_ferme(incident):
    incident_data = {
        'id': incident.id,
        'titre': incident.titre,
        'statut': incident.statut,
    }
    message = f"Incident #{incident.id} fermé avec succès"
    envoyer_notification('incidents_global', 'incident_ferme', incident_data, message)


def notifier_incident_reouvert(incident):
    incident_data = {
        'id': incident.id,
        'titre': incident.titre,
        'statut': incident.statut,
    }
    message = f"Incident #{incident.id} réouvert - Retour au technicien"
    envoyer_notification('incidents_global', 'incident_reouvert', incident_data, message)