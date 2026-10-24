#!/bin/bash

# Script de démarrage pour l'application de prédiction des ventes

echo "🚀 Démarrage de l'application de prédiction des ventes..."

# Vérifier que Python est installé
if ! command -v python &> /dev/null; then
    echo "❌ Python n'est pas installé ou n'est pas dans le PATH"
    exit 1
fi

# Vérifier que les dépendances sont installées
echo "📦 Vérification des dépendances..."
if ! python -c "import flask, flask_login, pandas, plotly" 2>/dev/null; then
    echo "❌ Certaines dépendances sont manquantes. Installation..."
    pip install -r requirements.txt
fi

# Créer le dossier data s'il n'existe pas
mkdir -p data

# Trouver un port libre
PORT=5001
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    echo "⚠️  Le port $PORT est occupé, essai du port suivant..."
    PORT=$((PORT + 1))
done

echo "✅ Port $PORT disponible"

# Démarrer l'application
echo "🌐 Démarrage de l'application sur http://localhost:$PORT"
echo "📝 Identifiants de connexion: admin / admin123"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter l'application"
echo ""

# Modifier temporairement le port dans app.py
sed -i.bak "s/port=[0-9]*/port=$PORT/" app.py

# Démarrer l'application
python app.py

# Restaurer le fichier original
mv app.py.bak app.py 2>/dev/null || true