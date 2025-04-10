import os
import time
import smtplib
from email.message import EmailMessage
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
CHECK_URL = "https://atleta.cc/e/nhIV3rcY9oXV/resale"

# Chemins pour les captures d'écran de debug
SCREENSHOT_STEP1 = "step1_before_cookies.png"
SCREENSHOT_STEP2 = "step2_after_cookies.png"
SCREENSHOT_FINAL = "page_vue_par_le_bot.png"

# Temps d'attente (en secondes)
INITIAL_WAIT = 10       # pour le chargement initial de la page
COOKIE_WAIT = 10        # attente max pour que le bouton soit cliquable
POST_CLICK_WAIT = 5     # temps d'attente après le clic pour que la page se stabilise
SCROLL_WAIT = 3         # temps pour que le défilement se fasse
CAPTURE_INTERVAL = 30   # intervalle entre les vérifications
MAIL_INTERVAL = 60      # intervalle d'envoi d'email maximal

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
        with open(attachment_path, "rb") as f:
            file_data = f.read()
            msg.add_attachment(file_data, maintype="image", subtype="png", filename=os.path.basename(attachment_path))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("✅ Mail envoyé", flush=True)
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi du mail : {e}", flush=True)

def click_cookie_button(driver):
    """
    Essaye de cliquer sur un bouton de cookies en testant plusieurs variantes.
    """
    # Liste des XPATH possibles pour le bouton de consentement
    xpath_candidates = [
        "//button[.//strong[contains(translate(text(), 'ACCEPTER', 'accepter'),'accepter')]]",
        "//button[contains(translate(text(), 'ACCEPTER', 'accepter'),'accepter')]",
        "//button[contains(translate(text(), 'ACCEPT', 'accept'),'accept')]",
        "//button[contains(translate(text(), 'OK', 'ok'),'ok')]",
        "//button[contains(translate(text(), \"J'accepte\", \"j'accepte\"),'j\'accepte')]",
        "//button[contains(translate(text(), 'I agree', 'i agree'),'i agree')]"
    ]
    
    for xp in xpath_candidates:
        try:
            # On attend que le bouton soit cliquable
            button = WebDriverWait(driver, COOKIE_WAIT).until(EC.element_to_be_clickable((By.XPATH, xp)))
            button.click()
            print(f"🍪 Bouton cliqué via xpath: {xp}", flush=True)
            # On attend que le bouton ne soit plus visible
            WebDriverWait(driver, COOKIE_WAIT).until(EC.invisibility_of_element_located((By.XPATH, xp)))
            print("🍪 Bouton de cookies disparu.", flush=True)
            return True
        except Exception as e:
            # Si on n'a pas pu cliquer avec ce xpath, on passe au suivant
            print(f"⚠️ Tentative avec xpath {xp} échouée : {e}", flush=True)
    return False

def scroll_page(driver):
    """
    Effectue un scroll de la page jusqu'en bas pour forcer le chargement complet.
    """
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("🔄 Page scrollée vers le bas.", flush=True)
    except Exception as e:
        print(f"⚠️ Erreur lors du scroll : {e}", flush=True)

def check_disponibilite():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 3000)
    driver.get(CHECK_URL)
    
    # Attendre que la page soit complètement chargée
    time.sleep(INITIAL_WAIT)
    
    # Capture d'écran avant interaction
    driver.save_screenshot(SCREENSHOT_STEP1)
    print("📸 Capture STEP 1 (avant cookies) sauvegardée.", flush=True)
    
    # Essayer de cliquer sur le bouton cookies (si présent)
    click_cookie_button(driver)
    
    # Attendre que la page se stabilise après le clic
    time.sleep(POST_CLICK_WAIT)
    
    # Scroll de la page pour charger tout le contenu dynamique
    scroll_page(driver)
    time.sleep(SCROLL_WAIT)
    
    # Capture d'écran finale
    driver.save_screenshot(SCREENSHOT_FINAL)
    print("📸 Capture finale sauvegardée.", flush=True)
    
    # Vérification de la présence d'un bloc ticket via la classe "ticket-card"
    ticket_detected = False
    try:
        tickets = driver.find_elements(By.CLASS_NAME, "ticket-card")
        if tickets and len(tickets) > 0:
            ticket_detected = True
            print(f"🎯 {len(tickets)} ticket(s) détecté(s) visuellement !", flush=True)
        else:
            print("⛔ Aucun ticket détecté (aucune carte trouvée).", flush=True)
    except Exception as e:
        print(f"⚠️ Erreur lors de la recherche des tickets : {e}", flush=True)
    
    driver.quit()
    return ticket_detected, SCREENSHOT_FINAL

#################################
# APPLICATION FLASK (optionnel)
#################################
from flask import Flask, send_file
app = Flask(__name__)

@app.route("/screenshot")
def screenshot():
    if os.path.exists(SCREENSHOT_FINAL):
        return send_file(SCREENSHOT_FINAL, mimetype="image/png")
    else:
        return "Pas de capture disponible.", 404

#################################
# LANCEMENT DE LA SURVEILLANCE
#################################
if __name__ == "__main__":
    # Envoi d'un email de démarrage avec la capture finale
    dispo, screenshot_file = check_disponibilite()
    envoyer_mail("🚀 Bot lancé", "Le bot est en ligne et surveille les dossards.", screenshot_file)
    
    alert_sent = False
    last_mail_time = 0
    
    # Lancement d'un thread pour la surveillance continue (synchronisé dans ce cas)
    while True:
        dispo, screenshot_file = check_disponibilite()
        now = time.time()
        if dispo and not alert_sent and (now - last_mail_time > MAIL_INTERVAL):
            envoyer_mail("🎟️ Dossard dispo", f"Un ticket est peut-être dispo sur {CHECK_URL}", screenshot_file)
            alert_sent = True
            last_mail_time = now
        elif not dispo and alert_sent:
            alert_sent = False
        time.sleep(CAPTURE_INTERVAL)
