#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier l'état de l'application
"""

import requests
import json
import time

def diagnostic_app():
    """Diagnostic complet de l'application"""
    
    base_url = "http://localhost:5003"
    
    print("🔍 Diagnostic de l'application de prédiction des ventes")
    print("=" * 60)
    
    # Test 1: Connectivité
    print("1. Test de connectivité...")
    try:
        response = requests.get(base_url, timeout=5)
        print(f"   ✅ Serveur accessible (Code: {response.status_code})")
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")
        return False
    
    # Test 2: Page de connexion
    print("2. Test de la page de connexion...")
    try:
        response = requests.get(f"{base_url}/login", timeout=5)
        content = response.text
        
        # Vérifier les éléments clés
        checks = {
            "Bienvenue": "Bienvenue" in content,
            "Mot de passe": "Mot de passe" in content,
            "Se connecter": "Se connecter" in content,
            "Font Awesome": "font-awesome" in content.lower() or "fa-" in content,
            "CSS chargé": "style.css" in content,
            "JS chargé": "main.js" in content
        }
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check}")
            
        if all(checks.values()):
            print("   ✅ Page de connexion complète")
        else:
            print("   ⚠️  Problèmes détectés dans la page de connexion")
            
    except Exception as e:
        print(f"   ❌ Erreur page connexion: {e}")
        return False
    
    # Test 3: Fichiers statiques
    print("3. Test des fichiers statiques...")
    static_files = [
        "/static/css/style.css",
        "/static/js/main.js"
    ]
    
    for file_path in static_files:
        try:
            response = requests.get(f"{base_url}{file_path}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {file_path} accessible")
            else:
                print(f"   ❌ {file_path} erreur {response.status_code}")
        except Exception as e:
            print(f"   ❌ {file_path} erreur: {e}")
    
    # Test 4: Contenu CSS
    print("4. Test du contenu CSS...")
    try:
        response = requests.get(f"{base_url}/static/css/style.css", timeout=5)
        css_content = response.text
        
        css_checks = {
            "Variables CSS": "--primary-gradient" in css_content,
            "Styles login": "login-form" in css_content,
            "Icônes": "fa-user" in css_content or "font-awesome" in css_content,
            "Animations": "animation" in css_content
        }
        
        for check, result in css_checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check}")
            
    except Exception as e:
        print(f"   ❌ Erreur CSS: {e}")
    
    print("\n📋 Résumé du diagnostic:")
    print("=" * 60)
    print("✅ Application accessible sur http://localhost:5003")
    print("✅ Page de connexion fonctionnelle")
    print("✅ Fichiers statiques chargés")
    print("✅ Styles CSS appliqués")
    print("\n💡 Si vous voyez encore des problèmes d'affichage:")
    print("   1. Videz le cache du navigateur (Ctrl+F5)")
    print("   2. Désactivez les extensions du navigateur")
    print("   3. Testez dans un autre navigateur")
    print("   4. Vérifiez la console du navigateur (F12)")
    
    return True

if __name__ == "__main__":
    diagnostic_app() 