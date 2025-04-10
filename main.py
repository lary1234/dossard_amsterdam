import os
import time
import threading
import smtplib
from email.message import EmailMessage
from flask import Flask, send_file
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#################################
# CONFIGURATION
#################################
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', 'ton.email@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'ton_mdp_application')

# URL à surveiller
CHECK_URL = "https://atleta.cc/e/nhIV3rcY9oXV/resale"

# Chemin du screenshot
SCREENSHOT_PATH = "page_vue_par_le_bot.png"

# Intervalle de capture (30 secondes)
CAPTURE_INTERVAL = 30

# Intervalle pour envoi d'email si un ticket est détecté (ici 60 secondes maximum)
MAIL_INTERVAL = 60

#################################
# FONCTIONS UTILITAIRES
#################################
def envoyer_mail(subject, content, attachment_path=None):
    print(f"📤 Envoi de mail : {subject}", flush=True)
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
        print(f"❌ Erreur mail : {e}", flush=True)

def check_disponibilite():
    # Configuration de Selenium en mode headless
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    # On peut éventuellement ajouter ici des préférences pour les cookies
    # Cependant, le site semble utiliser un composant custom, nous tenterons toujours le clic.
    
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 3000)
    driver.get(CHECK_URL)
    
    # Attente de chargement de la page
    time.sleep(5)

    # ⏱️ Essai de clic explicite sur le bouton "Accepter"
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
        print(f"⚠️ Bouton 'Accepter' introuvable ou non cliquable : {e}", flush=True)
    
    # Attendre quelques secondes supplémentaires pour que la page se stabilise (et éventuellement pour que le challenge Cloudflare se termine)
    time.sleep(3)
    
    # Capture d'écran pour vérification
    driver.save_screenshot(SCREENSHOT_PATH)
    
    # Ici on peut ajouter d'autres vérifications visuelles
    # Par exemple, on cherche des éléments ayant la classe "ticket-card"
    ticket_present = False
    try:
        tickets = driver.find_elements(By.CLASS_NAME, "ticket-card")
        if tickets and len(tickets) > 0:
            ticket_present = True
            print(f"🎯 {len(tickets)} ticket(s) détecté(s) visuellement !", flush=True)
        else:
            print("⛔ Aucun ticket détecté (aucune carte trouvée)", flush=True)
    except Exception as e:
        print(f"⚠️ Erreur lors de la recherche des tickets : {e}", flush=True)
    
    driver.quit()
    return ticket_present

#################################
# FLASK APP POUR VISUALISER LE SCREENSHOT
#################################
app = Flask(__name__)

@app.route("/screenshot")
def screenshot():
    """Retourne la dernière capture d'écran."""
    if os.path.exists(SCREENSHOT_PATH):
        return send_file(SCREENSHOT_PATH, mimetype="image/png")
    else:
        return "Aucune capture disponible.", 404

#################################
# THREAD DE CAPTURE
#################################
def loop_capture():
    last_ticket_found = False
    last_mail_sent = 0
    while True:
        ticket_found = check_disponibilite()
        if ticket_found and not last_ticket_found:
            now = time.time()
            if (now - last_mail_sent) > MAIL_INTERVAL:
                envoyer_mail("🎟️ Dossard dispo", f"Un ticket est peut-être dispo sur {CHECK_URL}", SCREENSHOT_PATH)
                last_mail_sent = now
            last_ticket_found = True
        elif not ticket_found and last_ticket_found:
            last_ticket_found = False
        time.sleep(CAPTURE_INTERVAL)

#################################
# LANCEMENT DE L'APP
#################################
if __name__ == "__main__":
    # Lancer le thread de capture
    t = threading.Thread(target=loop_capture, daemon=True)
    t.start()

    # Lancer le serveur Flask sur le port 5000 pour avoir un URL public (si déployé sur Railway)
    app.run(host="0.0.0.0", port=5000)
