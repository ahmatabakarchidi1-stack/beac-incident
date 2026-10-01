import uuid
from django.conf import settings
from supabase import create_client


def get_supabase_client():
    """Retourne un client Supabase configuré"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def uploader_photo(fichier, utilisateur_id):
    """
    Upload une photo vers Supabase Storage
    
    Args:
        fichier: Le fichier à uploader (InMemoryUploadedFile)
        utilisateur_id: L'ID de l'utilisateur qui upload
    
    Returns:
        dict: {
            'url': URL publique de la photo,
            'nom': Nom du fichier dans Supabase
        }
    """
    try:
        supabase = get_supabase_client()
        
        # Générer un nom unique
        extension = fichier.name.split('.')[-1].lower()
        nom_fichier = f"incidents/{utilisateur_id}/{uuid.uuid4().hex}.{extension}"
        
        # Lire le contenu
        contenu = fichier.read()
        
        # Uploader
        supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
            path=nom_fichier,
            file=contenu,
            file_options={
                "content-type": fichier.content_type,
                "upsert": "true"
            }
        )
        
        # Récupérer l'URL publique
        url = supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(nom_fichier)
        
        print(f"\n{'='*60}")
        print(f"✅ PHOTO UPLOADÉE")
        print(f"   Nom : {nom_fichier}")
        print(f"   URL : {url}")
        print(f"{'='*60}\n")
        
        return {
            'url': url,
            'nom': nom_fichier
        }
        
    except Exception as e:
        print(f"\n❌ ERREUR UPLOAD : {str(e)}\n")
        raise Exception(f"Erreur lors de l'upload : {str(e)}")


def supprimer_photo(nom_fichier):
    """Supprime une photo de Supabase Storage"""
    try:
        supabase = get_supabase_client()
        supabase.storage.from_(settings.SUPABASE_BUCKET).remove([nom_fichier])
        print(f"✅ Photo supprimée : {nom_fichier}")
        return True
    except Exception as e:
        print(f"❌ Erreur suppression : {str(e)}")
        return False