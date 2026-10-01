from django.urls import path
from . import views

urlpatterns = [
    path('connexion/etape1/', views.connexion_etape1, name='connexion_etape1'),
    path('connexion/etape2/', views.connexion_etape2, name='connexion_etape2'),
    path('connexion/google/', views.connexion_google, name='connexion_google'),
    path('creer/', views.creer_utilisateur, name='creer_utilisateur'),
    path('liste/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('supprimer/<int:user_id>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
]