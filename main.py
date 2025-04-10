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

        # On récupère toutes les balises qui contiennent "tickets available"
        all_elements = soup.find_all(True)  # Toutes les balises HTML

        for element in all_elements:
            text = element.get_text(strip=True).lower()
            if "tickets available" in text:
                print(f"ℹ️ Texte trouvé : \"{text}\"", flush=True)
                try:
                    nb_tickets = int(text.split(" ")[0])
                    print(f"🎫 Tickets détectés : {nb_tickets}", flush=True)
                    if nb_tickets > 0:
                        print("🎯 DOSSARDS DISPONIBLES !", flush=True)
                        return True
                    else:
                        print("⛔ Aucun ticket disponible.", flush=True)
                        return False
                except ValueError:
                    print("❌ Nombre de tickets non détectable dans :", text, flush=True)
                    return False

        print("⚠️ Aucun élément contenant 'tickets available' trouvé dans toute la page HTML.", flush=True)
        return False

    except Exception as e:
        print("⚠️ Erreur pendant la vérification :", e, flush=True)
        return False

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
