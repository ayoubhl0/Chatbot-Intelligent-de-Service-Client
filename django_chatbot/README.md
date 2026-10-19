# Chatbot Intelligent de Service Client

##  Présentation du projet

Ce projet de fin d'études (PFE) consiste à développer une application web de service client intégrant un chatbot permettant aux utilisateurs d'interagir avec le système de manière simple et intuitive.

L'application est développée avec **Django**, un framework web Python, et intègre un système de reconnaissance des gestes (*Gesture Recognition*) pour enrichir l'interaction avec l'utilisateur.

##  Objectifs

- Faciliter la communication entre les clients et le service client.
- Automatiser les réponses aux questions fréquentes.
- Améliorer l'expérience utilisateur grâce à une interface interactive.
- Intégrer la reconnaissance des gestes dans l'interaction avec l'application.

##  Fonctionnalités

-  Interface de discussion avec le chatbot.
-  Réponses automatisées aux questions des utilisateurs.
- Reconnaissance des gestes de la main.
- Application web développée avec Django.
-  Interface utilisateur intuitive.

*Les fonctionnalités présentées sont à adapter selon l'implémentation réelle du projet.*

## Technologies utilisées

- **Python** — Langage de programmation.
- **Django** — Framework de développement web.
- **HTML5 / CSS3 / JavaScript** — Technologies frontend.
- **Gesture Recognition** — Reconnaissance des gestes.
- **Git & GitHub** — Gestion de versions et hébergement du code.

## ⚙️ Installation et lancement
 1) Activer l'environnement virtuel
   .\tf_env\Scripts\activate 
2) Installer les dépendances

pip install -r requirements.txt

3) Appliquer les migrations

python manage.py migrate

4) Lancer le serveur Django

python manage.py runserver

Ouvrir ensuite l'adresse suivante dans le navigateur :

http://127.0.0.1:8000/

Remarque : ces commandes supposent que le projet contient manage.py et requirements.txt. Adapter les étapes selon la configuration réelle.