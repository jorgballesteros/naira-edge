# Módulo 4 · Ejercicios

## Sesión 1 — Fundamentos y detectores estadísticos

### Ejercicio 1 · Detector Z-score básico
**Objetivo:** implementar un detector de anomalías basado en z-score con ventana móvil.

**Tareas:**
1. Crear la clase `RollingAnomalyDetector` en `src/models/zscore_anomaly.py`.
2. Implementar el método `evaluate(ts, value)` que:
   - Mantenga una ventana deslizante de las últimas N horas de datos.
   - Calcule media y desviación estándar de la ventana.
   - Compute el z-score del valor actual.
   - Retorne un dict con `zscore`, `anomaly`, `mean`, `std`, `window_ready`.
3. Probar con un dataset sintético (lista de valores normales + outliers).

**Entregables:**
- Código funcional de `RollingAnomalyDetector`.
- Ejemplo de uso que detecte correctamente 2-3 anomalías insertadas manualmente.
- Breve comentario explicando el efecto de cambiar el umbral (ej: 2.0 vs 3.0).

**Datos de prueba sugeridos:**
```python
samples = [
    ("2026-02-12T10:00:00Z", 50.0),
    ("2026-02-12T10:10:00Z", 52.0),
    ("2026-02-12T10:20:00Z", 48.0),
    # ... valores normales entre 45-55
    ("2026-02-12T14:00:00Z", 95.0),  # ANOMALÍA
    ("2026-02-12T14:10:00Z", 51.0),
]
```

---

### Ejercicio 2 · Detector MAD
**Objetivo:** implementar un detector más robusto usando Median Absolute Deviation.

**Tareas:**
1. Crear la clase `RollingMadAnomalyDetector` en `src/models/mad_anomaly.py`.
2. Implementar el método `evaluate(ts, value)` análogo al z-score, pero usando mediana y MAD.
3. Comparar resultados MAD vs Z-score con un dataset que incluya outliers extremos.

**Entregables:**
- Código funcional de `RollingMadAnomalyDetector`.
- Tabla comparativa:
  ```
  | Valor | Z-score | ¿Anomalía? | MAD score | ¿Anomalía? |
  |-------|---------|------------|-----------|------------|
  | 50    | 0.1     | No         | 0.15      | No         |
  | 95    | 4.5     | Sí         | 3.8       | Sí         |
  | 200   | 15.2    | Sí         | 4.1       | Sí         |
  ```
- Breve explicación: ¿cuándo es MAD preferible a z-score?

---

### Ejercicio 3 · Integración con módulo de procesamiento
**Objetivo:** enriquecer las muestras procesadas con detección de anomalías.

**Tareas:**
1. Modificar `src/processing/stub.py` para invocar los detectores sobre cada muestra.
2. Añadir los resultados al dict procesado:
   ```python
   {
       "soil_moisture_pct": 45.0,
       "soil_moisture_pct_zscore": 1.2,
       "soil_moisture_pct_anomaly": False,
       "soil_moisture_pct_window_ready": True,
       ...
   }
   ```
3. Probar con un bucle de adquisición simulado que genere 100 muestras.

**Entregables:**
- Código actualizado de `process_sample()`.
- Log o CSV con muestras procesadas incluyendo campos de anomalía.

---

## Sesión 2 — Integración con InfluxDB y visualización

### Ejercicio 4 · Script CLI para consulta y detección
**Objetivo:** implementar un script que consulte InfluxDB y ejecute detección de anomalías.

**Tareas:**
1. Crear `src/tools/influx_anomaly.py` con CLI basado en `argparse`.
2. Parámetros requeridos:
   - `--metric`: métrica a consultar (ej: `soil_moisture_pct`).
   - `--hours`: ventana de lectura (ej: 24).
   - `--method`: `zscore` o `mad`.
   - `--bucket`: bucket de InfluxDB (ej: `naira_telemetry`).
3. Implementar funciones:
   - `fetch_metric_samples()`: consulta Flux a InfluxDB.
   - `detect_anomalies()`: ejecuta el detector sobre las muestras recuperadas.
4. Imprimir resultados: cantidad de anomalías, lista de timestamps y valores anómalos.

**Entregables:**
- Script funcional `influx_anomaly.py`.
- Ejemplo de ejecución:
  ```bash
  python -m src.tools.influx_anomaly \
    --metric soil_moisture_pct \
    --hours 24 \
    --method mad \
    --bucket naira_telemetry
  ```
- Captura de salida con al menos 1 anomalía detectada.

---

### Ejercicio 5 · Dashboard Streamlit
**Objetivo:** crear un dashboard interactivo para visualizar anomalías.

