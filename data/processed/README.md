# data/processed/

Carpeta para **datos procesados** listos para ML.

## Contenido

### training_data.csv
Dataset completo para entrenamiento del modelo Random Forest.

**Generado por:** `src/data_processing/feature_engineering.py`

**Características:**
- 20 features meteorológicas, topográficas y temporales
- Variable target: `ventana` (0=SEGURA, 1=MARGINAL, 2=PELIGROSA)
- ~10,000 registros
- Tamaño: ~2-3 MB

---

### provincias_geo.geojson
Geometrías y centroides de 48 provincias españolas.

**Generado por:** `src/data_collection/download_geodata.py`

**Fuente:** IGN / ESRI Living Atlas

---

## ⚠️ Importante

Estos archivos se descargan **desde Zenodo** en GitHub Actions.

**NO** se almacenan en GitHub (ver `.gitignore`).

**DOI del dataset:** 10.5281/zenodo.XXXXXXX (actualizar tras publicar en Zenodo)
