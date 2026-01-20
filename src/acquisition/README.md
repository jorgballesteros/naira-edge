# 📡 Módulo de Adquisición de Datos (Acquisition)

## 🎯 Descripción General

Módulo responsable de **leer datos sensoriales** del nodo Raspberry Pi y almacenarlos en una base de datos SQLite. Comunica con un **Arduino MKR** conectado por **puerto serie (USB)** que transmite datos de **3 sensores**:

1. 🌡️ **Temperatura del aire** (`temperature X.XX` en °C)
2. 💧 **Humedad del suelo** (`moisture X` en %)
3. ☀️ **Luz/Luminosidad** (`light X.XX` en lux)

El módulo soporta **modo real** (hardware con Arduino) y **modo simulado** (para desarrollo/testing sin hardware).

---

## 📦 Arquitectura

```
src/acquisition/
├── README.md                         ← Este archivo
├── MIGRATION_SCRIPTS_TO_TESTS.md     ← Documentación de migración
├── TESTS_SUMMARY.md                  ← Resumen de suite de tests
├── run_tests.sh                      ← Script helper para ejecutar tests
├── test_serial_reader.py             ← 🧪 Suite de 37 tests (nuevo)
├── db.py                             ← Base de datos SQLite
├── collector.py                      ← Colector de puerto serie (principal)
├── stub.py                           ← Simulador (default)
├── example_db_usage.py               ← Ejemplos de uso
├── listen_serial.py                  ← Lee puerto serie (raw - debug)
├── temp_serial.py                    ← Parsing de temperatura (debug)
├── light_serial.py                   ← Parsing de luz (debug)
├── test_api.py                       ← Ejemplo de API externa (demo)
├── __init__.py                       ← Exports del módulo
└── __pycache__/
```

### Módulos Componentes (Flujo Principal)

#### `db.py` (Base de Datos SQLite) ⭐
- **`SensorDatabase`**: Gestor de BD con operaciones CRUD
- **Tablas principales**:
  - `sensor_samples`: Muestras sensoriales crudas
  - `daily_aggregates`: Agregaciones diarias (min, max, avg)
  - `device_status`: Estado del dispositivo (CPU, RAM, temp)
- **Métodos clave**:
  - `insert_sample()`: Insertar una muestra
  - `insert_samples_batch()`: Insertar múltiples muestras
  - `get_samples()`: Consultar muestras recientes
  - `get_samples_time_range()`: Consultar por rango de tiempo
  - `compute_daily_aggregate()`: Calcular agregaciones diarias
  - `get_stats()`: Estadísticas de la BD
  - `delete_old_samples()`: Limpieza de datos antiguos
- **Ubicación**: `/home/naira/NAIRA/naira-edge/data/naira_sensors.db`
- **Índices optimizados**: `ts`, `metric`, `node_id`

#### `collector.py` (Colector de Puerto Serie) ⭐
- **`SerialCollector`**: Lee Arduino, parsea, normaliza y guarda en BD
- **Métodos clave**:
  - `connect()`: Abre puerto serie
  - `read_line()`: Lee una línea del puerto
  - `parse_line()`: Parsea formato "sensor_type value"
  - `normalize_sample()`: Convierte a estructura NAIRA
  - `read_and_store_one()`: Lee una línea y la guarda en BD
  - `read_and_store_loop()`: Bucle continuo de lectura
  - `get_last_values()`: Caché de últimos valores
  - `get_db_stats()`: Estadísticas de la BD
- **CLI**: `collect_cli()` para uso desde terminal
- **Validación**: Checks de rango para detectar datos defectuosos

#### `example_db_usage.py` (Ejemplos de Uso) ⭐
- 6 ejemplos prácticos completos:
  1. Insertar muestras
  2. Consultar muestras recientes
  3. Consultar rango de tiempo
  4. Estadísticas de la BD
  5. Insertar estado del dispositivo
  6. Exportar a JSON
- Ejecutable: `python -m src.acquisition.example_db_usage`

