from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Utiliser le backend non-interactif
import matplotlib.pyplot as plt
import io
import base64
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime

# Importer nos modules personnalisés
from model import SalesPredictor
from utils import (
    load_data, prepare_data, split_data, evaluate_model,
    generate_sample_data
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modèle utilisateur pour l'authentification
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Formulaires
class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')

class RegistrationForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('S\'inscrire')

class ModelConfigForm(FlaskForm):
    # Suppression de l'option de régression polynomiale
    model_type = SelectField('Type de modèle', choices=[('linear', 'Régression Linéaire')])
    # Champ poly_degree conservé mais caché pour éviter les erreurs
    poly_degree = IntegerField('Degré du polynôme', validators=[NumberRange(min=1, max=5)], default=2, render_kw={'style': 'display: none;'})
    test_size = FloatField('Proportion de test (%)', validators=[NumberRange(min=10, max=50)], default=20)
    submit = SubmitField('Entraîner le modèle')

class PredictionForm(FlaskForm):
    target_month = IntegerField('Mois à prédire (1-12)', validators=[NumberRange(min=1, max=12)], default=1)
    submit = SubmitField('Prédire ce mois')

# La classe StockRecommendationForm a été supprimée

# Fonction pour créer un utilisateur admin par défaut
def create_default_admin():
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(username='admin', password=hashed_password, is_admin=True)
            db.session.add(admin)
            db.session.commit()
            print("Utilisateur admin créé avec succès!")

# Fonction pour générer des graphiques
def create_figure_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    return string.decode('utf-8')

# Routes pour l'authentification
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Échec de la connexion. Veuillez vérifier votre nom d\'utilisateur et votre mot de passe', 'danger')
    return render_template('login.html', title='Connexion', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if not current_user.is_admin:
        flash('Accès refusé. Vous devez être administrateur pour accéder à cette page.', 'danger')
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Compte créé pour {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Inscription', form=form)

# Routes pour l'application
@app.route('/')
@login_required
def index():
    return render_template('index.html', title='Accueil')

@app.route('/data', methods=['GET', 'POST'])
@login_required
def data():
    # Récupérer les données de la session
    data_json = session.get('data')
    if data_json:
        data = pd.read_json(data_json, orient='split')
        
        # Créer un graphique avec plotly
        fig = px.line(data, x='mois', y='ventes', markers=True, title='Données de Ventes Mensuelles')
        # Ajouter explicitement des points (markers) sur la ligne
        fig.update_traces(mode='lines+markers', marker=dict(size=8, opacity=0.8))
        fig.update_layout(xaxis_title='Mois', yaxis_title='Ventes')
        graph_json = fig.to_json()
        
        # Créer un tableau de données
        table_data = data.to_dict('records')
        table_columns = [col for col in data.columns]
        
        return render_template('data.html', title='Données', 
                               graph_json=graph_json, 
                               table_data=table_data, 
                               table_columns=table_columns,
                               has_data=True)
    
    return render_template('data.html', title='Données', has_data=False)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'csv_file' not in request.files:
        flash('Aucun fichier sélectionné', 'warning')
        return redirect(url_for('data'))
    
    file = request.files['csv_file']
    
    # Vérifier si un fichier a été sélectionné
    if file.filename == '':
        flash('Aucun fichier sélectionné', 'warning')
        return redirect(url_for('data'))
    
    # Vérifier l'extension du fichier
    if not file.filename.lower().endswith('.csv'):
        flash('Veuillez sélectionner un fichier CSV valide', 'danger')
        return redirect(url_for('data'))
    
    try:
        # Créer le dossier data s'il n'existe pas
        data_dir = 'data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Sauvegarder temporairement le fichier
        file_path = os.path.join(data_dir, 'temp_' + file.filename)
        file.save(file_path)
        
        # Charger les données
        data = load_data(file_path)
        
        # Vérifier si les données ont été chargées avec succès
        if data is None or data.empty:
            flash('Le fichier CSV est vide ou mal formaté. Assurez-vous qu\'il contient les colonnes "mois" et "ventes".', 'danger')
            # Supprimer le fichier temporaire
            if os.path.exists(file_path):
                os.remove(file_path)
            return redirect(url_for('data'))
        
        # Vérifier que les données contiennent au moins quelques lignes
        if len(data) < 2:
            flash('Le fichier doit contenir au moins 2 lignes de données.', 'danger')
            if os.path.exists(file_path):
                os.remove(file_path)
            return redirect(url_for('data'))
        
        # Stocker les données dans la session
        session['data'] = data.to_json(orient='split')
        
        # Supprimer le fichier temporaire
        if os.path.exists(file_path):
            os.remove(file_path)
        
        flash(f'Données chargées avec succès! {len(data)} enregistrements importés.', 'success')
        return redirect(url_for('data'))
        
    except Exception as e:
        # Supprimer le fichier temporaire en cas d'erreur
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        # Log de l'erreur pour le débogage
        print(f"Erreur lors de l'upload: {str(e)}")
        
        flash(f'Erreur lors du chargement des données: {str(e)}', 'danger')
        return redirect(url_for('data'))

@app.route('/generate_sample', methods=['POST'])
@login_required
def generate_sample():
    try:
        # Générer des données d'exemple
        data = generate_sample_data(n_samples=24)
        
        # Stocker les données dans la session
        session['data'] = data.to_json(orient='split')
        
        flash('Données d\'exemple générées avec succès!', 'success')
        return redirect(url_for('data'))
    except Exception as e:
        flash(f'Erreur lors de la génération des données: {str(e)}', 'danger')
        return redirect(url_for('data'))

@app.route('/export_data')
@login_required
def export_data():
    data_json = session.get('data')
    if not data_json:
        flash('Aucune donnée disponible à exporter.', 'warning')
        return redirect(url_for('data'))
    
    try:
        data = pd.read_json(data_json, orient='split')
        csv_data = data.to_csv(index=False)
        
        response = app.response_class(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment;filename=export_ventes.csv'}
        )
        return response
    except Exception as e:
        flash(f'Erreur lors de l\'exportation des données: {str(e)}', 'danger')
        return redirect(url_for('data'))

@app.route('/model', methods=['GET', 'POST'])
@login_required
def model():
    form = ModelConfigForm()
    
    if form.validate_on_submit():
        # Récupérer les données de la session
        data_json = session.get('data')
        if not data_json:
            flash('Aucune donnée disponible. Veuillez d\'abord charger des données.', 'warning')
            return redirect(url_for('data'))
        
        try:
            data = pd.read_json(data_json, orient='split')
            
            # Préparer les données pour l'entraînement
            X, y = prepare_data(data)
            
            if X is None or y is None:
                flash('Erreur lors de la préparation des données. Vérifiez le format de votre fichier CSV.', 'danger')
                return redirect(url_for('model'))
            
            # Afficher les informations sur les données préparées
            print(f"📊 Données préparées: X shape={X.shape}, colonnes={list(X.columns)}, y shape={y.shape}")
            
            # Diviser les données
            test_size = form.test_size.data / 100.0
            X_train, X_test, y_train, y_test = split_data(X, y, test_size=test_size/100)
            
            if X_train is None or X_test is None:
                flash('Erreur lors de la division des données.', 'danger')
                return redirect(url_for('model'))
            
            print(f"📈 Division des données: Train={X_train.shape}, Test={X_test.shape}")
            
            # Créer et entraîner le modèle
            model = SalesPredictor()
            model.train(X_train, y_train)
            
            # Évaluer le modèle
            metrics = model.evaluate(X_test, y_test)
            
            # Sauvegarder le modèle
            model_path = os.path.join('data', 'sales_predictor_model.joblib')
            model.save_model(model_path)
            
            # Faire des prédictions sur l'ensemble de test pour les graphiques
            y_pred = model.predict(X_test)
            
            # Créer les graphiques avec plotly
            # Graphique 1: Prédictions vs Valeurs réelles avec ligne de régression
            fig1 = go.Figure()
            
            # Ajouter les points de prédiction vs réels
            fig1.add_trace(go.Scatter(
                x=y_test,
                y=y_pred,
                mode='markers',
                name='Prédictions vs Réels',
                marker=dict(color='blue', size=8, opacity=0.7)
            ))
            
            # Ajouter la ligne de régression parfaite (y=x)
            min_val = min(y_test.min(), y_pred.min())
            max_val = max(y_test.max(), y_pred.max())
            fig1.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                line=dict(color='red', dash='dash', width=2),
                name='Ligne parfaite (y=x)',
                showlegend=True
            ))
            
            fig1.update_layout(
                title='Prédictions vs Valeurs Réelles',
                xaxis_title='Valeurs Réelles',
                yaxis_title='Prédictions',
                showlegend=True,
                hovermode='closest'
            )
            
            # Graphique 2: Résidus avec ligne horizontale à y=0
            residuals = y_test - y_pred
            fig2 = go.Figure()
            
            fig2.add_trace(go.Scatter(
                x=y_pred,
                y=residuals,
                mode='markers',
                name='Résidus',
                marker=dict(color='green', size=8, opacity=0.7)
            ))
            
            # Ajouter la ligne horizontale à y=0
            fig2.add_shape(
                type="line",
                x0=y_pred.min(),
                y0=0,
                x1=y_pred.max(),
                y1=0,
                line=dict(color="red", width=2, dash="dash")
            )
            
            fig2.update_layout(
                title='Résidus du Modèle',
                xaxis_title='Prédictions',
                yaxis_title='Résidus (Réel - Prédit)',
                showlegend=True,
                hovermode='closest'
            )
            
            # Graphique 3: Régression linéaire
            fig3 = go.Figure()
            
            # Ajouter les points de données d'entraînement
            fig3.add_trace(go.Scatter(
                x=X_train['mois'],
                y=y_train,
                mode='markers',
                name='Données d\'entraînement',
                marker=dict(color='blue', size=8, opacity=0.8)
            ))
            
            # Ajouter les points de données de test
            fig3.add_trace(go.Scatter(
                x=X_test['mois'],
                y=y_test,
                mode='markers',
                name='Données de test',
                marker=dict(color='green', size=8, opacity=0.8)
            ))
            
            # Ajouter les prédictions sur les données de test
            fig3.add_trace(go.Scatter(
                x=X_test['mois'],
                y=y_pred,
                mode='markers',
                name='Prédictions (test)',
                marker=dict(color='red', size=8, opacity=0.8)
            ))
            
            # Créer la ligne de régression linéaire
            all_months = np.concatenate([X_train['mois'], X_test['mois']])
            all_y = np.concatenate([y_train, y_test])
            
            z = np.polyfit(all_months, all_y, 1)
            p = np.poly1d(z)
            
            x_range = np.linspace(all_months.min(), all_months.max(), 100)
            y_regression = p(x_range)
            
            fig3.add_trace(go.Scatter(
                x=x_range,
                y=y_regression,
                mode='lines',
                line=dict(color='purple', width=3),
                name='Régression linéaire',
                opacity=0.9
            ))
            
            fig3.update_layout(
                title='Régression Linéaire: Ventes vs Mois',
                xaxis_title='Mois',
                yaxis_title='Ventes',
                showlegend=True,
                hovermode='closest'
            )
            
            # Sauvegarder les graphiques dans des fichiers temporaires pour éviter les problèmes de session
            import tempfile
            
            # Créer un dossier temporaire pour les graphiques
            temp_dir = os.path.join('data', 'temp_graphs')
            os.makedirs(temp_dir, exist_ok=True)
            
            print(f"🔍 Tentative de sauvegarde des graphiques dans {temp_dir}")
            print(f"📊 fig1 type: {type(fig1)}, fig2 type: {type(fig2)}, fig3 type: {type(fig3)}")
            
            # Sauvegarder les graphiques en JSON
            try:
                # Sauvegarder le graphique 1
                pred_file = os.path.join(temp_dir, 'pred_vs_actual.json')
                print(f"💾 Sauvegarde de {pred_file}...")
                with open(pred_file, 'w', encoding='utf-8') as f:
                    json.dump(fig1.to_dict(), f, ensure_ascii=False, indent=2)
                print(f"✅ Graphique pred_vs_actual sauvegardé dans {pred_file}")
                
                # Sauvegarder le graphique 2
                residuals_file = os.path.join(temp_dir, 'residuals.json')
                print(f"💾 Sauvegarde de {residuals_file}...")
                with open(residuals_file, 'w', encoding='utf-8') as f:
                    json.dump(fig2.to_dict(), f, ensure_ascii=False, indent=2)
                print(f"✅ Graphique residuals sauvegardé dans {residuals_file}")
                
                # Sauvegarder le graphique 3
                regression_file = os.path.join(temp_dir, 'regression_line.json')
                print(f"💾 Sauvegarde de {regression_file}...")
                with open(regression_file, 'w', encoding='utf-8') as f:
                    json.dump(fig3.to_dict(), f, ensure_ascii=False, indent=2)
                print(f"✅ Graphique regression_line sauvegardé dans {regression_file}")
                
                # Vérifier que les fichiers ont été créés
                print(f"📁 Vérification des fichiers créés:")
                for filename in ['pred_vs_actual.json', 'residuals.json', 'regression_line.json']:
                    filepath = os.path.join(temp_dir, filename)
                    if os.path.exists(filepath):
                        size = os.path.getsize(filepath)
                        print(f"✅ {filename}: {size} octets")
                    else:
                        print(f"❌ {filename}: FICHIER MANQUANT!")
                    
            except Exception as e:
                print(f"❌ Erreur lors de la sauvegarde des graphiques: {e}")
                import traceback
                traceback.print_exc()
                flash(f'Erreur lors de la sauvegarde des graphiques: {str(e)}', 'warning')
            
            # Stocker seulement les métriques dans la session (plus léger)
            session['metrics'] = {
                'mse': float(metrics['mse']),
                'rmse': float(metrics['rmse']),
                'r2': float(metrics['r2'])
            }
            
            # Marquer que le modèle a été entraîné
            session['model_trained'] = True
            
            flash('Modèle entraîné avec succès!', 'success')
            return redirect(url_for('model'))
            
        except Exception as e:
            flash(f'Erreur lors de l\'entraînement du modèle: {str(e)}', 'danger')
    
    # Récupérer les métriques et les graphiques de la session
    metrics = session.get('metrics')
    
    # Vérifier si un modèle a été entraîné en regardant l'existence du fichier
    model_path = os.path.join('data', 'sales_predictor_model.joblib')
    model_exists = os.path.exists(model_path)
    
    # Si les métriques ne sont pas dans la session mais qu'un modèle existe, essayer de les recalculer
    if not metrics and model_exists:
        print("⚠️ Métriques non trouvées dans la session, tentative de recalcul...")
        try:
            # Charger les données de la session
            data_json = session.get('data')
            if data_json:
                data = pd.read_json(data_json, orient='split')
                
                # Préparer les données de la même manière qu'à l'entraînement
                X, y = prepare_data(data)
                if X is not None and y is not None:
                    X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2)
                    
                    # Charger le modèle et faire des prédictions
                    model = SalesPredictor.load_model(model_path)
                    y_pred = model.predict(X_test)
                    
                    # Recalculer les métriques
                    from sklearn.metrics import mean_squared_error, r2_score
                    mse = mean_squared_error(y_test, y_pred)
                    rmse = np.sqrt(mse)
                    r2 = r2_score(y_test, y_pred)
                    
                    metrics = {
                        'mse': float(mse),
                        'rmse': float(rmse),
                        'r2': float(r2)
                    }
                    
                    # Sauvegarder dans la session
                    session['metrics'] = metrics
                    print("✅ Métriques recalculées et sauvegardées")
                else:
                    print("❌ Erreur lors de la préparation des données")
            else:
                print("❌ Données non disponibles pour recalculer les métriques")
        except Exception as e:
            print(f"❌ Erreur lors du recalcul des métriques: {e}")
            import traceback
            traceback.print_exc()
            
            # Si le recalcul échoue, supprimer l'ancien modèle pour forcer un nouvel entraînement
            print("🔄 Suppression de l'ancien modèle pour forcer un nouvel entraînement...")
            try:
                if os.path.exists(model_path):
                    os.remove(model_path)
                    print("✅ Ancien modèle supprimé")
                
                # Supprimer aussi les anciens graphiques
                temp_dir = os.path.join('data', 'temp_graphs')
                if os.path.exists(temp_dir):
                    import shutil
                    shutil.rmtree(temp_dir)
                    print("✅ Anciens graphiques supprimés")
                
                # Nettoyer la session
                session.pop('metrics', None)
                session.pop('pred_vs_actual', None)
                session.pop('residuals', None)
                session.pop('regression_line', None)
                session.pop('model_trained', None)
                print("✅ Session nettoyée")
                
                # Rediriger vers la page pour forcer un nouvel entraînement
                flash('L\'ancien modèle était incompatible. Veuillez réentraîner le modèle avec vos nouvelles données.', 'warning')
                
            except Exception as cleanup_error:
                print(f"❌ Erreur lors du nettoyage: {cleanup_error}")
            
            metrics = None
    
    # Initialiser les variables JSON pour les graphiques
    pred_vs_actual_json = None
    residuals_json = None
    regression_line_json = None
    
    # Rechercher les graphiques dans le dossier temporaire
    temp_dir = os.path.join('data', 'temp_graphs')
    print(f"🔍 Recherche des graphiques dans: {temp_dir}")
    
    if os.path.exists(temp_dir):
        print(f"✅ Dossier temp_graphs trouvé")
        try:
            # Charger le graphique Prédictions vs Réelles
            pred_file = os.path.join(temp_dir, 'pred_vs_actual.json')
            if os.path.exists(pred_file):
                print(f"📁 Fichier pred_vs_actual.json trouvé")
                with open(pred_file, 'r') as f:
                    pred_data = json.load(f)
                    pred_vs_actual_json = pred_data  # ✅ Pas de re-sérialisation
                print(f"✅ Graphique pred_vs_actual chargé avec succès")
            else:
                print(f"❌ Fichier pred_vs_actual.json non trouvé")
            
            # Charger le graphique des Résidus
            residuals_file = os.path.join(temp_dir, 'residuals.json')
            if os.path.exists(residuals_file):
                print(f"📁 Fichier residuals.json trouvé")
                with open(residuals_file, 'r') as f:
                    residuals_data = json.load(f)
                    residuals_json = residuals_data  # ✅ Pas de re-sérialisation
                print(f"✅ Graphique residuals chargé avec succès")
            else:
                print(f"❌ Fichier residuals.json non trouvé")
            
            # Charger le graphique de régression linéaire
            regression_file = os.path.join(temp_dir, 'regression_line.json')
            if os.path.exists(regression_file):
                print(f"📁 Fichier regression_line.json trouvé")
                with open(regression_file, 'r') as f:
                    regression_data = json.load(f)
                    regression_line_json = regression_data  # ✅ Pas de re-sérialisation
                print(f"✅ Graphique regression_line chargé avec succès")
            else:
                print(f"❌ Fichier regression_line.json non trouvé")
                    
        except Exception as e:
            print(f"❌ Erreur lors du chargement des graphiques: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Dossier temp_graphs non trouvé")
    
    print(f"📊 Graphiques chargés: pred={pred_vs_actual_json is not None}, residuals={residuals_json is not None}, regression={regression_line_json is not None}")
    
    # Debug: afficher la taille des données JSON
    if pred_vs_actual_json:
        print(f"📏 Taille pred_vs_actual: {len(pred_vs_actual_json)} caractères")
    if residuals_json:
        print(f"📏 Taille residuals: {len(residuals_json)} caractères")
    if regression_line_json:
        print(f"📏 Taille regression_line: {len(regression_line_json)} caractères")
    
    # Debug: afficher les variables passées au template
    print(f"🔍 Variables passées au template:")
    print(f"  pred_vs_actual_json: {pred_vs_actual_json is not None}")
    print(f"  residuals_json: {residuals_json is not None}")
    print(f"  regression_line_json: {regression_line_json is not None}")
    
    return render_template('model.html', title='Modèle', 
                           form=form, 
                           metrics=metrics,
                           model_exists=model_exists,
                           pred_vs_actual_json=pred_vs_actual_json,
                           residuals_json=residuals_json,
                           regression_line_json=regression_line_json)

