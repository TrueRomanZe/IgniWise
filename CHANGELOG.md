# Changelog

Todos los cambios notables en este proyecto están documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

---

## [0.3.0] - Mayo 2026

### Añadido
- **Notebook Google Colab (`colab_real_features.ipynb`):** Pipeline completo para extraer features geográficas reales para las 48 provincias desde fuentes Copernicus, sin necesidad de infraestructura local.
- **Copernicus DEM GLO-30:** Elevación, pendiente y orientación medias provinciales calculadas mediante muestreo de 5 puntos por provincia y diferencias finitas. Fuente: opentopodata API (SRTM 90m).
- **NDVI real (Sentinel-2 / Google Earth Engine):** Mediana anual del Índice de Vegetación de Diferencia Normalizada para 2023-2024, con corrección estacional basada en Huete et al. (2002) y García-Haro et al. (2005).
- **CORINE Land Cover 2018:** Tipo de cobertura forestal dominante por provincia (coníferas, frondosas, matorral, mixto) calculado por área ponderada. Fuente: Copernicus Land Monitoring Service / CNIG.
- **Google Analytics 4:** Analítica web integrada con configuración de máxima privacidad (anonimización de IP, Google Signals desactivado, personalización de anuncios desactivada, retención de datos 60 días).
- **`CHANGELOG.md`:** Este documento de historial de cambios.

### Mejorado
- **`feature_engineering.py` (v2):** Las funciones `add_topographic_features` y `add_vegetation_features` leen datos reales desde `provincias_geo.geojson` en lugar de generar valores aleatorios. Incluye corrección estacional del NDVI y valores por defecto documentados con justificación científica.
- **`provincias_geo.geojson`:** Enriquecido con cinco nuevas columnas reales por provincia: `pendiente`, `orientacion`, `ndvi`, `tipo_bosque`, más `elevacion` actualizada desde DEM.
- **`update-predictions.yml`:** Simplificado — modelo y geodata se leen del repositorio directamente, eliminando descargas de Zenodo en cada ejecución (reduces latencia y dependencias externas).
- **`initial-setup.yml`:** Simplificado con el mismo criterio; incluye verificación explícita de archivos antes de ejecutar predicciones.
- **`README.md`:** Reescrito para reflejar fuentes de datos reales, metodología FWI honesta y descripción correcta del modelo.
- **`DATA_SOURCES.md`:** Añadidas secciones para Copernicus DEM GLO-30, Google Earth Engine / Sentinel-2 y CORINE Land Cover 2018 con licencias y atribuciones completas.
- **`PRIVACY.md`:** Actualizado con detalles de la configuración exacta de Google Analytics 4 y opciones de opt-out para el usuario.
- **Footer de la web:** Eliminada la cifra de accuracy descontextualizada; añadidas referencias a fuentes de datos reales (Copernicus DEM, CORINE, Sentinel-2).

### Corregido
- **Placeholders en documentación:** Eliminadas todas las referencias `[TU-USUARIO]` y DOI `XXXXXXX`, sustituidas por URLs y DOI reales.
- **Filtrado CORINE por CRS:** Corregido error de bbox en coordenadas WGS84 al cargar archivo en EPSG:25830 — se transforma la bbox antes del filtrado espacial.

---

## [0.2.0] - Marzo 2026

### Añadido
- **Dominio personalizado:** Aplicación desplegada en [igniwise.com](https://igniwise.com) via GitHub Pages con CNAME.
- **Dataset en Zenodo:** Publicación científica del dataset de entrenamiento con DOI permanente [10.5281/zenodo.19144668](https://doi.org/10.5281/zenodo.19144668).
- **`DATA_SOURCES.md`:** Documento de fuentes de datos y atribuciones obligatorias.
- **`PRIVACY.md`:** Política de privacidad completa conforme a RGPD y LOPD.
- **Sistema FWI completo:** Cálculo de los cuatro subcomponentes canadienses (FFMC, DMC, DC, FWI) integrado en las predicciones.
- **Panel de información detallada:** Al hacer clic en una provincia se muestran condiciones meteorológicas actuales, índices FWI y recomendación textual.

### Mejorado
- **Automatización GitHub Actions:** Predicciones actualizadas cada 6 horas sin intervención manual.
- **Visualización del mapa:** Marcadores con código de color (verde/naranja/rojo) posicionados en el centroide de cada provincia.

---

## [0.1.0] - Enero 2026

### Añadido
- Lanzamiento inicial de IgniWise.
- Mapa interactivo con Leaflet.js mostrando predicciones para 48 provincias españolas.
- Modelo Random Forest entrenado con datos históricos de incendios MITECO (2001-2024).
- Pipeline de datos con GitHub Actions: descarga de datos meteorológicos → cálculo FWI → predicción → actualización web.
- Clasificación tricolor de ventanas de quema: SEGURA / MARGINAL / PELIGROSA.
- Integración OpenWeatherMap para datos meteorológicos en tiempo real.
- Diseño responsive adaptado a dispositivos móviles y escritorio.
- Licencia MIT y código abierto en GitHub.

---

## Convenciones

- **Añadido:** Nuevas funcionalidades
- **Mejorado:** Cambios en funcionalidades existentes o mejoras de rendimiento
- **Corregido:** Corrección de errores
- **Eliminado:** Funcionalidades eliminadas
- **Seguridad:** Correcciones de seguridad
