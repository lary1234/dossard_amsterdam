import os
import smtplib
import time
import threading
import requests
from email.message import EmailMessage
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_server():
    print("🚀 Serveur Flask lancé sur le port 10000.", flush=True)
    app.run(host='0.0.0.0', port=10000)

EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']

def envoyer_mail():
    print("📤 Tentative d'envoi de l'e-mail...", flush=True)
    msg = EmailMessage()
    msg['Subject'] = "🎟️ Dossard disponible !"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg.set_content("Un ou plusieurs dossards sont probablement disponibles : https://atleta.cc/e/nhIV3rcY9oXV/resale")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("✅ Mail envoyé avec succès !", flush=True)
    except Exception as e:
        print("❌ Erreur d'envoi de mail :", e, flush=True)

def check_dossards():
    print("🔍 Début de vérification des dossards...", flush=True)
    try:
        headers = { "User-Agent": "Mozilla/5.0" }
        response = requests.get("https://atleta.cc/e/nhIV3rcY9oXV/resale", headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().lower()

        if "there are currently no tickets for sale" in page_text or "0 tickets available" in page_text:
            print("⛔ Aucun ticket disponible pour le moment.", flush=True)
            return False
        else:
            print("🎯 POSSIBLE TICKET DISPONIBLE – vérifier manuellement !", flush=True)
            return True
    except Exception as e:
        print("⚠️ Erreur pendant la vérification :", e, flush=True)
        return False

if __name__ == '__main__':
    threading.Thread(target=run_server).start()

    print("✅ Bot démarré avec protection anti-spam.", flush=True)

    alert_sent = False  # Anti-spam activé

    while True:
        ticket_present = check_dossards()

        if ticket_present and not alert_sent:
            envoyer_mail()
            alert_sent = True
        elif not ticket_present and alert_sent:
            print("🔁 Ticket disparu — alerte réactivée.", flush=True)
            alert_sent = False

        time.sleep(60)
