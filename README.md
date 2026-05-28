# 🔥 IgniWise - Sistema de Predicción de Ventanas de Quema Prescrita

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19144668.svg)](https://doi.org/10.5281/zenodo.19144668)

> **"Smart predictions for safer burns"**

Sistema que combina Machine Learning con el Sistema Canadiense FWI para predecir ventanas temporales seguras para realizar quemas prescritas en España, contribuyendo a la prevención de megaincendios forestales.

🌐 **Web:** [igniwise.com](https://igniwise.com)  
📊 **Dataset:** [DOI:10.5281/zenodo.19144668](https://doi.org/10.5281/zenodo.19144668)

---

## 🎯 El Problema

Las **quemas prescritas** son esenciales para prevenir megaincendios forestales, eliminando combustible vegetal acumulado. Sin embargo:

- ❌ Solo 20-30 días al año son seguros para ejecutarlas
- ❌ Un error puede convertir una quema controlada en incendio descontrolado
- ❌ La evaluación manual de condiciones es compleja y propensa a errores

**IgniWise automatiza esta evaluación** combinando índices meteorológicos validados científicamente con datos topográficos y de vegetación reales por provincia.

---

## ✨ Características

- 🤖 **Machine Learning:** Random Forest calibrado con datos históricos de incendios (MITECO, 2001-2024)
- 🔥 **FWI integrado:** Sistema Canadiense de Índice de Peligro de Incendio (Van Wagner, 1987), estándar internacional con más de 40 años de validación
- 🗺️ **Cobertura nacional:** 48 provincias de España peninsular
- 🛰️ **Datos reales:** Topografía (Copernicus DEM GLO-30), NDVI (Sentinel-2 / GEE), cobertura forestal (CORINE Land Cover 2018)
- 📊 **Predicciones actualizadas:** Automáticamente cada 6 horas
- 🎨 **Visualización intuitiva:** Código de colores (🟢 seguro / 🟡 precaución / 🔴 peligroso)
- ⚡ **Totalmente automatizado:** Sin intervención manual
- 🆓 **Gratuito y open source:** Código abierto bajo licencia MIT

---

## 🚀 Quick Start

### Opción A: Usar la Web (Recomendado)

Visita: **[igniwise.com](https://igniwise.com)**

### Opción B: Desarrollo Local

```bash
# Clonar repositorio
git clone https://github.com/TrueRomanZe/igniwise.git
cd igniwise

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu OPENWEATHER_API_KEY

# Ejecutar predicciones
python src/modeling/predict.py
```

---

## 📊 Fuentes de Datos

| Dato | Fuente | Uso |
|---|---|---|
| Incendios históricos | MITECO (2001-2024) | Entrenamiento del modelo |
| Meteorología en tiempo real | OpenWeatherMap API | Predicción diaria |
| Elevación, pendiente, orientación | Copernicus DEM GLO-30 | Features provinciales |
| NDVI (índice de vegetación) | Sentinel-2 via Google Earth Engine | Features provinciales |
| Cobertura forestal | CORINE Land Cover 2018 (Copernicus / CNIG) | Features provinciales |
| Metodología FWI | Van Wagner, C.E. (1987), Canadian Forest Service | Índices de peligro |

Ver [DATA_SOURCES.md](DATA_SOURCES.md) para licencias completas y atribuciones.

---

## 🧠 Metodología del Modelo

### Sistema de clasificación

IgniWise clasifica cada provincia en tres categorías:

- 🟢 **SEGURA:** Condiciones óptimas para ejecutar quemas prescritas
- 🟡 **MARGINAL:** Condiciones aceptables con precauciones adicionales
- 🔴 **PELIGROSA:** Condiciones adversas, no recomendado

### Variables utilizadas

**Meteorológicas (dinámicas, actualizadas cada 6h):**
temperatura, humedad relativa, velocidad y dirección del viento, precipitación acumulada, días sin lluvia, índices FWI/FFMC/DMC/DC

**Geográficas (estáticas, reales por provincia):**
elevación media, pendiente media, orientación predominante, NDVI estacional, tipo de cobertura forestal dominante (CORINE 2018)

### Índice FWI

El Fire Weather Index (FWI) es el componente central de la predicción. Desarrollado por el Canadian Forest Service (Van Wagner, 1987), integra temperatura, humedad, viento y precipitación en un índice de peligro de incendio validado internacionalmente. IgniWise calcula los cuatro subcomponentes: FFMC (Fine Fuel Moisture Code), DMC (Duff Moisture Code), DC (Drought Code) y el FWI final.

**Referencia:** Van Wagner, C.E. (1987). *Development and structure of the Canadian Forest Fire Weather Index System.* Forestry Technical Report 35. Canadian Forest Service, Ottawa.

### Nota sobre el modelo Random Forest

El modelo Random Forest fue entrenado con registros históricos de incendios del MITECO complementados con variables geográficas reales extraídas de fuentes Copernicus. Las variables meteorológicas del conjunto de entrenamiento son aproximaciones estadísticas basadas en climatología provincial; en predicción, se usan datos reales en tiempo real de OpenWeatherMap. **Para decisiones operativas, el FWI siempre debe consultarse junto a las alertas oficiales de AEMET.**

---

## 📁 Estructura del Proyecto

```
igniwise/
├── .github/workflows/
│   ├── initial-setup.yml       # Ejecución manual única para primera predicción
│   └── update-predictions.yml  # Actualización automática cada 6 horas
├── css/styles.css
├── data/
│   ├── processed/
│   │   ├── provincias_geo.geojson   # Geometrías + features reales por provincia
│   │   └── training_data.csv        # Dataset de entrenamiento
│   └── predictions/
│       └── current_windows.json     # Predicciones actuales (generado automáticamente)
├── js/app.js
├── models/
│   └── random_forest_v1.pkl         # Modelo entrenado
├── src/
│   ├── data_processing/
│   │   ├── feature_engineering.py   # Pipeline de features (v2: datos reales)
│   │   └── calculate_fwi.py
│   ├── modeling/
│   │   ├── train_model.py
│   │   └── predict.py
│   └── utils/
├── colab_real_features.ipynb    # Notebook para extraer features reales (Google Colab)
├── DATA_SOURCES.md
├── LICENSE
├── PRIVACY.md
├── README.md
├── CHANGELOG.md
├── index.html
└── requirements.txt
```

---

## ⚙️ Automatización (GitHub Actions)

Las predicciones se actualizan automáticamente cada 6 horas mediante GitHub Actions:

1. Descarga datos meteorológicos actuales de OpenWeatherMap para las 48 provincias
2. Calcula índices FWI para cada provincia
3. Ejecuta el modelo Random Forest
4. Actualiza `data/predictions/current_windows.json`
5. La web carga el JSON actualizado automáticamente

El modelo y los datos geográficos se leen directamente del repositorio, sin necesidad de descargas externas en cada ejecución.

---

## 🔒 Privacidad y Analítica

Utilizamos Google Analytics 4 configurado con las máximas restricciones de privacidad: anonimización de IP activada, Google Signals desactivado, personalización de anuncios desactivada. Solo estadísticas agregadas y anónimas.

Ver [PRIVACY.md](PRIVACY.md) para detalles completos.

---

## 📜 Licencia

**Código:** MIT License  
**Dataset:** CC BY 4.0 (Zenodo — citar con DOI)  
**Datos de terceros:** Ver atribuciones en [DATA_SOURCES.md](DATA_SOURCES.md)

---

## ⚠️ Disclaimer

IgniWise es una herramienta de **apoyo a la decisión**, NO un sistema autónomo de autorización. Las quemas prescritas deben ser ejecutadas SOLO por profesionales cualificados con las autorizaciones administrativas pertinentes.

Para alertas meteorológicas oficiales: [AEMET](https://www.aemet.es)

---

## 📞 Contacto

**Desarrollador:** Sergio Romera Martínez  
**Email:** s.romera92@gmail.com  
**GitHub:** [@TrueRomanZe](https://github.com/TrueRomanZe)  
**Web:** [igniwise.com](https://igniwise.com)

---

## 📚 Citación

Si usas IgniWise o su dataset en investigación:

```bibtex
@dataset{romera2026igniwise,
  author       = {Romera Martínez, Sergio},
  title        = {{IgniWise Training Dataset - Spanish Forest 
                   Fires (2001-2024)}},
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.19144668},
  url          = {https://doi.org/10.5281/zenodo.19144668}
}
```

---

## 🙏 Agradecimientos

- MITECO — Estadística General de Incendios Forestales
- OpenWeatherMap — Datos meteorológicos en tiempo real
- Copernicus Programme (ESA) — DEM GLO-30, Sentinel-2, CORINE Land Cover 2018
- Canadian Forest Service — Sistema FWI (Van Wagner, 1987)
- CERN & Zenodo — Publicación científica del dataset

---

**🔥 Desarrollado para la prevención de incendios forestales en España**

*Última actualización: Mayo 2026*
