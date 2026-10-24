import os
from datetime import timedelta

class Config:
    """Configuration de base de l'application"""
    
    # Configuration de base
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    
    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration de sécurité
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Configuration des uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    UPLOAD_FOLDER = 'data'
    ALLOWED_EXTENSIONS = {'csv'}
    
    # Configuration du modèle
    MODEL_SAVE_PATH = 'data/sales_predictor_model.joblib'
    GRAPHS_TEMP_PATH = 'data/temp_graphs'
    
    # Configuration des logs
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Configuration de l'application
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 50010))

class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
    # En production, utilisez une clé secrète forte
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY doit être définie en production")

class TestingConfig(Config):
    """Configuration pour les tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Dictionnaire des configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Retourne la configuration appropriée selon l'environnement"""
    config_name = os.environ.get('FLASK_ENV', 'default')
    return config.get(config_name, config['default'])
