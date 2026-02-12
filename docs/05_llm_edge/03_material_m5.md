# Módulo 5 · Material didáctico

## Objetivo general
Proporcionar al alumnado los conocimientos teóricos y prácticos para integrar modelos de lenguaje ligeros (LLMs) en sistemas IoT edge, evaluando su viabilidad técnica y aplicabilidad en casos de uso reales del sector agrícola y de gestión de recursos.

---

## Resultados de aprendizaje
Al finalizar el módulo, el alumnado será capaz de:
- Comprender los fundamentos de los modelos de lenguaje y su funcionamiento.
- Distinguir entre LLMs en la nube y LLMs ejecutables localmente.
- Instalar, configurar y gestionar Ollama en entornos Linux (Raspberry Pi).
- Implementar un cliente Python robusto para interactuar con LLMs locales.
- Diseñar prompts efectivos para casos de uso IoT.
- Evaluar críticamente cuándo un LLM aporta valor vs complejidad innecesaria.

---

## 1. Introducción a los LLMs y edge computing

### ¿Qué es un modelo de lenguaje?
Un **Large Language Model (LLM)** es una red neuronal entrenada en grandes cantidades de texto para predecir la siguiente palabra en una secuencia. Esto le permite:
- Completar texto
- Responder preguntas
- Generar contenido original
- Resumir información
- Traducir (limitadamente)

**Arquitectura típica:** Transformer (atención multi-cabeza).

### LLMs grandes vs ligeros

| Característica | LLM Grande (GPT-4, Claude) | LLM Ligero (TinyLlama) |
|----------------|---------------------------|------------------------|
| Parámetros | 100B+ | 1.1B |
| RAM requerida | 200+ GB (GPU) | 2-4 GB (CPU/GPU) |
| Latencia | <1s (en nube potente) | 5-30s (en RPi) |
| Calidad | Excelente | Aceptable para tareas simples |
| Costo | API de pago | Gratis (local) |
| Privacidad | Datos salen del dispositivo | Datos permanecen locales |

### ¿Por qué ejecutar LLMs localmente en IoT?

**Ventajas:**
- **Privacidad**: datos sensibles (ubicación, producción) no salen del edge.
- **Latencia**: no depende de conectividad a internet.
- **Costos**: sin pagos recurrentes por API.
- **Autonomía**: funciona offline.

**Desventajas:**
- **Recursos**: RAM, CPU, almacenamiento limitados.
- **Calidad**: respuestas menos sofisticadas.
- **Mantenimiento**: gestión de modelos, actualizaciones.

### Casos de uso realistas en IoT
- Generar alertas en lenguaje natural para operadores no técnicos.
- Resúmenes diarios automáticos (ej: "Hoy se detectaron 3 anomalías en riego, consumo normal de energía").
- Explicaciones de eventos: "La humedad bajó porque no llovió y el sistema de riego falló".

**NO es realista:**
- Razonamiento complejo o análisis avanzado.
- Generación en tiempo real crítico (<1s).
- Conversaciones largas o contexto extenso.

---

## 2. TinyLlama: arquitectura y capacidades

