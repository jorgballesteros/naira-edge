# Módulo 5 · LLMs ligeros en edge computing

## Objetivo general
Explorar y aplicar modelos de lenguaje ligeros (LLMs) en dispositivos IoT de recursos limitados, evaluando su viabilidad técnica para generar contenido contextual (alertas, explicaciones, resúmenes) a partir de datos de sensores y eventos del sistema.

## Resultados de aprendizaje
Al finalizar el módulo, el alumnado será capaz de:
- Comprender los fundamentos de los modelos de lenguaje y su arquitectura.
- Diferenciar entre LLMs en la nube y LLMs locales en edge.
- Instalar y configurar Ollama para ejecutar modelos localmente.
- Implementar un cliente robusto para interactuar con TinyLlama.
- Generar alertas y explicaciones en lenguaje natural a partir de datos IoT.
- Evaluar limitaciones de recursos (RAM, CPU, latencia) en Raspberry Pi.
- Diseñar casos de uso realistas donde un LLM ligero aporta valor.

## Contenidos

### 1. Introducción a los LLMs y edge computing
- ¿Qué es un modelo de lenguaje?
- LLMs grandes vs ligeros: trade-offs
- ¿Por qué ejecutar LLMs localmente en IoT?
- Privacidad, latencia y conectividad

### 2. TinyLlama: arquitectura y capacidades
- Orígenes: proyecto de la comunidad open-source
- Arquitectura: 1.1B parámetros, familia Llama
- Capacidades: generación de texto, completado, conversación básica
- Limitaciones: contexto reducido, conocimiento limitado

### 3. Ollama: framework para LLMs locales
- Instalación y configuración
- Descarga y gestión de modelos
- API HTTP: endpoints principales (`/api/generate`, `/api/pull`, `/api/tags`)
- Parámetros de generación: temperatura, top_p, stop tokens

### 4. Implementación de un cliente Python
- Diseño modular: configuración, conexión, generación
- Gestión de errores y timeouts
- Logging y trazabilidad
- Reintentos y backoff exponencial

### 5. Casos de uso en sistemas IoT agrícolas
- Generación de alertas en lenguaje natural
- Resúmenes diarios automáticos
- Explicaciones de anomalías detectadas
- Recomendaciones de acción para operadores

### 6. Evaluación de viabilidad en Raspberry Pi
- Requisitos de hardware: RAM, CPU, almacenamiento
- Benchmarking: latencia de generación
- Trade-offs: calidad vs velocidad
- Estrategias de optimización: modelos cuantizados, caching

## Relación con módulos anteriores
- Depende del Módulo 4 (detección de anomalías y eventos)
- Enriquece alertas generadas por detectores estadísticos
- Complementa dashboards con explicaciones automáticas

## Relación con módulos posteriores
- Base para sistemas de asistencia inteligente
- Apoyo para automatización guiada por lenguaje natural
- Fundamento para futuros módulos de IA conversacional
