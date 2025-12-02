# Ejercicios — Módulo 2. Preparación y diagnóstico del nodo

## Ejercicio 1 — Puesta en marcha básica del nodo

**Objetivo:** Preparar el sistema operativo y acceder remotamente al nodo.

1. Instala (o verifica) la imagen de Raspberry Pi OS en la tarjeta microSD.
2. Arranca la Raspberry Pi y realiza la configuración inicial:
   - Cambia la contraseña del usuario por defecto.
   - Configura zona horaria e idioma.
3. Habilita el acceso por SSH.
4. Desde tu portátil, conéctate a la Raspberry Pi por SSH.
5. Actualiza el sistema con `apt update` y `apt upgrade`.
6. Ejecuta `hostname` y anota el nombre del nodo.

**Entrega sugerida:**

- Captura de pantalla del acceso por SSH.
- Fichero de texto `info_nodo.txt` con:
  - hostname,
  - fecha de configuración inicial,
  - nombre del grupo.

---

## Ejercicio 2 — Diagnóstico de conectividad WiFi/4G

**Objetivo:** Verificar que el nodo dispone de conectividad a Internet y registrar el resultado.

1. Configura la conexión WiFi del nodo con las credenciales facilitadas.
2. Comprueba que obtienes dirección IP y que puedes hacer ping a:
   - el router/punto de acceso,
   - una web externa (por ejemplo, `ping -c 3` a una URL conocida).
3. (Opcional) Si se dispone de 4G:
   - Conecta el módem o router 4G.
   - Comprueba que el nodo tiene acceso a Internet a través de esa vía.
4. Crea un script sencillo en Bash o Python, llamado `diagnostico_red` que:
   - Intente hacer ping a una dirección IP local (p.ej. el router).
   - Intente hacer ping a una dirección externa.
   - Muestre un mensaje del tipo:
     - `OK_LOCAL`, `FALLO_LOCAL`, `OK_EXTERN`, `FALLO_EXTERN`.

**Entrega sugerida:**

- Script `diagnostico_red` en el directorio del grupo.
- Fichero `resultado_diagnostico.txt` con la salida del script.

---

## Ejercicio 3 — Lectura de un sensor y validación de rango

**Objetivo:** Confirmar que el nodo recibe datos de un sensor de campo y que se pueden validar.

1. Conecta el sensor asignado (por ejemplo, temperatura/humedad) siguiendo las indicaciones del docente.
2. Verifica que el sistema detecta el sensor (por ejemplo, con `i2cdetect` o comando equivalente).
3. Utiliza el script de ejemplo proporcionado para leer el sensor, o crea uno nuevo llamado `leer_sensor.py` que:
   - Lea un valor de temperatura y/o humedad (o el dato proporcionado por el sensor).
   - Muestre el valor por pantalla.
4. Añade al script una comprobación de rango:
   - Define un rango razonable (por ejemplo, temperatura entre 0 y 60 ºC).
   - Si el valor está fuera de rango, muestra un mensaje de alerta:
     - Ejemplo: `ALERTA: temperatura fuera de rango`.
5. Repite varias lecturas y anota al menos 5 valores.

**Entrega sugerida:**

- Script `leer_sensor.py`.
- Fichero `lecturas_sensor.csv` con:
  - marca de tiempo,
  - valor leído,
  - indicador de si está en rango (OK/ALERTA).

---

## Ejercicio 4 — Diagnóstico básico del nodo (CPU, RAM, disco)

**Objetivo:** Implementar un script que resuma el estado del nodo en un formato sencillo de interpretar.

1. Crea un script en Python llamado `estado_nodo.py` que:
   - Obtenga:
     - porcentaje de uso de CPU,
     - memoria libre/total,
     - espacio libre/total en la partición principal.
   - (Pista: se pueden usar utilidades del sistema o librerías como `psutil` si está disponible).
2. Haz que el script imprima un resumen en formato cercano a JSON, por ejemplo:

   ```json
   {
     "cpu_pct": 23.5,
     "mem_libre_mb": 512,
     "mem_total_mb": 1024,
     "disco_libre_gb": 12.3,
     "disco_total_gb": 29.7
   }
3. Ejecuta el script al menos 3 veces (en momentos distintos) y guarda las salidas en un fichero log_estado_nodo.txt.

**Entrega sugerida:**

- Script estado_nodo.py.
- Fichero log_estado_nodo.txt con las distintas ejecuciones.

## Ejercicio 5 — Consulta a una API desde el nodo

**Objetivo**: Consumir una API REST sencilla desde el nodo y combinar los datos con una lectura de sensor.

1. Identifica una API pública sencilla propuesta por el docente (por ejemplo, meteorología o hora mundial).
2. Crea un script consulta_api.py que:
   - Realice una petición GET a la API.
   - Procese la respuesta en formato JSON.
   - Extraiga al menos 2 campos relevantes (por ejemplo, temperatura prevista y humedad relativa).
3. Modifica el script para que:
   - Llame también al script de lectura de sensor (leer_sensor.py) o reutilice su lógica.
   - Genere un único JSON con:
      - datos del sensor local,
      - datos de la API remota,
      - marca de tiempo.
4. Imprime el JSON resultante por pantalla y guarda una copia en un fichero fusion_datos.json.

**Entrega sugerida:**

- Script consulta_api.py.
- Fichero fusion_datos.json con al menos 2 ejemplos de salida.

## Ejercicio 6 (opcional) — Checklist de nodo listo para campo

**Objetivo:** Elaborar una “ficha de nodo” para despliegue en un entorno agrícola NAIRA.

1. Crea un fichero `ficha_nodo.md` con:

   * Identificador del nodo.
   * Ubicación prevista (p.ej. parcela, sector de riego).
   * Lista de sensores conectados.
   * Tipo de conectividad (WiFi, 4G, ambos).
   * Scripts de diagnóstico disponibles (`diagnostico_red`, `estado_nodo`, etc.).
   * Última fecha de actualización.
2. Indica en la ficha si el nodo cumple los siguientes puntos:

   * [ ] Acceso por SSH verificado.
   * [ ] Conectividad a Internet verificada.
   * [ ] Lectura de sensor en rango plausible.
   * [ ] Consulta a API externa funcionando.
   * [ ] Scripts de diagnóstico probados.

**Entrega sugerida:**

* Fichero `ficha_nodo.md` en el directorio del grupo.