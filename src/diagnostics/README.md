# 🖥️ Sistema de Monitorización del Nodo NAIRA

## 🎯 Descripción General

Sistema integrado de **monitorización y alertas en tiempo real** para el nodo Raspberry Pi de NAIRA. Captura métricas críticas del sistema (CPU, RAM, disco, temperatura), las visualiza en un dashboard interactivo y envía notificaciones por Telegram cuando se alcanzan umbrales críticos.

**Capacidades principales:**
- 📊 **Dashboard en vivo**: Interfaz web interactiva con gráficas históricas (Streamlit)
- 📱 **Alertas por Telegram**: Notificaciones en tiempo real cuando métricas son críticas
- 🔧 **Umbrales configurables**: Personaliza límites de alerta sin código
- ⚙️ **Rate-limiting inteligente**: Evita spam de alertas repetidas
- 🔄 **Modo simulado**: Funciona sin Telegram, sin hardware específico

---

## 📦 Arquitectura del Sistema

### Módulos Componentes

```
src/diagnostics/
├── README.md                    ← Este archivo
├── diagnostics_app.py           ← Dashboard Streamlit (visualización en vivo)
├── telegram_alert.py            ← Motor de alertas por Telegram
├── node_monitor.py              ← Lectura de métricas del sistema
├── test_telegram_alerts.py      ← Script de prueba
└── stub.py                      ← Simulador
```

#### `diagnostics_app.py` (Dashboard)
- Aplicación Streamlit que muestra métricas en tiempo real
- 6 KPIs principales: CPU, RAM, Disco, Temperatura, Red, Uptime
- 3 gráficas históricas (CPU, RAM, Temperatura)
- Panel de alertas activas
- Umbrales ajustables desde slider
- Integración automática con Telegram

#### `telegram_alert.py` (Motor de Alertas)
- `TelegramAlertManager`: Gestor de alertas con rate-limiting
- `AlertThresholds`: Umbrales configurables
- `create_alert_manager()`: Factory que carga desde env vars
- Manejo robusto de errores de red
- Modo fallback silencioso sin credenciales

#### `node_monitor.py` (Recogida de Métricas)
- Funciones de lectura de CPU, RAM, disco, temperatura
- Lectura de temperatura RPi desde `/sys/class/thermal/thermal_zone0/temp`
- Lectura de uptime desde `/proc/uptime`
- Verificación de conectividad

#### `test_telegram_alerts.py` (Testing)
- Script para probar configuración de Telegram
- Envía alertas de prueba
- Verifica credenciales

---

## 📊 Eventos de Alerta

| Evento | Umbral Default | Emoji |
|--------|----------------|-------|
| Temperatura CPU | 60°C | 🌡️ |
| Uso de CPU | 85% | 🔴 |
| Uso de RAM | 90% | 💾 |
| Uso de Disco | 95% | 💿 |

**Rate-limiting**: No se envían 2 alertas del mismo tipo en menos de 5 minutos.

---

## 🚀 Inicio Rápido

### 1. Instalación de Dependencias

```bash
cd /home/naira/NAIRA/naira-edge
source venv/bin/activate
pip install -r requirements.txt
# Requiere: streamlit, psutil, paho-mqtt, requests
```

### 2. Configurar Telegram (Opcional)

Si **no quieres usar Telegram**, salta a la sección 3. El sistema funciona en modo simulado.

#### Paso A: Crear Bot en Telegram

1. Abre Telegram y busca `@BotFather`
2. Escribe `/newbot` y sigue los pasos
3. Copia el **TOKEN** (ej: `123456:ABCdefGHIjklmNOpqrSTUvwxYZ`)

#### Paso B: Obtener CHAT_ID

1. **Envía un mensaje** a tu bot en Telegram (ej: "hola")
2. **Abre esta URL** en tu navegador (reemplaza con tu token):
   ```
   https://api.telegram.org/bot<TU_TOKEN>/getUpdates
   ```
   
3. **Busca el campo `"id"`** en la respuesta JSON:
   ```json
   {
     "ok": true,
     "result": [
       {
         "message": {
           "chat": {
             "id": 987654321    ← ¡ESTE ES TU CHAT_ID!
           }
         }
       }
     ]
   }
   ```

#### Paso C: Configurar Variables de Entorno

Añade a tu `.bashrc`, `.profile` o `.env`:

