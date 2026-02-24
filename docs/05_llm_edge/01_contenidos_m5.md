# Módulo 5 · LLMs ligeros en edge computing

## Objetivo general
Explorar y aplicar modelos de lenguaje ligeros (LLMs) en dispositivos IoT de recursos limitados, evaluando su viabilidad técnica para generar contenido contextual (alertas, explicaciones, resúmenes) a partir de datos de sensores y eventos del sistema.

## Resultados de aprendizaje
Al finalizar el módulo, el alumnado será capaz de:
- Comprender los fundamentos de los modelos de lenguaje y su arquitectura.
- Diferenciar entre LLMs en la nube y LLMs locales en edge.
- Instalar y configurar Ollama para ejecutar modelos localmente.
- Implementar un cliente robusto para interactuar con modelos Ollama.
- Configurar el rol del modelo mediante un archivo externo (`role.md`).
- Implementar un simulador (`stub.py`) para desarrollar sin hardware ni red.
- Construir una interfaz de chat con Streamlit conectada al LLM local.
- Integrar el LLM en el pipeline de adquisición y procesamiento del nodo.
- Generar alertas y explicaciones en lenguaje natural a partir de datos IoT.
- Evaluar limitaciones de recursos (RAM, CPU, latencia) en Raspberry Pi.
- Seleccionar el modelo más adecuado según recursos disponibles.

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
- Comparación de modelos por tag (`_model_matches`)

### 4b. Simulador y modo offline
- Patrón `stub.py`: mismo interfaz, sin dependencia de Ollama
- `StubLlamaClient`: respuestas basadas en keywords para desarrollo y tests
- `get_client(sim=True)`: selector de modo según entorno

### 4c. Rol configurable del modelo
- Qué es un system prompt y para qué sirve
- Archivo `role.md`: definición del rol como experto en series temporales agrícolas
- `load_role(path)`: carga y fallback ante errores de fichero
- Variable de entorno `NAIRA_OLLAMA_ROLE_PATH` para personalización
- Parámetro `system` en `/api/generate` de Ollama

### 4d. Parámetros de generación: num_ctx
- Qué es el contexto en un LLM
- `num_ctx`: ventana de tokens que el modelo puede considerar
- Trade-off: más contexto → más RAM y latencia
- Configuración mediante `NAIRA_OLLAMA_NUM_CTX`

### 4e. Interfaz Streamlit para el LLM
- Arquitectura de `llm_app.py`
- Panel de conexión: host, puerto, modelo, timeout, num_ctx
- Estado del modelo en tiempo real: verificación y descarga
- Panel de rol editable en sesión
- Panel de contexto/datos: pegado de datos para análisis
- Historial de chat con `st.chat_message`

### 5. Casos de uso en sistemas IoT agrícolas
- Generación de alertas en lenguaje natural
- Resúmenes diarios automáticos
- Explicaciones de anomalías detectadas
- Recomendaciones de acción para operadores

### 6. Selección de modelo para edge
- Comparativa: TinyLlama (1.1B) vs qwen2.5:1.5b vs llama3.2:1b
- Criterios: tamaño en disco, RAM, calidad en tareas estructuradas
- `qwen2.5:1.5b` como referencia para análisis de datos en RPi

### 7. Evaluación de viabilidad en Raspberry Pi
- Requisitos de hardware: RAM, CPU, almacenamiento
- Benchmarking: latencia de generación
- Trade-offs: calidad vs velocidad
- Estrategias de optimización: modelos cuantizados, num_ctx, caching

## Relación con módulos anteriores
- Depende del Módulo 4 (detección de anomalías y eventos)
- Enriquece alertas generadas por detectores estadísticos
- Complementa dashboards con explicaciones automáticas

## Relación con módulos posteriores
- Base para sistemas de asistencia inteligente
- Apoyo para automatización guiada por lenguaje natural
- Fundamento para futuros módulos de IA conversacional
