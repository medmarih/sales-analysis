import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

class SalesPredictor:
    """
    Classe pour prédire les ventes mensuelles à l'aide d'un modèle de régression linéaire
    """
    
    def __init__(self, model_type='linear', poly_degree=2):
        """
        Initialise le prédicteur de ventes
        
        Args:
            model_type (str): Type de modèle (uniquement 'linear' est supporté)
            poly_degree (int): Paramètre conservé pour compatibilité mais non utilisé
        """
        self.model_type = 'linear'  # Toujours linéaire
        self.poly_degree = poly_degree  # Conservé pour compatibilité
        
        # Utilisation uniquement de la régression linéaire
        self.model = LinearRegression()
        
        self.is_trained = False
        self.feature_names = None
    
    def train(self, X, y):
        """
        Entraîne le modèle sur les données fournies
        
        Args:
            X: Caractéristiques d'entraînement
            y: Cible d'entraînement (ventes)
            
        Returns:
            self: Le modèle entraîné
        """
        if X is None or y is None:
            print("Données d'entraînement invalides")
            return self
        
        # Enregistrer les noms des caractéristiques
        if isinstance(X, pd.DataFrame):
            self.feature_names = X.columns.tolist()
        
        # Entraîner le modèle
        self.model.fit(X, y)
        self.is_trained = True
        
        return self
    
    def predict(self, X):
        """
        Fait des prédictions avec le modèle entraîné
        
        Args:
            X: Caractéristiques pour la prédiction
            
        Returns:
            array: Prédictions de ventes
        """
        if not self.is_trained:
            print("Le modèle n'est pas encore entraîné")
            return None
        
        return self.model.predict(X)
    
    def evaluate(self, X_test, y_test):
        """
        Évalue les performances du modèle
        
        Args:
            X_test: Caractéristiques de test
            y_test: Cible de test
            
        Returns:
            dict: Métriques d'évaluation
        """
        if not self.is_trained:
            print("Le modèle n'est pas encore entraîné")
            return None
        
        y_pred = self.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        return {
            'mse': mse,
            'rmse': rmse,
            'r2': r2
        }
    
    def get_model_params(self):
        """
        Récupère les paramètres du modèle
        
        Returns:
            dict: Paramètres du modèle
        """
        if not self.is_trained:
            print("Le modèle n'est pas encore entraîné")
            return None
        
        params = {}
        
        if self.model_type == 'linear':
            params['coefficients'] = self.model.coef_
            params['intercept'] = self.model.intercept_
        elif self.model_type == 'polynomial':
            params['coefficients'] = self.model.named_steps['linear'].coef_
            params['intercept'] = self.model.named_steps['linear'].intercept_
        
        return params
    
    def save_model(self, file_path='sales_predictor_model.joblib'):
        """
        Sauvegarde le modèle entraîné
        
        Args:
            file_path (str): Chemin où sauvegarder le modèle
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        if not self.is_trained:
            print("Le modèle n'est pas encore entraîné")
            return False
        
        try:
            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Sauvegarder le modèle
            joblib.dump({
                'model': self.model,
                'model_type': self.model_type,
                'poly_degree': self.poly_degree,
                'feature_names': self.feature_names,
                'is_trained': self.is_trained
            }, file_path)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du modèle: {e}")
            return False
    
    @classmethod
    def load_model(cls, file_path='sales_predictor_model.joblib'):
        """
        Charge un modèle entraîné
        
        Args:
            file_path (str): Chemin vers le modèle sauvegardé
            
        Returns:
            SalesPredictor: Instance du modèle chargé
        """
        try:
            # Charger le modèle
            data = joblib.load(file_path)
            
            # Créer une nouvelle instance
            predictor = cls(model_type=data['model_type'], poly_degree=data['poly_degree'])
            predictor.model = data['model']
            predictor.feature_names = data['feature_names']
            predictor.is_trained = data['is_trained']
            
            return predictor
        except Exception as e:
            print(f"Erreur lors du chargement du modèle: {e}")
            return None