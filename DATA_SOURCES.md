# 📊 IgniWise - Fuentes de Datos y Licencias

Este documento detalla todas las fuentes de datos utilizadas en IgniWise, sus licencias y atribuciones obligatorias.

---

## 🔥 Datos de Incendios Históricos

### MITECO / IEPNB

**Fuente:** Estadística General de Incendios Forestales — Instituto Español para la conservación de la Naturaleza y la Biodiversidad (IEPNB) / Ministerio para la Transición Ecológica (MITECO)
**URL:** https://datos.iepnb.es/datasets/mfe50.tgz
**Período:** 1983-2015
**Registros:** ~287.000 incendios forestales

**Datos incluidos:**
- Identificador único del incendio
- Provincia y municipio (código INE)
- Año del incendio
- Superficie afectada: forestal arbolada, forestal no arbolada, agrícola (hectáreas)
- Geometría de origen del incendio (disponible para incendios posteriores a 2005)

**Uso en IgniWise:**
Los registros de ocurrencia histórica de incendios definen la estructura espacial y temporal del dataset de entrenamiento. Las variables meteorológicas del día de cada incendio **no están disponibles en esta fuente** y fueron aproximadas mediante distribuciones estadísticas calibradas con climatología provincial.

**Licencia:** Datos Abiertos del Gobierno de España
**Atribución requerida:**
```
Datos de incendios forestales: MITECO / IEPNB — Ministerio para la
Transición Ecológica y el Reto Demográfico del Gobierno de España
```

---

## 🌤️ Datos Meteorológicos

### OpenWeatherMap

**Fuente:** OpenWeatherMap API
**URL:** https://openweathermap.org
**Tipo:** Datos meteorológicos en tiempo real

**Datos utilizados:**
- Temperatura actual (°C)
- Humedad relativa (%)
- Velocidad y dirección del viento (km/h, grados)
- Precipitación (mm)
- Descripción del clima

**Uso en IgniWise:** Datos en tiempo real para predicciones operativas (actualización cada 6 horas)

**Licencia:** ODbL (Open Database License)
**Atribución requerida:**
```
Datos meteorológicos: OpenWeatherMap (https://openweathermap.org)
```

---

## 🗺️ Datos Geográficos y Topográficos

### IGN España (Instituto Geográfico Nacional)

**Fuente:** Centro de Descargas CNIG
**URL:** https://centrodedescargas.cnig.es

**Datos utilizados:**
- Límites administrativos provinciales

**Licencia:** CC BY 4.0
**Atribución requerida:**
```
Datos geográficos: IGN - Instituto Geográfico Nacional de España
© Instituto Geográfico Nacional de España
```

### Copernicus DEM (Digital Elevation Model)

**Fuente:** Copernicus Land Monitoring Service / ESA
**URL:** https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model
**Resolución:** GLO-30 (30 metros)

**Datos utilizados:**
- Elevación media provincial (m)
- Pendiente media provincial (grados)
- Orientación predominante (grados)

**Método de extracción:** Muestreo de 5 puntos por provincia (centro + N/S/E/W a 3 km) via opentopodata API; pendiente calculada por diferencias finitas.

**Licencia:** Acceso libre con atribución
**Atribución requerida:**
```
Elevation data: Copernicus DEM GLO-30 © DLR e.V. 2010-2014
and © Airbus Defence and Space GmbH 2014-2018
```

---

## 🛰️ Datos de Vegetación Satelital

### Copernicus Sentinel-2 via Google Earth Engine

**Fuente:** Copernicus Sentinel-2 Level-2A, procesado en Google Earth Engine
**URL:** https://earthengine.google.com
**Período:** 2023-2024 (mediana anual)

**Datos utilizados:**
- NDVI (Normalized Difference Vegetation Index) por provincia
- Resolución base: 10 metros (Bandas B4 y B8 de Sentinel-2)
- Corrección estacional aplicada: Huete et al. (2002); García-Haro et al. (2005)

