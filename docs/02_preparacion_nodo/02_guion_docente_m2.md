# Guion docente — Módulo 2. Preparación y diagnóstico del nodo

Duración estimada: 3–4 horas.
Modalidad: Preferentemente **práctica** con una Raspberry Pi por persona o pareja.

---

## 0. Antes de la sesión

- Comprobar que se dispone de:
  - 1 Raspberry Pi 4 por grupo (o al menos 1 por cada 3–4 personas).
  - Tarjeta microSD preparada o lista para flashear.
  - Fuente de alimentación adecuada.
  - Al menos un sensor sencillo (temperatura/humedad, o similar).
  - Acceso a WiFi y/o router 4G.
- Tener a mano:
  - Usuario y contraseña por defecto de la Raspberry Pi.
  - Datos de red (SSID y contraseña WiFi; APN del 4G si aplica).
- Opcional: preparar una imagen de SD ya configurada para acelerar la parte de instalación si el tiempo es limitado.

---

## 1. Introducción (15–20 min)

**Objetivo:** Enmarcar el módulo dentro de NAIRA y explicar qué se va a conseguir.

1. Recordatorio breve del Módulo 1:
   - Definición de Edge Computing.
   - Papel del nodo en la arquitectura.
2. Presentación de la Raspberry Pi 4:
   - Características principales.
   - Ventajas para despliegues en agricultura de precisión.
3. Explicar el objetivo práctico:
   - "Hoy vamos a dejar el nodo listo para funcionar en campo, con sensores y conectividad."

**Notas docente:**  
Conviene mostrar una Raspberry Pi físicamente, enseñar puertos, conectores y algún ejemplo real o foto de un nodo en entorno agrícola.

---

## 2. Preparación hardware y sistema operativo (45–60 min)

**Objetivo:** Dejar el sistema operativo instalado y la Raspberry Pi accesible por red.

### 2.1. Explicación (10–15 min)

- Describir brevemente:
  - Lista de componentes.
  - Esquema de conexión en un diagrama simple (puedes usar material de apoyo del repo).
- Comentar buenas prácticas al preparar el hardware para campo (protección, etiquetado).

### 2.2. Demostración (10–15 min)

- Flasheo de la imagen de Raspberry Pi OS en una microSD.
- Primer arranque:
  - Conectar teclado, pantalla (o usar ya SSH si está preparado).
  - Cambio de contraseña.
  - Configuración rápida (zona horaria, idioma).
  - Actualización del sistema.

### 2.3. Práctica guiada (20–30 min)

- Cada grupo repite el proceso:
  - Inserta SD, arranca la Raspberry.
  - Accede por SSH.
  - Ejecuta la actualización del sistema.
  - Comprueba conectividad a Internet.

**Notas docente:**  
Si el tiempo es limitado, se puede dar una SD ya flasheada y empezar desde la parte de configuración inicial.

---

## 3. Configuración de red: WiFi y 4G (45–60 min)

**Objetivo:** Conseguir conectividad estable desde el nodo.

### 3.1. Explicación (10–15 min)

- Diferenciar:
  - Conexión por cable (si existe).
  - Conexión WiFi.
  - Conexión 4G.
- Comentar casos de uso:
  - Riego en finca sin cobertura WiFi → 4G.
  - Entornos mixtos WiFi/4G.

### 3.2. Demostración (15–20 min)

- Configurar una red WiFi:
  - Fichero de configuración o herramienta interactiva.
  - Comprobación de IP y ping a una web.
- Mostrar un ejemplo de conexión 4G:
  - Explicar la configuración básica (sin entrar en detalles complejos).
  - Verificar conectividad (ping, consulta a API sencilla).

### 3.3. Práctica guiada (15–25 min)

- Cada grupo:
  - Configura el acceso WiFi del nodo.
  - Ejecuta un pequeño script de prueba (ping o `requests.get` a una URL).
  - Registra en un fichero de texto si la prueba fue correcta.

**Notas docente:**  
Es buena idea tener un "plan B" (por ejemplo, una red WiFi propia del aula) para evitar problemas de credenciales o saturación de red.

---

## 4. Lectura de sensores y diagnóstico básico (45–60 min)

**Objetivo:** Ver que el nodo realmente está leyendo algo útil y que podemos diagnosticar su estado.

### 4.1. Explicación (10–15 min)

- Revisar los tipos de sensores disponibles:
  - Cómo se conectan (I2C, 1-Wire, GPIO…).
- Introducir la idea de **diagnóstico**:
  - No sólo leer datos, sino saber si el nodo está "sano":
    - CPU, RAM, disco, temperatura.
    - Conectividad (ping, API).

### 4.2. Demostración (15–20 min)

- Mostrar comandos de bajo nivel:
  - `i2cdetect` u otros según el sensor.
- Ejecutar un script en Python que:
  - Lea un valor del sensor.
  - Controle que el valor está en rango.
- Ejecutar un segundo script de diagnóstico:
  - Mida uso de CPU, RAM, disco.
  - Haga un ping o una llamada a una API.
  - Devuelva un resumen en JSON o texto estructurado.

### 4.3. Práctica guiada (15–25 min)

- Cada grupo:
  - Comprueba que el sensor aparece correctamente en el sistema.
  - Ejecuta y modifica el script de lectura del sensor.
  - Añade una comprobación de rango (si el valor es absurdo, marcar error).

**Notas docente:**  
Se puede facilitar un repositorio con scripts base y proponer pequeñas modificaciones para que no se pierda tiempo en detalles de código.

---

## 5. Consulta a una API desde el nodo (30–40 min)

**Objetivo:** Integrar el nodo con una API sencilla para simular el uso de datos externos.

### 5.1. Explicación (10 min)

- Recordar qué es una API REST (muy brevemente).
- Mostrar un ejemplo de JSON de respuesta.
- Conectar con el contexto agrícola:
  - Consultar meteorología, por ejemplo, para ajustar riego.

### 5.2. Demostración (10–15 min)

- Script de ejemplo:
  - Llamada `GET` a una API pública simple.
  - Parseo del JSON.
  - Impresión de 2–3 campos relevantes.

### 5.3. Práctica guiada (10–15 min)

- Cada grupo:
  - Ejecuta el script en su nodo.
  - Modifica el script para que además imprima una pequeña combinación de:
    - `dato_sensor_local` + `dato_api_remota`.

---

## 6. Cierre y checklist de nodo listo (10–15 min)

**Objetivo:** Que el alumnado se quede con una lista clara de verificación.

- Repaso rápido:
  - ¿El nodo arranca y es accesible por SSH?
  - ¿Tiene conectividad WiFi/4G?
  - ¿Lee al menos un sensor con valores razonables?
  - ¿Es capaz de consultar una API y procesar la respuesta?
- Proponer que documenten su nodo:
  - ID del nodo.
  - Sensores conectados.
  - Tipo de conectividad.
- Introducir cómo se usará este nodo en módulos posteriores (envío de datos a la nube, dashboards, IA, etc.).
