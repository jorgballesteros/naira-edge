# Módulo 3 · Adquisición de datos de sensores

## Objetivo general
Diseñar e implementar una capa de adquisición de datos robusta, modular y reutilizable para sistemas IoT, capaz de operar tanto con sensores reales como simulados, garantizando la calidad, trazabilidad y persistencia local de los datos.

Este módulo construye la **base técnica** sobre la que se apoyan la visualización, el análisis avanzado y la inteligencia artificial de los módulos posteriores.

---

## Resultados de aprendizaje
Al finalizar el módulo, el alumnado será capaz de:
- Comprender el papel de la adquisición de datos en arquitecturas IoT y edge.
- Identificar sensores habituales en energía y agua y su forma de integración.
- Implementar lectores de sensores reales (RS485 / Modbus RTU) o simulados.
- Normalizar datos (timestamps, unidades, calidad).
- Almacenar datos de forma estructurada (CSV y SQLite).
- Desarrollar un bucle de adquisición periódico y tolerante a fallos.

---

## 1. Introducción a la adquisición de datos en entornos IoT

::contentReference[oaicite:0]{index=0}


### Conceptos clave
- Qué significa **adquirir datos** en un sistema IoT.
- Diferencia entre:
  - adquisición
  - almacenamiento
  - visualización
  - análisis
- Por qué la adquisición suele ejecutarse en **edge devices** (Raspberry Pi, gateways industriales).

### Ideas clave para el alumnado
- Los sensores pueden fallar.
- Las comunicaciones no son perfectas.
- El sistema debe seguir funcionando aunque falte un sensor.

---

## 2. Sensores y protocolos de comunicación

::contentReference[oaicite:1]{index=1}


### Tipología de sensores tratados
- Meteorológicos: temperatura, humedad, radiación, lluvia.
- Energía: potencia, consumo, tensión.
- Agua y riego: caudal, presión.
- Suelo: humedad, temperatura, conductividad, pH.
- Diagnóstico del nodo: CPU, temperatura, conectividad.

### RS485 y Modbus RTU (visión práctica)
- Comunicación robusta y muy extendida en industria.
- Topología bus.
- Lectura periódica (polling).
- Uso de registros y escalados.

> Nota docente: no es necesario entender el protocolo en profundidad para implementar una adquisición funcional.

---

## 3. Arquitectura software de la capa de adquisición

::contentReference[oaicite:2]{index=2}


### Principios de diseño
- Modularidad.
- Separación de responsabilidades.
- Escalabilidad.
- Reutilización de código.

### Componentes
- Drivers de sensores.
- Normalización de datos.
- Persistencia local.
- Bucle de adquisición.

### Diagrama lógico
```mermaid
flowchart LR
    Sensor --> Driver
    Driver --> Normalizacion
    Normalizacion --> Almacenamiento
    Normalizacion --> Logs
````

---

## 4. Modo real vs modo simulado

![Image](https://f.hubspotusercontent40.net/hubfs/742943/Blog/tutorials/Use-Losant-to-Simulate-IoT-Data/food-truck-dashboard.jpeg)

![Image](https://bitperfect.at/assets/blog-images/Advanced_Statistics_Histogram.png)

![Image](https://www.qatouch.com/wp-content/uploads/2024/09/Components-of-IoT-testing.webp)

### Modo real

* Lectura desde sensores físicos.
* Dependencia de hardware.
* Posibles fallos de comunicación.

### Modo simulado

* Generación de datos sintéticos.
* Ideal para:

  * aprendizaje
  * pruebas
  * desarrollo sin hardware
* Permite introducir eventos:

  * picos
  * cortes
  * valores anómalos

### Beneficio clave

Un mismo sistema puede funcionar **sin cambiar su arquitectura**, solo cambiando la fuente de datos.

---

## 5. Persistencia local de datos

![Image](https://www.researchgate.net/publication/341795623/figure/fig5/AS%3A897684781166593%401591036138222/Data-logging-in-the-form-of-CSV-file.ppm)

![Image](https://www.sqlitetutorial.net/wp-content/uploads/2015/11/sqlite-sample-database-color.jpg)

![Image](https://techcommunity.microsoft.com/t5/s/gxcuf89792/images/bS03ODYxNjEtMTE5OTUyaUFBNDY1NjgwQzU5NzE2RkE?revision=33)

### CSV

* Simple.
* Fácil de inspeccionar.
* Ideal para depuración y exportación rápida.

### SQLite

* Base de datos ligera.
* Permite consultas.
* Ideal para histórico local estructurado.

### Comparativa conceptual

| CSV           | SQLite              |
| ------------- | ------------------- |
| Simple        | Más estructurado    |
| Fácil de leer | Permite consultas   |
| Sin índices   | Mejor escalabilidad |

---

## 6. Bucle de adquisición y control de errores

![Image](https://www.qorvo.com/-/media/images/qorvopublic/blog/2018/zigbee/zigbee-poll-control-in-fire-alarm-system.jpg)

![Image](https://www.mdpi.com/sensors/sensors-21-07181/article_deploy/html/images/sensors-21-07181-g001.png)

![Image](https://www.researchgate.net/publication/376223171/figure/fig1/AS%3A11431281209407453%401701790894692/A-view-of-IoT-edge-cloud-continuum-showing-several-IoT-verticals-with-programmable-edge.jpg)

### Elementos clave

* Intervalo de adquisición.
* Gestión de errores.
* Etiquetado de calidad del dato.

### Estados típicos del dato

* ok
* warn
* bad

### Diagrama de funcionamiento

```mermaid
flowchart TD
    Start --> ReadSensors
    ReadSensors -->|OK| Store
    ReadSensors -->|Fail| MarkBad
    Store --> Sleep
    MarkBad --> Sleep
    Sleep --> Start
```