### Módulos de Utilidad (Debugging/Ejemplos)

#### `stub.py` (Simulador - Default)
- Devuelve datos simulados aleatorios
- **No requiere hardware**
- Función: `read_sensor(sim: bool = True) -> Dict[str, float]`

#### `listen_serial.py` (Lectura Raw - Debug)
- Lee líneas crudas del puerto serie
- Útil para verificar qué envía el Arduino
- Ejecutable: `python src/acquisition/listen_serial.py`

#### `temp_serial.py` y `light_serial.py` (Parsing - Debug)
- Ejemplos de parsing específico de sensores
- Útiles para troubleshooting
- No usados en flujo principal

#### `test_api.py` (Ejemplo - Demo)
- Demostración de lectura de API externa (WorldTimeAPI)
- Ejemplo de pattern: fetch → parse → consolidate
- No usado en flujo de adquisición principal

---

## 🔌 Comunicación Arduino MKR → Raspberry Pi

### Conexión Física

```
Arduino MKR ← USB Serial Cable → Raspberry Pi
             (9600 baud, 8N1)
```

### Protocolo de Datos Esperado

El Arduino MKR envía líneas de texto en el puerto serie. Cada sensor envía su dato en formato:

```
moisture 800
light 5.00
temperature 18.96
```

**Características del Protocolo**:
- Una línea por sensor por ciclo de lectura
- Separador: espacio único
- Terminador: `\n` (newline/salto de línea)
- Baudrate: 9600 bps
- Sin handshake especial requerido
- Sin checksum o validación en protocolo

### Mapeo de Sensores

| Línea Arduino | Métrica Interna | Unidad | Rango Típico | Source |
|---|---|---|---|---|
| `moisture X` | `humedad_suelo` | % (0-1023) | 400-800 | `suelo` |
| `light X.XX` | `luminosidad` | lux (0-1023) | 0-1023 | `meteo` |
| `temperature X.XX` | `temp_aire` | °C | 0-50°C | `meteo` |

---

## 📋 Contrato de Datos Normalizado

Todos los sensores **deben retornar** esta estructura (dict):

```python
{
  "ts": "2026-01-15T14:30:45.123Z",    # ISO8601-UTC
  "node_id": "naira-node-001",          # Desde config
  "source": "meteo|suelo|riego|light",  # Tipo de dato
  "metric": "temp_aire|humedad|caudal", # Métrica específica
  "value": 23.45,                       # Valor numérico
  "unit": "°C|%|lux|l/min",             # Unidad
  "quality": "ok|suspect|bad"           # Estado del dato
}
```

**Ejemplo completo**:
```python
{
  "ts": "2026-01-15T14:30:45.123Z",
  "node_id": "naira-node-001",
  "source": "meteo",
  "metric": "temp_aire",
  "value": 23.45,
  "unit": "°C",
  "quality": "ok"
}
```

---

## 🚀 Uso del Colector

### Opción 1: Línea de Comandos (CLI) ⭐ Recomendado

**Uso básico - Leer 50 líneas:**
```bash
cd /home/naira/NAIRA/naira-edge
python -m src.acquisition.collector --count 50
```

**Lectura continua (sin límite):**
```bash
python -m src.acquisition.collector
# Presiona Ctrl+C para detener
```

**Con opciones personalizadas:**
```bash
python -m src.acquisition.collector \
    --port /dev/ttyACM0 \
    --baudrate 9600 \
    --node-id "naira-node-001" \
    --count 100 \
    --log-level DEBUG
```

**Output esperado:**
```
2026-01-15 14:30:45,123 [INFO] Conectado a /dev/ttyACM0 @ 9600 baud
2026-01-15 14:30:45,234 [INFO] Guardado: temp_aire=18.96 °C
2026-01-15 14:30:45,345 [INFO] Guardado: luminosidad=5.00 lux
2026-01-15 14:30:45,456 [INFO] Guardado: humedad_suelo=800 %

✓ 3 muestras guardadas
Stats: {'total_samples': 3, 'total_metrics': 3, ...}
```

