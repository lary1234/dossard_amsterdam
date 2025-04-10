import os
import time
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']

def envoyer_mail(subject, content, attachment_path=None):
    print("📤 Envoi de mail :", subject, flush=True)
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg.set_content(content)

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            msg.add_attachment(file_data, maintype='image', subtype='png', filename=os.path.basename(attachment_path))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("✅ Mail envoyé", flush=True)
    except Exception as e:
        print("❌ Erreur mail :", e, flush=True)

def check_disponibilite():
    options = Options()
    options.add_argument("--headless")  # mode headless
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    # On peut ajouter d'éventuelles prefs ici, mais on se concentre sur le clic.
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 3000)
    driver.get("https://atleta.cc/e/nhIV3rcY9oXV/resale")
    
    # Attendre un peu le chargement de la page
    time.sleep(5)

    # Utiliser un attente explicite pour cliquer sur le bouton "Accepter"
    try:
        # On attend que le bouton devienne cliquable
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//strong[contains(text(),'Accepter')]]"))
        )
        accept_button.click()
        print("🍪 Bouton 'Accepter' cliqué avec succès", flush=True)
        # Attendre que le bouton disparaisse après le clic
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.XPATH, "//button[.//strong[contains(text(),'Accepter')]]"))
        )
        print("🍪 Bouton 'Accepter' a disparu, pop-up cookies enlevé.", flush=True)
    except Exception as e:
        print("⚠️ Bouton 'Accepter' introuvable ou non cliquable :", e, flush=True)

    # Attendre un peu pour être sûr que la page se mette à jour
    time.sleep(2)

    # Capture d'écran après interaction
    screenshot_path = "page_vue_par_le_bot.png"
    driver.save_screenshot(screenshot_path)

    # Vérifier la présence d'une carte ticket (ici on se base sur la classe "ticket-card")
    try:
        tickets = driver.find_elements(By.CLASS_NAME, "ticket-card")
        if tickets and len(tickets) > 0:
            print(f"🎯 {len(tickets)} ticket(s) détecté(s) visuellement !", flush=True)
            driver.quit()
            return True, screenshot_path
        else:
            print("⛔ Aucun ticket détecté (aucune carte trouvée)", flush=True)
            driver.quit()
            return False, screenshot_path
    except Exception as e:
        print("⚠️ Erreur lors de la vérification des tickets :", e, flush=True)
        driver.quit()
        return False, screenshot_path

if __name__ == "__main__":
    dispo, screenshot = check_disponibilite()
    envoyer_mail("🚀 Bot Selenium lancé", "Le bot Selenium est en ligne et surveille les dossards.", screenshot)

    alert_sent = False

    while True:
        dispo, screenshot = check_disponibilite()
        if dispo and not alert_sent:
            envoyer_mail("🎟️ Dossard dispo", "Un ticket est peut-être dispo sur https://atleta.cc/e/nhIV3rcY9oXV/resale", screenshot)
            alert_sent = True
        elif not dispo and alert_sent:
            alert_sent = False
        time.sleep(60)
