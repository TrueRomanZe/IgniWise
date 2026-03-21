"""
IgniWise - Entrenamiento del Modelo Random Forest
Entrena el modelo de Machine Learning para predecir ventanas de quema

Input:  data/processed/training_data.csv
Output: models/random_forest_v1.pkl
        models/model_metrics.json
"""

import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

from src.utils.config import (
    DATA_PROCESSED, MODELS_DIR,
    RF_N_ESTIMATORS, RF_MAX_DEPTH, RF_MIN_SAMPLES_SPLIT,
    RF_MIN_SAMPLES_LEAF, RF_MAX_FEATURES, RANDOM_SEED,
    TRAIN_TEST_SPLIT, CV_FOLDS
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__, 'train_model')

# ============================================================================
# FUNCIONES DE ENTRENAMIENTO
# ============================================================================

def load_training_data() -> tuple:
    """
    Carga dataset de entrenamiento y separa features/target
    
    Returns:
        X: Features (DataFrame)
        y: Target (Series)
        feature_names: Nombres de features (list)
    """
    logger.info("Cargando dataset de entrenamiento...")
    
    data_file = DATA_PROCESSED / 'training_data.csv'
    
    if not data_file.exists():
        raise FileNotFoundError(
            f"Dataset no encontrado: {data_file}\n"
            "Ejecuta primero: python src/data_processing/feature_engineering.py"
        )
    
    df = pd.read_csv(data_file)
    
    logger.info(f"  ✓ Cargado dataset: {len(df)} registros")
    
    # Separar features y target
    X = df.drop('ventana', axis=1)
    y = df['ventana']
    
    # Verificar balance de clases
    class_counts = y.value_counts().sort_index()
    logger.info(f"  Distribución de clases:")
    logger.info(f"    SEGURA (0):     {class_counts.get(0, 0):5d} ({class_counts.get(0, 0)/len(y)*100:5.1f}%)")
    logger.info(f"    MARGINAL (1):   {class_counts.get(1, 0):5d} ({class_counts.get(1, 0)/len(y)*100:5.1f}%)")
    logger.info(f"    PELIGROSA (2):  {class_counts.get(2, 0):5d} ({class_counts.get(2, 0)/len(y)*100:5.1f}%)")
    
    return X, y, X.columns.tolist()


def split_data(X: pd.DataFrame, y: pd.Series) -> tuple:
    """
    Divide datos en train/test con estratificación
    
    Args:
        X: Features
        y: Target
        
    Returns:
        X_train, X_test, y_train, y_test
    """
    logger.info(f"Dividiendo datos (train: {(1-TRAIN_TEST_SPLIT)*100:.0f}%, test: {TRAIN_TEST_SPLIT*100:.0f}%)...")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TRAIN_TEST_SPLIT,
        random_state=RANDOM_SEED,
        stratify=y  # Mantener proporciones de clases
    )
    
    logger.info(f"  ✓ Train: {len(X_train)} registros")
    logger.info(f"  ✓ Test:  {len(X_test)} registros")
    
    return X_train, X_test, y_train, y_test


def train_random_forest(X_train: pd.DataFrame, y_train: pd.Series) -> RandomForestClassifier:
    """
    Entrena modelo Random Forest
    
    Args:
        X_train: Features de entrenamiento
        y_train: Target de entrenamiento
        
    Returns:
        Modelo Random Forest entrenado
    """
    logger.info("Entrenando modelo Random Forest...")
    logger.info(f"  Hiperparámetros:")
    logger.info(f"    n_estimators:      {RF_N_ESTIMATORS}")
    logger.info(f"    max_depth:         {RF_MAX_DEPTH}")
    logger.info(f"    min_samples_split: {RF_MIN_SAMPLES_SPLIT}")
    logger.info(f"    min_samples_leaf:  {RF_MIN_SAMPLES_LEAF}")
    logger.info(f"    max_features:      {RF_MAX_FEATURES}")
    logger.info(f"    class_weight:      balanced")
    logger.info(f"    random_state:      {RANDOM_SEED}")
    
    # Crear modelo
    model = RandomForestClassifier(
        n_estimators=RF_N_ESTIMATORS,
        max_depth=RF_MAX_DEPTH,
        min_samples_split=RF_MIN_SAMPLES_SPLIT,
        min_samples_leaf=RF_MIN_SAMPLES_LEAF,
        max_features=RF_MAX_FEATURES,
        class_weight='balanced',  # Importante para clases desbalanceadas
        random_state=RANDOM_SEED,
        n_jobs=-1,  # Usar todos los cores
        verbose=1
    )
    
    # Entrenar
    logger.info("  Entrenando... (esto puede tardar 1-2 minutos)")
    model.fit(X_train, y_train)
    
    logger.info("  ✓ Modelo entrenado exitosamente")
    
    return model


