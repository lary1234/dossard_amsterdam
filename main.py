import os
import smtplib
import time
import threading
import requests
from email.message import EmailMessage
from bs4 import BeautifulSoup
from flask import Flask

# ==== FAUX SERVEUR POUR RENDER ====
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_server():
    print("🚀 Serveur Flask lancé sur le port 10000.", flush=True)
    app.run(host='0.0.0.0', port=10000)

# ==== CONFIGURATION DES EMAILS ====
EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']

def envoyer_mail(subject, content):
    print(f"📤 Tentative d'envoi de l'e-mail avec sujet: {subject}", flush=True)
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg.set_content(content)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("✅ Mail envoyé avec succès !", flush=True)
    except Exception as e:
        print("❌ Erreur d'envoi de mail :", e, flush=True)

# ==== FONCTION DE VÉRIFICATION DES DOSSARDS ====
def check_dossards():
    print("🔍 Vérification des dossards (structure HTML)...", flush=True)
    try:
        headers = { "User-Agent": "Mozilla/5.0" }
        response = requests.get("https://atleta.cc/e/nhIV3rcY9oXV/resale", headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Cherche un bloc spécifique avec un style ou une classe bien connue liée à l'absence
        message_blocks = soup.find_all("div", string=lambda s: s and "no tickets for sale" in s.lower())

        if message_blocks:
            print("⛔ Bloc de message d'absence détecté → aucun ticket.", flush=True)
            return False
        else:
            print("🎯 Bloc de message d'absence NON détecté → POSSIBLE TICKET !", flush=True)
            return True

    except Exception as e:
        print("⚠️ Erreur pendant la vérification :", e, flush=True)
        return False

# ==== SCRIPT PRINCIPAL ====
if __name__ == '__main__':
    # Lancer le serveur Flask dans un thread séparé
    threading.Thread(target=run_server).start()

    # Envoyer un mail de démarrage pour confirmer que le bot est lancé
    envoyer_mail("🚀 Bot démarré", "Le bot de surveillance des tickets a démarré avec succès.")

    # Variable pour l'anti-spam : on n'envoie le mail qu'une fois par période de disponibilité
    alert_sent = False

    while True:
        ticket_available = check_dossards()

        # S'il y a une disponibilité et que l'alerte n'a pas déjà été envoyée, on envoie le mail
        if ticket_available and not alert_sent:
            envoyer_mail("🎟️ Dossard disponible !", "Un ou plusieurs dossards sont possiblement disponibles : https://atleta.cc/e/nhIV3rcY9oXV/resale")
            alert_sent = True

        # Si plus aucun ticket n'est disponible et qu'une alerte a été envoyée, réinitialiser l'anti-spam
        elif not ticket_available and alert_sent:
            print("🔁 Ticket disparu — réinitialisation de l'alerte.", flush=True)
            alert_sent = False

        # Pause de 60 secondes entre chaque vérification
        time.sleep(60)
