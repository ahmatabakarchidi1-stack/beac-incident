import os
import uuid
from django.conf import settings
from supabase import create_client


class SupabaseStorage:
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self.bucket = settings.SUPABASE_BUCKET
        self.client = create_client(self.url, self.key)

    def upload_file(self, file, folder='incidents'):
        """
        Upload un fichier vers Supabase Storage
        Retourne l'URL publique du fichier
        """
        try:
            # Générer un nom unique
            extension = os.path.splitext(file.name)[1].lower()
            filename = f"{folder}/{uuid.uuid4()}{extension}"

            # Lire le fichier
            file_content = file.read()

            # Détecter le content-type (compatible avec tous les types de fichiers)
            content_type = getattr(file, 'content_type', None)
            if not content_type:
                # Deviner le content-type selon l'extension
                content_type = self._get_content_type(extension)

            # Upload vers Supabase
            self.client.storage.from_(self.bucket).upload(
                path=filename,
                file=file_content,
                file_options={"content-type": content_type}
            )

            # Récupérer l'URL publique
            public_url = self.client.storage.from_(self.bucket).get_public_url(filename)

            print(f"✅ Fichier uploadé : {filename}")
            print(f"🔗 URL publique : {public_url}")

            return {
                'url': public_url,
                'path': filename,
            }

        except Exception as e:
            print(f"❌ Erreur upload Supabase : {str(e)}")
            raise e

    def delete_file(self, file_path):
        """Supprime un fichier de Supabase Storage"""
        try:
            self.client.storage.from_(self.bucket).remove([file_path])
            print(f"✅ Fichier supprimé : {file_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur suppression : {str(e)}")
            return False

    def _get_content_type(self, extension):
        """Devine le content-type selon l'extension"""
        types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        }
        return types.get(extension, 'application/octet-stream')


# Instance globale
supabase_storage = SupabaseStorage()