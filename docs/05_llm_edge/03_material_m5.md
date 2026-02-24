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
1. **`OllamaConfig`**: configuración (host, port, model, timeouts, num_ctx)
2. **`TinyLlamaClient`**: lógica de interacción con Ollama
3. **`config_from_settings()`**: integración con `src.config`
4. **`load_role(path)`**: carga del rol desde archivo externo
5. **`StubLlamaClient`** (`stub.py`): simulador sin Ollama

### Comparación de modelos con tag

Un problema habitual es que Ollama reporta el modelo con tag (`"tinyllama:latest"`) pero la config puede no incluirlo. La lógica correcta:

```python
def _model_matches(self, installed_name: str) -> bool:
    desired = (self._config.model or "").strip().lower()
    installed = (installed_name or "").strip().lower()
    if ":" in desired:
        return installed == desired        # tag explícito: coincidencia exacta
    return installed.split(":", 1)[0] == desired  # sin tag: acepta cualquier variante
```

Esto evita falsos positivos: si configuras `"tinyllama:1.1b"` no se acepta `"tinyllama:latest"`.

### Implementación completa

```python
from dataclasses import dataclass
from pathlib import Path
import requests, logging, json, time

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class OllamaConfig:
    host: str
    port: int
    model: str
    timeout_s: float = 120.0   # generoso en RPi
    pull_retries: int = 2
    retry_backoff_s: float = 2.0

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


def load_role(path: str | Path | None = None) -> str:
    """Carga el rol del modelo desde un archivo de texto."""
    if not path:
        return ""
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except OSError as exc:
        logger.warning("No se pudo cargar el rol desde '%s': %s", path, exc)
        return ""


class TinyLlamaClient:
    def __init__(self, config: OllamaConfig):
        self._config = config

    def is_model_ready(self) -> bool:
        url = f"{self._config.base_url}/api/tags"
        try:
            r = requests.get(url, timeout=self._config.timeout_s)
            r.raise_for_status()
            models = r.json().get("models") or []
            r.close()
            return any(self._model_matches(m.get("name", "")) for m in models)
        except Exception as exc:
            logger.warning("No se pudo consultar Ollama: %s", exc)
            return False

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        options: dict | None = None,
        stream: bool = False,
    ) -> str:
        if not prompt.strip():
            raise ValueError("prompt no puede estar vacío")
        payload = {"model": self._config.model, "prompt": prompt, "stream": stream}
        if system:
            payload["system"] = system
        if options:
            payload["options"] = options
        try:
            r = requests.post(
                f"{self._config.base_url}/api/generate",
                json=payload,
                timeout=self._config.timeout_s,
                stream=stream,
            )
            r.raise_for_status()
        except Exception as exc:
            raise RuntimeError("No se pudo generar respuesta") from exc
        if stream:
            try:
                chunks = [c.get("response", "") for c in self._iter_stream(r)]
            finally:
                r.close()
            return "".join(chunks).strip()
        data = r.json()
        r.close()
        return str(data.get("response", "")).strip()

    def _model_matches(self, installed_name: str) -> bool:
        desired = (self._config.model or "").strip().lower()
        installed = (installed_name or "").strip().lower()
        if ":" in desired:
            return installed == desired
        return installed.split(":", 1)[0] == desired
```

### Rol configurable (`role.md`)

El rol define la personalidad y especialización del modelo. Se guarda en `src/llm/role.md` y se carga en cada ciclo:

```python
role = load_role(settings.ollama_role_path)
response = client.generate(prompt, system=role, options={"num_ctx": 4096})
```

**Ejemplo de `role.md`:**
```
Eres un experto en análisis de series temporales aplicadas a la agricultura de precisión.
Interpreta datos de sensores (temperatura, humedad del suelo, caudal) y proporciona
diagnósticos claros y recomendaciones accionables. Respuestas cortas y directas.
```

El campo `system` de la API de Ollama inyecta este texto antes del prompt del usuario, condicionando el comportamiento del modelo sin consumir tokens del historial visible.

### Parámetro `num_ctx`

Controla el número de tokens que el modelo puede considerar como contexto:

