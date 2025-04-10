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
    print("🚀 Serveur Flask lancé sur le port 10000.")
    app.run(host='0.0.0.0', port=10000)

# ==== CONFIG MAIL ====
EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']

def envoyer_mail():
    print("📤 Tentative d'envoi de l'e-mail...")
    msg = EmailMessage()
    msg['Subject'] = "✅ TEST : Dossard dispo !"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg.set_content("Ceci est un test. Si tu reçois ce mail, le bot fonctionne !")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("✅ Mail envoyé avec succès !")
    except Exception as e:
        print("❌ Erreur d'envoi de mail :", e)

def check_dossards():
    print("🔍 Début de vérification des dossards...")
    try:
        headers = { "User-Agent": "Mozilla/5.0" }
        response = requests.get("https://atleta.cc/e/nhIV3rcY9oXV/resale", headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        tickets = soup.find_all(class_='ticket-card')
        print(f"🔎 {len(tickets)} éléments trouvés avec 'ticket-card'.")

        for ticket in tickets:
            if "Disponible" in ticket.text or "Available" in ticket.text:
                print("🎯 DOSSARD DISPONIBLE !")
                envoyer_mail()
                return True
        print("⛔ Pas de dossards.")
        return False
    except Exception as e:
        print("⚠️ Erreur pendant le check :", e)
        return False

# ==== LANCE LE SERVEUR + LE BOT EN PARALLÈLE ====
if __name__ == '__main__':
    threading.Thread(target=run_server).start()

    # Envoi de mail de test immédiat pour validation
    print("💬 TEST : envoi d'un mail de test dès le lancement.")
    envoyer_mail()

    while True:
        check_dossards()
        time.sleep(60)
