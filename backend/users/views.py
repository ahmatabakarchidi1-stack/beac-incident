import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Utilisateur, OTPCode


def generer_code_otp():
    """Génère un code OTP à 6 chiffres"""
    return str(random.randint(100000, 999999))


@api_view(['POST'])
@permission_classes([AllowAny])
def connexion_etape1(request):
    """
    Étape 1 : Vérifier EMAIL/MOT DE PASSE et envoyer OTP par email
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {'erreur': 'Email et mot de passe requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Chercher l'utilisateur par email
    try:
        user = Utilisateur.objects.get(email=email)
    except Utilisateur.DoesNotExist:
        return Response(
            {'erreur': 'Email ou mot de passe incorrect'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Vérifier le mot de passe
    if not user.check_password(password):
        return Response(
            {'erreur': 'Email ou mot de passe incorrect'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Supprimer les anciens OTP non utilisés
    OTPCode.objects.filter(user=user, is_used=False).update(is_used=True)
    
    # Générer un nouveau code OTP
    code = generer_code_otp()
    expires_at = timezone.now() + timedelta(minutes=5)
    
    OTPCode.objects.create(
        user=user,
        code=code,
        expires_at=expires_at
    )
    
    # ============================================
    # ENVOYER L'EMAIL AVEC LE CODE OTP
    # ============================================
    sujet = '🔐 Code de vérification - BEAC INCIDENT'
    
    message_texte = f"""
Bonjour {user.username},

Votre code de vérification pour BEAC INCIDENT est :

    {code}

Ce code expire dans 5 minutes.

Si vous n'avez pas demandé ce code, ignorez cet email.