### Orígenes
- Proyecto open-source de la comunidad ([https://github.com/jzhang38/TinyLlama](https://github.com/jzhang38/TinyLlama))
- Basado en la arquitectura Llama de Meta
- Entrenado en ~3 trillones de tokens (menos que Llama-2)
- Objetivo: modelo ligero para dispositivos con recursos limitados

### Especificaciones técnicas
- **Parámetros:** 1.1B (comparado con 7B de Llama-2, 70B de Llama-2-70B)
- **Arquitectura:** Transformer decoder-only
- **Contexto:** ~2048 tokens (~1500 palabras)
- **Vocabulario:** ~32K tokens (subword)
- **Tamaño en disco:** ~637 MB (fp16), ~400 MB (cuantizado Q4)

### Capacidades
✅ **Funciona bien para:**
- Completar frases cortas
- Generar alertas o notificaciones breves (1-3 frases)
- Responder preguntas simples con contexto inmediato
- Traducción básica entre idiomas cercanos

❌ **Limitaciones:**
- Razonamiento matemático o lógico complejo
- Conversaciones largas (pierde contexto)
- Conocimiento especializado profundo
- Instrucciones multi-paso complejas

### Ejemplo de uso
**Prompt:**
```
Genera una alerta para el operador:
- Sensor: humedad del suelo
- Valor actual: 12%
- Valor normal: 40-60%
- Causa probable: fallo en bomba de riego
```

**Respuesta típica de TinyLlama:**
```
⚠️ ALERTA: Humedad del suelo críticamente baja (12%). 
Se detectó posible fallo en la bomba de riego. 
Revisar sistema inmediatamente para evitar daños en cultivos.
```

---

## 3. Ollama: framework para LLMs locales

### ¿Qué es Ollama?
- Framework open-source para ejecutar LLMs localmente
- Similar a Docker para modelos de lenguaje
- API HTTP sencilla (REST)
- Gestión automática de modelos (descarga, caché)

### Instalación
```bash
# Linux / macOS
curl -fsSL https://ollama.com/install.sh | sh

# Windows (desde ollama.com)
```

### Comandos básicos
```bash
# Descargar un modelo
ollama pull tinyllama

# Listar modelos instalados
ollama list

# Ejecutar modelo interactivamente
ollama run tinyllama

# Eliminar modelo
ollama rm tinyllama
```

### API HTTP

**Endpoint principal: `/api/generate`**
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "tinyllama",
  "prompt": "Resume en una frase: temperatura 45°C detectada",
  "stream": false
}'
```

**Respuesta:**
```json
{
  "model": "tinyllama",
  "created_at": "2026-02-12T10:30:00Z",
  "response": "Alerta: temperatura muy alta detectada.",
  "done": true
}
```

**Otros endpoints útiles:**
- `GET /api/tags`: listar modelos locales
- `POST /api/pull`: descargar modelo
- `DELETE /api/delete`: eliminar modelo

### Parámetros de generación

| Parámetro | Tipo | Descripción | Rango |
|-----------|------|-------------|-------|
| `temperature` | float | Aleatoriedad | 0.0 (determinista) - 1.0 (creativo) |
| `top_p` | float | Nucleus sampling | 0.0 - 1.0 |
| `top_k` | int | Top-k sampling | 1 - 100 |
| `num_predict` | int | Máximo tokens a generar | 1 - 2048 |
| `stop` | list | Secuencias de parada | [".", "\n\n"] |
| `stream` | bool | Respuesta incremental | true / false |

**Ejemplo con parámetros:**
```json
{
  "model": "tinyllama",
  "prompt": "Genera una alerta breve sobre humedad baja",
  "options": {
    "temperature": 0.7,
    "num_predict": 50
  }
}
```

---

## 4. Implementación de un cliente Python

### Diseño modular

**Componentes:**
1. **OllamaConfig**: configuración (host, port, model, timeouts)
2. **TinyLlamaClient**: lógica de interacción con Ollama
3. **config_from_settings()**: integración con `src.config`

### Implementación básica

```python
from dataclasses import dataclass
import requests
import logging

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class OllamaConfig:
    host: str
    port: int
    model: str
    timeout_s: float = 30.0
    
    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class TinyLlamaClient:
    def __init__(self, config: OllamaConfig):
        self._config = config
    
    def is_model_ready(self) -> bool:
        """Verifica si el modelo está disponible localmente."""
        url = f"{self._config.base_url}/api/tags"
        try:
            response = requests.get(url, timeout=self._config.timeout_s)
            response.raise_for_status()
            data = response.json()
            models = [m["name"].split(":")[0] for m in data.get("models", [])]
            return self._config.model in models
        except Exception as e:
            logger.warning("Error verificando modelo: %s", e)
            return False
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Genera texto a partir de un prompt."""
        if not prompt.strip():
            raise ValueError("El prompt no puede estar vacío")
        
        url = f"{self._config.base_url}/api/generate"
        payload = {
            "model": self._config.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature}
        }
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                timeout=self._config.timeout_s
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except Exception as e:
            logger.error("Error generando texto: %s", e)
            raise RuntimeError("No se pudo generar respuesta") from e
```

### Gestión de errores robusta

**Casos a manejar:**
- Ollama no está ejecutándose → `ConnectionError`
- Modelo no está descargado → descargar automáticamente con `pull_model()`
- Timeout → configurar timeouts generosos (30-60s)
- Respuesta vacía o malformada → validar y registrar

**Ejemplo con reintentos:**
```python
def ensure_model_available(self) -> bool:
    """Descarga el modelo si no está disponible."""
    if self.is_model_ready():
        return True
    
    for attempt in range(1, 3):
        logger.info("Descargando modelo (intento %d/2)", attempt)
        if self.pull_model() and self.is_model_ready():
            return True
        time.sleep(2)
    
    return False
```

---

## 5. Casos de uso en sistemas IoT agrícolas

### Caso 1: Alertas en lenguaje natural

**Problema:** alertas técnicas son difíciles de interpretar.

**Solución con LLM:**
```python
def generate_alert(anomaly: dict, client: TinyLlamaClient) -> str:
    prompt = f"""
    Genera una alerta breve en español para el operador:
    - Métrica: {anomaly['metric']}
    - Valor: {anomaly['value']} {anomaly['unit']}
    - Z-score: {anomaly['zscore']:.1f}
    - Nodo: {anomaly['node_id']}
    
    Máximo 2 frases.
    """
    return client.generate(prompt, temperature=0.5)
```

### Caso 2: Resúmenes diarios

**Prompt:**
```
Genera un resumen del día para el operador del sistema de riego NAIRA:
- 120 muestras recolectadas
- 3 anomalías detectadas (2 en humedad, 1 en temperatura)
- Sistema operativo: sin fallos críticos
- Recomendación: revisar sensor de temperatura del sector norte

Resume en 2-3 frases.
```

### Caso 3: Explicaciones de eventos

**Prompt:**
```
Explica por qué una humedad del suelo de 15% es anómala:
- Contexto: sistema de riego automático en cultivo de tomate
- Rango normal: 40-60%
- Última lectura normal: hace 6 horas (55%)
- Posibles causas: fallo en bomba, obstrucción en tubería

Respuesta breve y clara.
```

---

## 6. Evaluación de viabilidad en Raspberry Pi

### Requisitos de hardware

| Modelo | RAM | CPU | Viabilidad TinyLlama |
|--------|-----|-----|---------------------|
| RPi 3B | 1 GB | 4 núcleos ARMv8 | ❌ Insuficiente |
| RPi 4 (4GB) | 4 GB | 4 núcleos ARMv8 | ⚠️ Justo, lento |
| RPi 4 (8GB) | 8 GB | 4 núcleos ARMv8 | ✅ Funcional |
| RPi 5 (8GB) | 8 GB | 4 núcleos ARMv8.2 | ✅ Recomendado |

### Benchmarking típico

**Configuración:** RPi 4 (8GB), TinyLlama Q4 (cuantizado)

| Tarea | Tokens generados | Latencia |
|-------|-----------------|----------|
| Alerta breve | ~30 | 8-15s |
| Resumen | ~100 | 25-40s |
| Explicación | ~150 | 40-60s |

**Conclusión:** viable para alertas no urgentes, NO para interacción en tiempo real.

### Estrategias de optimización

1. **Modelos cuantizados:** usar Q4 o Q5 (reduce RAM y acelera)
2. **Caching:** guardar respuestas comunes (ej: alertas repetidas)
3. **Batch prompts:** procesar múltiples alertas juntas al final del día
4. **Alternativas ligeras:** Phi-2 (2.7B, mejor que TinyLlama pero más pesado)

---

## Resumen de tecnologías clave

| Componente | Tecnología | Propósito |
|------------|-----------|-----------|
| LLM ligero | TinyLlama (1.1B) | Generación de texto |
| Framework | Ollama | Ejecución local y gestión |
| Cliente | Python + requests | Integración con sistema IoT |
| Hardware | Raspberry Pi 4/5 (8GB) | Edge computing |

---

## Referencias recomendadas

- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [TinyLlama GitHub](https://github.com/jzhang38/TinyLlama)
- [Hugging Face: LLM Leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)
- Vaswani et al. (2017). "Attention Is All You Need". NeurIPS.
- Brown et al. (2020). "Language Models are Few-Shot Learners". NeurIPS.