**Licencia:** Copernicus Sentinel Data — acceso completo, abierto y gratuito
**Atribución requerida:**
```
Vegetation index: Contains modified Copernicus Sentinel data [2023-2024]
processed via Google Earth Engine
```

### CORINE Land Cover 2018

**Fuente:** Copernicus Land Monitoring Service / Centro Nacional de Información Geográfica (CNIG)
**URL:** https://centrodedescargas.cnig.es
**Tipo:** Clasificación de usos y coberturas del suelo

**Datos utilizados:**
- Tipo de cobertura forestal dominante por provincia (clases 311-324)
- Clasificación: bosque de coníferas (0), frondosas (1), matorral (2), mixto (3)
- Calculado por área ponderada de polígonos CORINE dentro de cada provincia

**Licencia:** Copernicus Land Monitoring Service — uso libre con atribución
**Atribución requerida:**
```
Land cover: CORINE Land Cover 2018 — Copernicus Land Monitoring Service
```

---

## 🗺️ Mapas Base (Visualización Web)

### OpenStreetMap

**Fuente:** OpenStreetMap Contributors
**URL:** https://www.openstreetmap.org/
**Licencia:** ODbL (Open Database License)
**Atribución requerida:**
```
© OpenStreetMap contributors
```

---

## 📚 Metodología Científica

### Sistema Canadiense FWI (Fire Weather Index)

**Referencia:** Van Wagner, C.E. 1987. *Development and structure of the Canadian Forest Fire Weather Index System.* Forestry Technical Report 35. Canadian Forestry Service, Ottawa.
**DOI:** https://cfs.nrcan.gc.ca/publications?id=19927

**Licencia:** Dominio público (metodología científica publicada)
**Atribución:**
```
Fire Weather Index: Canadian Forest Fire Weather Index System
Van Wagner, C.E. (1987). Forestry Technical Report 35, Canadian Forest Service.
```

---

## 🔮 Fuentes de Datos para Versiones Futuras

### IEPNB — Incendios Forestales con Geometría (datos.gob.es)

**URL:** https://datos.gob.es (formato TTL/RDF, 1983-2015)
**Potencial uso:** Dataset con geometría detallada de perímetros de incendio, municipio y provincia para +287.000 registros. Combinado con datos históricos meteorológicos de AEMET, podría servir como base para un dataset de entrenamiento con variables meteorológicas reales del día del incendio — actualmente la limitación principal del modelo.

### AEMET OpenData

**URL:** https://opendata.aemet.es
**Potencial uso:** Datos meteorológicos históricos diarios por estación, para reemplazar las aproximaciones estadísticas del dataset de entrenamiento actual por mediciones reales del día de cada incendio.

---

## 📋 Resumen de Atribuciones Obligatorias

```
IgniWise - Sistema de Predicción de Ventanas de Quema Prescrita
Copyright © 2026 Sergio Romera Martínez

Fuentes de datos:
- Incendios históricos: MITECO / IEPNB (Gobierno de España)
- Meteorología en tiempo real: OpenWeatherMap
- Geografía: IGN España © Instituto Geográfico Nacional
- Modelo de elevación: Copernicus DEM GLO-30
- Índice de vegetación: Copernicus Sentinel-2 via Google Earth Engine
- Cobertura del suelo: CORINE Land Cover 2018 (Copernicus / CNIG)
- Mapa base: © OpenStreetMap contributors
- Metodología FWI: Van Wagner, C.E. (1987), Canadian Forest Service
```

---

## ⚖️ Licencia del Código IgniWise

**Código fuente:** MIT License
**Dataset (Zenodo):** CC BY 4.0
**Visualización web:** MIT License

Ver [LICENSE](LICENSE) para términos completos.

---

## 📞 Contacto

**Email:** s.romera92@gmail.com
**GitHub:** [@TrueRomanZe](https://github.com/TrueRomanZe)

---

**Última actualización:** Mayo 2026
**Autor:** Sergio Romera Martínez
