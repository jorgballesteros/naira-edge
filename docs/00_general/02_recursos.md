# Recursos y Hardware

*Raspberry Pi, sensores agrícolas, conectividad y requisitos de operación*

Este documento describe los recursos necesarios para completar el curso **“Edge Computing para la Gestión de Cultivos”** y para desplegar un nodo edge funcional basado en Raspberry Pi dentro del proyecto NAIRA. Incluye hardware, sensores disponibles, requisitos de red y consideraciones prácticas para funcionamiento en campo.

---

## **1. Raspberry Pi y configuración básica**

El nodo edge del curso se implementa sobre una **Raspberry Pi** (recomendada: *Raspberry Pi 4 Model B* o superior), seleccionada por su balance entre rendimiento, eficiencia energética y ecosistema de software.

### **1.1 Hardware recomendado**

* Raspberry Pi 4 Model B (2–8 GB RAM)
* Tarjeta microSD clase A2 (32–64 GB mínimo)
* Fuente de alimentación oficial (5V, 3A)
* Caja con ventilación o disipadores
* Módulo RTC (opcional para entornos sin conexión)
* Batería externa (opnional para validación en campo)

### **1.2 Periféricos útiles durante el curso**

* Teclado y ratón USB
* Monitor HDMI
* Adaptador USB–UART para depuración
* Lector de tarjetas microSD

---

## **2. Sensores disponibles en el curso**

Los sensores utilizados en el curso cubren las principales capas de información de un sistema agrícola inteligente: **clima, suelo, cultivo, riego y estado del nodo**. El nodo permitirá trabajar con datos reales o simulados según disponibilidad.

La siguiente tabla presenta el conjunto de sensores que podrían ser integrados:

| BLOQUE                | NIVEL    | TIPO                                   | Interfaz definitiva      | Comentario técnico                                           |
|-----------------------|----------|----------------------------------------|---------------------------|----------------------------------------------------------------|
| Estación Meteorológica| Básico   | Temperatura Aire                       | RS485 (Modbus RTU)        | Parte de la estación completa; lectura por registros Modbus.  |
| Estación Meteorológica| Básico   | Humedad Aire                           | RS485 (Modbus RTU)        | Integrado en la estación.                                     |
| Estación Meteorológica| Básico   | Radiación solar                        | RS485 (Modbus RTU)        | Integrado o como canal adicional de la misma estación.         |
| Estación Meteorológica| Medio    | Pluviómetro                            | RS485 (Modbus RTU)        | Pulsos totalizados por la estación + lectura Modbus.           |
| Estación Meteorológica| Medio    | Dirección Viento                       | RS485 (Modbus RTU)        | Sensor mecánico/electrónico, la estación lo expone por Modbus.|
| Estación Meteorológica| Medio    | Velocidad Viento                       | RS485 (Modbus RTU)        | Anemómetro con salida consolidada en la estación.             |
| Suelo                 | Básico   | Humedad Suelo                          | RS485 (Modbus RTU)        | Sensor multimodal: humedad, temperatura y EC.                 |
| Suelo                 | Medio    | Temperatura Suelo                      | RS485 (Modbus RTU)        | Parte del sensor multimodal.                                  |
| Suelo                 | Medio    | PH y CE                                | RS485 (Modbus RTU)        | Integrado en el sensor multimodal.                            |
| Suelo                 | Medio    | Potasio, Fósforo y Nitrógeno           | RS485 (Modbus RTU)        | Sensor NPK Modbus; mismo dispositivo multimodal.              |
| Suelo                 | Elevado  | Tensiómetro 10/30 cm                    | RS485 (Modbus RTU)        | Registrado vía Modbus; opcional como equipo avanzado.         |
| Cultivo               | Elevado  | Humectación de hoja                    | RS485 (Modbus RTU)        | Sensor resistivo/capacitivo con módulo RS485.                 |
| Riego                 | Básico   | Cantidad de agua                       | RS485 (Modbus RTU)        | Caudalímetro o contador digital con salida Modbus.            |
| Cultivo               | Elevado  | Cámara VGA                              | SPI                        | Conexión directa a la Raspberry Pi (CSI alternativo).         |
| Cultivo               | Elevado  | Sensor Hiperespectral                   | SPI                        | Módulo hiperespectral de bajo coste (ej. AS7341 extendido).   |
| Diagnóstico Nodo      | Básico   | Temperatura interna                    | I2C / interno del sistema | Puede usarse CPU thermal o un sensor I2C opcional.            |
| Diagnóstico Nodo      | Básico   | Tensión de la batería                  | ADC + RS485 (gateway)     | Lectura de batería vía conversor ADC con módulo RS485.        |

