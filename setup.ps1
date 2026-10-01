# ============================================
# SCRIPT DE GÉNÉRATION - BEAC-INCIDENT (CORRIGÉ)
# ============================================

Write-Host "Creation de la structure Beac-incident..." -ForegroundColor Cyan

# 1. DOSSIERS
$dossiers = @(
    "backend",
    "backend\beac_incidents",
    "backend\incidents",
    "backend\incidents\ml",
    "backend\incidents\ml\models",
    "backend\incidents\ml\data",
    "backend\users",
    "backend\notifications",
    "frontend-web",
    "frontend-web\src",
    "frontend-web\src\components",
    "frontend-web\src\pages",
    "frontend-web\src\services",
    "mobile-app",
    "mobile-app\lib",
    "mobile-app\lib\screens",
    "mobile-app\lib\services",
    "mobile-app\lib\models",
    "docs",
    "rapport",
    "soutenance"
)

foreach ($d in $dossiers) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
}
Write-Host "Dossiers crees" -ForegroundColor Green

# 2. FICHIERS
$files = @{}

$files["README.md"] = "# Beac-incident`n`nPlateforme Web et Mobile intelligente de gestion des incidents informatiques.`nCas : BEAC d'Abéché"

$files["backend\requirements.txt"] = @"
Django==4.2.0
djangorestframework==3.14.0
djangorestframework-simplejwt==5.2.2
django-cors-headers==4.0.0
scikit-learn==1.2.2
pandas==2.0.1
numpy==1.24.3
pillow==9.5.0
djoser==2.2.0
"@

$files["backend\manage.py"] = @"
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beac_incidents.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
"@

$files["backend\beac_incidents\__init__.py"] = ""

$files["backend\beac_incidents\settings.py"] = @"
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-beac-incident-2026'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'djoser',
    'incidents',
    'users',
    'notifications',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'beac_incidents.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'beac_incidents.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Ndjamena'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.Utilisateur'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

CORS_ALLOW_ALL_ORIGINS = True
"@

$files["backend\beac_incidents\urls.py"] = @"
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('incidents.urls')),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"@

$files["backend\beac_incidents\wsgi.py"] = @"
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beac_incidents.settings')
application = get_wsgi_application()
"@

$files["backend\beac_incidents\asgi.py"] = @"
import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beac_incidents.settings')
application = get_asgi_application()
"@

$files["backend\users\__init__.py"] = ""

$files["backend\users\models.py"] = @"
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
"@

$files["backend\users\admin.py"] = @"
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'service', 'is_active')
    list_filter = ('role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Infos supp', {'fields': ('role', 'telephone', 'service')}),
    )
"@

$files["backend\users\apps.py"] = @"
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
"@

$files["backend\incidents\__init__.py"] = ""

$files["backend\incidents\models.py"] = @"
from django.db import models
from django.conf import settings

class Incident(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
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

    titre = models.CharField(max_length=200)
    description = models.TextField()
    categorie = models.CharField(max_length=50, choices=CATEGORIE_CHOICES, default='Non_classifie')
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='moyenne')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_resolution = models.DateTimeField(null=True, blank=True)

    createur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='incidents_crees')
    technicien_assigne = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents_assignes')
    classification_ia = models.BooleanField(default=False)

    def __str__(self):
        return self.titre
"@

$files["backend\incidents\apps.py"] = @"
from django.apps import AppConfig

class IncidentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'incidents'
"@

$files["backend\incidents\admin.py"] = @"
from django.contrib import admin
from .models import Incident

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'priorite', 'statut', 'date_creation')
    list_filter = ('categorie', 'priorite', 'statut')
    search_fields = ('titre', 'description')
"@

$files["backend\incidents\serializers.py"] = @"
from rest_framework import serializers
from .models import Incident
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class IncidentSerializer(serializers.ModelSerializer):
    createur = UserSerializer(read_only=True)
    technicien_assigne = UserSerializer(read_only=True)

    class Meta:
        model = Incident
        fields = '__all__'
        read_only_fields = ['createur', 'date_creation']
