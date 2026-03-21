# models/

Carpeta para **modelos ML entrenados**.

## Contenido

### random_forest_v1.pkl
Modelo Random Forest entrenado (clasificación multiclase).

**Generado por:** `src/modeling/train_model.py` en Google Colab

**Características:**
- Algoritmo: Random Forest Classifier (scikit-learn)
- Hiperparámetros:
  - n_estimators: 200
  - max_depth: 15
  - class_weight: balanced
- Accuracy: ~87%
- Precision SEGURA: ~92%
- Tamaño: ~100 MB

---

### model_metrics.json
Métricas de evaluación del modelo.

**Contenido:**
```json
{
  "accuracy": 0.87,
  "precision_per_class": {
    "SEGURA": 0.92,
    "MARGINAL": 0.84,
    "PELIGROSA": 0.86
  },
  "confusion_matrix": [...],
  "hyperparameters": {...}
}
```

---

### feature_importance.csv
Importancia de cada feature en el modelo.

---

## 🔄 Actualización del Modelo

El modelo se re-entrena **manualmente** cada 6-12 meses en Google Colab.

Tras reentrenar:
1. Subir nuevo `random_forest_v1.pkl` a Zenodo (sobrescribir versión anterior)
2. Actualizar métricas en `model_metrics.json`
3. Commit de métricas a GitHub

**⚠️ El modelo .pkl NO se versiona en Git** (demasiado grande, 100MB).

Se descarga desde Zenodo en cada ejecución de GitHub Actions.
