# Módulo 4 · Material didáctico

## Objetivo general
Proporcionar al alumnado las herramientas conceptuales y técnicas necesarias para diseñar, implementar y desplegar detectores de anomalías en series temporales, optimizados para ejecutarse en hardware limitado (edge computing) y aplicables a sistemas IoT reales en agricultura y gestión de recursos.

---

## Resultados de aprendizaje
Al finalizar el módulo, el alumnado será capaz de:
- Comprender los fundamentos matemáticos de la detección de anomalías estadísticas.
- Implementar algoritmos de ventana móvil con estructuras de datos eficientes.
- Integrar detectores con bases de datos de series temporales (InfluxDB).
- Construir pipelines completos: adquisición → almacenamiento → detección → visualización.
- Evaluar y ajustar umbrales de detección según contexto aplicado.
- Explorar el uso de LLMs ligeros para enriquecer sistemas IoT.

---

## 1. Introducción a la detección de anomalías en IoT

### ¿Qué es una anomalía?
Una anomalía (o outlier) es una observación que se desvía significativamente del comportamiento esperado en un conjunto de datos.

**Tipos de anomalías:**
- **Puntuales:** un valor aislado extremo (ej: sensor reporta 150°C).
- **Contextuales:** un valor normal en otro contexto pero anómalo en este (ej: humedad alta en invierno seco).
- **Colectivas:** una secuencia de valores que juntos forman un patrón inusual.

### ¿Por qué detectarlas en tiempo real?
- Prevenir fallos en infraestructura crítica (bombas, riego).
- Optimizar consumo de recursos (agua, energía).
- Generar alertas tempranas para el operador.
- Mejorar la calidad de los datos (descartar lecturas malas).

### Desafíos en edge computing
- **Recursos limitados:** CPU, RAM, almacenamiento (ej: Raspberry Pi).
- **Latencia baja:** decisiones deben tomarse en segundos, no minutos.
- **Conectividad intermitente:** no siempre hay acceso a la nube.
- **Robustez:** algoritmos deben funcionar con datos ruidosos o incompletos.

---

## 2. Series temporales y ventanas móviles

### Conceptos básicos
Una **serie temporal** es una secuencia de valores medidos en intervalos de tiempo sucesivos:
```
[(t1, v1), (t2, v2), ..., (tn, vn)]
```

**Características clave:**
- Timestamps ordenados cronológicamente.
- Frecuencia de muestreo (ej: cada 10 segundos, cada hora).
- Posibles valores faltantes o erróneos.

### Ventanas móviles (sliding windows)
Para detectar anomalías, se mantiene una **ventana** de las últimas N muestras y se compara cada nuevo valor contra las estadísticas de esa ventana.

**Parámetros críticos:**
- **Tamaño de ventana:** ¿cuánto histórico considerar? (ej: últimas 72 horas, últimas 500 muestras).
- **Mínimo de muestras:** cuántas muestras necesito antes de poder detectar (arranque en frío).
- **Umbral:** qué tan extremo debe ser un valor para considerarse anómalo.

**Trade-offs:**
- Ventana muy pequeña → sensible a ruido, muchos falsos positivos.
- Ventana muy grande → menos reactiva, puede perder anomalías puntuales o contextuales.

---

## 3. Detectores estadísticos clásicos

### 3.1. Z-score (puntuación estándar)

**Fórmula:**
```
z = (x - μ) / σ
```
donde:
- `x`: valor actual
- `μ`: media de la ventana
- `σ`: desviación estándar de la ventana

**Interpretación:**
- `|z| < 2`: valor normal (dentro de ~95% de los datos si distribución normal).
- `|z| >= 2.5`: posible anomalía.
- `|z| >= 3`: anomalía muy probable.

**Implementación eficiente:**
```python
from collections import deque
from statistics import fmean, pstdev

class RollingAnomalyDetector:
    def __init__(self, metric: str, window: timedelta, z_threshold: float = 3.0):
        self.metric = metric
        self.window = window
        self.z_threshold = z_threshold
        self._samples = deque()  # Ventana móvil

    def evaluate(self, ts: datetime, value: float) -> dict:
        self._trim(ts)  # Eliminar muestras fuera de ventana
        self._samples.append((ts, value))
        
        if len(self._samples) < 2:
            return {"anomaly": False}
        
        values = [v for _, v in self._samples]
        avg = fmean(values)
        std = pstdev(values)
        
        zscore = (value - avg) / std if std > 0 else 0.0
        anomaly = abs(zscore) >= self.z_threshold
        
        return {
            "zscore": zscore,
            "anomaly": anomaly,
            "mean": avg,
            "std": std
        }
```

**Ventajas:**
- Simple, intuitivo, ampliamente conocido.
- Funciona bien si los datos tienen distribución aproximadamente normal.

**Desventajas:**
- Sensible a outliers extremos (la media y σ se distorsionan).
- Asume normalidad de los datos.

---

### 3.2. MAD (Median Absolute Deviation)

**Fórmula:**
```
MAD = median(|x_i - median(X)|)
```
Para convertir MAD en una escala comparable a desviación estándar (asumiendo normalidad):
```
MAD_scaled = MAD * 1.4826
```

Luego se calcula un "MAD score":
```
mad_score = (x - median) / MAD_scaled
```

**Interpretación:**
- Similar al z-score, pero usando mediana en vez de media.
- `|mad_score| >= 3.5`: anomalía probable (umbral típico, ajustable).

