# 📊 IgniWise - Fuentes de Datos y Licencias

Este documento detalla todas las fuentes de datos utilizadas en IgniWise, sus licencias y atribuciones obligatorias.

---

## 🔥 Datos de Incendios Históricos

### MITECO (Ministerio para la Transición Ecológica)

**Fuente:** Estadística General de Incendios Forestales  
**URL:** https://www.miteco.gob.es/es/biodiversidad/estadisticas/  
**Período:** 2001-2024  
**Registros:** ~10,000+ incendios forestales  

**Datos incluidos:**
- Fecha y hora del incendio
- Coordenadas geográficas (lat/lon)
- Superficie afectada (hectáreas)
- Causa del incendio
- Provincia y municipio
- Tipo de vegetación afectada

**Licencia:** Datos Abiertos del Gobierno de España  
**Condiciones de uso:** Uso libre con atribución  
**Atribución requerida:**
```
Datos de incendios forestales: MITECO - Ministerio para la Transición 
Ecológica y el Reto Demográfico del Gobierno de España
```

**Términos completos:** https://www.miteco.gob.es/es/ministerio/avisolegal/default.aspx

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
- Presión atmosférica (hPa)
- Descripción del clima

**Licencia:** ODbL (Open Database License)  
**Plan utilizado:** Free tier (1,000 llamadas/día)  
**Atribución requerida:**
```
Datos meteorológicos: OpenWeatherMap (https://openweathermap.org)
```

**Términos completos:** https://openweathermap.org/terms

### AEMET (Agencia Estatal de Meteorología)

**Fuente:** AEMET OpenData  
**URL:** https://opendata.aemet.es  
**Tipo:** Datos meteorológicos oficiales de España  

**Datos utilizados:**
- Datos históricos meteorológicos
- Predicciones meteorológicas
- Índices climáticos

**Licencia:** CC BY 4.0 (Creative Commons Atribución)  
**Condiciones:** Uso libre con atribución  
**Atribución requerida:**
```
Datos meteorológicos: AEMET - Agencia Estatal de Meteorología
```

**Términos completos:** https://www.aemet.es/es/nota_legal

---

## 🗺️ Datos Geográficos y Topográficos

### IGN España (Instituto Geográfico Nacional)

**Fuente:** Centro de Descargas CNIG  
**URL:** https://centrodedescargas.cnig.es  

**Datos utilizados:**
- Límites administrativos provinciales (shapefile)
- Modelo Digital del Terreno (MDT) 25m — elevación, pendiente, orientación

**Licencia:** CC BY 4.0 (Creative Commons Atribución)  
**Condiciones:** Uso libre con atribución  
**Atribución requerida:**
```
Datos geográficos: IGN - Instituto Geográfico Nacional de España
© Instituto Geográfico Nacional de España
```

**Términos completos:** https://www.ign.es/web/resources/docs/IGNCnig/LOPD-Aviso-Legal.pdf

### Copernicus DEM (Digital Elevation Model)

**Fuente:** Copernicus Land Monitoring Service / ESA  
**URL:** https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model  
**Resolución:** GLO-30 (30 metros)  

**Datos utilizados:**
- Elevación del terreno por provincia
- Pendiente media provincial
- Orientación predominante

**Licencia:** Copernicus DEM — acceso libre con atribución  
**Atribución requerida:**
```
Elevation data: Copernicus DEM GLO-30 © DLR e.V. 2010-2014 
and © Airbus Defence and Space GmbH 2014-2018
```

**Términos completos:** https://spacedata.copernicus.eu/documents/20126/0/CSCDA_ESA_Mission-specific+Annex.pdf

---

## 🛰️ Datos de Vegetación Satelital

### Google Earth Engine + Copernicus Sentinel-2

**Fuente:** Copernicus Sentinel-2 procesado vía Google Earth Engine  
**URL:** https://earthengine.google.com  
**Tipo:** Índice de vegetación calculado a partir de imágenes multiespectrales  

