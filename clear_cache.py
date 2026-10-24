#!/usr/bin/env python3
"""
Script pour ajouter des paramètres de cache-busting aux fichiers statiques
"""

import os
import time
import hashlib

def add_cache_busting():
    """Ajoute des paramètres de cache-busting aux fichiers statiques"""
    
    # Timestamp pour forcer le rafraîchissement
    timestamp = int(time.time())
    
    # Fichiers à modifier
    files_to_update = [
        'templates/layout.html',
        'templates/login.html'
    ]
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            print(f"🔄 Mise à jour de {file_path}...")
            
            # Lire le contenu
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ajouter le timestamp aux fichiers CSS et JS
            content = content.replace(
                'href="/static/css/style.css"',
                f'href="/static/css/style.css?v={timestamp}"'
            )
            content = content.replace(
                'src="/static/js/main.js"',
                f'src="/static/js/main.js?v={timestamp}"'
            )
            
            # Écrire le contenu modifié
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ {file_path} mis à jour")

if __name__ == "__main__":
    print("🧹 Nettoyage du cache...")
    add_cache_busting()
    print("✅ Cache nettoyé !")
    print("💡 Rechargez la page avec Ctrl+F5 pour forcer le rafraîchissement") 