### Opción 2: Desde Python

```python
from src.acquisition.collector import SerialCollector

collector = SerialCollector(
    port="/dev/ttyACM0",
    baudrate=9600,
    node_id="naira-node-001"
)

if collector.connect():
    # Leer 100 líneas y guardarlas
    saved = collector.read_and_store_loop(count=100)
    print(f"Guardadas {saved} muestras")
    
    # Obtener últimos valores
    last_values = collector.get_last_values()
    print(f"Últimos valores: {last_values}")
    
    collector.disconnect()
```

### Opción 3: Modo Simulado (Sin Arduino)

```bash
# Usar el simulador (stub.py)
cd /home/naira/NAIRA/naira-edge
source venv/bin/activate
python -m src.main --sim --log INFO
```

**Ventajas del modo simulado:**
- ✅ No requiere Arduino
- ✅ No requiere puerto serie
- ✅ Genera datos aleatorios realistas
- ✅ Útil para testing/debugging

---

## 🔧 Debugging: Herramientas Auxiliares

### Leer Puerto Serie Raw (Debugging)

Para ver exactamente qué envía el Arduino:

```bash
python src/acquisition/listen_serial.py
```

**Output esperado:**
```
Leyendo temperatura desde /dev/ttyACM0...
moisture 800
light 5.00
temperature 18.96
moisture 805
light 4.98
...
```

### Identificar Puerto del Arduino

En Raspberry Pi:

```bash
# Listar puertos serie disponibles
ls /dev/tty*

# Si no ves /dev/ttyACM0, prueba:
ls /dev/ttyUSB*

# Usar dmesg para ver eventos USB
dmesg | tail -20
```

# Ver permisos
ls -la /dev/ttyACM0
```

### Cambiar Puerto (si es necesario)

1. Edita el archivo correspondiente (ej: `temp_serial.py`)
2. Cambia: `PORT = "/dev/ttyUSB0"`
3. Guarda y ejecuta

### Permisos del Puerto

Si obtienes error `Permission denied`:

```bash
# Añade tu usuario al grupo dialout
sudo usermod -a -G dialout naira

# Logout y login nuevamente
exit
```

---

## 📊 Flujo de Datos Completo

### Modo Simulado
```
stub.py:read_sensor()
    ↓
Genera valores aleatorios
    ↓
Retorna dict normalizado
    ↓
processing/ → comms/ → diagnostics/
```

### Modo Real (Arduino + Puerto Serie)
```
Arduino MKR (sensores físicos)
    ↓
Puerto serie /dev/ttyACM0 (9600 baud)
    ↓
listen_serial.py (lectura raw)
    ↓
temp_serial.py / light_serial.py (parsing)
    ↓
Normalización a dict
    ↓
processing/ → comms/ → diagnostics/
```

---

## 🔍 Estructura de Datos Dentro del Módulo

### Diccionario de Salida (read_sensor)

```python
def read_sensor(sim: bool = True) -> Dict[str, float]:
    return {
        "air_temp_c": 23.45,           # Temperatura en °C
        "air_humidity_pct": 65.2,      # Humedad en %
        "soil_moisture": 0.45,         # Humedad suelo (0-1)
    }
