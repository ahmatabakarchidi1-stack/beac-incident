import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beac_incidents.settings')
django.setup()

from django.conf import settings
from supabase import create_client
from datetime import datetime

print("=" * 60)
print("TEST UPLOAD SUPABASE")
print("=" * 60)

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Créer un fichier texte de test
contenu = f"Test upload BEAC INCIDENT - {datetime.now()}"
nom_fichier = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

print(f"Bucket : {settings.SUPABASE_BUCKET}")
print(f"Fichier : {nom_fichier}")
print()

# Uploader
try:
    result = supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
        path=nom_fichier,
        file=contenu.encode('utf-8'),
        file_options={"content-type": "text/plain", "upsert": "true"}
    )
    print(f"✅ Fichier uploadé avec succès !")
    
    # Récupérer l'URL publique
    url = supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(nom_fichier)
    print(f"✅ URL publique :")
    print(f"   {url}")
    
    print()
    print("🎉 SUPABASE STORAGE FONCTIONNE !")
    
except Exception as e:
    print(f"❌ ERREUR : {str(e)}")

print("=" * 60)