**Datos utilizados:**
- NDVI estacional por provincia (media anual)
- Resolución base: 10 metros (Sentinel-2 Banda 4 y Banda 8)

**Licencia:** Copernicus Sentinel Data — acceso completo, abierto y gratuito  
**Atribución requerida:**
```
Vegetation index: Contains modified Copernicus Sentinel data [2024]
processed via Google Earth Engine
```

**Términos completos:** https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice

### CORINE Land Cover 2018

**Fuente:** Copernicus Land Monitoring Service / Centro Nacional de Información Geográfica (CNIG)  
**URL:** https://centrodedescargas.cnig.es  
**Tipo:** Clasificación de usos y coberturas del suelo  

**Datos utilizados:**
- Tipo de cobertura forestal por provincia (clases 311-324)
- Clasificación: bosque de coníferas, frondosas, mixto, matorral

**Licencia:** Copernicus Land Monitoring Service — uso libre con atribución  
**Atribución requerida:**
```
Land cover: CORINE Land Cover 2018 — Copernicus Land Monitoring Service
```

**Términos completos:** https://land.copernicus.eu/pan-european/corine-land-cover/clc2018

---

## 🗺️ Mapas Base (Visualización Web)

### OpenStreetMap

**Fuente:** OpenStreetMap Contributors  
**URL:** https://www.openstreetmap.org/  
**Tipo:** Mapa base para visualización  

**Licencia:** ODbL (Open Database License)  
**Atribución requerida:**
```
© OpenStreetMap contributors
```

**Términos completos:** https://www.openstreetmap.org/copyright

---

## 📚 Metodología Científica

### Sistema Canadiense FWI (Fire Weather Index)

**Fuente:** Canadian Forest Service  
**Referencia:** Van Wagner, C.E. 1987. Development and structure of the Canadian Forest Fire Weather Index System. Forestry Technical Report 35. Canadian Forestry Service, Ottawa.  
**DOI:** https://cfs.nrcan.gc.ca/publications?id=19927  

**Licencia:** Dominio público (metodología científica publicada)  
**Atribución recomendada:**
```
Fire Weather Index: Canadian Forest Fire Weather Index System
Van Wagner, C.E. (1987). Forestry Technical Report 35, Canadian Forest Service.
```

---

## 📋 Resumen de Atribuciones Obligatorias

Cuando uses IgniWise o su dataset, DEBES incluir las siguientes atribuciones:

```
IgniWise - Sistema de Predicción de Ventanas de Quema Prescrita
Copyright © 2026 Sergio Romera Martínez

Fuentes de datos:
- Incendios forestales: MITECO (Gobierno de España)
- Meteorología en tiempo real: OpenWeatherMap
- Geografía y topografía: IGN España © Instituto Geográfico Nacional
- Modelo de elevación: Copernicus DEM GLO-30
- Índice de vegetación: Copernicus Sentinel-2 vía Google Earth Engine
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

## 🔗 Enlaces Útiles

- **Repositorio GitHub:** https://github.com/TrueRomanZe/igniwise
- **Dataset Zenodo:** https://doi.org/10.5281/zenodo.19144668
- **Web oficial:** https://igniwise.com
- **Documentación:** https://github.com/TrueRomanZe/igniwise/blob/main/README.md

---

## 📞 Contacto para Licencias

Si tienes dudas sobre licencias o permisos:

**Email:** s.romera92@gmail.com  
**GitHub:** [@TrueRomanZe](https://github.com/TrueRomanZe)

---

## ✅ Cumplimiento Legal

IgniWise cumple con todas las licencias de las fuentes de datos utilizadas:
- ✅ Atribuciones completas incluidas
- ✅ Términos de uso respetados
- ✅ Código abierto bajo MIT
- ✅ Dataset científico bajo CC BY 4.0
- ✅ GDPR/LOPD compliance

---

**Última actualización:** Mayo 2026  
**Autor:** Sergio Romera Martínez