```

**Notas**:
- Si `sim=True`: devuelve valores simulados
- Si `sim=False`: intenta leer hardware (placeholder)
- Siempre devuelve float
- Siempre devuelve los 3 sensores

---

## ⚙️ Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `NAIRA_NODE_ID` | ID del nodo | `"naira-node-001"` |
| `NAIRA_SERIAL_PORT` | Puerto serie | `"/dev/ttyACM0"` |
| `NAIRA_SERIAL_BAUDRATE` | Baudrate | `9600` |
| `NAIRA_SIM` | Modo simulado | `1` (activado) |

---

## 🆘 Solución de Problemas

### ❌ `FileNotFoundError: [Errno 2] No such file or directory: '/dev/ttyACM0'`

**Causa**: Puerto serie no existe o Arduino no está conectado.

**Soluciones**:
1. Verifica conexión USB: `ls /dev/tty*`
2. Prueba `/dev/ttyUSB0` en su lugar
3. Si no ves nada, reconecta el USB y espera 2 segundos
4. Usa modo simulado: `--sim`

---

### ❌ `PermissionError: [Errno 13] Permission denied`

**Causa**: Usuario sin permisos en el puerto serie.

**Solución**:
```bash
sudo usermod -a -G dialout naira
# Logout y login nuevamente
```

---

### ❌ Arduino conectado pero no recibe datos

**Checklist**:
- [ ] ¿El Arduino MKR está programado para enviar datos?
- [ ] ¿El baudrate es 9600?
- [ ] ¿El cable USB es de datos (no solo de carga)?
- [ ] ¿Has probado `listen_serial.py`?
- [ ] ¿El Arduino está alimentado?

---

### ✅ Usar Modo Simulado (Recomendado para Desarrollo)

```bash
python -m src.main --sim --log INFO
```

**Beneficios**:
- No requiere Arduino
- Genera datos realistas
- Depuración sin hardware

---

## � Base de Datos SQLite

El módulo incluye almacenamiento persistente de datos en SQLite con **3 tablas principales**:

### Tabla: `sensor_samples`

Almacena todas las muestras sensoriales crudas:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER | ID único (auto-increment) |
| `ts` | TEXT | Timestamp ISO8601-UTC |
| `node_id` | TEXT | ID del nodo |
| `source` | TEXT | Fuente (meteo, suelo, riego) |
| `metric` | TEXT | Tipo de métrica |
| `value` | REAL | Valor numérico |
| `unit` | TEXT | Unidad (°C, %, lux) |
| `quality` | TEXT | Calidad (ok, suspect, bad) |
| `created_at` | TEXT | Timestamp de inserción |

**Índices**: `ts`, `metric`, `node_id`

### Tabla: `daily_aggregates`

Agregaciones diarias (min, max, promedio):

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `date` | TEXT | Fecha YYYY-MM-DD |
| `node_id` | TEXT | ID del nodo |
| `metric` | TEXT | Tipo de métrica |
| `value_min` | REAL | Mínimo del día |
| `value_max` | REAL | Máximo del día |
| `value_avg` | REAL | Promedio del día |
| `value_count` | INTEGER | Número de muestras |

### Tabla: `device_status`

Estado del dispositivo (CPU, RAM, temperatura):

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `ts` | TEXT | Timestamp |
| `node_id` | TEXT | ID del nodo |
| `status` | TEXT | Estado (ok, warning, error) |
| `cpu_pct` | REAL | Uso de CPU (%) |
| `ram_pct` | REAL | Uso de RAM (%) |
| `disk_pct` | REAL | Uso de disco (%) |
| `temp_c` | REAL | Temperatura (°C) |
| `uptime_s` | REAL | Uptime en segundos |

---

### 🔧 Uso de la Base de Datos

#### Insertar una Muestra

```python
from src.acquisition.db import get_database
from datetime import datetime

from datetime import datetime, UTC

db = get_database()

sample = {
    "ts": datetime.now(UTC).isoformat().replace("+00:00", "") + "Z",
    "node_id": "naira-node-001",
    "source": "meteo",
    "metric": "temp_aire",
    "value": 23.45,
    "unit": "°C",
    "quality": "ok"
}

row_id = db.insert_sample(sample)
print(f"Muestra insertada con ID: {row_id}")
```

#### Insertar Múltiples Muestras (Lote)

```python
samples = [
    {...},  # Muestra 1
    {...},  # Muestra 2
    {...},  # Muestra 3
]

inserted = db.insert_samples_batch(samples)
print(f"Insertadas {inserted} muestras")
```

#### Consultar Muestras Recientes

```python
# Últimas 100 muestras
samples = db.get_samples(limit=100)

# Últimas 10 muestras de temperatura
temp_samples = db.get_samples(metric="temp_aire", limit=10)

for sample in samples:
    print(f"{sample['ts']} | {sample['metric']}={sample['value']} {sample['unit']}")
```

#### Consultar Rango de Tiempo

```python
from datetime import datetime, timedelta, UTC

start = (datetime.now(UTC) - timedelta(days=1)).isoformat().replace("+00:00", "") + "Z"
end = datetime.now(UTC).isoformat().replace("+00:00", "") + "Z"

samples = db.get_samples_time_range(start, end, metric="temp_aire")
print(f"Encontradas {len(samples)} muestras")
```

#### Calcular Agregaciones Diarias

```python
aggregate = db.compute_daily_aggregate(
    date_str="2026-01-15",
    metric="temp_aire",
    node_id="naira-node-001"
)

print(f"Min: {aggregate['value_min']}")
print(f"Max: {aggregate['value_max']}")
print(f"Avg: {aggregate['value_avg']}")
print(f"Count: {aggregate['value_count']}")
```

#### Obtener Estadísticas

```python
stats = db.get_stats()
print(f"Total muestras: {stats['total_samples']}")
print(f"Métricas únicas: {stats['total_metrics']}")
print(f"Rango: {stats['earliest_ts']} → {stats['latest_ts']}")
print(f"Tamaño BD: {stats['db_size_mb']:.2f} MB")
```

#### Limpiar Datos Antiguos

```python
# Eliminar muestras más antiguas de 30 días
deleted = db.delete_old_samples(days_old=30)
print(f"Eliminadas {deleted} muestras antiguas")
```

---

### 🔌 Colector de Puerto Serie

El módulo `collector.py` **automatiza** la lectura desde Arduino y el almacenamiento en BD:

#### Uso Programático

```python
from src.acquisition.collector import SerialCollector

# Crear colector
collector = SerialCollector(
    port="/dev/ttyACM0",
    baudrate=9600,
    node_id="naira-node-001"
)

# Conectar
if collector.connect():
    # Leer 100 líneas y guardarlas
    saved = collector.read_and_store_loop(count=100)
    print(f"Guardadas {saved} muestras")
    
    # Obtener últimos valores (caché)
    last_values = collector.get_last_values()
    print(f"Últimos valores: {last_values}")
    
    collector.disconnect()
```

#### Uso desde Línea de Comandos

```bash
# Leer 50 líneas del puerto serie y guardar
python -m src.acquisition.collector --count 50 --log-level INFO

# Especificar puerto y baudrate
python -m src.acquisition.collector \
    --port /dev/ttyUSB0 \
    --baudrate 9600 \
    --count 100

# Lectura continua (sin límite)
python -m src.acquisition.collector --log-level DEBUG
```

#### Parseo de Datos

El colector espera líneas del Arduino en formato:
```
moisture 800
light 5.00
temperature 18.96
```

Y las convierte automáticamente a:
```python
{
    "ts": "2026-01-15T14:30:45.123Z",
    "node_id": "naira-node-001",
    "source": "suelo|meteo",
    "metric": "humedad_suelo|luminosidad|temp_aire",
    "value": 18.96,
    "unit": "%|lux|°C",
    "quality": "ok"
}
```

**Mapeo de conversión:**
- `moisture 800` → `metric: "humedad_suelo"`, `unit: "%"`, `source: "suelo"`
- `light 5.00` → `metric: "luminosidad"`, `unit: "lux"`, `source: "meteo"`
- `temperature 18.96` → `metric: "temp_aire"`, `unit: "°C"`, `source: "meteo"`

---

### 📍 Ubicación de la Base de Datos

La BD se crea automáticamente en:
```
/home/naira/NAIRA/naira-edge/data/naira_sensors.db
```

Puedes consultar directamente con sqlite3:

```bash
sqlite3 /home/naira/NAIRA/naira-edge/data/naira_sensors.db

# Dentro de sqlite3:
sqlite> SELECT COUNT(*) FROM sensor_samples;
sqlite> SELECT * FROM sensor_samples LIMIT 5;
sqlite> SELECT DISTINCT metric FROM sensor_samples;
sqlite> .quit
```

---

### 💡 Ejemplos Completos

Ver `example_db_usage.py` para ejemplos prácticos:

```bash
python src/acquisition/example_db_usage.py
```

**Output esperado**:
```
============================================================
EJEMPLO 1: Insertar Muestras
============================================================
[INFO] Insertadas 4 muestras de ejemplo

============================================================
EJEMPLO 2: Consultar Muestras
============================================================
Últimas 10 muestras: 4 filas
  2026-01-15T14:28:45.123Z | temp_aire       = 23.45 °C (ok)
  ...

============================================================
EJEMPLO 3: Estadísticas de la BD
============================================================
Total de muestras:        4
Métricas únicas:          3
...
```

---

## �📚 Archivos Relacionados

- **src/main.py** — Orquestación (elige stub vs hardware)
- **src/config.py** — Configuración centralizada
- **src/processing/** — Procesamiento de datos
- **src/comms/** — Publicación de datos
- **requirements.txt** — Dependencias (pyserial)

---

## 📝 Notas de Implementación

### Lectura Bloqueante

Los scripts de lectura son **bloqueantes**:
```python
line = ser.readline()  # Espera hasta timeout
```

Para uso en tiempo real, considera:
- Threads/asyncio
- Queue de lectura
- Non-blocking I/O

### Tolerancia de Errores

- Líneas incompletas → ignoradas
- Líneas malformadas → ignoradas
- Puerto desconectado → error con reintentos (en main.py)

### Encoding

Decodificación con tolerancia:
```python
line = ser.readline().decode("utf-8", errors="ignore")
```

---

## 🧪 Suite de Tests (test_serial_reader.py)

Se incluye suite de tests pytest que **valida completamente el parsing y normalización** de datos:

### Categorías de Tests

| Categoría | Tests | Descripción |
|-----------|-------|-------------|
| **Serial Reading** | 4 | Lectura de líneas del puerto (raw bytes → string) |
| **Temperature Parsing** | 5 | Parsing de formato `temperature X.XX` |
| **Light Parsing** | 4 | Parsing de formato `light X.XX` |
| **Moisture Parsing** | 5 | Parsing de formato `moisture X` |
| **Unknown Sensors** | 3 | Rechazo de sensores desconocidos |
| **Quality Assessment** | 9 | Evaluación de rangos válidos |
| **Normalization** | 3 | Estructura normalizada NAIRA |
| **Integration** | 4 | Pipeline completo raw → normalizado |

**Total**: 37 tests, todos pasando ✅

### Ejecutar Tests

Opción 1: **Usar el script helper** (recomendado)
```bash
# Todos los tests (output silencioso)
bash src/acquisition/run_tests.sh

# Tests verbose
bash src/acquisition/run_tests.sh verbose

# Con reporte de cobertura
bash src/acquisition/run_tests.sh coverage

# HTML report
bash src/acquisition/run_tests.sh html

# Tests específicos
bash src/acquisition/run_tests.sh temperature
bash src/acquisition/run_tests.sh moisture
bash src/acquisition/run_tests.sh quality
bash src/acquisition/run_tests.sh integration
```

Opción 2: **Usar pytest directamente**
```bash
cd /home/naira/NAIRA/naira-edge

# Todos los tests
/home/naira/NAIRA/naira-edge/venv/bin/python -m pytest src/acquisition/test_serial_reader.py -q

# Verbose
/home/naira/NAIRA/naira-edge/venv/bin/python -m pytest src/acquisition/test_serial_reader.py -v

# Con cobertura
/home/naira/NAIRA/naira-edge/venv/bin/python -m pytest src/acquisition/test_serial_reader.py --cov=src.acquisition --cov-report=term-missing

# HTML report
/home/naira/NAIRA/naira-edge/venv/bin/python -m pytest src/acquisition/test_serial_reader.py --cov=src.acquisition --cov-report=html
```

### Resultados Actuales

✅ **37 tests** - 100% passing  
✅ **99% code coverage** - test_serial_reader.py  
✅ **49% coverage** - collector.py (lógica bajo test)

**Cobertura por módulo:**

| Módulo | Cobertura | Estado |
|--------|-----------|--------|
| `collector.py` | 49% | ✅ Métodos de parsing cubiertos |
| `db.py` | 26% | ⚠️ Necesita tests de integración |
| `test_serial_reader.py` | 99% | ✅ Suite de tests completa |
| **Total** | **51%** | ✅ Buen baseline |

**Missing coverage en collector.py**: conexión serial, lectura de líneas (bloqueantes), storage en BD
- → Requerirían tests de integración con mocking más profundo

### Mocking y Fixtures

Los tests mockean el puerto serie (`serial.Serial`), no requieren hardware real:

```python
from unittest.mock import MagicMock

mock_serial = MagicMock()
mock_serial.is_open = True
mock_serial.readline.return_value = b"temperature 23.45\n"
collector.ser = mock_serial

# Ahora puedes probar sin Arduino físico
```

### Ejemplos de Tests

#### ✅ Test: Parsing Temperatura Válida
```python
def test_parse_valid_temperature():
    collector = SerialCollector()
    result = collector.parse_line("temperature 23.45")
    
    assert result["metric"] == "temp_aire"
    assert result["value"] == 23.45
    assert result["unit"] == "°C"
```

#### ✅ Test: Rechazo de Temperatura Fuera de Rango
```python
def test_quality_bad_for_temperature_too_low():
    collector = SerialCollector()
    quality = collector._assess_quality("temp_aire", -50.0)
    
    assert quality == "bad"  # Fuera de rango válido
```

#### ✅ Test: Pipeline Completo
```python
def test_full_pipeline_moisture():
    collector = SerialCollector()
    
    # Raw line from Arduino
    line = "moisture 800"
    
    # Parse
    parsed = collector.parse_line(line)
    
    # Normalize
    normalized = collector.normalize_sample(parsed)
    
    # Verify structure
    assert normalized["metric"] == "humedad_suelo"
    assert normalized["value"] == 800
    assert normalized["source"] == "suelo"
    assert normalized["quality"] == "ok"
```

### Rango de Validación (Quality Assessment)

Valores aceptables para cada métrica:

| Métrica | Rango OK | Unidad |
|---------|----------|--------|
| `temp_aire` | -20 a 60 | °C |
| `humedad_suelo` | 0 a 1023 | % |
| `luminosidad` | 0 a 65535 | lux |

Fuera de estos rangos → quality = "bad"

### Archivos Relacionados

- **`test_serial_reader.py`**: Suite de 37 tests
- **`collector.py`**: Lógica de parsing (`parse_line()`, `_assess_quality()`)
- **`example_db_usage.py`**: Ejemplos complementarios (integración con BD)

---

## ✅ Checklist de Integración

- [x] Simulador funcional (stub.py)
- [x] Lectura del puerto serie (listen_serial.py)
- [x] Parsing de datos con validación
- [x] Estructura de datos normalizada NAIRA
- [x] Manejo robusto de errores
- [x] Base de datos SQLite (db.py) con 3 tablas
- [x] Colector de puerto serie (collector.py) - Clase SerialCollector
- [x] CLI del colector - Función collect_cli()
- [x] Ejemplos de uso (example_db_usage.py) - 6 ejemplos
- [x] **Suite de tests (test_serial_reader.py) - 37 tests**
- [x] Documentación actualizada y consolidada
- [x] Trama de datos correcta: moisture, light, temperature

---

**Status**: ✅ Listo para usar  
**Versión**: v1.0  
**Fecha**: 15 de enero de 2026  
**Hardware**: Arduino MKR + 3 sensores por RS485/USB