En la versión actual del nodo NAIRA utilizada en este curso solo se integran físicamente sensores de **nivel Básico y Medio**, tanto en campo (estación meteorológica, suelo y riego) como en diagnóstico del propio nodo (temperatura interna y tensión de batería). Todos los sensores de campo se agrupan en un único bus **RS485 con protocolo Modbus RTU**, lo que simplifica el cableado y la programación desde la Raspberry Pi.

Los sensores de **nivel Elevado** (tensiómetros, humectación de hoja, cámara VGA y sensor hiperespectral) se consideran elementos de **ampliación futura del nodo** y no forman parte de las prácticas de esta edición del curso, aunque se han tenido en cuenta en el diseño de la arquitectura para facilitar su integración posterior.

---
Aquí tienes el texto **reescrito y adaptado a la configuración real seleccionada**, donde los sensores **Básico + Medio** trabajan sobre **RS485 (Modbus RTU)** y únicamente los sensores avanzados (no usados en esta edición del curso) quedarían en SPI/I2C como ampliación futura.

El texto queda totalmente alineado con el nodo NAIRA y listo para integrarlo en `/m2_materiales.md`.

---

### **2.1 Estación meteorológica**

La estación meteorológica utilizada en el curso es un equipo **de bajo coste con salida RS485 (Modbus RTU)**.
Todos los parámetros se consultan directamente desde la Raspberry Pi a través del bus RS485, sin necesidad de APIs externas para su funcionamiento básico.

Variables disponibles:

* **Temperatura del aire**
* **Humedad relativa del aire**
* **Radiación solar**
* **Pluviómetro** (lluvia acumulada)
* **Dirección del viento**
* **Velocidad del viento**

Como **redundancia opcional**, se permitirá complementar la estación local con datos externos proporcionados por APIs meteorológicas cercanas, a fin de validar las mediciones o rellenar huecos en caso de fallo del sensor.

**Uso en el curso:**

* cálculo de evaporación y estimaciones básicas de ETc;
* detección de estrés térmico o hídrico;
* validación de modelos locales de microclima;
* identificación de eventos meteorológicos relevantes.

---

### **2.2 Sensores de suelo**

Los sensores de suelo empleados en esta edición del curso se integran mediante un **sensor multimodal RS485 (Modbus RTU)**, que combina múltiples mediciones en un solo dispositivo.

Sensores disponibles:

* **Humedad del suelo**
* **Temperatura del suelo**
* **pH del suelo**
* **Conductividad eléctrica (CE)**
* **Nutrientes NPK (Potasio, Fósforo y Nitrógeno)**

> Nota: Los **tensiómetros** se consideran sensores de nivel avanzado y no se utilizarán en esta edición del curso, aunque la arquitectura permite su futura integración.

**Uso en el curso:**

* cálculo del balance hídrico;
* interpretación de salinidad, acidez y fertilidad del suelo;
* soporte a la activación automatizada del riego;
* identificación de anomalías o condiciones de estrés radicular.

---

### **2.3 Sensores de cultivo**

En esta edición del curso **no se utilizarán sensores de cultivo de nivel avanzado** (cámara o multiespectral), ya que están clasificados como Nivel Elevado dentro del plan NAIRA.
No obstante, se deja documentada su función para la evolución futura del nodo.

