from pathlib import Path
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

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
    'channels',  
    'fcm_django', 
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
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'beac_incident_db',
        'USER': 'beac_user',
        'PASSWORD': 'Beac2026!',
        'HOST': 'localhost',
        'PORT': '5432',
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

# ============================================
# REST FRAMEWORK
# ============================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ),
}

CORS_ALLOW_ALL_ORIGINS = True

# ============================================
# CONFIGURATION EMAIL GMAIL
# ============================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'chidimalimi@gmail.com'
EMAIL_HOST_PASSWORD = 'bvrtthhbpcmmcwzu'
DEFAULT_FROM_EMAIL = 'BEAC INCIDENT <chidimalimi@gmail.com>'

# ============================================
# GOOGLE OAUTH
# ============================================
GOOGLE_CLIENT_ID = '171130408532-3a95526835n4qff8rcrt2tdu968nta09.apps.googleusercontent.com'

# ============================================
# CONFIGURATION SUPABASE
# ============================================
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_BUCKET = os.getenv('SUPABASE_BUCKET', 'incidents')

# Nettoyer l'URL Supabase (enlever /rest/v1/ s'il existe)
if SUPABASE_URL:
    SUPABASE_URL = SUPABASE_URL.rstrip('/').replace('/rest/v1', '')

# ============================================
# CONFIGURATION FICHIERS
# ============================================
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),   # 7 jours
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),  # 30 jours
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ============================================
# CONFIGURATION DJANGO CHANNELS (WebSockets)
# ============================================
ASGI_APPLICATION = 'beac_incidents.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Pour la production (avec Redis) :
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [('127.0.0.1', 6379)],
#         },
#     },
# }

# ============================================
# CONFIGURATION DJANGO CHANNELS (WebSockets)
# ============================================
ASGI_APPLICATION = 'beac_incidents.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# ============================================
# CONFIGURATION FIREBASE CLOUD MESSAGING (FCM)
# ============================================
import firebase_admin
from firebase_admin import credentials

# Chemin vers le fichier de credentials Firebase
FIREBASE_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'firebase-credentials.json')

# Initialiser Firebase Admin SDK
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialisé avec succès")
    except Exception as e:
        print(f"❌ Erreur initialisation Firebase : {str(e)}")

# Configuration fcm-django
FCM_DJANGO_SETTINGS = {
    "DEFAULT_FIREBASE_APP": None,
    "ONE_DEVICE_PER_USER": False,
    "DELETE_INACTIVE_DEVICES": False,
    "UPDATE_ON_DUPLICATE_REG_ID": True,
}