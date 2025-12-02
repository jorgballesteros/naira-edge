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
* Batería externa o sistema solar (para validación en campo)

### **1.2 Periféricos útiles durante el curso**

* Teclado y ratón USB
* Monitor HDMI
* Adaptador USB–UART para depuración
* Lector de tarjetas microSD

---

## **2. Sensores disponibles en el curso**

Los sensores utilizados en el curso cubren las principales capas de información de un sistema agrícola inteligente: **clima, suelo, cultivo, riego y estado del nodo**. El nodo permitirá trabajar con datos reales o simulados según disponibilidad.

---

### **2.1 Estación meteorológica**

La Raspberry Pi **no se conecta directamente** a estos sensores; su integración se hará a través de **APIs externas**.
Variables disponibles:

* Temperatura del aire
* Humedad relativa del aire
* Radiación solar *(API)*
* Pluviómetro *(API)*
* Dirección del viento *(API)*
* Velocidad del viento *(API)*

**Uso en el curso:**

* cálculo de evaporación/ETc;
* predicción de estrés;
* validación de modelos locales;
* detección de eventos meteorológicos relevantes.

---

### **2.2 Sensores de suelo**

Conectados localmente a la Raspberry Pi mediante I2C, analógico-digital o protocolos simples según modelo.

Sensores disponibles:

* **Tensiómetros de 10 y 30 cm**
* **Humedad del suelo**
* *Opcionales:*

  * Temperatura del suelo
  * pH
  * Conductividad eléctrica (CE)

**Uso en el curso:**

* balance hídrico;
* activación automática del riego;
* modelos ligeros de predicción local;
* detección de anomalías.

---

### **2.3 Sensores de cultivo**

* **Cámara VGA**

  * imágenes puntuales o secuenciales
  * útil para detección de estados visuales simples en edge

* **Sensor multiespectral**

  * captura de bandas espectrales
  * cálculo de índices básicos (NDVI, GNDVI, SAVI)
  * procesado ligero local o reenvío filtrado al servidor

**Uso en el curso:**

* detección de humectación, vigor, estrés visual;
* activación de captura según eventos;
* reducción de datos en el borde.

---

### **2.4 Sensores de riego**

* **Caudalímetro / contador de agua**

**Uso en el curso:**

* cálculo de volumen aplicado;
* relación riego–respuesta del cultivo;
* activación automática de válvulas.

---

### **2.5 Diagnóstico del nodo (salud del sistema)**

* **Temperatura interna de la Raspberry Pi**
* **Tensión de la batería** (si aplica)

**Uso en el curso:**

* prevención de sobrecalentamiento;
* gestión de energía en campo;
* envío de alertas de degradación.

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

