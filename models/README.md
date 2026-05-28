# models/

Carpeta para **modelos ML entrenados**.

El modelo se almacena directamente en el repositorio GitHub y se lee desde
él en cada ejecución de GitHub Actions. No se usan servicios externos para
servir el modelo en producción.

---

## Contenido

### random_forest_v1.pkl

Modelo Random Forest entrenado para clasificación de ventanas de quema prescrita.

**Generado por:** `colab_real_features.ipynb` (Google Colab) — Paso 8

**Algoritmo:** Random Forest Classifier (scikit-learn)

**Hiperparámetros:**

| Parámetro | Valor |
|---|---|
| n_estimators | 200 |
| max_depth | 15 |
| min_samples_split | 20 |
| min_samples_leaf | 10 |
| max_features | sqrt |
| class_weight | balanced |
| random_state | 42 |

**Métricas de validación:**

| Métrica | Valor |
|---|---|
| CV Accuracy (5-fold) | 99.5% ± 0.2% |
| Accuracy test set | 99.5% |
| Precision SEGURA | 100% |
| Precision MARGINAL | 99% |
| Precision PELIGROSA | 99% |

**Nota sobre el accuracy:** El 99.5% refleja que el modelo aprende correctamente
los umbrales de clasificación FWI definidos en el pipeline. La validez operativa
real solo puede evaluarse con datos de campo de quemas prescritas ejecutadas.
Ver sección metodológica del [README principal](../README.md) para más detalle.

**Features utilizadas (20):**
meteorológicas (9) + FWI/subíndices (4) + topográficas reales (3) + vegetación real (2) + temporales (2)

**Tamaño aproximado:** 50-150 MB

---

## 🔄 Actualización del Modelo

El modelo se re-entrena **manualmente** ejecutando `colab_real_features.ipynb`
en Google Colab cuando se dispone de nuevos datos o se quiere mejorar el pipeline.

Tras reentrenar:
1. Descargar `random_forest_v1.pkl` desde Google Drive
2. Subir directamente a GitHub en `models/random_forest_v1.pkl` (reemplazar)
3. Actualizar este README con las nuevas métricas si cambian significativamente
4. Ejecutar manualmente el workflow "Initial Setup" en GitHub Actions para
   verificar que las predicciones se generan correctamente con el nuevo modelo
