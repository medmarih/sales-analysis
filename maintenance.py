#!/usr/bin/env python3
"""
Script de maintenance pour l'application de prédiction des ventes
"""

import os
import shutil
import sqlite3
import json
from datetime import datetime, timedelta

def clean_temp_files():
    """Nettoie les fichiers temporaires"""
    print("🧹 Nettoyage des fichiers temporaires...")
    
    temp_dirs = [
        'data/temp_graphs',
        'data/visualisations'
    ]
    
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                print(f"✅ Dossier {temp_dir} supprimé")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {temp_dir}: {e}")
    
    # Nettoyer les fichiers temporaires dans data/
    data_dir = 'data'
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.startswith('temp_'):
                file_path = os.path.join(data_dir, filename)
                try:
                    os.remove(file_path)
                    print(f"✅ Fichier temporaire {filename} supprimé")
                except Exception as e:
                    print(f"❌ Erreur lors de la suppression de {filename}: {e}")

def clean_old_models():
    """Nettoie les anciens modèles"""
    print("\n🤖 Nettoyage des anciens modèles...")
    
    model_path = 'data/sales_predictor_model.joblib'
    if os.path.exists(model_path):
        # Vérifier l'âge du modèle
        stat = os.stat(model_path)
        model_age = datetime.now() - datetime.fromtimestamp(stat.st_mtime)
        
        if model_age.days > 30:  # Modèle de plus de 30 jours
            try:
                os.remove(model_path)
                print("✅ Ancien modèle supprimé (plus de 30 jours)")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression du modèle: {e}")
        else:
            print(f"✅ Modèle conservé (âge: {model_age.days} jours)")

def optimize_database():
    """Optimise la base de données SQLite"""
    print("\n🗄️  Optimisation de la base de données...")
    
    db_path = 'instance/users.db'
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # VACUUM pour optimiser l'espace
            cursor.execute("VACUUM")
            
            # ANALYZE pour optimiser les requêtes
            cursor.execute("ANALYZE")
            
            # Vérifier l'intégrité
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            
            if integrity == 'ok':
                print("✅ Base de données optimisée et intégrité vérifiée")
            else:
                print(f"⚠️  Problème d'intégrité détecté: {integrity}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erreur lors de l'optimisation de la base: {e}")
    else:
        print("ℹ️  Base de données non trouvée")

def check_disk_space():
    """Vérifie l'espace disque utilisé"""
    print("\n💾 Vérification de l'espace disque...")
    
    data_dir = 'data'
    if os.path.exists(data_dir):
        total_size = 0
        file_count = 0
        
        for dirpath, dirnames, filenames in os.walk(data_dir):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                    file_count += 1
                except OSError:
                    pass
        
        total_size_mb = total_size / (1024 * 1024)
        print(f"📊 Espace utilisé: {total_size_mb:.2f} MB")
        print(f"📁 Nombre de fichiers: {file_count}")
        
        if total_size_mb > 100:  # Plus de 100MB
            print("⚠️  L'espace utilisé est important, considérez un nettoyage")
        else:
            print("✅ Espace disque normal")

def create_backup():
    """Crée une sauvegarde des données importantes"""
    print("\n💾 Création d'une sauvegarde...")
    
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"backup_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        # Créer le dossier de sauvegarde
        os.makedirs(backup_path)
        
        # Copier les fichiers importants
        important_files = [
            'data/sales_predictor_model.joblib',
            'instance/users.db'
        ]
        
        for file_path in important_files:
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                backup_file = os.path.join(backup_path, filename)
                shutil.copy2(file_path, backup_file)
                print(f"✅ {filename} sauvegardé")
        
        # Créer un fichier de métadonnées
        metadata = {
            'timestamp': timestamp,
            'backup_date': datetime.now().isoformat(),
            'files_backed_up': [f for f in important_files if os.path.exists(f)]
        }
        
        metadata_file = os.path.join(backup_path, 'metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Sauvegarde créée: {backup_path}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la sauvegarde: {e}")

def main():
    """Fonction principale de maintenance"""
    print("🔧 DÉMARRAGE DE LA MAINTENANCE DE L'APPLICATION")
    print("=" * 50)
    
    # Créer une sauvegarde avant le nettoyage
    create_backup()
    
    # Nettoyer les fichiers temporaires
    clean_temp_files()
    
    # Nettoyer les anciens modèles
    clean_old_models()
    
    # Optimiser la base de données
    optimize_database()
    
    # Vérifier l'espace disque
    check_disk_space()
    
    print("\n" + "=" * 50)
    print("✅ MAINTENANCE TERMINÉE AVEC SUCCÈS")
    print("=" * 50)

if __name__ == "__main__":
    main()
