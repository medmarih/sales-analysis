# 🚀 Application de Prédiction des Ventes

Une application web moderne pour la prédiction des ventes mensuelles utilisant le machine learning.

## ✨ Fonctionnalités

- 🎨 **Interface moderne** avec design glassmorphism et animations
- 📊 **Visualisation interactive** des données avec Plotly
- 🤖 **Modèles de machine learning** (Régression linéaire)
- 📈 **Prédictions de ventes** avec graphiques
- 🔐 **Système d'authentification** sécurisé
- 📁 **Import/Export** de fichiers CSV
- 📱 **Design responsive** pour tous les appareils

## 🛠️ Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de packages Python)

### Installation rapide

1. **Cloner ou télécharger** le projet
2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```
3. **Démarrer l'application** :
   ```bash
   ./start_app.sh
   ```
   ou
   ```bash
   python app.py
   ```

## 🌐 Utilisation

### Accès à l'application
- **URL** : http://localhost:5003 (ou le port affiché)
- **Identifiants par défaut** :
  - Utilisateur : `admin`
  - Mot de passe : `admin123`

### Workflow d'utilisation

1. **📊 Import des données**
   - Allez dans la section "Données"
   - Importez un fichier CSV ou générez des données d'exemple
   - Format CSV requis : `mois,ventes`

2. **🤖 Entraînement du modèle**
   - Allez dans la section "Modèle"
   - Configurez les paramètres d'entraînement
   - Lancez l'entraînement du modèle

3. **📈 Génération de prédictions**
   - Allez dans la section "Prédictions"
   - Spécifiez le nombre de mois à prédire
   - Visualisez les résultats

## 📁 Format des données

### Fichier CSV requis
```csv
mois,ventes
1,150
2,200
3,180
4,220
5,250
...
```

### Colonnes
- **mois** : Numéro du mois (1, 2, 3, ...)
- **ventes** : Valeur des ventes (nombre)
- **annee** : Année (optionnel, généré automatiquement)
- **mois_annee** : Mois de l'année (optionnel, généré automatiquement)

## 🎨 Design moderne

L'application utilise :
- **CSS Variables** pour une palette de couleurs cohérente
- **Glassmorphism** pour des effets de transparence
- **Animations CSS** pour une expérience fluide
- **Gradients modernes** pour un design attrayant
- **Fonts Inter** pour une typographie contemporaine

## 🔧 Configuration

### Variables d'environnement
- `FLASK_ENV` : Environnement (development/production)
- `SECRET_KEY` : Clé secrète pour les sessions

### Ports
- **Port par défaut** : 5001
- **Port alternatif** : 8080 (si 5001 est occupé)

## 📦 Dépendances principales

- **Flask** : Framework web
- **Flask-Login** : Authentification
- **Pandas** : Manipulation des données
- **Scikit-learn** : Machine learning
- **Plotly** : Visualisation interactive
- **Bootstrap 5** : Interface utilisateur

## 🐛 Dépannage

### Problèmes courants

1. **Port déjà utilisé**
   - L'application trouve automatiquement un port libre
   - Ou utilisez : `python app.py --port 5002`

2. **Erreur d'import de fichier**
   - Vérifiez le format CSV
   - Assurez-vous que les colonnes `mois` et `ventes` existent

3. **Erreur de dépendances**
   - Réinstallez : `pip install -r requirements.txt`

### Logs
Les erreurs sont affichées dans la console et dans les messages flash de l'interface.

## 🚀 Déploiement

### Production
```bash
export FLASK_ENV=production
python app.py --host 0.0.0.0 --port 80
```

### Docker (optionnel)
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5001
CMD ["python", "app.py"]
```

## 📝 Licence

Ce projet est sous licence MIT.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests

---

**Développé avec ❤️ pour la prédiction des ventes**