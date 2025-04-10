import os
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

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

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def check_dossards():
    driver.get("https://atleta.cc/e/nhIV3rcY9oXV/resale")
    time.sleep(3)

    try:
        refresh_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Refresh')]")
        refresh_button.click()
        time.sleep(3)

        ticket_texts = driver.find_elements(By.CLASS_NAME, "ticket-card")
        for ticket in ticket_texts:
            if "Disponible" in ticket.text or "Available" in ticket.text:
                print("DOSSARD DISPONIBLE !")
                envoyer_mail()
                return True
        print("Pas de dossards.")
        return False
    except Exception as e:
        print("Erreur :", e)
        return False

while True:
    dispo = check_dossards()
    if dispo:
        break
    time.sleep(60)
