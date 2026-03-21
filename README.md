# 🔥 IgniWise - Sistema de Predicción de Ventanas de Quema Prescrita

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

> **"Smart predictions for safer burns"**

Sistema innovador que utiliza Machine Learning para predecir ventanas temporales seguras para realizar quemas prescritas en España, contribuyendo a la prevención de megaincendios forestales.

🌐 **Web:** [igniwise.com](https://igniwise.com)  
📊 **Dataset:** [DOI:10.5281/zenodo.XXXXXXX](https://doi.org/10.5281/zenodo.19144668)

---

## 🎯 El Problema

Las **quemas prescritas** son esenciales para prevenir megaincendios forestales, eliminando combustible vegetal acumulado. Sin embargo:

- ❌ Solo 20-30 días al año son seguros para ejecutarlas
- ❌ Un error puede convertir una quema controlada en incendio descontrolado
- ❌ La evaluación manual de condiciones es compleja y propensa a errores

**IgniWise automatiza esta evaluación** mediante Machine Learning, proporcionando predicciones basadas en datos históricos y condiciones actuales.

---

## ✨ Características

- 🤖 **Machine Learning:** Random Forest entrenado con 10,000+ incendios históricos
- 🗺️ **Cobertura nacional:** España peninsular completa (50 provincias)
- 📊 **Predicciones actualizadas:** Automáticamente cada 6 horas
- 🎨 **Visualización intuitiva:** Código de colores (🟢 seguro / 🟡 precaución / 🔴 peligroso)
- ⚡ **Totalmente automatizado:** Sin intervención manual
- 🆓 **Gratuito y open source:** Código abierto bajo licencia MIT
- 🎓 **Dataset científico:** Publicado en Zenodo con DOI permanente

---

## 🚀 Quick Start

### Opción A: Usar la Web (Recomendado)

Visita: **[igniwise.com](https://igniwise.com)**

### Opción B: Desarrollo Local

```bash
# Clonar repositorio
git clone https://github.com/[TU-USUARIO]/igniwise.git
cd igniwise

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# Ejecutar predicciones
python src/modeling/predict.py
```

---

## 📊 Fuentes de Datos

- **Incendios históricos:** MITECO (Gobierno de España) - 2001-2024
- **Meteorología:** OpenWeatherMap + AEMET
- **Topografía:** IGN España (MDT 25m)
- **Vegetación:** Copernicus Sentinel-2 (NDVI)

Ver [DATA_SOURCES.md](DATA_SOURCES.md) para licencias completas y atribuciones.

---

## 📁 Estructura del Proyecto

```
igniwise/
├── src/                    # Código fuente Python
│   ├── data_collection/    # Descarga de datos
│   ├── data_processing/    # Procesamiento y features
│   ├── modeling/           # Entrenamiento y predicción
│   └── utils/              # Utilidades
├── web/                    # Frontend (HTML/CSS/JS)
├── data/                   # Datos (raw, processed, predictions)
├── models/                 # Modelos ML entrenados
└── .github/workflows/      # Automatización (GitHub Actions)
```

---

## 🔒 Privacidad

IgniWise respeta tu privacidad. Solo recopilamos estadísticas anónimas agregadas mediante Google Analytics (con anonimización de IP activada).

Ver [PRIVACY.md](PRIVACY.md) para detalles completos.

---

## 📜 Licencia

**Código:** MIT License  
**Datos:** Ver atribuciones en [DATA_SOURCES.md](DATA_SOURCES.md)  
**Dataset:** CC BY 4.0 (Zenodo)

---

## ⚠️ Disclaimer

IgniWise es una herramienta de **apoyo a la decisión**, NO un sistema autónomo. Las quemas prescritas deben ser ejecutadas SOLO por profesionales cualificados y con las autorizaciones pertinentes.

Para alertas oficiales, consulta: [AEMET](https://www.aemet.es)

---

## 📞 Contacto

**Desarrollador:** Sergio Romera Martínez  
**Email:** s.romera92@gmail.com  
**GitHub:** [@TrueRomanZe](https://github.com/TrueRomanZe)  
**Web:** [igniwise.com](https://igniwise.com)

**Issues:** [github.com/TrueRomanZe/igniwise/issues](https://github.com/TrueRomanZe/igniwise/issues)

---

## 🙏 Agradecimientos

- MITECO - Datos de incendios forestales
- OpenWeatherMap & AEMET - Datos meteorológicos
- IGN España - Datos geográficos y topográficos
- Copernicus Programme - Datos satelitales
- CERN & Zenodo - Publicación científica del dataset

---

## 📚 Citación

Si usas IgniWise o su dataset en investigación, por favor cita:

```bibtex
@dataset{romera2026igniwise,
  author       = {Romera Martínez, Sergio},
  title        = {{IgniWise Training Dataset - Spanish Forest 
                   Fires (2001-2024)}},
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.XXXXXXX},
  url          = {https://doi.org/10.5281/zenodo.XXXXXXX}
}
```

---

**🔥 Desarrollado para la prevención de incendios forestales en España**

*Última actualización: Marzo 2026*
