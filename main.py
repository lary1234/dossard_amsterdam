import os
import time
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']

def envoyer_mail(subject, content):
    print("📤 Envoi de mail :", subject, flush=True)
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg.set_content(content)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("✅ Mail envoyé", flush=True)
    except Exception as e:
        print("❌ Erreur mail :", e, flush=True)

def check_disponibilite():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)
    driver.get("https://atleta.cc/e/nhIV3rcY9oXV/resale")

    time.sleep(5)  # attendre le chargement JS

    try:
        # Nouvelle stratégie : chercher un bloc ticket réel visible uniquement en cas de dispo
        ticket_elements = driver.find_elements(By.CLASS_NAME, "ticket-card")
        if len(ticket_elements) > 0:
            print(f"🎯 {len(ticket_elements)} ticket(s) détecté(s) !", flush=True)
            driver.quit()
            return True
        else:
            print("⛔ Aucun ticket détecté (aucune carte trouvée)", flush=True)
            driver.quit()
            return False

    except Exception as e:
        print("⚠️ Erreur pendant la vérification :", e, flush=True)
        driver.quit()
        return False

if __name__ == "__main__":
    envoyer_mail("🚀 Bot Selenium lancé", "Le bot Selenium est en ligne et surveille les dossards.")

    alert_sent = False

    while True:
        if check_disponibilite() and not alert_sent:
            envoyer_mail("🎟️ Dossard dispo", "Un ticket est peut-être dispo sur https://atleta.cc/e/nhIV3rcY9oXV/resale")
            alert_sent = True
        elif not check_disponibilite() and alert_sent:
            alert_sent = False
        time.sleep(60)
