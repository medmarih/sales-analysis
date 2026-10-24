import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import os

def load_data(file_path=None, data=None):
    """
    Charge les données depuis un fichier CSV ou un DataFrame fourni
    
    Args:
        file_path (str, optional): Chemin vers le fichier CSV
        data (pd.DataFrame, optional): DataFrame contenant les données
        
    Returns:
        pd.DataFrame: Les données chargées
    """
    if file_path:
        try:
            # Vérifier que le fichier existe
            if not os.path.exists(file_path):
                print(f"Le fichier {file_path} n'existe pas")
                return None
            
            # Essayer plusieurs stratégies de lecture (délimiteurs / encodages)
            last_error = None
            df = None
            encodings_to_try = ['utf-8-sig', 'utf-8', 'latin1']
            seps_to_try = [None, ';', ',', '\t']

            for enc in encodings_to_try:
                for sep in seps_to_try:
                    try:
                        tmp = pd.read_csv(file_path, sep=sep, engine='python', encoding=enc)
                        # Normaliser les noms de colonnes
                        tmp.columns = [
                            str(col).strip().lower().replace(' ', '_').replace(';', '_').replace('-', '_')
                        for col in tmp.columns
                        ]
                        # Nettoyer colonnes
                        tmp = tmp.loc[:, ~tmp.columns.duplicated()]
                        tmp = tmp.dropna(axis=1, how='all')
                        # Vérifier présence des colonnes
                        if {'mois', 'ventes'}.issubset(set(tmp.columns)):
                            df = tmp
                            break
                    except Exception as e:
                        last_error = e
                if df is not None:
                    break

            if df is None:
                print(f"Impossible de lire le CSV avec les stratégies testées. Dernière erreur: {last_error}")
                return None
            
            # Vérifier que le DataFrame n'est pas vide
            if df.empty:
                print("Le fichier CSV est vide")
                return None
            
            # Vérifier que les colonnes requises existent
            # Colonnes minimales requises
            required_columns = ['mois', 'ventes']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"Colonnes manquantes: {missing_columns}")
                print(f"Colonnes disponibles: {list(df.columns)}")
                return None
            
            # Convertir les colonnes en types appropriés
            try:
                df['mois'] = pd.to_numeric(df['mois'], errors='coerce')
                df['ventes'] = pd.to_numeric(df['ventes'], errors='coerce')
                
                # Supprimer les lignes avec des valeurs NaN
                df = df.dropna(subset=['mois', 'ventes'])
                
                if df.empty:
                    print("Aucune donnée valide après nettoyage")
                    return None
            except Exception as e:
                print(f"Erreur lors de la conversion des types de données: {e}")
                return None
            
            # Si les colonnes année / mois_annee sont présentes mais non numériques, tenter une conversion
            for optional_col in ['annee', 'mois_annee']:
                if optional_col in df.columns:
                    df[optional_col] = pd.to_numeric(df[optional_col], errors='coerce')
            
            # Trier par mois pour assurer l'ordre chronologique
            df = df.sort_values('mois').reset_index(drop=True)
            
            print(f"Données chargées avec succès: {len(df)} lignes")
            return df
            
        except pd.errors.EmptyDataError:
            print("Le fichier CSV est vide")
            return None
        except pd.errors.ParserError as e:
            print(f"Erreur de parsing du fichier CSV: {e}")
            return None
        except Exception as e:
            print(f"Erreur lors du chargement du fichier: {e}")
            return None
    elif data is not None:
        return data
    else:
        return None

def prepare_data(data, target_col='ventes', feature_cols=None):
    """
    Prépare les données pour l'entraînement du modèle
    
    Args:
        data (pd.DataFrame): Les données à préparer
        target_col (str): Nom de la colonne cible (ventes)
        feature_cols (list, optional): Liste des colonnes de caractéristiques
        
    Returns:
        tuple: (X, y) - caractéristiques et cible
    """
    if data is None:
        return None, None
    
    # Si aucune colonne de caractéristiques n'est spécifiée, 
    # utiliser seulement la colonne 'mois' qui est numérique
    if feature_cols is None:
        if 'mois' in data.columns:
            feature_cols = ['mois']
        else:
            # Fallback: utiliser toutes les colonnes numériques sauf la cible
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            feature_cols = [col for col in numeric_cols if col != target_col]
    
    # Vérifier que les colonnes existent
    for col in [target_col] + feature_cols:
        if col not in data.columns:
            print(f"La colonne {col} n'existe pas dans les données")
            return None, None
    
    # S'assurer que toutes les colonnes sont numériques
    for col in feature_cols:
        if not pd.api.types.is_numeric_dtype(data[col]):
            print(f"La colonne {col} n'est pas numérique. Conversion en cours...")
            try:
                data[col] = pd.to_numeric(data[col], errors='coerce')
                # Supprimer les lignes avec des valeurs NaN
                data = data.dropna(subset=[col])
                if data.empty:
                    print(f"Aucune donnée valide après conversion de {col}")
                    return None, None
            except Exception as e:
                print(f"Impossible de convertir {col} en numérique: {e}")
                return None, None
    
    # S'assurer que la colonne cible est numérique
    if not pd.api.types.is_numeric_dtype(data[target_col]):
        print(f"Conversion de la colonne cible {target_col} en numérique...")
        try:
            data[target_col] = pd.to_numeric(data[target_col], errors='coerce')
            data = data.dropna(subset=[target_col])
            if data.empty:
                print(f"Aucune donnée valide après conversion de {target_col}")
                return None, None
        except Exception as e:
            print(f"Impossible de convertir {target_col} en numérique: {e}")
            return None, None
    
    X = data[feature_cols]
    y = data[target_col]
    
    print(f"✅ Données préparées: X={X.shape}, y={y.shape}")
    print(f"📊 Colonnes utilisées: {list(X.columns)}")
    
    return X, y

