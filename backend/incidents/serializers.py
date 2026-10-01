from rest_framework import serializers
from .models import Incident
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'service']


class IncidentSerializer(serializers.ModelSerializer):
    createur = UserSerializer(read_only=True)
    technicien_assigne = UserSerializer(read_only=True)

    class Meta:
        model = Incident
        exclude = ['photo', 'photo_nom']  # ← Exclure photo et photo_nom
        read_only_fields = [
            'createur',
            'date_creation',
            'date_derniere_modification',
            'classification_ia',
            'confidence_score',
        ]