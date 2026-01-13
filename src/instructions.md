# instructions.md

## 1) Objetivo del código (reglas de diseño)

Este repositorio implementa un **Nodo Edge NAIRA** capaz de:

* adquirir datos de sensores (principalmente **RS485/Modbus RTU**),
* procesar y calcular indicadores localmente,
* detectar eventos/anomalías,
* controlar actuadores (p. ej. riego),
* publicar datos vía **MQTT** y/o **HTTP**,
* operar en **modo offline** con buffer y reenvío.  

**Prioridades no negociables:**

1. Robustez (no caerse por fallos de red/sensores).
2. Trazabilidad (logs + timestamps coherentes).
3. Modularidad (cada componente aislado y testeable).
4. Simulación (todo debe poder correr sin hardware real).

---

## 2) Estructura del repo y dónde añadir código

Respetar la estructura (no mezclar responsabilidades): 

* `src/main.py`: orquestación (loop principal, scheduling).
* `src/config.py`: carga/validación de configuración.
* `src/acquisition/`: lectura de sensores (reales y simulados).
* `src/processing/`: filtros, agregaciones, indicadores.
* `src/models/`: inferencia TinyML/ONNX (si aplica).
* `src/comms/`: MQTT/HTTP, colas offline, reintentos.
* `src/control/`: lógica de actuadores, reglas, seguridad.
* `src/diagnostics/`: salud del nodo (temp CPU, batería, etc.).
* `tools/`: scripts auxiliares (simulación, generación de datos).
* `exercises/` y `notebooks/`: material docente, no “producción”.

**Regla:** si un cambio toca más de 2 carpetas, probablemente falta una abstracción.

---

## 3) Convenciones de código

* **Python 3.11+** (tipado y dataclasses).
* Estilo: funciones pequeñas, nombres descriptivos, sin “magia”.
* Tipado obligatorio en APIs públicas (`def fn(x: int) -> str:`).
* Manejo de errores: nunca `except: pass`. Siempre log + fallback.
* No hardcodear credenciales/URLs/puertos: todo en `config`.

---

## 4) Contratos de datos (formato estándar)

Todo dato que salga de `acquisition/` debe normalizarse a:

```python
{
  "ts": "ISO8601 UTC o local consistente",
  "node_id": "string",
  "source": "meteo|suelo|riego|diagnostics|...",
  "metric": "humedad_suelo|temp_aire|caudal|...",
  "value": 12.34,
  "unit": "%|C|l_min|...",
  "quality": "ok|suspect|bad",
  "meta": {...}
}
```

**Reglas:**

* `ts` siempre presente.
* `unit` siempre presente (aunque sea `"raw"`).
* `quality` se rellena con heurísticas simples (rangos/NaN/outlier).
* El “shape” no cambia entre modo real y simulado.

---

## 5) Sensores: implementación mínima esperada

En esta edición, el hardware base usa **RS485 (Modbus RTU)** para estación meteo, suelo y riego. 

Cada sensor/familia debe exponer:

* `read()` → devuelve una lista de medidas normalizadas (contrato anterior).
* `health()` → diagnóstico básico (última lectura, latencia, errores).
* modo simulado (flag `SIMULATION=True` o driver alternativo).

No incluir sensores “nivel avanzado” (cámara/hiperespectral) salvo stubs. 

---

## 6) Procesamiento e indicadores (processing/)

Implementar procesamiento como **pipeline puro**:

* entradas: lista de medidas (dicts)
* salidas: lista de medidas derivadas + flags/eventos
* sin IO de red, sin dependencias MQTT/HTTP aquí

Incluye:

* filtros (media móvil, eliminación outliers),
* agregaciones (ventanas 1–5 min),
* indicadores (balance hídrico básico, alertas por umbrales, etc.). 

---

## 7) Comunicaciones (comms/) y modo offline

### MQTT

* Publicar métricas periódicas por tópico (separar por `source/metric`).
* Alertas/eventos en un tópico específico (no mezclar con telemetría).

### HTTP

* Usar POST para payloads grandes (p. ej. imágenes, si existieran stubs).

### Offline-first

* Si falla la red: encolar payloads localmente.
* Reintentos con backoff.
* Reenvío por lotes cuando vuelve la conectividad. 

---

## 8) Control y seguridad (control/)

Las reglas de control (riego, relés, etc.) deben:

* tener **interlocks** (mínimos y máximos; cooldown; “fail-safe off”),
* registrar cada decisión (motivo + variables usadas),
* poder ejecutarse en “dry-run” (sin actuar, solo log). 

---

## 9) Diagnóstico del nodo (diagnostics/)

Debe incluir (mínimo): temperatura interna/CPU y estado básico del sistema. 
Entregar métricas también con el contrato estándar (source=`diagnostics`).

---

## 10) Logging y observabilidad

* Logger único por módulo (`logging.getLogger(__name__)`).
* Niveles: `INFO` para operación, `WARNING` para degradación, `ERROR` para fallo.
* Incluir `node_id`, `module`, y contexto mínimo del error.
* Evitar logs “ruidosos” en loops rápidos (agrupar / rate limit).

---

## 11) Pruebas y simulación

* Cada driver de sensor debe tener un “simulator” equivalente.
* Añadir tests unitarios a funciones puras (processing, parsers, reglas).
* Incluir un script en `tools/` para ejecutar el nodo en modo simulado end-to-end.

---

## 12) Checklist antes de abrir PR / entregar código

* [ ] Corre en Raspberry Pi **y** en portátil (modo simulado).
* [ ] No hay credenciales hardcodeadas.
* [ ] No rompe el contrato de datos.
* [ ] Maneja pérdida de red (cola offline).
* [ ] Logs claros (sin spam).
* [ ] Código modular (acquisition/processing/comms/control separados).
* [ ] Documentado: cómo ejecutar y variables de config.
