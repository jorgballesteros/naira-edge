# Módulo 5 · Ejercicios

## Sesión 1 — Instalación y primeros pasos

### Ejercicio 1 · Instalación de Ollama
**Objetivo:** configurar el entorno para ejecutar LLMs localmente.

**Tareas:**
1. Instalar Ollama en el sistema:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
2. Verificar instalación:
   ```bash
   ollama --version
   ```
3. Descargar TinyLlama:
   ```bash
   ollama pull tinyllama
   ```
4. Listar modelos instalados:
   ```bash
   ollama list
   ```
5. Probar generación interactiva:
   ```bash
   ollama run tinyllama
   # Prompt: "Resume en una frase: temperatura 45°C detectada"
   ```

**Entregables:**
- Captura de pantalla de `ollama list` mostrando tinyllama instalado.
- Captura de la respuesta generada en modo interactivo.
- Breve comentario sobre la calidad de la respuesta (¿coherente? ¿útil?).

---

### Ejercicio 2 · Configuración y conexión básica
**Objetivo:** implementar la configuración para el cliente Python.

**Tareas:**
1. Crear `src/llm/ollama_client.py`.
2. Implementar dataclass `OllamaConfig`:
   ```python
   @dataclass(frozen=True)
   class OllamaConfig:
       host: str
       port: int
       model: str
       timeout_s: float = 30.0
       
       @property
       def base_url(self) -> str:
           return f"http://{self.host}:{self.port}"
   ```
3. Implementar función `config_from_settings()` que lea de `src.config.Settings`:
   ```python
   def config_from_settings(settings=None) -> OllamaConfig:
       cfg = settings or load_settings()
       return OllamaConfig(
           host=cfg.ollama_host,
           port=cfg.ollama_port,
           model=cfg.ollama_model,
           timeout_s=cfg.ollama_timeout_s
       )
   ```
4. Añadir variables de entorno en `.env` (si no existen):
   ```
   NAIRA_OLLAMA_HOST=127.0.0.1
   NAIRA_OLLAMA_PORT=11434
   NAIRA_OLLAMA_MODEL=tinyllama
   NAIRA_OLLAMA_TIMEOUT=30
   ```

**Entregables:**
- Código funcional de `OllamaConfig` y `config_from_settings()`.
- Script de prueba que imprima la configuración cargada.

---

### Ejercicio 3 · Verificación de modelo disponible
**Objetivo:** implementar lógica para verificar si el modelo está descargado.

**Tareas:**
1. Implementar método `TinyLlamaClient.is_model_ready()`:
   - Consultar `GET /api/tags`
   - Parsear respuesta JSON
   - Verificar si el modelo configurado está en la lista
2. Probar con modelo existente (tinyllama) y modelo inexistente (ej: "fake-model").

**Entregables:**
- Código funcional de `is_model_ready()`.
- Test que muestre:
  ```
  tinyllama: ✓ disponible
  fake-model: ✗ no disponible
  ```

---

## Sesión 2 — Cliente completo y generación de texto

### Ejercicio 4 · Generación de texto básica
**Objetivo:** implementar el método principal de generación.

**Tareas:**
1. Implementar `TinyLlamaClient.generate(prompt, temperature)`:
   - Validar que el prompt no esté vacío
   - Construir payload JSON para `POST /api/generate`
   - Enviar petición con timeout configurado
   - Parsear respuesta y extraer texto generado
   - Gestionar errores (conexión, timeout, JSON inválido)
2. Probar con diferentes prompts:
   - "Resume: temperatura 45°C en invernadero"
   - "Genera alerta: humedad suelo 12%, normal 40-60%"
   - "Explica por qué 12% humedad es crítico para tomates"

**Entregables:**
- Código funcional de `generate()`.
- Tabla con 3 prompts y sus respuestas generadas.
- Comentario sobre:
  - Tiempo de generación observado.
  - Calidad de las respuestas (1-5 estrellas).
  - ¿Son útiles para operadores no técnicos?

---

### Ejercicio 5 · Descarga automática de modelos
**Objetivo:** implementar lógica para descargar modelos faltantes.

**Tareas:**
1. Implementar `TinyLlamaClient.pull_model()`:
   - Enviar petición a `POST /api/pull` con `{"name": model}`
   - Gestionar respuesta stream (líneas NDJSON)
   - Parsear estado de descarga
   - Retornar `True` si éxito, `False` si falla
2. Implementar `TinyLlamaClient.ensure_model_available()`:
   - Si modelo disponible → retornar `True`
   - Si no disponible → intentar descarga (hasta 2 reintentos)
   - Retornar `True` si finalmente está disponible
3. Probar eliminando el modelo y ejecutando `ensure_model_available()`:
   ```bash
   ollama rm tinyllama  # Eliminar modelo
   python test_ensure_model.py  # Debería descargarlo automáticamente
   ```

**Entregables:**
- Código funcional de `pull_model()` y `ensure_model_available()`.
- Log de ejecución mostrando:
  - Modelo no disponible
  - Iniciando descarga
  - Descarga completada
  - Modelo disponible

---

### Ejercicio 6 · Integración con detección de anomalías
**Objetivo:** generar alertas en lenguaje natural a partir de anomalías detectadas.

**Tareas:**
1. Crear función `generate_anomaly_alert(anomaly: dict, client: TinyLlamaClient) -> str`:
   ```python
   def generate_anomaly_alert(anomaly: dict, client: TinyLlamaClient) -> str:
       prompt = f"""
       Genera una alerta breve en español para el operador del sistema de riego:
       - Métrica: {anomaly['metric']}
       - Valor actual: {anomaly['value']} {anomaly['unit']}
       - Valor esperado: {anomaly.get('expected_range', 'no disponible')}
       - Severidad: {anomaly.get('severity', 'media')}
       
       Máximo 2 frases. Sé directo y claro.
       """
       return client.generate(prompt, temperature=0.5)
   ```
2. Probar con datos de anomalías reales del Módulo 4.
3. Comparar alertas:
   - Alerta técnica (del detector)
   - Alerta generada por LLM

**Entregables:**
- Código funcional de `generate_anomaly_alert()`.
- Tabla comparativa:
  ```
  | Anomalía | Alerta técnica | Alerta LLM |
  |----------|---------------|------------|
  | soil_moisture_pct=12, zscore=4.2 | "soil_moisture_pct anomaly detected" | "⚠️ Humedad crítica (12%). Revisar riego urgente." |
  ```
- Opinión: ¿qué versión es más útil? ¿por qué?

---

### Ejercicio 7 · Benchmarking de latencia
**Objetivo:** medir el rendimiento de TinyLlama en Raspberry Pi.

**Tareas:**
1. Crear script `benchmark_llm.py` que:
   - Ejecute 10 generaciones con prompts de diferentes longitudes (corto, medio, largo)
   - Mida tiempo de cada generación
   - Calcule estadísticas: media, min, max, desviación estándar
2. Ejecutar en RPi (o máquina de desarrollo si no hay RPi disponible).
3. Documentar:
   - Hardware usado (CPU, RAM)
   - Modelo usado (tinyllama, tinyllama:q4, etc.)
   - Resultados de latencia

**Entregables:**
- Script de benchmarking.
- Tabla de resultados:
  ```
  | Longitud prompt | Tokens generados | Latencia media | Min | Max |
  |----------------|-----------------|---------------|-----|-----|
  | Corto (~10 palabras) | ~30 | 12.3s | 10.1s | 15.2s |
  | Medio (~30 palabras) | ~100 | 38.5s | 35.0s | 42.1s |
  | Largo (~50 palabras) | ~150 | 58.7s | 55.3s | 63.4s |
  ```
- Conclusión: ¿es viable para alertas urgentes? ¿para resúmenes diarios?

---

## Sesión 3 — Rol, interfaz Streamlit y selección de modelo

### Ejercicio 8 · Rol configurable del modelo
**Objetivo:** condicionar el comportamiento del LLM mediante un archivo de rol externo.

**Tareas:**
1. Crear `src/llm/role.md` con el rol de experto en series temporales agrícolas:
   - Especialización: anomalías estadísticas, balance hídrico, sensores de campo.
   - Estilo: respuestas cortas, orientadas a la acción, en español.
2. Implementar `load_role(path: str | Path | None) -> str`:
   - Leer el archivo con `Path.read_text(encoding="utf-8")`.
   - Devolver cadena vacía y registrar `logger.warning` si el archivo no existe.
3. Añadir parámetro `system: str | None` a `TinyLlamaClient.generate()` y pasarlo al payload de Ollama.
4. Añadir `NAIRA_OLLAMA_ROLE_PATH` a `src/config.py` apuntando a `role.md` por defecto.
5. Probar el mismo prompt con y sin rol:
   ```python
   r1 = client.generate("Humedad suelo: 12%. ¿Qué hago?")
   r2 = client.generate("Humedad suelo: 12%. ¿Qué hago?", system=load_role("src/llm/role.md"))
   ```

**Entregables:**
- Código de `load_role()` y modificación de `generate()`.
- Comparativa de respuestas con y sin rol (tabla).
- Archivo `role.md` con el rol creado.

---

### Ejercicio 9 · Simulador `stub.py`
**Objetivo:** implementar un simulador que permite desarrollar y testear sin Ollama.

**Tareas:**
1. Crear `src/llm/stub.py` con `StubLlamaClient`:
   - Mismos métodos que `TinyLlamaClient`: `is_model_ready`, `pull_model`, `ensure_model_available`, `generate`.
   - `generate()` responde según keywords en el prompt (p. ej. `"anomaly"`, `"irrigation"`).
2. Implementar `get_client(sim: bool) -> StubLlamaClient | TinyLlamaClient`.
3. Verificar que los tests del módulo pasan con el simulador.
4. Integrar en `src/main.py`: usar `get_client(sim=args.sim)` en el pipeline.

**Entregables:**
- Código de `StubLlamaClient` y `get_client()`.
- Demostración de `python -m src.main --sim` mostrando la respuesta del LLM en el log.

---

### Ejercicio 10 · Interfaz de chat con Streamlit
**Objetivo:** construir una interfaz visual para interactuar con el LLM local.

**Tareas:**
1. Crear `src/llm/llm_app.py` con:
   - Sidebar: toggle modo simulado, host, puerto, modelo, timeout, num_ctx.
   - Indicador de estado del modelo (verde/rojo) con botón de descarga.
   - Panel "Rol del modelo": carga `role.md`, editable en sesión.
   - Panel "Contexto / Datos": área para pegar datos de sensores.
   - Historial de chat con `st.chat_message`.
2. El prompt enviado al modelo debe incluir el contexto si está relleno:
   ```
   Contexto:
   <datos pegados>

   Pregunta: <consulta del usuario>
   ```
3. Abrir el firewall si es necesario:
   ```bash
   sudo ufw allow 8501
   ```
4. Probar con datos reales: pegar una lectura de sensores en el panel de contexto y preguntar al modelo.

**Entregables:**
- Código funcional de `llm_app.py`.
- Captura de una conversación con datos de sensores en el contexto.

---

### Ejercicio 11 · Selección de modelo y benchmarking
**Objetivo:** comparar TinyLlama y qwen2.5:1.5b para decidir cuál usar en producción.

**Tareas:**
1. Descargar `qwen2.5:1.5b`:
   ```bash
   ollama pull qwen2.5:1.5b
   ```
2. Ejecutar el mismo prompt con ambos modelos:
   ```
   Datos: temperatura_aire=34.2°C, humedad_suelo=18%, caudal=0.0 l/min.
   Describe el estado del sistema y recomienda una acción.
   ```
3. Medir latencia de cada respuesta (usar `time.time()` o el campo `total_duration` de la respuesta Ollama).
4. Evaluar calidad subjetiva (1-5) en:
   - Coherencia con el rol definido.
   - Concisión (¿responde en 1-2 frases?).
   - Utilidad para un operador no técnico.

