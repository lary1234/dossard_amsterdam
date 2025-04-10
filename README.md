# Bot de Surveillance de Dossards

Ce bot surveille la page Atleta et t'envoie un email dès qu'un dossard est disponible.

## Étapes d'utilisation :

1. **Crée un repo GitHub** et push ce projet dessus.
2. **Va sur [Render.com](https://render.com)** > New > Web Service ou Background Worker.
3. Configure :
   - Build command: `pip install -r requirements.txt`
   - Start command: `python main.py`
4. Ajoute deux variables d'environnement :
   - `EMAIL_ADDRESS`: ton adresse Gmail
   - `EMAIL_PASSWORD`: mot de passe d'application généré via [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

Le bot vérifiera toutes les 60 secondes si des dossards sont disponibles.
