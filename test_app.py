#!/usr/bin/env python3
"""
Script de test pour vérifier le bon fonctionnement de l'application
"""

import os
import sys
import json
import requests
from pathlib import Path

def test_app_health():
    """Test de santé de l'application"""
    try:
        response = requests.get('http://127.0.0.1:5008/')
        print(f"✅ Application accessible: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Application non accessible")
        return False

def test_files_exist():
    """Vérifier que tous les fichiers nécessaires existent"""
    required_files = [
        'app.py',
        'templates/layout.html',
        'templates/model.html',
        'static/css/style.css',
        'static/js/main.js',
        'requirements.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Fichiers manquants: {missing_files}")
        return False
    else:
        print("✅ Tous les fichiers requis sont présents")
        return True

def test_directories():
    """Vérifier que les dossiers nécessaires existent"""
    required_dirs = [
        'data',
        'templates',
        'static',
        'static/css',
        'static/js',
        'static/img'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ Dossiers manquants: {missing_dirs}")
        return False
    else:
        print("✅ Tous les dossiers requis sont présents")
        return True

def test_template_syntax():
    """Vérifier la syntaxe des templates"""
    try:
        with open('templates/model.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier les balises Jinja2 de base
        if '{% extends "layout.html" %}' in content:
            print("✅ Template model.html syntaxe correcte")
            return True
        else:
            print("❌ Template model.html syntaxe incorrecte")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du template: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🔍 Test de l'application Prédiction des Ventes")
    print("=" * 50)
    
    tests = [
        ("Fichiers requis", test_files_exist),
        ("Dossiers requis", test_directories),
        ("Syntaxe des templates", test_template_syntax),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Test: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Résultats des tests:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Score: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! L'application est prête.")
        return True
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les problèmes identifiés.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 