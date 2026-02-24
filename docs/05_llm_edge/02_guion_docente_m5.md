# Módulo 5 · Guion docente

## Enfoque general
Este módulo es **exploratorio y práctico**.  
El objetivo NO es formar expertos en LLMs, sino que el alumnado **experimente** con modelos ligeros, entienda sus limitaciones y evalúe en qué casos aportan valor real en sistemas IoT.

La teoría debe ser **mínima y pragmática**. Enfoque: "¿esto funciona en un RPi? ¿vale la pena?"

---

## Sesión 1 (2-3 h) — Fundamentos y primeros pasos con Ollama

### 1. Introducción y contexto (20 min)
- ¿Qué es un LLM?
  - Modelo entrenado para predecir texto
  - Variantes: GPT, Llama, Mistral, TinyLlama
- ¿Por qué ejecutar localmente?
  - Privacidad: datos no salen del edge
  - Latencia: sin depender de internet
  - Costos: sin pagar APIs externas
- Realidad en edge:
  - Hardware limitado
  - Generación lenta (segundos, no milisegundos)
  - Calidad inferior a modelos grandes

### 2. Teoría esencial: arquitectura de TinyLlama (20 min)
- Familia Llama (Meta)
- TinyLlama: versión reducida (1.1B parámetros vs 7B-70B)
- Entrenamiento: corpus de texto general
- Capacidades:
  - Completado de texto
  - Generación de respuestas cortas
  - Traducción básica
- Limitaciones:
  - Contexto: ~2K tokens
  - Conocimiento: datos hasta 2023
  - Razonamiento: limitado comparado con GPT-4

👉 No entrar en detalles de arquitectura Transformer. Enfoque funcional.

### 3. Ejercicio práctico 1 (40 min)
- Instalar Ollama:
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```
- Descargar TinyLlama:
  ```bash
  ollama pull tinyllama
  ```
- Probar desde CLI:
  ```bash
  ollama run tinyllama "Resume en una frase: temperatura 45°C detectada"
  ```
- Explorar otros modelos disponibles:
  ```bash
  ollama list
  ollama pull llama2:7b  # (si hay recursos)
  ```

Acompañar paso a paso. Resolver problemas de instalación.

### 4. Ejercicio práctico 2 (40 min)
- Implementar `OllamaConfig` (dataclass con host, port, model, timeout)
- Implementar `TinyLlamaClient.__init__()` y `config_from_settings()`
- Probar conexión básica: consultar `/api/tags` para listar modelos

---

## Sesión 2 (3 h) — Cliente completo y casos de uso

### 1. Repaso guiado (15 min)
- Revisar código de la sesión anterior
- Resolver dudas sobre Ollama y su API

### 2. Teoría: API HTTP de Ollama (25 min)
- Endpoints principales:
  - `POST /api/generate`: generar texto
  - `POST /api/pull`: descargar modelo
  - `GET /api/tags`: listar modelos locales
- Parámetros de generación:
  - `temperature`: aleatoriedad (0.0 = determinista, 1.0 = creativo)
  - `top_p`: nucleus sampling
  - `stream`: respuesta incremental vs completa
- Formato de respuesta (JSON)

### 3. Ejercicio práctico 1 (60 min)
- Completar `TinyLlamaClient`:
  - `is_model_ready()`: verificar si el modelo está descargado
  - `ensure_model_available()`: descargar si falta
  - `pull_model()`: gestionar descarga con reintentos
  - `generate(prompt, options, stream)`: invocar generación
- Probar con prompts variados:
  - Alertas: "Temperatura alta: 45°C. Genera alerta."
  - Resúmenes: "Resumir: 120 muestras, 3 anomalías..."
  - Explicaciones: "¿Por qué humedad 15% es anómala?"

### 4. Ejercicio práctico 2 (40 min)
- Integrar con detectores de anomalías del Módulo 4
- Crear función `generate_anomaly_alert(anomaly_data)`
- Comparar alertas técnicas vs generadas por LLM:
  ```
  Técnica: "soil_moisture_pct anomaly: value=12, zscore=4.2"
  LLM: "Alerta: nivel de humedad crítico (12%). Revisar riego."
  ```

### 5. Discusión y benchmarking (20 min)
- Medir latencia de generación en RPi
- Evaluar calidad de las respuestas
- Discutir casos de uso realistas vs "juguetes"

---

## Sesión 3 (2-3 h) — Rol, interfaz y selección de modelo

### 1. Repaso (10 min)
- Verificar que todos tienen `generate()` con `system` y `options` funcionando.

### 2. Rol configurable del modelo (30 min)
- Concepto de system prompt: ¿qué cambia con él?
- Mostrar diferencia entre respuestas con y sin rol definido.
- Crear `src/llm/role.md` como experto en series temporales agrícolas.
- Implementar `load_role(path)` con fallback ante errores.
- Variable de entorno `NAIRA_OLLAMA_ROLE_PATH` para cambiar el rol sin modificar código.

### 3. Ejercicio práctico 1 (30 min)
- Añadir parámetro `system` a `generate()` y pasarlo a Ollama.
- Probar el mismo prompt con y sin rol. Comparar respuestas.
- Ajustar `num_ctx` (empezar con 2048, subir a 4096 si la RPi lo permite).

### 4. Interfaz Streamlit (60 min)
- Crear `src/llm/llm_app.py`:
  - Sidebar: conexión, modelo, timeout, num_ctx.
  - Panel de rol editable (carga de `role.md`).
  - Panel de contexto/datos (pegar JSON de sensores).
  - Historial de chat.
- Probar con datos reales de sensores pegados en el panel de contexto.

### 5. Selección de modelo para RPi (20 min)
- Comparativa práctica: descargar `qwen2.5:1.5b` y comparar latencia y calidad vs `tinyllama`.
  ```bash
  ollama pull qwen2.5:1.5b
  ```
- Medir tiempos con el mismo prompt en ambos modelos.
- Actualizar `NAIRA_OLLAMA_MODEL=qwen2.5:1.5b` si los recursos lo permiten.

### 6. Sesión opcional: optimización (30 min)
- `num_ctx` vs latencia: tabla empírica con la RPi del aula.
- Estrategias: caching de prompts repetidos, generación fuera del ciclo crítico.
- ¿Cuándo es mejor una plantilla estática? Discusión abierta.

---

## Notas para el docente

### Expectativas realistas
- TinyLlama NO es ChatGPT. Las respuestas serán imperfectas.
- El objetivo es **explorar**, no producir sistemas en producción.
- Enfatizar el trade-off: complejidad vs beneficio.

### Gestión de frustración
- Algunos estudiantes esperarán magia → aclarar limitaciones desde el inicio.
- Latencia puede ser frustrante → enfatizar que es normal en edge.

### Alternativas si Ollama falla
- Usar APIs de OpenAI/Anthropic (requiere internet y cuenta)
- Usar plantillas estáticas (más simple, menos "inteligente")
- Mostrar videos de demos si el hardware no coopera
