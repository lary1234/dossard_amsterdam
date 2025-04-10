import os
import time
import smtplib
import threading
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration des identifiants email via les variables d'environnement
EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASSWORD  = os.environ['EMAIL_PASSWORD']

# Chemin du fichier de capture (il sera mis à jour toutes les 2 sec)
SCREENSHOT_PATH = "page_vue_par_le_bot.png"

# Verrou pour synchroniser l'accès au driver Selenium
driver_lock = threading.Lock()

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

def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Exécute sans interface graphique
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    # Possibilité d'ajouter d'autres options ou préférences si nécessaire
    
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 3000)
    driver.get("https://atleta.cc/e/nhIV3rcY9oXV/resale")
    time.sleep(5)  # Attendre que la page se charge
    
    # Attente explicite pour cliquer sur le bouton "Accepter"
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//strong[contains(text(),'Accepter')]]"))
        )
        accept_button.click()
        print("🍪 Bouton 'Accepter' cliqué avec succès", flush=True)
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.XPATH, "//button[.//strong[contains(text(),'Accepter')]]"))
        )
        print("🍪 Bouton 'Accepter' a disparu, pop-up cookies enlevé.", flush=True)
    except Exception as e:
        print("⚠️ Bouton 'Accepter' introuvable ou non cliquable :", e, flush=True)
    
    return driver

def screenshot_updater(driver):
    """ Met à jour la capture d'écran toutes les 2 secondes. """
    while True:
        with driver_lock:
            driver.save_screenshot(SCREENSHOT_PATH)
        # Cette capture se fait toutes les 2 secondes
        time.sleep(2)

def check_ticket_availability(driver):
    """ Vérifie la présence d'au moins un ticket visible via la classe 'ticket-card'. """
    with driver_lock:
        tickets = driver.find_elements(By.CLASS_NAME, "ticket-card")
    if tickets and len(tickets) > 0:
        print(f"🎯 {len(tickets)} ticket(s) détecté(s) !", flush=True)
        return True
    else:
        print("⛔ Aucun ticket détecté", flush=True)
        return False

def main():
    global alert_sent
    driver = setup_driver()
    
    # Démarrage du thread pour actualiser la capture d'écran toutes les 2 secondes
    updater_thread = threading.Thread(target=screenshot_updater, args=(driver,), daemon=True)
    updater_thread.start()
    
    # Envoi d'un mail de démarrage avec la capture d'écran actuelle
    envoyer_mail("🚀 Bot lancé", "Le bot est actif et surveille la page.", SCREENSHOT_PATH)
    
    alert_sent = False
    
    # Boucle principale qui vérifie la disponibilité toutes les 60 secondes
    while True:
        available = check_ticket_availability(driver)
        if available and not alert_sent:
            envoyer_mail("🎟️ Dossard dispo", 
                         "Un ticket semble être disponible sur https://atleta.cc/e/nhIV3rcY9oXV/resale", 
                         SCREENSHOT_PATH)
            alert_sent = True
        elif not available and alert_sent:
            alert_sent = False
        time.sleep(60)

if __name__ == "__main__":
    main()