Cordialement,
L'équipe BEAC INCIDENT
    """
    
    message_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
            <h1 style="color: white; margin: 0;">🔐 BEAC INCIDENT</h1>
            <p style="color: white; margin: 10px 0 0 0;">Vérification en 2 étapes</p>
        </div>
        
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0;">
            <p style="font-size: 16px; color: #333;">Bonjour <strong>{user.username}</strong>,</p>
            
            <p style="font-size: 16px; color: #333;">Voici votre code de vérification :</p>
            
            <div style="background: white; border: 2px dashed #667eea; border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0;">
                <h2 style="color: #667eea; font-size: 42px; letter-spacing: 10px; margin: 0; font-family: monospace;">
                    {code}
                </h2>
            </div>
            
            <p style="font-size: 14px; color: #666;">⏰ Ce code expire dans <strong>5 minutes</strong>.</p>
            
            <p style="font-size: 14px; color: #999; margin-top: 30px;">
                Si vous n'avez pas demandé ce code, veuillez ignorer cet email.
            </p>
            
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
            
            <p style="font-size: 12px; color: #999; text-align: center;">
                Cordialement,<br>
                L'équipe BEAC INCIDENT
            </p>
        </div>
    </div>
    """
    
    try:
        send_mail(
            subject=sujet,
            message=message_texte,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=message_html,
            fail_silently=False,
        )
        print(f"\n{'='*60}")
        print(f"✅ EMAIL ENVOYÉ À {email}")
        print(f"🔐 CODE OTP : {code}")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"\n❌ ERREUR ENVOI EMAIL : {str(e)}\n")
        return Response(
            {'erreur': f'Erreur lors de l\'envoi de l\'email : {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response({
        'message': 'Code OTP envoyé à votre adresse email',
        'email': email,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def connexion_etape2(request):
    """
    Étape 2 : Vérifier l'OTP et retourner le token JWT
    """
    email = request.data.get('email')
    code = request.data.get('code')
    
    try:
        user = Utilisateur.objects.get(email=email)
    except Utilisateur.DoesNotExist:
        return Response(
            {'erreur': 'Utilisateur non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Chercher le dernier OTP valide
    otp = OTPCode.objects.filter(
        user=user,
        code=code,
        is_used=False
    ).order_by('-created_at').first()
    
    if not otp or not otp.is_valid():
        return Response(
            {'erreur': 'Code OTP invalide ou expiré'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Marquer l'OTP comme utilisé
    otp.is_used = True
    otp.save()
    
    # Générer les tokens JWT
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'utilisateur': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'service': user.service,
        }
    })


from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def creer_utilisateur(request):
    """Créer un nouvel utilisateur (Admin uniquement)"""
    
    # Vérifier que l'utilisateur connecté est admin
    if request.user.role != 'admin':
        return Response(
            {'erreur': 'Seul l\'administrateur peut créer des comptes'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role', 'utilisateur')
    service = request.data.get('service', '')
    telephone = request.data.get('telephone', '')
    
    # Vérifier que les champs requis sont présents
    if not username or not email or not password:
        return Response(
            {'erreur': 'Nom d\'utilisateur, email et mot de passe sont requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérifier si le username existe déjà
    if Utilisateur.objects.filter(username=username).exists():
        return Response(
            {'erreur': 'Ce nom d\'utilisateur existe déjà'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérifier si l'email existe déjà
    if Utilisateur.objects.filter(email=email).exists():
        return Response(
            {'erreur': 'Cet email est déjà utilisé'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Créer l'utilisateur
    try:
        user = Utilisateur.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            role=role,
            service=service,
            telephone=telephone,
        )
        
        print(f"\n{'='*60}")
        print(f"✅ NOUVEL UTILISATEUR CRÉÉ")
        print(f"   Username : {username}")
        print(f"   Email    : {email}")
        print(f"   Rôle     : {role}")
        print(f"   Service  : {service}")
        print(f"{'='*60}\n")
        
        return Response({
            'message': 'Utilisateur créé avec succès',
            'utilisateur': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'service': user.service,
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'erreur': f'Erreur lors de la création : {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_utilisateurs(request):
    """Liste tous les utilisateurs (Admin uniquement)"""
    
    if request.user.role != 'admin':
        return Response(
            {'erreur': 'Accès réservé à l\'administrateur'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    utilisateurs = Utilisateur.objects.all().order_by('username')
    
    return Response([
        {
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'role': u.role,
            'service': u.service,
            'telephone': u.telephone,
            'is_active': u.is_active,
        }
        for u in utilisateurs
    ])


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def supprimer_utilisateur(request, user_id):
    """Supprimer un utilisateur (Admin uniquement)"""
    
    if request.user.role != 'admin':
        return Response(
            {'erreur': 'Seul l\'administrateur peut supprimer des comptes'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        user = Utilisateur.objects.get(id=user_id)
        
        # Empêcher la suppression de son propre compte
        if user.id == request.user.id:
            return Response(
                {'erreur': 'Vous ne pouvez pas supprimer votre propre compte'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        username = user.username
        user.delete()
        
        return Response({
            'message': f'Utilisateur {username} supprimé avec succès'
        })
        
    except Utilisateur.DoesNotExist:
        return Response(
            {'erreur': 'Utilisateur non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings as django_settings


@api_view(['POST'])
@permission_classes([AllowAny])
def connexion_google(request):
    """Connexion via Google OAuth"""
    token = request.data.get('credential')
    
    if not token:
        return Response(
            {'erreur': 'Token Google manquant'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Vérifier le token Google
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            django_settings.GOOGLE_CLIENT_ID
        )
        
        email = idinfo['email']
        nom = idinfo.get('name', email.split('@')[0])
        
        print(f"\n{'='*60}")
        print(f"🔐 CONNEXION GOOGLE")
        print(f"   Email : {email}")
        print(f"   Nom   : {nom}")
        print(f"{'='*60}\n")
        
        # Chercher l'utilisateur par email
        try:
            user = Utilisateur.objects.get(email=email)
        except Utilisateur.DoesNotExist:
            return Response(
                {'erreur': f'Votre email ({email}) n\'est pas autorisé. Contactez l\'administrateur.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'utilisateur': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'service': user.service,
            }
        })
    
    except Exception as e:
        print(f"\n❌ ERREUR GOOGLE : {str(e)}\n")
        return Response(
            {'erreur': f'Token Google invalide : {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )    