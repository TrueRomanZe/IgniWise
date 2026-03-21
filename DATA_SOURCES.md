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
**Tipo:** Datos meteorológicos en tiempo real y históricos  

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
- Modelo Digital del Terreno (MDT) 25m
- Elevación, pendiente, orientación

**Licencia:** CC BY 4.0 (Creative Commons Atribución)  
**Condiciones:** Uso libre con atribución  
**Atribución requerida:**
```
Datos geográficos: IGN - Instituto Geográfico Nacional de España
© Instituto Geográfico Nacional de España
```

**Términos completos:** https://www.ign.es/web/resources/docs/IGNCnig/LOPD-Aviso-Legal.pdf

### ESRI España

**Fuente:** Living Atlas of the World  
**URL:** https://livingatlas.arcgis.com/  

**Datos utilizados:**
- Límites administrativos (respaldo)
- Capas base de referencia

**Licencia:** Varios (según capa, generalmente uso libre con atribución)  
**Atribución requerida:**
```
Fuente: ESRI España
```

---

## 🛰️ Datos de Vegetación Satelital

### Copernicus Sentinel-2

**Fuente:** Copernicus Open Access Hub  
**URL:** https://scihub.copernicus.eu/  
**Tipo:** Imágenes satelitales multiespectrales  

**Datos utilizados:**
- NDVI (Normalized Difference Vegetation Index)
- Resolución: 10 metros
- Frecuencia: Cada 5 días

**Licencia:** Copernicus Sentinel Data - Acceso completo, abierto y gratuito  
**Condiciones:** Uso libre con atribución  
**Atribución requerida:**
```
Datos satelitales: Copernicus Sentinel-2 imagery
Contains modified Copernicus Sentinel data [Year]
```

**Términos completos:** https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice

### MAPAMA - Mapa Forestal de España

**Fuente:** Ministerio de Agricultura  
**URL:** https://www.mapa.gob.es/  
**Tipo:** Clasificación de tipos de vegetación  

**Datos utilizados:**
- Tipos de bosque (pinar, encinar, matorral, etc.)
- Carga de combustible vegetal estimada

**Licencia:** Datos Abiertos del Gobierno de España  
**Atribución requerida:**
```
Mapa Forestal: MAPAMA - Ministerio de Agricultura, Pesca y Alimentación
```

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
**Referencia:** Van Wagner, C.E. 1987. Development and structure of the Canadian Forest Fire Weather Index System. Forestry Technical Report 35.  

**Licencia:** Dominio público (metodología científica publicada)  
**Atribución recomendada:**
```
Fire Weather Index: Canadian Forest Fire Weather Index System (Van Wagner, 1987)
```

---

## 📋 Resumen de Atribuciones Obligatorias

Cuando uses IgniWise o su dataset, DEBES incluir las siguientes atribuciones:

```
IgniWise - Sistema de Predicción de Ventanas de Quema Prescrita
Copyright © 2026 Sergio Romera Martínez

Fuentes de datos:
- Incendios forestales: MITECO (Gobierno de España)
- Meteorología: OpenWeatherMap y AEMET
- Geografía: IGN España © Instituto Geográfico Nacional
- Vegetación satelital: Copernicus Sentinel-2
- Mapa base: © OpenStreetMap contributors
- Metodología: Canadian FWI System (Van Wagner, 1987)
```

---

## ⚖️ Licencia del Código IgniWise

**Código fuente:** MIT License  
**Dataset (Zenodo):** CC BY 4.0  
**Visualización web:** MIT License  

Ver [LICENSE](LICENSE) para términos completos.

---

## 🔗 Enlaces Útiles

- **Repositorio GitHub:** https://github.com/[TU-USUARIO]/igniwise
- **Dataset Zenodo:** https://doi.org/10.5281/zenodo.XXXXXXX
- **Web oficial:** https://igniwise.com
- **Documentación:** https://github.com/[TU-USUARIO]/igniwise/blob/main/README.md

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

**Última actualización:** Marzo 2026  
**Autor:** Sergio Romera Martínez
