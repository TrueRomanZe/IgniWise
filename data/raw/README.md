# data/raw/

Carpeta para **datos crudos** sin procesar.

Los archivos de datos crudos **no se suben a GitHub** (ver `.gitignore`) por
su tamaño. Se procesan localmente o en Google Colab durante el setup inicial.

---

## Contenido esperado

### incendios_miteco/

Datos históricos de incendios forestales del MITECO / IEPNB (1983-2015).

**Fuente oficial:**
- MITECO — Estadística General de Incendios Forestales
- IEPNB — Instituto Español para la conservación de la Naturaleza y la Biodiversidad
- URL: https://datos.iepnb.es (formato TTL/RDF) o https://www.miteco.gob.es/es/biodiversidad/estadisticas/

**Período disponible:** 1983-2015

**Datos incluidos:**
- Identificador único del incendio
- Provincia y municipio (código INE)
- Año del incendio
- Superficie afectada: forestal arbolada, no arbolada, agrícola (hectáreas)
- Geometría del punto de origen (disponible para incendios posteriores a 2005)

**Nota:** El script `src/data_collection/download_miteco.py` muestra el
proceso de descarga y procesamiento de estos datos. En la práctica, los
datos se generaron en Google Colab usando `colab_real_features.ipynb`.

---

## ⚠️ Importante

Los archivos en esta carpeta **NO se suben a GitHub** porque son grandes
y se generan durante el proceso de setup inicial.

El dataset procesado final (`training_data.csv`) sí está en el repositorio,
en `data/processed/`.
