# Módulo 3 · Adquisición de datos de sensores

## Objetivo general
Diseñar e implementar una capa de adquisición de datos robusta y modular para sistemas IoT, capaz de leer datos de sensores reales o simulados, normalizarlos y almacenarlos localmente como base para su posterior análisis, visualización y uso con IA.

## Resultados de aprendizaje
Al finalizar el módulo, el alumnado será capaz de:
- Comprender el flujo completo de adquisición de datos en un nodo IoT.
- Leer datos de sensores físicos mediante protocolos industriales (RS485 / Modbus RTU).
- Implementar un modo simulado para pruebas sin hardware.
- Normalizar lecturas (unidades, timestamps, calidad).
- Almacenar datos localmente en formatos estructurados (CSV y SQLite).
- Construir un bucle de adquisición periódico y tolerante a fallos.

## Contenidos

### 1. Introducción a la adquisición de datos en entornos IoT
- Qué es la adquisición de datos en edge computing
- Diferencia entre adquisición, almacenamiento y análisis
- Importancia de la robustez y la trazabilidad

### 2. Sensores y protocolos de comunicación
- Tipología de sensores en energía y agua
- RS485 y Modbus RTU: conceptos básicos
- Registros, escalado y polling

### 3. Arquitectura software de la capa de adquisición
- Separación por módulos y responsabilidades
- Drivers de sensores
- Normalización de datos
- Persistencia local

### 4. Modo real vs modo simulado
- Por qué simular sensores
- Generación de datos sintéticos realistas
- Gestión de eventos y errores simulados

### 5. Persistencia local de datos
- Almacenamiento en CSV
- Almacenamiento en SQLite
- Ventajas e inconvenientes de cada opción

### 6. Bucle de adquisición y control de errores
- Frecuencia de muestreo
- Timeouts y fallos de comunicación
- Etiquetado de calidad del dato

## Relación con módulos posteriores
- Base para visualización (Módulo 4)
- Base para detección de anomalías e IA (Módulos 5 y 6)
- Integración con automatización (Módulos IoT avanzados)
