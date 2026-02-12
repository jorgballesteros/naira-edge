# Módulo 4 · IA/ML en series temporales para detección de anomalías

## Objetivo general
Diseñar e implementar detectores de anomalías en series temporales basados en técnicas estadísticas y Machine Learning ligero, ejecutables en hardware limitado (edge computing), para identificar patrones anómalos en datos de sensores IoT en tiempo real.

## Resultados de aprendizaje
Al finalizar el módulo, el alumnado será capaz de:
- Comprender los fundamentos de la detección de anomalías en series temporales.
- Implementar detectores estadísticos (z-score, MAD) sobre ventanas móviles.
- Integrar detectores con bases de datos de series temporales (InfluxDB).
- Diseñar pipelines de procesamiento en tiempo real compatibles con edge computing.
- Visualizar resultados de detección mediante dashboards interactivos.

## Contenidos

### 1. Introducción a la detección de anomalías en IoT
- Qué es una anomalía y por qué detectarlas
- Tipos de anomalías: puntuales, contextuales, colectivas
- Desafíos en edge computing: recursos limitados, latencia baja
- Casos de uso: agricultura, energía, agua

### 2. Series temporales y ventanas móviles
- Conceptos básicos de series temporales
- Ventanas deslizantes (sliding windows)
- Parámetros clave: tamaño de ventana, mínimo de muestras
- Trade-offs: sensibilidad vs falsos positivos

### 3. Detectores estadísticos clásicos
- Z-score: media y desviación estándar
- MAD (Median Absolute Deviation): robustez ante outliers
- Umbrales de detección
- Implementación eficiente con `collections.deque`

### 4. Integración con InfluxDB
- InfluxDB como base de datos de series temporales
- Consultas Flux para recuperar ventanas históricas
- Pipeline: almacenamiento → consulta → detección → alerta
- Gestión de múltiples métricas y nodos

### 5. Visualización de anomalías
- Dashboards con Streamlit
- Representación gráfica de series y anomalías
- Configuración de umbrales en tiempo real
- Exportación de resultados

## Relación con módulos anteriores
- Depende del Módulo 3 (adquisición y normalización de datos)
- Utiliza datos almacenados localmente o en InfluxDB
- Sienta las bases para módulos avanzados de automatización y toma de decisiones

## Relación con módulos posteriores
- Base para sistemas de alerta temprana (Módulo 5: LLMs ligeros)
- Integración con dashboards de monitoreo
- Apoyo para optimización de recursos (agua, energía)
- Los detectores se integran con LLMs ligeros para generar alertas en lenguaje natural (Módulo 5)
