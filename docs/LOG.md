20251204
---
- Módulo 1 Intro a edge computing
- Edge vs Cloud computing
- Limitaciones, consumos, ancho de banda, etc..

20251209
---
- Continua módulo 1
- Definición de requisitos de computación, sensores
- Arquitectura del nodo

20251211
---
- Módulo 2 Preparación y diagnóstico del nodo
- Instalación de Rpi, OS y herramientas de sistema
- Pruebas de conexión
- Configuración de seguridad del sistema
- Mejoras en rendimiento

20251218
---
- Continua módulo 2
- Diagnóstico no herramientas de termnial
- Programación de interfaces de diagnóstico en python
- Interfaz de visualización de monitoring

20260113
---
- Continúa Módulo 2
- Prueab de concepto de sensores para valorar efecto en consumos de procesos/servicos

20260115
---
- Continúa Módulo 2 
- Replicar almacenamiento DB en influx.
- Visualizacion de consumo de recursos para ambos sistemas de DB.
- Recolectar datos de diagnostico y guardar en DB.

20260120
---
- Módulo 3 Adquisición de datos de sensores
- Almacenamiento replicado en influxDB
- Analisis de comsumos de recuros influxDB vs SQLite
- Consumo elevado proviene de VSCode server, no quedaría en producción

20260122
---
- Continua Módulo 3
- Replicar ingesta de datos de diagnóstico en SQlite/InfluxDB. 
- Implementación de interfaz web para visualización de datos sensores y estado de recursos del nodo. Grafana vs Streamlit.
Mejoras
- Completar implementación del panel en Grafana.
- Streamlit avanzado con diagnostico y sensores.
- Importar panel grafana Rpi y telegraf

20260210
---
- Módulo 4 IA/ML en datos temporales
- Detector de anomalías con ventana móvil (3 días) en src/models/zscore_anomaly.py
- Pruebas con temp_aire y luminosidad
- Ajuste del detector de ventana deslizante (z-threshold o ventana)
- Nuevo detector algo más complejo
- Detector MAD (mediana) en src/models/mad_anomaly.py y CLI (--method mad)
Mejoras
- Integración con interfaz de visualización (Streamlit: src/visualization/anomaly_dashboard.py)
- Predictor sencillo

20260112
---
- Módulo 5 Introducción a LLMs y limitaciones en dispostivos de borde
- Instalación de ollama
- Prueba de modelo tinyllama en terminal
- Instalación de docker y open-webui
Mejoras
- Configuración de open-webui para conexión con ollama
- Definir contexto del modelo y propósito
- Realizar pruebas con consultas sobre datos

TODO
---
Muestreo y promediado de datos de sensores
Generación de datasets en csv para uso con modelo LLM