```bash
export TELEGRAM_BOT_TOKEN="123456:ABCdefGHIjklmNOpqrSTUvwxYZ"
export TELEGRAM_CHAT_ID="987654321"

# Umbrales de alerta (opcionales - estos son los defaults)
export ALERT_TEMP_C="60"
export ALERT_CPU_PCT="85"
export ALERT_RAM_PCT="90"
export ALERT_DISK_PCT="95"
```

Recarga el shell:
```bash
source ~/.bashrc
```

### 3. Ejecutar el Dashboard

```bash
cd /home/naira/NAIRA/naira-edge
source venv/bin/activate
streamlit run src/diagnostics/diagnostics_app.py
```

Se abrirá automáticamente en `http://localhost:8501`

### 4. Probar Alertas (Opcional)

```bash
cd /home/naira/NAIRA/naira-edge
python src/diagnostics/test_telegram_alerts.py
```

Deberías recibir un mensaje de prueba en Telegram.

---

## 📋 Variables de Entorno

| Variable | Descripción | Default | Requerida |
|----------|-------------|---------|-----------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram | `""` | No (para alertas) |
| `TELEGRAM_CHAT_ID` | ID del chat destino | `""` | No (para alertas) |
| `ALERT_TEMP_C` | Umbral de temperatura crítica | `"60"` | No |
| `ALERT_CPU_PCT` | Umbral de CPU crítica | `"85"` | No |
| `ALERT_RAM_PCT` | Umbral de RAM crítica | `"90"` | No |
| `ALERT_DISK_PCT` | Umbral de disco crítico | `"95"` | No |

---

## 💻 Uso del Dashboard (Streamlit)

### Interfaz Principal

#### 📊 Panel de Control (Sidebar Izquierdo)
- **Intervalo de refresco**: 1-10 segundos (default: 2s)
- **Longitud histórico**: 30-300 puntos (default: 120)
- **Umbrales de alerta**: Sliders para personalizar límites

#### 📈 KPIs (6 columnas en la parte superior)
```
CPU (%)     RAM (%)     Disco (%)     Temp (°C)     Red           Uptime
86.5%       78.2%       45.3%         52.1°C        Online        15h 23m
```

#### ⚠️ Panel de Alertas
- **Verde (✅)**: Sistema operativo, sin alertas
- **Rojo/Naranja (🔴)**: Alertas activas que superan umbrales

#### 📋 Panel de Detalles (2 columnas)
- **Estado del sistema**: CPU freq, RAM usada/total, Swap, Disco
- **Red**: Contadores de tráfico (RX/TX), paquetes

#### 📊 Gráficas Históricas (3 columnas)
- CPU (%)
- RAM (%)
- Temperatura (°C)

### Personalización de Umbrales

Usa los sliders en el sidebar para ajustar los umbrales sin reiniciar:
- CPU: 50-100% (default: 80%)
- RAM: 50-100% (default: 85%)
- Disco: 70-100% (default: 90%)
- Temperatura: 40-85°C (default: 70°C)

---

## 💻 Uso Programático

### Lectura de Métricas Directa

```python
from src.diagnostics.telegram_alert import create_alert_manager

# Carga configuración desde env vars
manager = create_alert_manager()

# Verifica una métrica individual
manager.check_temperature(72.5)  # Alerta si > 60°C
manager.check_cpu(88.0)           # Alerta si > 85%
manager.check_ram(91.0)           # Alerta si > 90%
manager.check_disk(96.0)          # Alerta si > 95%

# Verifica todas las métricas de una vez
manager.check_all(
    temp_c=72.5,
    cpu_pct=88.0,
    ram_pct=91.0,
    disk_pct=96.0
)
```

### Uso sin Telegram

```python
# El sistema funciona igual si no configuras credenciales
# Solo registra logs, no envía mensajes
manager = create_alert_manager()
manager.check_all(...)  # Sin crash, sin errores
```

---

## 🆘 Solución de Problemas

### ❌ `{"ok":true,"result":[]}`

**Causa**: No has mandado mensaje al bot en Telegram.

**Solución**:
1. Abre Telegram
2. Busca tu bot por nombre
3. Manda un mensaje (ej: "hola")
4. Vuelve a ejecutar la URL de `getUpdates`

---

### ❌ Token inválido: `{"ok":false,"error_code":401}`

**Solución**: Token incorrecto o expirado. Crea un bot nuevo en BotFather.

---

### ❌ No recibo alertas en Telegram