**Entregables:**
- Tabla comparativa: modelo, tamaño, latencia media, calidad (1-5).
- Justificación de la elección para el proyecto.

---

## Sesión 4 (opcional) — Caso práctico y optimización

### Ejercicio 12 · Sistema de alertas inteligente
**Objetivo:** integrar LLM en pipeline completo de detección y alerta.

**Descripción:**
Construir un sistema que:
1. Detecte anomalías (usando detectores del Módulo 4).
2. Clasifique severidad:
   - **Crítico:** `|zscore| >= 4.0` → alerta inmediata (sin LLM, plantilla rápida)
   - **Advertencia:** `3.0 <= |zscore| < 4.0` → alerta con LLM
   - **Info:** `2.5 <= |zscore| < 3.0` → log solamente
3. Para advertencias: genere alerta con LLM y envíe por Telegram (o log si no hay Telegram).
4. Al final del día: genere resumen con LLM de todas las anomalías detectadas.

**Componentes técnicos:**
- `src/models/zscore_anomaly.py`: detección
- `src/llm/ollama_client.py`: generación de alertas
- `src/diagnostics/telegram_alert.py` (opcional): envío

**Entregables:**
- Código completo del sistema.
- Demo con datos reales o simulados (al menos 10 muestras, 2-3 anomalías).
- Capturas de:
  - Alerta crítica (plantilla rápida)
  - Alerta advertencia (generada por LLM)
  - Resumen diario
- Informe técnico (2-3 páginas) con:
  - Arquitectura del sistema
  - Flujo de decisión (diagrama)
  - Análisis de latencias
  - Evaluación crítica: ¿vale la pena la complejidad del LLM?

---

### Ejercicio 13 · Optimización con modelos cuantizados
**Objetivo:** evaluar trade-off entre calidad y velocidad.

**Tareas:**
1. Descargar versiones cuantizadas de TinyLlama:
   ```bash
   ollama pull tinyllama:latest    # FP16 (~637 MB)
   ollama pull tinyllama:q4_0      # Q4 (~400 MB)
   ollama pull tinyllama:q5_0      # Q5 (~500 MB)
   ```
2. Ejecutar el mismo prompt con cada versión.
3. Medir:
   - Tiempo de generación
   - Uso de RAM (usar `htop` o similar)
   - Calidad de la respuesta (evaluación subjetiva 1-5)

**Entregables:**
- Tabla comparativa:
  ```
  | Versión | Tamaño | RAM | Latencia | Calidad |
  |---------|--------|-----|----------|---------|
  | FP16 | 637MB | 2.8GB | 18s | 5/5 |
  | Q4 | 400MB | 1.9GB | 12s | 4/5 |
  | Q5 | 500MB | 2.2GB | 14s | 4.5/5 |
  ```
- Recomendación justificada: ¿cuál usar en producción?

---

### Ejercicio 14 · Evaluación crítica
**Objetivo:** reflexionar sobre la viabilidad de LLMs en edge.

**Tareas:**
Escribir un ensayo breve (1-2 páginas) respondiendo:
1. ¿En qué casos un LLM ligero aporta valor real?
2. ¿Cuándo es mejor usar plantillas estáticas simples?
3. ¿Cuáles son los principales problemas técnicos encontrados?
4. ¿Qué mejoras futuras harían los LLMs más viables en IoT?

**Criterios de evaluación:**
- Argumentos claros basados en experiencia práctica.
- Honestidad sobre limitaciones (no vender humo).
- Propuestas constructivas.

---

## Criterios de evaluación

| Criterio | Peso |
|----------|------|
| Instalación y configuración correcta | 10% |
| Cliente funcional (generate, pull, _model_matches) | 20% |
| Simulador `stub.py` funcional | 10% |
| Rol configurable (`role.md` + `system` en generate) | 15% |
| Interfaz Streamlit con chat y contexto | 15% |
| Integración en pipeline `main.py` | 10% |
| Benchmarking y selección de modelo justificada | 10% |
| Evaluación crítica y reflexión | 10% |

**Nota:** el caso práctico final puede desarrollarse en grupos de 2-3 personas.
