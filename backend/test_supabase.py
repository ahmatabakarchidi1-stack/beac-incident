import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beac_incidents.settings')
django.setup()

from django.conf import settings
from supabase import create_client

print("=" * 50)
print("TEST DE CONNEXION SUPABASE")
print("=" * 50)

print(f"URL : {settings.SUPABASE_URL}")
print(f"Bucket : {settings.SUPABASE_BUCKET}")
print(f"KEY (début) : {settings.SUPABASE_KEY[:30] if settings.SUPABASE_KEY else 'VIDE'}")
print()

try:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    print("✅ Client Supabase créé")
    
    buckets = supabase.storage.list_buckets()
    print(f"✅ Buckets trouvés : {[b.name for b in buckets]}")
    
except Exception as e:
    print(f"❌ ERREUR : {str(e)}")

print("=" * 50)