Sensores previstos para mejoras futuras:

* **Cámara VGA (SPI)**

  * Captura de imágenes puntuales o periódicas.
  * Útil para detección visual simple (color, forma, vigor).

* **Sensor multiespectral / hiperespectral (SPI)**

  * Captura de bandas espectrales e índices vegetativos.
  * Procesado ligero en edge o envío filtrado al servidor.

**Uso futuro (no incluido en el curso):**

* análisis visual de vigor y estrés;
* detección de humectación foliar;
* análisis espectral para agricultura de precisión.

---

### **2.4 Sensores de riego**

Los sensores de riego utilizados en el curso se conectan mediante **RS485 (Modbus RTU)**.

* **Caudalímetro / Contador de agua**

**Uso en el curso:**

* cálculo del volumen de agua aplicado en cada riego;
* análisis de la relación riego–respuesta del cultivo;
* apoyo a automatizaciones básicas (activar o detener riego según umbrales).

---

### **2.5 Diagnóstico del nodo (salud del sistema)**

Estos sensores permiten monitorizar el estado físico y energético del nodo NAIRA.

Sensores disponibles:

* **Temperatura interna de la Raspberry Pi**
  (lectura directa del SoC o sensor I2C auxiliar)
* **Tensión de la batería**
  (a través de un módulo ADC con salida RS485)

**Uso en el curso:**

* evitar sobrecalentamientos y throttling;
* gestionar energía cuando el nodo opera con baterías;
* emitir alertas ante degradación, fallos o condiciones anómalas del sistema.

---

## **3. Conectividad y red**

El nodo edge puede operar en distintos escenarios de red:

### **3.1 Modos de conexión**

* **Wi-Fi** (modo normal en granjas o invernaderos con cobertura)
* **Ethernet** (entornos controlados en laboratorio)
* **Modo offline** (buffer local + envío diferido)

### **3.2 Requisitos de red para el curso**

* Conexión a un **broker MQTT** (Mosquitto local o remoto).
* Acceso HTTP/HTTPS para:

  * APIs meteorológicas
  * envío de datos al backend NAIRA
* NTP para sincronización temporal (o RTC en modo offline).

---

## **4. Integración eléctrica**

Los sensores pueden requerir:

* Alimentación a **3.3V** o **5V**
* Conversores ADC si son sensores analógicos
* Cables impermeables o de baja pérdida para campo
* Protección contra humedad y polvo (IP54–IP65)

---

## **5. Requisitos de software**

El entorno base del curso utiliza:

* Raspberry Pi OS Lite
* Python 3.11+
* pip, venv
* Docker (opcional)
* Mosquitto cliente (mosquitto-clients)
* Git
* Herramientas de diagnóstico:

  * `vcgencmd`
  * `i2cdetect`
  * `systemd` + servicios

---

## **6. Consideraciones para despliegue en campo**

* Encapsulado en caja estanca (IP65 recomendado).
* Protección de conectores y cableado.
* Gestión térmica (temperatura interna crítica > 70 °C).
* Alimentación autónoma (batería + panel solar opcional).
* Montaje seguro y accesible para mantenimiento.
* Registro local resiliente en caso de pérdida de red.
* Verificación periódica de la tensión de batería.
* Control de sesgos y ruido por interferencias del entorno.

---

## **7. Resumen de recursos mínimos**

| Recurso          | Requisito mínimo            | Recomendado                  |
| ---------------- | --------------------------- | ---------------------------- |
| Raspberry Pi     | Pi 4+ (4–8 GB)              | Pi 5.                        |
| Almacenamiento   | 32 GB SD                    | 64 GB A2                     |
| Conectividad     | Wi-Fi                       | Wi-Fi + Ethernet   |
| Sensores mínimos | Humedad suelo, caudalímetro | Tensiómetros, multiespectral |
| Alimentación     | 5V 3A                       | Batería + solar              |
| Software         | Python + MQTT               | Docker + API externas        |