**Implementación:**
```python
from statistics import median

class RollingMadAnomalyDetector:
    def __init__(self, metric: str, window: timedelta, mad_threshold: float = 3.5):
        self.metric = metric
        self.window = window
        self.mad_threshold = mad_threshold
        self.scale_factor = 1.4826  # Conversión a escala σ
        self._samples = deque()

    def evaluate(self, ts: datetime, value: float) -> dict:
        self._trim(ts)
        self._samples.append((ts, value))
        
        if len(self._samples) < 2:
            return {"anomaly": False}
        
        values = [v for _, v in self._samples]
        med = median(values)
        deviations = [abs(v - med) for v in values]
        mad = median(deviations)
        scaled_mad = self.scale_factor * mad
        
        mad_score = (value - med) / scaled_mad if scaled_mad > 0 else 0.0
        anomaly = abs(mad_score) >= self.mad_threshold
        
        return {
            "mad_score": mad_score,
            "anomaly": anomaly,
            "median": med,
            "mad": mad
        }
```

**Ventajas:**
- Robusto: outliers extremos no distorsionan la mediana.
- Más confiable en datos con ruido o distribuciones no normales.

**Desventajas:**
- Computacionalmente más costoso (calcular mediana requiere ordenar).
- Menos conocido que z-score.

**¿Cuándo usar cada uno?**
- **Z-score:** datos limpios, distribución aproximadamente normal, velocidad crítica.
- **MAD:** datos ruidosos, presencia de outliers, mayor robustez requerida.

---

## 4. Integración con InfluxDB

### ¿Por qué InfluxDB?
- Base de datos optimizada para series temporales.
- Almacenamiento comprimido y eficiente.
- Consultas Flux potentes para agregaciones y filtros.
- Tags para organizar métricas por nodo, sensor, ubicación.

### Arquitectura típica
```
Sensores → Collector → InfluxDB → Detector → Dashboard / Alertas
```

### Consulta típica (Flux)
```flux
from(bucket: "naira_telemetry")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "naira_samples")
  |> filter(fn: (r) => r["metric"] == "soil_moisture_pct")
  |> filter(fn: (r) => r["node_id"] == "naira-node-001")
  |> sort(columns: ["_time"])
  |> limit(n: 5000)
```

### Pipeline Python
```python
from influxdb_client import InfluxDBClient

client = InfluxDBClient(url=url, token=token, org=org)
samples = fetch_metric_samples(
    client=client,
    bucket="naira_telemetry",
    metric="soil_moisture_pct",
    hours=24
)

detector = RollingAnomalyDetector(...)
for sample in samples:
    result = detector.evaluate(sample["ts"], sample["value"])
    if result["anomaly"]:
        print(f"Anomalía detectada: {sample}")
```

---

## 5. Visualización de anomalías

### Dashboard interactivo con Streamlit

**Componentes básicos:**
- **Selector de métricas:** permite al usuario elegir qué métrica analizar.
- **Configuración de parámetros:** ventana, umbral, método (z-score / MAD).
- **Gráfico de serie temporal:** línea con valores normales y anomalías marcadas.
- **Tabla de anomalías:** lista detallada con timestamps, valores y scores.

**Ejemplo simplificado:**
```python
import streamlit as st
import pandas as pd

st.title("NAIRA · Detección de Anomalías")

metric = st.text_input("Métrica", value="soil_moisture_pct")
hours = st.slider("Ventana (horas)", 1, 168, 24)
method = st.selectbox("Método", ["zscore", "mad"])

# Consultar InfluxDB y ejecutar detector...
samples, anomalies = fetch_and_detect(metric, hours, method)

# Visualizar
df = pd.DataFrame(samples)
st.line_chart(df.set_index("ts")["value"])

if anomalies:
    st.warning(f"{len(anomalies)} anomalías detectadas")
    st.dataframe(pd.DataFrame(anomalies))
else:
    st.success("No se detectaron anomalías")
```

---

## 6. LLMs ligeros en edge (introducción)

### ¿Qué es TinyLlama?
- Modelo de lenguaje pequeño (~1.1B parámetros).
- Puede ejecutarse en CPU (lento) o GPU pequeña.
- Ideal para generar texto breve (alertas, explicaciones).

### ¿Qué es Ollama?
- Framework para ejecutar LLMs localmente.
- API HTTP sencilla.
- Descarga automática de modelos.

### Caso de uso en NAIRA
**Problema:** las alertas `"soil_moisture_pct: anomaly detected, score=4.2"` son difíciles de interpretar para usuarios no técnicos.

**Solución:** usar TinyLlama para generar descripciones en lenguaje natural:
```
"Se ha detectado un nivel de humedad del suelo inusualmente bajo (15%) 
en el nodo agrícola. Esto podría indicar un fallo en el sistema de riego 
o condiciones de sequía. Se recomienda revisión inmediata."
```

### Limitaciones en Raspberry Pi
- **RAM:** TinyLlama requiere al menos 4 GB (RPi 4 con 8 GB recomendado).
- **Latencia:** generación puede tardar varios segundos en CPU.
- **Trade-off:** útil para alertas no urgentes, no para decisiones en tiempo real crítico.

---

## Resumen de tecnologías clave

| Componente | Tecnología | Propósito |
|------------|-----------|-----------|
| Detector estadístico | Python (stdlib) | Z-score, MAD |
| Base de datos | InfluxDB | Almacenamiento series temporales |
| Consultas | Flux | Recuperación de ventanas históricas |
| Visualización | Streamlit | Dashboard interactivo |
| LLM ligero | Ollama + TinyLlama | Generación de texto (alertas) |
| Hardware | Raspberry Pi 4 | Edge computing |

---

## Referencias recomendadas

- [InfluxDB Documentation](https://docs.influxdata.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Ollama](https://ollama.ai/)
- Chandola, V., Banerjee, A., & Kumar, V. (2009). "Anomaly detection: A survey". ACM Computing Surveys.
- Rousseeuw, P. J., & Croux, C. (1993). "Alternatives to the Median Absolute Deviation". Journal of the American Statistical Association.
