# Guide de déploiement de l'application de prédiction des ventes

Ce document explique comment déployer l'application de prédiction des ventes dans différents environnements de production.

## Table des matières

1. [Prérequis](#prérequis)
2. [Déploiement local](#déploiement-local)
3. [Déploiement avec Docker](#déploiement-avec-docker)
4. [Déploiement sur un serveur VPS](#déploiement-sur-un-serveur-vps)
5. [Déploiement sur Heroku](#déploiement-sur-heroku)
6. [Configuration de la base de données](#configuration-de-la-base-de-données)
7. [Sécurité](#sécurité)
8. [Maintenance](#maintenance)

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Virtualenv (recommandé)
- Git (pour le déploiement via contrôle de version)

## Déploiement local

### Installation

1. Clonez le dépôt ou copiez les fichiers de l'application dans un dossier local
2. Créez un environnement virtuel et activez-le :

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installez les dépendances :

```bash
pip install -r requirements.txt
```

4. Initialisez la base de données :

```bash
python run.py --init-db
```

### Lancement

Pour lancer l'application en mode développement :

```bash
python run.py --debug
```

Pour lancer l'application en mode production :

```bash
python run.py --host 0.0.0.0 --port 8000
```

L'application sera accessible à l'adresse http://localhost:8000

## Déploiement avec Docker

### Création de l'image Docker

1. Créez un fichier `Dockerfile` à la racine du projet avec le contenu suivant :

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data
RUN python -c "from app import app, db; app.app_context().push(); db.create_all()"

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

2. Créez un fichier `.dockerignore` avec le contenu suivant :

```
__pycache__/
*.py[cod]
*$py.class
.env
.venv
env/
venv/
*.db
*.sqlite
*.sqlite3
.git/
.gitignore
```

3. Construisez l'image Docker :

```bash
docker build -t sales-prediction-app .
```

4. Exécutez le conteneur :

```bash
docker run -d -p 5000:5000 --name sales-app sales-prediction-app
```

L'application sera accessible à l'adresse http://localhost:5000

## Déploiement sur un serveur VPS

### Configuration du serveur

1. Connectez-vous à votre serveur VPS via SSH
2. Installez les dépendances système :

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx
```

3. Clonez le dépôt ou copiez les fichiers de l'application
4. Configurez un environnement virtuel et installez les dépendances

### Configuration de Gunicorn et Nginx

1. Installez Gunicorn :

```bash
pip install gunicorn
```

2. Créez un fichier de service systemd pour Gunicorn :

```bash
sudo nano /etc/systemd/system/sales-app.service
```

Avec le contenu suivant :

```ini
[Unit]
Description=Gunicorn instance to serve sales prediction application
After=network.target

[Service]
User=your_username
Group=www-data
WorkingDirectory=/path/to/your/app
Environment="PATH=/path/to/your/app/venv/bin"
ExecStart=/path/to/your/app/venv/bin/gunicorn --workers 3 --bind unix:sales-app.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

3. Activez et démarrez le service :

```bash
sudo systemctl start sales-app
sudo systemctl enable sales-app
```

4. Configurez Nginx :

```bash
sudo nano /etc/nginx/sites-available/sales-app
```

Avec le contenu suivant :

```nginx
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/your/app/sales-app.sock;
    }

    location /static {
        alias /path/to/your/app/static;
    }
}
```

5. Activez la configuration et redémarrez Nginx :

```bash
sudo ln -s /etc/nginx/sites-available/sales-app /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

## Déploiement sur Heroku

1. Installez le CLI Heroku et connectez-vous
2. Créez un fichier `Procfile` à la racine du projet :

```
web: gunicorn app:app
```

3. Créez un fichier `runtime.txt` :

```
python-3.10.0
```

4. Déployez l'application :

```bash
heroku create sales-prediction-app
git push heroku main
heroku run python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## Configuration de la base de données

Par défaut, l'application utilise SQLite. Pour une utilisation en production, il est recommandé d'utiliser PostgreSQL ou MySQL.

Pour configurer PostgreSQL :

1. Installez les dépendances :

```bash
pip install psycopg2-binary
```

2. Modifiez la configuration de la base de données dans `app.py` :

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/dbname'
```

## Sécurité

- Utilisez HTTPS en production
- Changez la clé secrète (`SECRET_KEY`) en production
- Utilisez des variables d'environnement pour les informations sensibles
- Mettez régulièrement à jour les dépendances

## Maintenance

### Sauvegardes

Pour sauvegarder la base de données SQLite :

```bash
cp instance/users.db backup/users_$(date +%Y%m%d).db
```

### Mises à jour

1. Arrêtez l'application
2. Sauvegardez la base de données
3. Mettez à jour le code source
4. Mettez à jour les dépendances
5. Redémarrez l'application

```bash
pip install -r requirements.txt --upgrade
sudo systemctl restart sales-app
```