**Tareas:**
1. Crear `src/visualization/anomaly_dashboard.py`.
2. Componentes del dashboard:
   - Sidebar con inputs:
     - Métrica a consultar.
     - Bucket, measurement.
     - Ventana temporal (slider).
     - Método de detección (selectbox: zscore / mad).
     - Umbrales ajustables.
   - Gráfico principal: serie temporal con anomalías marcadas en rojo.
   - Tabla: lista de anomalías detectadas con timestamp, valor, score.
   - Métricas resumen: total de muestras, total de anomalías, score máximo.
3. Ejecutar con:
   ```bash
   streamlit run src/visualization/anomaly_dashboard.py
   ```

**Entregables:**
- Código del dashboard.
- Capturas de pantalla mostrando:
  - Serie temporal con anomalías marcadas.
  - Configuración de parámetros en la sidebar.
  - Tabla de anomalías detectadas.

---

### Ejercicio 6 · Comparación de métodos
**Objetivo:** evaluar cuándo usar z-score vs MAD.

**Tareas:**
1. Seleccionar una métrica real con datos de al menos 48 horas.
2. Ejecutar detección con ambos métodos (z-score y MAD) usando parámetros idénticos:
   - Ventana: 24 horas.
   - Umbral z-score: 2.5.
   - Umbral MAD: 3.5.
3. Comparar resultados:
   - ¿Cuántas anomalías detecta cada método?
   - ¿Hay diferencias significativas?
   - ¿Cuál parece más confiable para estos datos?

**Entregables:**
- Informe PDF/Markdown (1-2 páginas) con:
  - Descripción de la métrica analizada.
  - Gráficos comparativos.
  - Tabla resumiendo diferencias.
  - Conclusión justificada sobre qué método es preferible en este caso.

---

## Sesión 3 (opcional) — LLMs ligeros y caso práctico final

### Ejercicio 7 · Cliente Ollama para TinyLlama
**Objetivo:** implementar un cliente para generar descripciones de anomalías en lenguaje natural.

**Tareas:**
1. Instalar Ollama en el entorno de desarrollo:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull tinyllama
   ```
2. Crear `src/llm/ollama_client.py` con la clase `TinyLlamaClient`.
3. Implementar método `generate(prompt)` que invoque la API HTTP de Ollama.
4. Probar con un prompt de ejemplo:
   ```python
   prompt = """
   Se ha detectado una anomalía en el sensor de humedad del suelo.
   Valor actual: 12%
   Valor esperado: 45-55%
   Z-score: 4.2
   
   Genera una alerta breve en español para el operador del sistema de riego.
   """
   client = TinyLlamaClient()
   response = client.generate(prompt)
   print(response)
   ```

**Entregables:**
- Código funcional de `TinyLlamaClient`.
- Ejemplo de salida generada por TinyLlama.
- Comentario sobre viabilidad en Raspberry Pi (latencia observada, uso de RAM).

---

### Caso práctico final · Sistema completo de detección

**Objetivo:** integrar todos los componentes en un sistema funcional end-to-end.

**Descripción:**
Construir un pipeline completo que:
1. Adquiera datos de sensores (reales o simulados).
2. Almacene en InfluxDB (o SQLite si InfluxDB no está disponible).
3. Ejecute detección de anomalías cada N minutos sobre ventanas deslizantes.
4. Muestre resultados en un dashboard Streamlit.
5. (Opcional) Genere alertas por Telegram o email cuando se detecte anomalía.

**Componentes técnicos:**
- `src/acquisition/collector.py`: adquisición periódica.
- `src/models/zscore_anomaly.py` o `mad_anomaly.py`: detección.
- `src/acquisition/influx.py`: replicación a InfluxDB.
- `src/visualization/anomaly_dashboard.py`: visualización.
- `src/diagnostics/telegram_alert.py` (opcional): notificaciones.

**Entregables:**
- Código completo documentado.
- README con instrucciones de ejecución.
- Dashboard funcional (demo en vivo o video de 2-3 min).
- Informe técnico (3-5 páginas) con:
  - Arquitectura del sistema.
  - Decisiones de diseño (por qué z-score o MAD, tamaño de ventana, umbrales).
  - Resultados: capturas del dashboard, ejemplos de anomalías detectadas.
  - Limitaciones y trabajo futuro.

---

## Criterios de evaluación

| Criterio | Peso |
|----------|------|
| Correctitud técnica de los detectores | 30% |
| Integración con InfluxDB y consultas Flux | 20% |
| Dashboard funcional y usable | 20% |
| Documentación y claridad del código | 15% |
| Análisis comparativo (z-score vs MAD) | 10% |
| Creatividad y mejoras opcionales (LLM, alertas) | 5% |

**Nota:** el caso práctico final puede desarrollarse en grupos de 2-3 personas.
