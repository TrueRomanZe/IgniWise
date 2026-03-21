# data/predictions/

Carpeta para **predicciones actuales** generadas cada 6 horas.

## Contenido

### current_windows.json
Predicciones de ventanas de quema para todas las provincias.

**Generado por:** `src/modeling/predict.py`

**Actualización:** Cada 6 horas vía GitHub Actions

**Estructura:**
```json
{
  "metadata": {
    "timestamp": "2026-03-20T14:30:00",
    "fecha_actualizacion": "20/03/2026 14:30",
    "total_provincias": 48
  },
  "provincias": [
    {
      "provincia": "Madrid",
      "prediccion": {
        "ventana": "SEGURA",
        "color": "#10b981",
        "confianza": 87.5
      },
      "clima": { ... },
      "indices": { ... }
    }
  ]
}
```

---

## ✅ Este archivo SÍ se sube a GitHub

Es el único archivo de `data/` que se versiona en Git.

Actualizado automáticamente por GitHub Actions cada 6 horas.
