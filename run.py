#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de démarrage pour l'application de prédiction des ventes.
Ce script permet de lancer l'application avec des options de configuration.
"""

import os
import argparse
from app import app, db, create_default_admin


def parse_args():
    """
    Parse les arguments de ligne de commande.
    
    Returns:
        argparse.Namespace: Les arguments parsés.
    """
    parser = argparse.ArgumentParser(description='Démarrer l\'application de prédiction des ventes')
    parser.add_argument('--host', default='0.0.0.0', help='Adresse IP d\'écoute (défaut: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port d\'écoute (défaut: 5000)')
    parser.add_argument('--debug', action='store_true', help='Activer le mode debug')
    parser.add_argument('--init-db', action='store_true', help='Initialiser la base de données')
    return parser.parse_args()


def main():
    """
    Fonction principale pour démarrer l'application.
    """
    args = parse_args()
    
    # Créer le dossier data s'il n'existe pas
    os.makedirs('data', exist_ok=True)
    
    # Initialiser la base de données si demandé
    if args.init_db:
        with app.app_context():
            db.create_all()
            create_default_admin()
            print("Base de données initialisée avec succès!")
    
    # Démarrer l'application
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )


if __name__ == '__main__':
    main()