# Módulo 4 · Guion docente

## Enfoque general
Este módulo es **teórico-práctico equilibrado**.  
La teoría debe ser **suficiente** para que el alumnado entienda los fundamentos estadísticos, pero la práctica debe ocupar el **70% del tiempo**.

El objetivo es que el alumnado implemente detectores funcionales, los integre con datos reales y visualice resultados de forma profesional.

---

## Sesión 1 (3 h) — Fundamentos y primeros detectores

### 1. Introducción y contexto (20 min)
- ¿Qué es una anomalía?
  - Sensor falla
  - Valor extremo pero válido
  - Patrón inusual
- ¿Por qué detectarlas en tiempo real?
  - Alertas tempranas
  - Ahorro de recursos
  - Prevención de fallos
- Ejemplos en agricultura y energía

### 2. Teoría esencial (40 min)
- Series temporales:
  - timestamps ordenados
  - ventanas móviles
- Z-score:
  - fórmula: `(x - μ) / σ`
  - interpretación: cuántas desviaciones estándar se aleja un valor
- MAD (Median Absolute Deviation):
  - más robusto que z-score ante outliers extremos
  - fórmula: `MAD = median(|x - median(x)|)`
  - conversión a escala comparable con σ: `MAD * 1.4826`

👉 Usar ejemplos visuales (gráficos con anomalías marcadas).

### 3. Ejercicio práctico 1 (60 min)
- Implementar `RollingAnomalyDetector` (z-score)
  - ventana deslizante con `deque`
  - cálculo de media y desviación estándar
  - umbral configurable (ej: 2.5 o 3.0)
- Probar con datos simulados
- Identificar anomalías sintéticas

Acompañar paso a paso, explicar cada decisión de diseño.

### 4. Ejercicio práctico 2 (40 min)
- Implementar `RollingMadAnomalyDetector` (MAD)
- Comparar resultados MAD vs z-score con un dataset con outliers extremos
- Discutir cuándo usar cada método

---

## Sesión 2 (3 h) — Integración con InfluxDB y visualización

### 1. Repaso guiado (20 min)
- Revisar código de la sesión anterior
- Resolver dudas conceptuales
- Analizar errores comunes

### 2. Teoría: InfluxDB y Flux (30 min)
- ¿Qué es InfluxDB?
  - base de datos optimizada para series temporales
- Conceptos: bucket, measurement, tags, fields
- Consultas Flux básicas:
  - `range(start: -24h)`
  - filtros por métrica y nodo
- Pipeline: adquisición → InfluxDB → lectura → detección

### 3. Ejercicio práctico 1 (60 min)
- Crear script CLI `influx_anomaly.py`
  - consultar últimas N horas de una métrica
  - ejecutar detector z-score o MAD
  - listar anomalías detectadas
- Probar con datos reales del nodo
- Ajustar umbrales y ventanas

### 4. Ejercicio práctico 2 (50 min)
- Dashboard Streamlit `anomaly_dashboard.py`
  - input: métrica, bucket, ventana temporal
  - visualización: serie temporal + anomalías marcadas
  - controles interactivos para ajustar umbrales
- Probar diferentes configuraciones
- Exportar resultados

---

## Sesión 3 (opcional, 2-3 h) — LLMs ligeros y caso práctico final

### 1. Introducción a LLMs ligeros (30 min)
- ¿Qué es TinyLlama?
- ¿Qué es Ollama?
- Ejecución local vs APIs en la nube
- Casos de uso en IoT: generación de alertas en lenguaje natural

### 2. Ejercicio práctico: cliente Ollama (40 min)
- Configurar Ollama en el entorno
- Implementar `TinyLlamaClient`
- Generar descripciones de anomalías detectadas
- Discutir limitaciones (latencia, RAM)

### 3. Caso práctico final (60-90 min)
Sistema completo de detección:
- Adquisición de datos de múltiples sensores
- Almacenamiento en InfluxDB
- Detección de anomalías (z-score / MAD)
- Dashboard interactivo
- Alertas opcionales (Telegram, logs)

Entrega:
- Código documentado
- Dashboard funcional
- Informe breve explicando configuración y resultados
