# Bot Dossard avec Flask (triche Render)

Ce bot vérifie les dossards sur Atleta et envoie un mail quand un dossard est dispo.

### ⚙️ Déploiement Render (gratuit) :

1. Crée un repo GitHub avec ces fichiers.
2. Va sur https://render.com > New > Web Service.
3. Configure :
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `python main.py`
4. Ajoute deux variables d'environnement :
   - `EMAIL_ADDRESS` = ton Gmail
   - `EMAIL_PASSWORD` = mot de passe d'application Gmail

### ✅ Bonus : un mini serveur Flask est lancé en fond pour "tromper" Render.

Tu peux visiter `https://<ton-service>.onrender.com` pour vérifier que le bot tourne.