def evaluate_model(model: RandomForestClassifier, 
                   X_test: pd.DataFrame, 
                   y_test: pd.Series) -> dict:
    """
    Evalúa el modelo en test set y calcula métricas
    
    Args:
        model: Modelo entrenado
        X_test: Features de test
        y_test: Target de test
        
    Returns:
        Diccionario con todas las métricas
    """
    logger.info("Evaluando modelo en test set...")
    
    # Predicciones
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Métricas globales
    accuracy = accuracy_score(y_test, y_pred)
    precision_macro = precision_score(y_test, y_pred, average='macro')
    recall_macro = recall_score(y_test, y_pred, average='macro')
    f1_macro = f1_score(y_test, y_pred, average='macro')
    
    # Métricas por clase
    precision_per_class = precision_score(y_test, y_pred, average=None)
    recall_per_class = recall_score(y_test, y_pred, average=None)
    f1_per_class = f1_score(y_test, y_pred, average=None)
    
    # Matriz de confusión
    cm = confusion_matrix(y_test, y_pred)
    
    # Log de métricas
    logger.info("=" * 70)
    logger.info("MÉTRICAS DEL MODELO")
    logger.info("=" * 70)
    logger.info(f"Accuracy global:       {accuracy:.4f} ({accuracy*100:.2f}%)")
    logger.info(f"Precision (macro):     {precision_macro:.4f}")
    logger.info(f"Recall (macro):        {recall_macro:.4f}")
    logger.info(f"F1-Score (macro):      {f1_macro:.4f}")
    logger.info("")
    logger.info("Métricas por clase:")
    logger.info(f"  SEGURA (0):")
    logger.info(f"    Precision: {precision_per_class[0]:.4f} ({precision_per_class[0]*100:.2f}%)")
    logger.info(f"    Recall:    {recall_per_class[0]:.4f} ({recall_per_class[0]*100:.2f}%)")
    logger.info(f"    F1-Score:  {f1_per_class[0]:.4f}")
    logger.info(f"  MARGINAL (1):")
    logger.info(f"    Precision: {precision_per_class[1]:.4f} ({precision_per_class[1]*100:.2f}%)")
    logger.info(f"    Recall:    {recall_per_class[1]:.4f} ({recall_per_class[1]*100:.2f}%)")
    logger.info(f"    F1-Score:  {f1_per_class[1]:.4f}")
    logger.info(f"  PELIGROSA (2):")
    logger.info(f"    Precision: {precision_per_class[2]:.4f} ({precision_per_class[2]*100:.2f}%)")
    logger.info(f"    Recall:    {recall_per_class[2]:.4f} ({recall_per_class[2]*100:.2f}%)")
    logger.info(f"    F1-Score:  {f1_per_class[2]:.4f}")
    logger.info("")
    logger.info("Matriz de confusión:")
    logger.info(f"                 Predicho:")
    logger.info(f"                 SEGURA  MARGINAL  PELIGROSA")
    logger.info(f"  SEGURA      {cm[0][0]:7d}  {cm[0][1]:8d}  {cm[0][2]:9d}")
    logger.info(f"  MARGINAL    {cm[1][0]:7d}  {cm[1][1]:8d}  {cm[1][2]:9d}")
    logger.info(f"  PELIGROSA   {cm[2][0]:7d}  {cm[2][1]:8d}  {cm[2][2]:9d}")
    logger.info("=" * 70)
    
    # Preparar métricas para guardar
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'test_size': len(y_test),
        'accuracy': float(accuracy),
        'precision_macro': float(precision_macro),
        'recall_macro': float(recall_macro),
        'f1_macro': float(f1_macro),
        'precision_per_class': {
            'SEGURA': float(precision_per_class[0]),
            'MARGINAL': float(precision_per_class[1]),
            'PELIGROSA': float(precision_per_class[2])
        },
        'recall_per_class': {
            'SEGURA': float(recall_per_class[0]),
            'MARGINAL': float(recall_per_class[1]),
            'PELIGROSA': float(recall_per_class[2])
        },
        'f1_per_class': {
            'SEGURA': float(f1_per_class[0]),
            'MARGINAL': float(f1_per_class[1]),
            'PELIGROSA': float(f1_per_class[2])
        },
        'confusion_matrix': cm.tolist(),
        'hyperparameters': {
            'n_estimators': RF_N_ESTIMATORS,
            'max_depth': RF_MAX_DEPTH,
            'min_samples_split': RF_MIN_SAMPLES_SPLIT,
            'min_samples_leaf': RF_MIN_SAMPLES_LEAF,
            'max_features': RF_MAX_FEATURES,
            'class_weight': 'balanced',
            'random_state': RANDOM_SEED
        }
    }
    
    return metrics


