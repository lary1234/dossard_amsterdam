import os
import time
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

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
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 3000)
    driver.get("https://atleta.cc/e/nhIV3rcY9oXV/resale")
    time.sleep(5)

    # 🍪 Clic "Accepter" s'il existe
    try:
        bouton = driver.find_element(By.XPATH, "//button[.//strong[contains(text(), 'Accepter')]]")
        bouton.click()
        print("🍪 Bouton 'Accepter' cliqué", flush=True)
        time.sleep(2)
    except Exception as e:
        print("⚠️ Bouton 'Accepter' introuvable :", e, flush=True)

    # 📸 Capture d’écran
    screenshot_path = "page_vue_par_le_bot.png"
    driver.save_screenshot(screenshot_path)

    # 🔍 Recherche du message d'absence
    try:
        message = driver.find_element(By.XPATH, "//*[contains(text(), \"Il n'y a actuellement aucun ticket à vendre\")]")
        print("⛔ Message d'absence trouvé → aucun ticket", flush=True)
        driver.quit()
        return False, screenshot_path
    except:
        print("🎯 Message d'absence NON trouvé → POSSIBLE ticket !", flush=True)
        driver.quit()
        return True, screenshot_path

if __name__ == "__main__":
    dispo, screenshot = check_disponibilite()
    envoyer_mail("🚀 Bot lancé", "Le bot est en ligne et surveille les dossards.", screenshot)

    alert_sent = False

    while True:
        dispo, screenshot = check_disponibilite()
        if dispo and not alert_sent:
            envoyer_mail("🎟️ Dossard dispo", "Un ticket est peut-être dispo sur https://atleta.cc/e/nhIV3rcY9oXV/resale", screenshot)
            alert_sent = True
        elif not dispo and alert_sent:
            alert_sent = False
        time.sleep(60)