@app.route('/predictions', methods=['GET', 'POST'])
@login_required
def predictions():
    form = PredictionForm()
    
    if form.validate_on_submit():
        # Vérifier si un modèle a été entraîné
        model_path = os.path.join('data', 'sales_predictor_model.joblib')
        if not os.path.exists(model_path):
            flash('Aucun modèle entraîné. Veuillez d\'abord entraîner un modèle.', 'warning')
            return redirect(url_for('model'))
        
        # Récupérer les données de la session
        data_json = session.get('data')
        if not data_json:
            flash('Aucune donnée disponible. Veuillez d\'abord charger des données.', 'warning')
            return redirect(url_for('data'))
        
        try:
            data = pd.read_json(data_json, orient='split')
            
            # Charger le modèle
            model = SalesPredictor.load_model(model_path)
            
            # Mois spécifique à prédire
            target_month = form.target_month.data
            
            # Dernier mois dans les données
            last_month = data['mois'].max()
            
            # Créer un DataFrame pour le mois spécifique
            print(f"🔍 Debug - Prédiction pour un mois spécifique:")
            print(f"  Dernier mois historique: {last_month}")
            print(f"  Mois demandé: {target_month}")
            
            # Simplifier : utiliser directement le mois demandé
            future_month = target_month
            
            print(f"  Mois futur calculé: {future_month}")
            
            future_data = pd.DataFrame({'mois': [future_month]})
            
            # Faire des prédictions
            future_predictions = model.predict(future_data[['mois']])
            
            # Créer un DataFrame avec les prédictions
            predictions = pd.DataFrame({
                'mois': [target_month],  # Afficher le mois demandé (1-12)
                'ventes_predites': future_predictions
            })
            
            # Ajouter des colonnes pour l'année et le mois
            # Utiliser directement le mois demandé (1-12)
            month = target_month  # 1-12
            year = 2024  # Année de base
            
            predictions['annee'] = [year]
            predictions['mois_annee'] = [month]
            
            # Afficher les informations de débogage
            print(f"🔍 Debug - Prédictions générées:")
            print(f"  Dernier mois historique: {last_month}")
            print(f"  Mois demandé: {target_month}")
            print(f"  Mois futur calculé: {future_month}")
            print(f"  Année: {year}")
            print(f"  Mois (1-12): {month}")
            print(f"  Prédiction: {list(future_predictions)}")
            
            # Stocker les prédictions dans la session
            session['predictions'] = predictions.to_json(orient='split')
            
            # Créer un graphique avec plotly
            fig = go.Figure()
            
            # Tracer les données historiques
            fig.add_trace(go.Scatter(
                x=data['mois'],
                y=data['ventes'],
                mode='lines+markers',
                name='Ventes historiques',
                line=dict(color='blue', width=3),
                marker=dict(color='blue', size=6)
            ))
            
            # Tracer les prédictions
            fig.add_trace(go.Scatter(
                x=predictions['mois'],
                y=predictions['ventes_predites'],
                mode='lines+markers',
                line=dict(dash='dash', color='red', width=3),
                marker=dict(color='red', size=6),
                name='Prédictions'
            ))
            
            # Ajouter la ligne de tendance (régression linéaire) sur toutes les données
            print(f"🔍 Debug - Types des données:")
            print(f"  data['mois']: {type(data['mois'])} - {data['mois'].dtype}")
            print(f"  predictions['mois']: {type(predictions['mois'])} - {predictions['mois'].dtype}")
            print(f"  data['ventes']: {type(data['ventes'])} - {data['ventes'].dtype}")
            print(f"  predictions['ventes_predites']: {type(predictions['ventes_predites'])} - {predictions['ventes_predites'].dtype}")
            
            # Convertir en numpy arrays avec types cohérents
            months_data = data['mois'].values.astype(float)
            months_pred = predictions['mois'].values.astype(float)
            ventes_data = data['ventes'].values.astype(float)
            ventes_pred = predictions['ventes_predites'].values.astype(float)
            
            all_months = np.concatenate([months_data, months_pred])
            all_ventes = np.concatenate([ventes_data, ventes_pred])
            
            print(f"✅ Concaténation réussie - all_months: {all_months.shape}, all_ventes: {all_ventes.shape}")
            
            # Calculer la régression linéaire
            z = np.polyfit(all_months, all_ventes, 1)
            p = np.poly1d(z)
            trend_line = p(all_months)
            
            fig.add_trace(go.Scatter(
                x=all_months,
                y=trend_line,
                mode='lines',
                line=dict(color='green', width=2, dash='dot'),
                name='Tendance linéaire',
                opacity=0.7
            ))
            
            fig.update_layout(
                title='Prédictions des Ventes Mensuelles avec Tendance',
                xaxis_title='Mois',
                yaxis_title='Ventes',
                legend=dict(y=0.99, x=0.01),
                hovermode='closest',
                showlegend=True
            )
            
            # Stocker le graphique dans la session
            session['forecast_graph'] = fig.to_json()
            
            flash('Prédictions générées avec succès!', 'success')
            return redirect(url_for('predictions'))
            
        except Exception as e:
            flash(f'Erreur lors de la génération des prédictions: {str(e)}', 'danger')
    
    # Récupérer les prédictions et le graphique de la session
    predictions_json = session.get('predictions')
    forecast_graph_json = session.get('forecast_graph')
    
    if predictions_json:
        predictions = pd.read_json(predictions_json, orient='split')
        table_data = predictions.to_dict('records')
        table_columns = [{'id': col, 'name': col} for col in predictions.columns]
    else:
        table_data = None
        table_columns = None
    
    return render_template('predictions.html', title='Prédictions', 
                           form=form, 
                           forecast_graph_json=forecast_graph_json,
                           table_data=table_data,
                           table_columns=table_columns)

# La fonctionnalité de recommandations a été supprimée

# Gestionnaire d'erreurs global
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash('Une erreur interne s\'est produite. Veuillez réessayer.', 'danger')
    return redirect(url_for('index')), 500

@app.errorhandler(404)
def not_found_error(error):
    flash('Page non trouvée.', 'warning')
    return redirect(url_for('index')), 404

@app.errorhandler(Exception)
def handle_exception(e):
    # Log de l'erreur
    print(f"Erreur non gérée: {str(e)}")
    flash('Une erreur inattendue s\'est produite. Veuillez réessayer.', 'danger')
    return redirect(url_for('index')), 500

# Point d'entrée de l'application
if __name__ == '__main__':
    # Créer le dossier data s'il n'existe pas
    os.makedirs('data', exist_ok=True)
    
    # Créer la base de données et l'utilisateur admin par défaut
    with app.app_context():
        db.create_all()
        create_default_admin()
    
    app.run(debug=True, host='0.0.0.0', 
    port=50011)