| `num_ctx` | RAM aprox. (qwen2.5:1.5b) | Uso recomendado |
|---|---|---|
| 512 | mínimo | Alertas muy cortas |
| 2048 | ~1.2 GB | Uso general |
| 4096 | ~1.5 GB | Análisis con datos (por defecto) |
| 8192 | ~2.0 GB | Series temporales largas |

```python
options = {"num_ctx": settings.ollama_num_ctx}  # NAIRA_OLLAMA_NUM_CTX=4096
response = client.generate(prompt, system=role, options=options)
```

### Simulador (`stub.py`)

Permite desarrollar y testear sin Ollama activo:

```python
class StubLlamaClient:
    def generate(self, prompt: str, system: str | None = None, **kwargs) -> str:
        keywords = {"anomaly": "Anomalía detectada. Verificar calibración.",
                    "irrigation": "Condiciones adecuadas para iniciar riego."}
        for key, msg in keywords.items():
            if key in prompt.lower():
                return msg
        return "Sistema operando dentro de parámetros normales."

def get_client(sim: bool = True):
    if sim:
        return StubLlamaClient()
    return TinyLlamaClient(config_from_settings())
```

### Gestión de errores robusta

**Casos a manejar:**
- Ollama no está ejecutándose → `ConnectionError`
- Modelo no está descargado → descargar automáticamente con `ensure_model_available()`
- Timeout en RPi → configurar `NAIRA_OLLAMA_TIMEOUT=120` (o más)
- Respuesta vacía o malformada → `response.close()` en `finally`

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

## 5b. Interfaz Streamlit (`llm_app.py`)

### Estructura
```
streamlit run src/llm/llm_app.py
```

**Sidebar:**
- Toggle modo simulado (usa `StubLlamaClient` si activo)
- Host, puerto, modelo, timeout, num_ctx
- Estado del modelo en tiempo real + botón de descarga

**Panel principal:**
1. **Rol del modelo** (colapsado): muestra y permite editar el contenido de `role.md` en sesión
2. **Contexto / Datos**: área para pegar datos de sensores (JSON, CSV, texto)
3. **Historial de chat**: burbujas usuario/asistente con `st.chat_message`

**Construcción del prompt:**
```python
if context:
    full_prompt = f"Contexto:\n{context}\n\nPregunta: {prompt}"
else:
    full_prompt = prompt

response = client.generate(full_prompt, system=role, options={"num_ctx": num_ctx})
```

---

## 6. Selección de modelo para Raspberry Pi

| Modelo | Tamaño | RAM | Calidad (datos estructurados) | Recomendado |
|--------|--------|-----|-------------------------------|-------------|
| `tinyllama` | 608 MB | ~1.2 GB | ⭐⭐ | Solo si RPi con <4 GB |
| `qwen2.5:0.5b` | ~400 MB | ~0.9 GB | ⭐⭐⭐ | RPi muy limitada |
| `qwen2.5:1.5b` | 940 MB | ~1.6 GB | ⭐⭐⭐⭐ | **Recomendado** |
| `llama3.2:1b` | ~700 MB | ~1.3 GB | ⭐⭐⭐ | Alternativa a qwen |
| `phi3.5` (3.8B) | ~2.2 GB | ~4 GB | ⭐⭐⭐⭐⭐ | Solo RPi 5 (8 GB) |

**`qwen2.5:1.5b`** es el balance óptimo para análisis de datos estructurados en RPi 4/5: sigue instrucciones con precisión y entiende bien tablas, JSON y series numéricas.

---

## Resumen de tecnologías clave

| Componente | Tecnología | Propósito |
|------------|-----------|-----------|
| LLM ligero | qwen2.5:1.5b (recomendado) | Generación de texto contextual |
| Framework | Ollama | Ejecución local y gestión de modelos |
| Cliente | Python + requests | Integración con el nodo NAIRA |
| Simulador | StubLlamaClient | Desarrollo y tests sin hardware |
| Interfaz | Streamlit | Chat interactivo con el LLM |
| Hardware | Raspberry Pi 4/5 (4-8 GB) | Edge computing |

---

## Referencias recomendadas

- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [TinyLlama GitHub](https://github.com/jzhang38/TinyLlama)
- [Hugging Face: LLM Leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)
- Vaswani et al. (2017). "Attention Is All You Need". NeurIPS.
- Brown et al. (2020). "Language Models are Few-Shot Learners". NeurIPS.