**Checklist**:
- [ ] ¿Es correcto `TELEGRAM_BOT_TOKEN`?
- [ ] ¿Es correcto `TELEGRAM_CHAT_ID`?
- [ ] ¿Mandaste un mensaje inicial al bot?
- [ ] ¿Está el bot activo en BotFather?
- [ ] ¿Tiene la RPi conexión a internet?
- [ ] ¿Ejecutaste `test_telegram_alerts.py`?

---

### ❌ Temperatura muestra "N/A"

**Normal** si no es Raspberry Pi. El sistema intenta leer `/sys/class/thermal/thermal_zone0/temp` (específico de RPi).

---

### ❌ Red muestra "Sin salida"

**Solución**: Verifica conectividad con:
```bash
ping 8.8.8.8
```

---

### ❌ Streamlit no inicia

**Solución**: Verifica dependencias:
```bash
pip install streamlit psutil paho-mqtt requests
```

---

### ✅ Modo Simulado (sin Telegram)

Si **no configuras** `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID`:
- El dashboard funciona normalmente
- Solo registra logs de alertas
- No envía mensajes reales
- No causa errores

---

## 📊 Características del Sistema

✅ **Dashboard en vivo**: Métricas en tiempo real con gráficas históricas  
✅ **Alertas por Telegram**: Notificaciones push con rate-limiting  
✅ **Rate-limiting**: No envía 2 alertas del mismo tipo en < 5 minutos  
✅ **Robusto**: Maneja errores de red gracefully  
✅ **Configurable**: Umbrales personalizables por env vars o sliders  
✅ **Sin dependencias nuevas**: Solo `streamlit`, `psutil`, `paho-mqtt`, `requests`  
✅ **Modo simulado**: Funciona sin Telegram si no está configurado  
✅ **Trazable**: Logs detallados de cada acción  

---

## 🔍 Funciones Clave (diagnostics_app.py)

### `read_cpu_temp_c() → float | None`
Lee temperatura del CPU desde `/sys/class/thermal/thermal_zone0/temp` (RPi).

### `read_uptime_s() → float | None`
Lee uptime en segundos desde `/proc/uptime`.

### `has_default_route() → bool`
Verifica conectividad mediante interfaces de red activas.

### `check_alerts() → dict`
Verifica si métricas exceden umbrales.  
Retorna dict con descripciones de alertas activas.

### `bytes_to_human(n: float) → str`
Convierte bytes a formato legible (B, KB, MB, GB, TB).

---

## 📚 Estructura Interna

### Almacenamiento de Sesión (Streamlit)

```python
st.session_state = {
    "ts_hist": deque(maxlen=120),      # Timestamps
    "cpu_hist": deque(maxlen=120),     # CPU %
    "temp_hist": deque(maxlen=120),    # Temperatura
    "ram_hist": deque(maxlen=120),     # RAM %
    "rx_hist": deque(maxlen=120),      # Bytes recibidos
    "tx_hist": deque(maxlen=120),      # Bytes enviados
}
```

El tamaño máximo se configura con el slider "Longitud histórico".

### Flujo de Datos

```
1. diagnostics_app.py inicia
2. Lee métricas del sistema (psutil)
3. Guarda en histórico (session_state)
4. Verifica alertas locales (check_alerts)
5. Si Telegram está configurado:
   - Carga TelegramAlertManager
   - Envía alertas
6. Renderiza UI (KPIs, gráficas, alertas)
7. Refresca cada N segundos
```

---

## ✅ Checklist de Integración

- [x] Dashboard Streamlit funcional
- [x] Motor de alertas robusto
- [x] Rate-limiting para evitar spam
- [x] Modo fallback sin Telegram
- [x] Logging detallado
- [x] Script de prueba
- [x] Documentación completa

---

## 📚 Archivos Relacionados

- **src/diagnostics/diagnostics_app.py** — Dashboard Streamlit
- **src/diagnostics/telegram_alert.py** — Motor de alertas
- **src/diagnostics/node_monitor.py** — Lectura de métricas
- **src/diagnostics/test_telegram_alerts.py** — Testing
- **src/config.py** — Configuración centralizada
- **requirements.txt** — Dependencias del proyecto

---

**Status**: ✅ Listo para usar  
**Versión**: v1.0  
**Fecha**: 15 de enero de 2026  
**Documentación**: ✅ Consolidada en este archivo
