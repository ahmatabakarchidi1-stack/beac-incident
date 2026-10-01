import json
from channels.generic.websocket import AsyncWebsocketConsumer


class IncidentConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket pour les notifications en temps réel des incidents.
    Version démo : accepte tous les utilisateurs (même anonymes).
    """

    async def connect(self):
        print("🔌 Tentative de connexion WebSocket...")
        self.user = self.scope['user']
        print(f"👤 Utilisateur : {self.user}")

        # ⚠️ MODE DÉMO : accepter tous les utilisateurs
        # En production, on utiliserait JWT pour authentifier
        self.groupe_global = "incidents_global"

        # Rejoindre le groupe global
        await self.channel_layer.group_add(self.groupe_global, self.channel_name)

        await self.accept()
        print("✅ WebSocket accepté (mode démo)")

        # Envoyer un message de bienvenue
        await self.send(text_data=json.dumps({
            'type': 'connection_etablie',
            'message': 'Connecté au service de notifications en temps réel',
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'groupe_global'):
            await self.channel_layer.group_discard(self.groupe_global, self.channel_name)
            print(f"❌ WebSocket déconnecté (code {close_code})")

    async def receive(self, text_data):
        """Recevoir un message du client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'ping')

            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'message': 'Connexion active',
                }))
        except Exception as e:
            print(f"Erreur réception : {e}")

    # ============================================================
    # HANDLERS POUR LES ÉVÉNEMENTS DU GROUPE
    # ============================================================

    async def nouvel_incident(self, event):
        """Notification : nouvel incident créé"""
        await self.send(text_data=json.dumps({
            'type': 'nouvel_incident',
            'incident': event['incident'],
            'message': event['message'],
        }))

    async def incident_assigne(self, event):
        """Notification : incident assigné à un technicien"""
        await self.send(text_data=json.dumps({
            'type': 'incident_assigne',
            'incident': event['incident'],
            'message': event['message'],
        }))

    async def incident_resolu(self, event):
        """Notification : incident résolu"""
        await self.send(text_data=json.dumps({
            'type': 'incident_resolu',
            'incident': event['incident'],
            'message': event['message'],
        }))

    async def incident_ferme(self, event):
        """Notification : incident fermé"""
        await self.send(text_data=json.dumps({
            'type': 'incident_ferme',
            'incident': event['incident'],
            'message': event['message'],
        }))

    async def incident_reouvert(self, event):
        """Notification : incident réouvert"""
        await self.send(text_data=json.dumps({
            'type': 'incident_reouvert',
            'incident': event['incident'],
            'message': event['message'],
        }))