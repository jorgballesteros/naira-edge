# Guion docente — Módulo 1 Introducción al Edge Computing

Duración estimada: **3 horas**

---

## 1. Apertura (10 min)
- Presentación breve del módulo.
- Pregunta inicial al grupo:  
  “¿Qué pasa hoy en vuestro centro/empresa cuando un sensor deja de tener internet?”
- Explicar el concepto general de Edge Computing con ejemplos cotidianos.

---

## 2. Qué es el Edge Computing (25 min)
- Definición formal + explicaciones de IBM y Microsoft.
- Ejemplos de edge en agricultura, industria y energía.
- Ventajas clave: latencia, coste, autonomía, seguridad.
- Comparación cloud vs edge (centrarse en latencia y dependencia de red).

**Apoyo visual:**  
Slide de “sensor → nube → acción” vs “sensor → edge → acción”.

---

## 3. Agricultura como caso ideal para el Edge (35 min)
- Flujos de datos reales: humedad, tensiómetros, meteo, imágenes, multiespectral.
- Problemas habituales: mala cobertura, microcortes, enlaces 4G caros.
- Por qué el cloud puro falla en agricultura.
- Introducir la idea: **“Procesar donde se genera”**.

**Demostración recomendada:**  
Mostrar valores de un sensor en tiempo real (simulación Python o dashboard).

---

## 4. IA ligera en el borde (30 min)
- Explicar la diferencia entre:
  - IA local (rápida, limitada, orientada a eventos)
  - IA cloud (profunda, pesada, predictiva)
- Presentar ejemplos:  
  - balance hídrico,  
  - riesgo de enfermedades,  
  - anomalías en caudal,  
  - detección simple basada en reglas.

**Punto clave:**  
Enfatizar que IA ligera “no reemplaza” al servidor, lo complementa.

---

## 5. Modelo híbrido (Edge + Cloud) (30 min)
- Cómo repartimos tareas:
  - edge → decisiones rápidas,  
  - cloud → predición, análisis profundo, historización.
- Ventajas del modelo NAIRA aplicado a FP y agricultura.

---

## 6. Arquitectura NAIRA (40 min)
- Explicación de cada capa:
  - Edge: sensores, filtrado, IA ligera, actuadores.
  - Cloud: MQTT, API, DB, dashboards.
  - IA híbrida: coordinación Edge ↔ Cloud.
- Revisión guiada del diagrama (Mermaid).
- Destacar puntos de fallo típicos y cómo NAIRA los mitiga.

**Preguntas-guía:**
- ¿Qué ocurre si se corta la red?
- ¿Qué datos son “útiles” para enviar a la nube?
- ¿Cuándo debe actuar el nodo sin esperar?

---

## 7. Cierre + preparación para Módulo 2 (10 min)
- Relacionar este módulo con lo que viene:
  - En M2 empezamos a trabajar con **APIs, datos reales y extracción automática**.
- Pregunta final para reflexión:
  “Si tuvieras solo 1 sensor funcionando en un cultivo durante 2 semanas sin internet, ¿qué decisiones dejarías al edge?”