def cross_validate_model(model: RandomForestClassifier, 
                         X: pd.DataFrame, 
                         y: pd.Series) -> dict:
    """
    Realiza validación cruzada para estimar generalización
    
    Args:
        model: Modelo a validar
        X: Features completas
        y: Target completo
        
    Returns:
        Diccionario con resultados de CV
    """
    logger.info(f"Realizando validación cruzada ({CV_FOLDS}-fold)...")
    
    # Estratificación para mantener proporciones
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    
    # Calcular accuracy en cada fold
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy', n_jobs=-1)
    
    logger.info(f"  ✓ CV Accuracy scores: {cv_scores}")
    logger.info(f"  ✓ Media: {cv_scores.mean():.4f} ({cv_scores.mean()*100:.2f}%)")
    logger.info(f"  ✓ Std:   {cv_scores.std():.4f}")
    
    return {
        'cv_scores': cv_scores.tolist(),
        'cv_mean': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std())
    }


def get_feature_importance(model: RandomForestClassifier, 
                           feature_names: list) -> pd.DataFrame:
    """
    Extrae importancia de features del modelo
    
    Args:
        model: Modelo entrenado
        feature_names: Nombres de features
        
    Returns:
        DataFrame con importancias ordenadas
    """
    logger.info("Calculando importancia de features...")
    
    # Obtener importancias
    importances = model.feature_importances_
    
    # Crear DataFrame
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    logger.info("  Top 10 features más importantes:")
    for idx, row in feature_importance.head(10).iterrows():
        logger.info(f"    {row['feature']:20s}: {row['importance']:.4f}")
    
    return feature_importance


def save_model(model: RandomForestClassifier, 
               metrics: dict, 
               feature_importance: pd.DataFrame):
    """
    Guarda modelo entrenado y métricas
    
    Args:
        model: Modelo a guardar
        metrics: Métricas del modelo
        feature_importance: Importancias de features
    """
    logger.info("Guardando modelo y métricas...")
    
    # Crear carpeta models si no existe
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Guardar modelo
    model_file = MODELS_DIR / 'random_forest_v1.pkl'
    joblib.dump(model, model_file)
    logger.info(f"  ✓ Modelo guardado: {model_file}")
    logger.info(f"    Tamaño: {model_file.stat().st_size / (1024*1024):.1f} MB")
    
    # Guardar métricas
    metrics_file = MODELS_DIR / 'model_metrics.json'
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"  ✓ Métricas guardadas: {metrics_file}")
    
    # Guardar feature importance
    fi_file = MODELS_DIR / 'feature_importance.csv'
    feature_importance.to_csv(fi_file, index=False)
    logger.info(f"  ✓ Feature importance guardada: {fi_file}")


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Pipeline completo de entrenamiento del modelo"""
    
    logger.info("=" * 70)
    logger.info("IgniWise - Entrenamiento del Modelo Random Forest")
    logger.info("=" * 70)
    logger.info(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    # 1. Cargar datos
    X, y, feature_names = load_training_data()
    
    # 2. Dividir train/test
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    # 3. Entrenar modelo
    model = train_random_forest(X_train, y_train)
    
    # 4. Evaluar en test set
    metrics = evaluate_model(model, X_test, y_test)
    
    # 5. Validación cruzada
    cv_results = cross_validate_model(model, X, y)
    metrics['cross_validation'] = cv_results
    
    # 6. Feature importance
    feature_importance = get_feature_importance(model, feature_names)
    
    # 7. Guardar todo
    save_model(model, metrics, feature_importance)
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("✓ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
    logger.info("=" * 70)
    logger.info(f"Modelo final:")
    logger.info(f"  Accuracy:     {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    logger.info(f"  CV Accuracy:  {cv_results['cv_mean']:.4f} ± {cv_results['cv_std']:.4f}")
    logger.info(f"  Precision SEGURA: {metrics['precision_per_class']['SEGURA']:.4f}")
    logger.info("")
    logger.info(f"Archivos generados:")
    logger.info(f"  - models/random_forest_v1.pkl")
    logger.info(f"  - models/model_metrics.json")
    logger.info(f"  - models/feature_importance.csv")
    logger.info("")
    logger.info(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar si el modelo cumple requisitos mínimos
    if metrics['accuracy'] < 0.80:
        logger.warning("⚠️  ADVERTENCIA: Accuracy < 80% - Revisar datos o hiperparámetros")
    if metrics['precision_per_class']['SEGURA'] < 0.85:
        logger.warning("⚠️  ADVERTENCIA: Precision SEGURA < 85% - Crítico para seguridad")
    
    if metrics['accuracy'] >= 0.85 and metrics['precision_per_class']['SEGURA'] >= 0.90:
        logger.info("🎯 ¡EXCELENTE! Modelo cumple objetivos de accuracy y precision")


if __name__ == "__main__":
    main()
