# Bot de Surveillance de Dossards (Version légère)

Ce bot surveille la page Atleta et t'envoie un email dès qu'un dossard est disponible.

## Utilisation sur Render

1. Crée un repo GitHub avec ces fichiers.
2. Va sur https://render.com > "New" > "Web Service" ou "Background Worker"
3. Configure :
   - Build Command : `pip install -r requirements.txt`
   - Start Command : `python main.py`
4. Dans "Environment", ajoute :
   - `EMAIL_ADDRESS` : ton Gmail
   - `EMAIL_PASSWORD` : mot de passe d’application

Le bot tourne en boucle et vérifie toutes les 60 secondes.

**Avantage :** pas besoin de navigateur (Chrome, Selenium, etc.)