def split_data(X, y, test_size=0.2, random_state=42):
    """
    Divise les données en ensembles d'entraînement et de test
    
    Args:
        X: Caractéristiques
        y: Cible
        test_size (float): Proportion de l'ensemble de test
        random_state (int): Graine aléatoire pour la reproductibilité
        
    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
    if X is None or y is None:
        return None, None, None, None
    
    return train_test_split(X, y, test_size=test_size, random_state=random_state)

def evaluate_model(model, X_test, y_test):
    """
    Évalue les performances du modèle
    
    Args:
        model: Le modèle entraîné
        X_test: Caractéristiques de test
        y_test: Cible de test
        
    Returns:
        dict: Métriques d'évaluation
    """
    if model is None or X_test is None or y_test is None:
        return None
    
    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    return {
        'mse': mse,
        'rmse': rmse,
        'r2': r2
    }

def plot_predictions(y_true, y_pred, title="Prédictions vs Valeurs Réelles"):
    """
    Affiche un graphique des prédictions vs valeurs réelles
    
    Args:
        y_true: Valeurs réelles
        y_pred: Valeurs prédites
        title (str): Titre du graphique
    """
    plt.figure(figsize=(10, 6))
    plt.scatter(y_true, y_pred, alpha=0.7)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--')
    plt.xlabel('Valeurs Réelles')
    plt.ylabel('Prédictions')
    plt.title(title)
    plt.tight_layout()
    return plt.gcf()

def plot_residuals(y_true, y_pred, title="Résidus"):
    """
    Affiche un graphique des résidus
    
    Args:
        y_true: Valeurs réelles
        y_pred: Valeurs prédites
        title (str): Titre du graphique
    """
    residuals = y_true - y_pred
    plt.figure(figsize=(10, 6))
    plt.scatter(y_pred, residuals, alpha=0.7)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('Prédictions')
    plt.ylabel('Résidus')
    plt.title(title)
    plt.tight_layout()
    return plt.gcf()

def generate_sample_data(n_samples=24, trend=0.5, seasonality=0.3, noise=0.2, seed=42):
    """
    Génère des données d'exemple pour les ventes mensuelles
    
    Args:
        n_samples (int): Nombre d'échantillons (mois)
        trend (float): Force de la tendance
        seasonality (float): Force de la saisonnalité
        noise (float): Niveau de bruit
        seed (int): Graine aléatoire
        
    Returns:
        pd.DataFrame: Données générées
    """
    np.random.seed(seed)
    
    # Créer une séquence de mois
    months = np.arange(1, n_samples + 1)
    
    # Créer une tendance linéaire
    trend_component = trend * months / n_samples
    
    # Créer une composante saisonnière (cycle annuel)
    seasonality_component = seasonality * np.sin(2 * np.pi * months / 12)
    
    # Ajouter du bruit aléatoire
    noise_component = noise * np.random.randn(n_samples)
    
    # Combiner les composantes pour créer les ventes
    base_sales = 100  # Ventes de base
    sales = base_sales + trend_component * 100 + seasonality_component * 100 + noise_component * 50
    sales = np.maximum(sales, 0)  # Assurer que les ventes ne sont pas négatives
    
    # Créer un DataFrame
    data = pd.DataFrame({
        'mois': months,
        'ventes': sales.round(2)
    })
    
    # Ajouter des colonnes pour le mois et l'année
    start_year = 2020
    data['annee'] = start_year + (data['mois'] - 1) // 12
    data['mois_annee'] = (data['mois'] - 1) % 12 + 1
    
    return data

def calculate_stock_recommendations(predicted_sales, safety_factor=1.2, min_stock=10):
    """
    Calcule les recommandations de stock basées sur les ventes prédites
    
    Args:
        predicted_sales (float or array): Ventes prédites
        safety_factor (float): Facteur de sécurité pour le stock
        min_stock (float): Stock minimum à maintenir
        
    Returns:
        float or array: Recommandations de stock
    """
    return np.maximum(predicted_sales * safety_factor, min_stock)