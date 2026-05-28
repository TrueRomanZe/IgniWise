# data/processed/

Carpeta para **datos procesados** listos para ML. Todos los archivos aquí
se almacenan directamente en el repositorio GitHub y se leen desde él en
cada ejecución de GitHub Actions.

---

## Contenido

### training_data.csv

Dataset de entrenamiento del modelo Random Forest.

**Generado por:** `colab_real_features.ipynb` (Google Colab) + `src/data_processing/feature_engineering.py`

**Características:**
- 11.996 registros derivados de ocurrencias históricas de incendios (MITECO / IEPNB, 1983-2015)
- 20 features + variable target `ventana` (0=SEGURA, 1=MARGINAL, 2=PELIGROSA)
- Variables meteorológicas: aproximaciones estadísticas calibradas con climatología provincial española
- Variables geográficas: datos reales por provincia (Copernicus DEM, Sentinel-2, CORINE 2018)

**Features incluidas:**

| Feature | Tipo | Fuente |
|---|---|---|
| temperatura | Meteorológica | Aproximación estadística |
| humedad | Meteorológica | Aproximación estadística |
| viento_velocidad | Meteorológica | Aproximación estadística |
| viento_direccion | Meteorológica | Aproximación estadística |
| precip_24h | Meteorológica | Aproximación estadística |
| dias_sin_lluvia | Meteorológica | Aproximación estadística |
| precip_7d | Meteorológica | Aproximación estadística |
| precip_30d | Meteorológica | Aproximación estadística |
| temp_max_3d | Meteorológica | Aproximación estadística |
| fwi | FWI | Calculado (Van Wagner, 1987) |
| ffmc | FWI | Calculado (Van Wagner, 1987) |
| dmc | FWI | Calculado (Van Wagner, 1987) |
| dc | FWI | Calculado (Van Wagner, 1987) |
| elevacion | Topográfica | Copernicus DEM GLO-30 |
| pendiente | Topográfica | Copernicus DEM GLO-30 |
| orientacion | Topográfica | Copernicus DEM GLO-30 |
| ndvi | Vegetación | Sentinel-2 via Google Earth Engine |
| tipo_bosque | Vegetación | CORINE Land Cover 2018 |
| mes | Temporal | Derivada |
| dia_año | Temporal | Derivada |

---

### provincias_geo.geojson

Geometrías y features reales de las 48 provincias españolas.

**Generado por:** `colab_real_features.ipynb` (Google Colab)

**Fuentes de datos:**
- Geometrías provinciales: IGN España (CNIG)
- Elevación, pendiente, orientación: Copernicus DEM GLO-30 via opentopodata API
- NDVI: Sentinel-2 Level-2A (2023-2024), mediana anual via Google Earth Engine
- Tipo de cobertura forestal: CORINE Land Cover 2018 (Copernicus / CNIG)

**Columnas:**

| Columna | Descripción | Fuente |
|---|---|---|
| nombre | Nombre de la provincia | IGN |
| centroide_lat | Latitud del centroide | IGN |
| centroide_lon | Longitud del centroide | IGN |
| elevacion | Elevación media (m) | Copernicus DEM GLO-30 |
| pendiente | Pendiente media (grados) | Copernicus DEM GLO-30 |
| orientacion | Orientación predominante (grados) | Copernicus DEM GLO-30 |
| ndvi | NDVI mediano anual | Sentinel-2 / GEE |
| tipo_bosque | Cobertura forestal dominante (0-3) | CORINE Land Cover 2018 |
| geometry | Polígono provincial | IGN |

**Codificación tipo_bosque:** 0=Pinar (coníferas), 1=Encinar/frondosas, 2=Matorral, 3=Mixto