"@

$files["backend\incidents\views.py"] = @"
from rest_framework import viewsets, permissions
from .models import Incident
from .serializers import IncidentSerializer
from .ml.classifier import IncidentClassifier

classifier = IncidentClassifier()

class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all().order_by('-date_creation')
    serializer_class = IncidentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        description = self.request.data.get('description', '')
        try:
            categorie = classifier.predict(description)
        except Exception:
            categorie = 'Non_classifie'
        serializer.save(
            createur=self.request.user,
            categorie=categorie,
            classification_ia=True
        )
"@

$files["backend\incidents\urls.py"] = @"
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IncidentViewSet

router = DefaultRouter()
router.register(r'incidents', IncidentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
"@

$files["backend\incidents\ml\__init__.py"] = ""

$files["backend\incidents\ml\classifier.py"] = @"
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
import os

class IncidentClassifier:
    def __init__(self, model_path='models/classifier.pkl'):
        self.model_path = model_path
        self.model = None
        self.load_or_train()

    def load_or_train(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        else:
            self.train()

    def train(self):
        data = [
            {'description': 'le wifi ne fonctionne plus', 'categorie': 'Reseau'},
            {'description': 'impossible de se connecter au serveur', 'categorie': 'Reseau'},
            {'description': 'le reseau local est lent', 'categorie': 'Reseau'},
            {'description': 'le VPN ne se connecte plus', 'categorie': 'Reseau'},
            {'description': 'l application bancaire plante', 'categorie': 'Application'},
            {'description': 'erreur lors d un virement', 'categorie': 'Application'},
            {'description': 'l application mobile ne s ouvre pas', 'categorie': 'Application'},
            {'description': 'bug sur l app de gestion', 'categorie': 'Application'},
            {'description': 'tentative de connexion suspecte', 'categorie': 'Securite'},
            {'description': 'compte bloque apres plusieurs tentatives', 'categorie': 'Securite'},
            {'description': 'alerte de securite sur le firewall', 'categorie': 'Securite'},
            {'description': 'tentative d intrusion detectee', 'categorie': 'Securite'},
            {'description': 'je ne recois plus mes emails', 'categorie': 'Email'},
            {'description': 'emails non recus depuis hier', 'categorie': 'Email'},
            {'description': 'le serveur mail refuse les connexions', 'categorie': 'Email'},
            {'description': 'impossible d envoyer un mail', 'categorie': 'Email'},
            {'description': 'la telephonie ip ne fonctionne plus', 'categorie': 'Telephonie'},
            {'description': 'les appels sont coupes', 'categorie': 'Telephonie'},
            {'description': 'probleme de son sur les appels', 'categorie': 'Telephonie'},
            {'description': 'telephone IP en panne', 'categorie': 'Telephonie'},
        ]
        df = pd.DataFrame(data)
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
            ('clf', LinearSVC(C=1.0, max_iter=1000))
        ])
        self.model.fit(df['description'], df['categorie'])
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)

    def predict(self, description):
        if not self.model:
            self.load_or_train()
        return self.model.predict([description])[0]
"@

$files["backend\notifications\__init__.py"] = ""

$files["backend\notifications\apps.py"] = @"
from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
"@

$files["backend\notifications\models.py"] = @"
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
"@

$files["docs\cahier_des_charges.md"] = "# Cahier des charges - Beac-incident"

# 3. ECRITURE
foreach ($path in $files.Keys) {
    $content = $files[$path]
    $dir = Split-Path $path -Parent
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    Set-Content -Path $path -Value $content -Encoding UTF8
}

Write-Host "Tous les fichiers ont ete crees avec succes !" -ForegroundColor Green
Write-Host ""
Write-Host "Structure :" -ForegroundColor Yellow
Get-ChildItem -Recurse -File | Select-Object FullName