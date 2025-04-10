import os
import smtplib
import time
import requests
from email.message import EmailMessage
from bs4 import BeautifulSoup

EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']

def envoyer_mail():
    msg = EmailMessage()
    msg['Subject'] = "Dossard dispo !"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg.set_content("Un ou plusieurs dossards sont disponibles ici : https://atleta.cc/e/nhIV3rcY9oXV/resale")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def check_dossards():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get("https://atleta.cc/e/nhIV3rcY9oXV/resale", headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        tickets = soup.find_all(class_='ticket-card')

        for ticket in tickets:
            if "Disponible" in ticket.text or "Available" in ticket.text:
                print("DOSSARD DISPONIBLE !")
                envoyer_mail()
                return True
        print("Pas de dossards.")
        return False
    except Exception as e:
        print("Erreur de récupération :", e)
        return False

while True:
    if check_dossards():
        break
    time.sleep(60)
