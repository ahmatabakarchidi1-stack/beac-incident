import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beac_incidents.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from incidents.services.supabase_storage import uploader_photo

# Créer un fichier de test
contenu = b"Contenu de test pour Supabase"
fichier = SimpleUploadedFile(
    name="test_photo.jpg",
    content=contenu,
    content_type="image/jpeg"
)

# Uploader
try:
    result = uploader_photo(fichier, utilisateur_id=1)
    print("\n🎉 TEST RÉUSSI !")
    print(f"URL : {result['url']}")
    print(f"Nom : {result['nom']}")
except Exception as e:
    print(f"\n❌ ERREUR : {str(e)}")