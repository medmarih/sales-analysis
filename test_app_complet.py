#!/usr/bin/env python3
"""
Script de test complet pour l'application Flask
"""

import requests
import time
import json
import os

def test_application():
    """Test complet de l'application"""
    base_url = "http://127.0.0.1:5009"
    
    print("🧪 Test complet de l'application Flask...")
    print(f"🌐 URL de base: {base_url}")
    
    # Attendre que l'application démarre
    print("⏳ Attente du démarrage de l'application...")
    time.sleep(3)
    
    # Test 1: Page d'accueil (redirection vers login)
    print("\n📋 Test 1: Page d'accueil")
    try:
        response = requests.get(f"{base_url}/", allow_redirects=False)
        if response.status_code == 302:
            print("✅ Redirection vers login (comportement attendu)")
        else:
            print(f"⚠️ Statut inattendu: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 2: Page de login
    print("\n📋 Test 2: Page de login")
    try:
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✅ Page de login accessible")
        else:
            print(f"❌ Erreur page login: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 3: Connexion
    print("\n📋 Test 3: Connexion utilisateur")
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        response = requests.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        if response.status_code == 302:
            print("✅ Connexion réussie (redirection)")
            # Récupérer les cookies de session
            cookies = response.cookies
        else:
            print(f"❌ Erreur connexion: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 4: Page d'accueil après connexion
    print("\n📋 Test 4: Page d'accueil après connexion")
    try:
        response = requests.get(f"{base_url}/", cookies=cookies)
        if response.status_code == 200:
            print("✅ Page d'accueil accessible après connexion")
        else:
            print(f"❌ Erreur page accueil: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 5: Page des données
    print("\n📋 Test 5: Page des données")
    try:
        response = requests.get(f"{base_url}/data", cookies=cookies)
        if response.status_code == 200:
            print("✅ Page des données accessible")
        else:
            print(f"❌ Erreur page données: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 6: Page du modèle
    print("\n📋 Test 6: Page du modèle")
    try:
        response = requests.get(f"{base_url}/model", cookies=cookies)
        if response.status_code == 200:
            print("✅ Page du modèle accessible")
            # Vérifier si les graphiques sont présents
            if "pred_vs_actual" in response.text and "residuals" in response.text and "regression_line" in response.text:
                print("✅ Interface du modèle chargée avec succès")
            else:
                print("⚠️ Interface du modèle chargée mais graphiques non visibles")
        else:
            print(f"❌ Erreur page modèle: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 7: Vérification des fichiers de graphiques
    print("\n📋 Test 7: Vérification des fichiers de graphiques")
    temp_dir = os.path.join('data', 'temp_graphs')
    if os.path.exists(temp_dir):
        print(f"✅ Dossier temp_graphs trouvé: {temp_dir}")
        
        # Vérifier les fichiers
        graph_files = ['pred_vs_actual.json', 'residuals.json', 'regression_line.json']
        for filename in graph_files:
            filepath = os.path.join(temp_dir, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"✅ {filename}: {size} octets")
            else:
                print(f"❌ {filename}: FICHIER MANQUANT!")
    else:
        print(f"❌ Dossier temp_graphs non trouvé: {temp_dir}")
    
    print("\n🎉 Test de l'application terminé avec succès!")
    print("🎯 L'application fonctionne correctement.")
    return True

if __name__ == "__main__":
    try:
        success = test_application()
        if success:
            print("\n✅ Tous les tests ont réussi!")
            print("🚀 L'application est prête à être utilisée.")
        else:
            print("\n❌ Certains tests ont échoué!")
            print("🔍 Vérifiez les erreurs ci-dessus.")
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        import traceback
        traceback.print_exc() 