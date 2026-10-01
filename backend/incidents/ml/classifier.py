import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
import os

class IncidentClassifier:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), 'models', 'classifier.pkl')
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
            # ===== RESEAU =====
            {'description': 'le wifi ne fonctionne plus dans tout le batiment', 'categorie': 'Reseau'},
            {'description': 'impossible de se connecter au serveur', 'categorie': 'Reseau'},
            {'description': 'le reseau local est tres lent', 'categorie': 'Reseau'},
            {'description': 'les utilisateurs n ont plus acces a internet', 'categorie': 'Reseau'},
            {'description': 'le VPN ne se connecte plus', 'categorie': 'Reseau'},
            {'description': 'probleme de connexion au reseau', 'categorie': 'Reseau'},
            {'description': 'la connexion internet est instable', 'categorie': 'Reseau'},
            {'description': 'le reseau est en panne depuis ce matin', 'categorie': 'Reseau'},
            {'description': 'impossible d acceder au serveur de fichiers', 'categorie': 'Reseau'},
            {'description': 'le wifi est tres faible', 'categorie': 'Reseau'},
            {'description': 'la connexion reseau est coupee', 'categorie': 'Reseau'},
            {'description': 'je n arrive pas a me connecter au reseau', 'categorie': 'Reseau'},
            {'description': 'le switch reseau ne repond plus', 'categorie': 'Reseau'},
            {'description': 'probleme de routeur reseau', 'categorie': 'Reseau'},
            {'description': 'la bande passante est saturee', 'categorie': 'Reseau'},
            {'description': 'impossible d acceder a l intranet', 'categorie': 'Reseau'},
            {'description': 'le reseau est tres lent aujourd hui', 'categorie': 'Reseau'},
            {'description': 'probleme de cable reseau', 'categorie': 'Reseau'},
            {'description': 'le point d acces wifi est hors service', 'categorie': 'Reseau'},
            {'description': 'connexion reseau instable', 'categorie': 'Reseau'},

            # ===== APPLICATION =====
            {'description': 'l application bancaire plante au lancement', 'categorie': 'Application'},
            {'description': 'erreur lors d un virement sur l app mobile', 'categorie': 'Application'},
            {'description': 'le logiciel de caisse ne repond plus', 'categorie': 'Application'},
            {'description': 'impossible d ouvrir l application de gestion', 'categorie': 'Application'},
            {'description': 'l application core banking est inaccessible', 'categorie': 'Application'},
            {'description': 'bug sur l application de virement', 'categorie': 'Application'},
            {'description': 'l app mobile se ferme toute seule', 'categorie': 'Application'},
            {'description': 'erreur de connexion a l application bancaire', 'categorie': 'Application'},
            {'description': 'le module de virement ne fonctionne pas', 'categorie': 'Application'},
            {'description': 'impossible de consulter mon compte sur l app', 'categorie': 'Application'},
            {'description': 'l application de gestion des comptes plante', 'categorie': 'Application'},
            {'description': 'erreur lors de la validation d un virement', 'categorie': 'Application'},
            {'description': 'l application mobile ne s ouvre pas', 'categorie': 'Application'},
            {'description': 'bug sur l application de la banque', 'categorie': 'Application'},
            {'description': 'impossible de realiser un virement', 'categorie': 'Application'},
            {'description': 'l application ne repond plus', 'categorie': 'Application'},
            {'description': 'erreur 500 sur l application bancaire', 'categorie': 'Application'},
            {'description': 'le logiciel metier est en panne', 'categorie': 'Application'},
            {'description': 'impossible de lancer l application', 'categorie': 'Application'},
            {'description': 'l application affiche une erreur', 'categorie': 'Application'},

            # ===== SECURITE =====
            {'description': 'tentative de connexion suspecte depuis l etranger', 'categorie': 'Securite'},
            {'description': 'compte utilisateur bloque apres plusieurs tentatives', 'categorie': 'Securite'},
            {'description': 'activite inhabituelle detectee sur le serveur', 'categorie': 'Securite'},
            {'description': 'alerte de securite sur le firewall', 'categorie': 'Securite'},
            {'description': 'tentative de connexion suspecte', 'categorie': 'Securite'},
            {'description': 'compte bloque pour raison de securite', 'categorie': 'Securite'},
            {'description': 'alerte antivirus sur le poste de travail', 'categorie': 'Securite'},
            {'description': 'tentative d intrusion detectee', 'categorie': 'Securite'},
            {'description': 'compte compromis suspecte', 'categorie': 'Securite'},
            {'description': 'firewall bloque des connexions suspectes', 'categorie': 'Securite'},
            {'description': 'tentative de piratage detectee', 'categorie': 'Securite'},
            {'description': 'compte administrateur bloque', 'categorie': 'Securite'},
            {'description': 'alerte de securite sur le serveur', 'categorie': 'Securite'},
            {'description': 'activite suspecte sur le compte bancaire', 'categorie': 'Securite'},
            {'description': 'tentative de connexion depuis un pays etranger', 'categorie': 'Securite'},
            {'description': 'virus detecte sur le poste', 'categorie': 'Securite'},
            {'description': 'acces non autorise detecte', 'categorie': 'Securite'},
            {'description': 'mot de passe compromis', 'categorie': 'Securite'},
            {'description': 'intrusion dans le systeme', 'categorie': 'Securite'},
            {'description': 'alerte de phishing recue', 'categorie': 'Securite'},

            # ===== EMAIL =====
            {'description': 'je ne recois plus mes emails depuis ce matin', 'categorie': 'Email'},
            {'description': 'emails non recus depuis hier', 'categorie': 'Email'},
            {'description': 'le serveur mail refuse les connexions', 'categorie': 'Email'},
            {'description': 'impossible d envoyer des emails avec pieces jointes', 'categorie': 'Email'},
            {'description': 'email non recus', 'categorie': 'Email'},
            {'description': 'probleme de serveur mail', 'categorie': 'Email'},
            {'description': 'je ne peux pas envoyer de mail', 'categorie': 'Email'},
            {'description': 'les emails arrivent en retard', 'categorie': 'Email'},
            {'description': 'la messagerie est inaccessible', 'categorie': 'Email'},
            {'description': 'impossible de recevoir des mails', 'categorie': 'Email'},
            {'description': 'les emails ne s envoient pas', 'categorie': 'Email'},
            {'description': 'probleme de reception de mail', 'categorie': 'Email'},
            {'description': 'le serveur mail est en panne', 'categorie': 'Email'},
            {'description': 'impossible d acceder a ma boite mail', 'categorie': 'Email'},
            {'description': 'les mails importants ne sont pas recus', 'categorie': 'Email'},

            # ===== TELEPHONIE =====
            {'description': 'la telephonie ip ne fonctionne plus', 'categorie': 'Telephonie'},
            {'description': 'les appels sont coupes en plein milieu', 'categorie': 'Telephonie'},
            {'description': 'probleme de son sur les appels IP', 'categorie': 'Telephonie'},
            {'description': 'impossible de passer des appels via l IP', 'categorie': 'Telephonie'},
            {'description': 'telephonie ip en panne', 'categorie': 'Telephonie'},
            {'description': 'les appels IP ne fonctionnent pas', 'categorie': 'Telephonie'},
            {'description': 'le telephone IP ne s allume pas', 'categorie': 'Telephonie'},
            {'description': 'probleme de qualite audio sur les appels', 'categorie': 'Telephonie'},
            {'description': 'impossible de joindre le standard via IP', 'categorie': 'Telephonie'},
            {'description': 'les appels sont renvoyes vers la messagerie', 'categorie': 'Telephonie'},
            {'description': 'la telephonie IP est indisponible', 'categorie': 'Telephonie'},
            {'description': 'les appels ne sonnent pas', 'categorie': 'Telephonie'},
            {'description': 'probleme de reseau sur la telephonie IP', 'categorie': 'Telephonie'},
            {'description': 'impossible de passer des appels exterieurs', 'categorie': 'Telephonie'},
            {'description': 'la qualite des appels est mauvaise', 'categorie': 'Telephonie'},
        ]
        df = pd.DataFrame(data)
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
            ('clf', LinearSVC(C=1.0, max_iter=1000))
        ])
        self.model.fit(df['description'], df['categorie'])
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print("Modele IA entraine et sauvegarde avec", len(data), "exemples")

    def predict(self, description):
        if not self.model:
            self.load_or_train()
        return self.model.predict([description])[0]
    