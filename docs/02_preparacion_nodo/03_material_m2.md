# Contenidos - Módulo 2. Preparación y diagnóstico del nodo

## 0. Contexto

En este módulo se trabaja con un nodo físico basado en **Raspberry Pi 4**, conectado a sensores de campo (por ejemplo, humedad de suelo, temperatura, caudal, presión, etc.) y con conectividad **WiFi/4G** para enviar y consultar datos mediante **APIs**.

El objetivo es que el alumnado pueda:

- Preparar el nodo desde cero (hardware + sistema operativo).
- Configurar la conectividad de red (WiFi y 4G).
- Verificar el funcionamiento de los sensores conectados.
- Implementar pruebas básicas de diagnóstico del nodo y de la conectividad.
- Realizar consultas a una API remota desde el nodo.

---

## 1. Objetivos de aprendizaje

Al finalizar el módulo, el alumnado será capaz de:

1. Identificar los componentes principales de un nodo de Edge basado en Raspberry Pi 4.
2. Instalar y configurar el sistema operativo en la Raspberry Pi para uso como nodo de campo.
3. Configurar la conectividad de red mediante WiFi y/o 4G.
4. Verificar la comunicación con sensores de campo conectados al nodo.
5. Implementar scripts sencillos de diagnóstico de estado del nodo (CPU, RAM, disco, conectividad).
6. Realizar llamadas a una API REST desde el nodo y procesar la respuesta.
7. Documentar la configuración mínima del nodo para su despliegue en campo.

---

## 2. Contenidos

### 2.1. Arquitectura del nodo NAIRA en campo

- Papel del nodo en la arquitectura NAIRA (edge → cloud → IA).
- Funciones del nodo:
  - Adquisición de datos de sensores físicos.
  - Preprocesado ligero de datos.
  - Envío/recepción de datos mediante APIs.
  - Monitorización de estado (health checks).
- Componentes típicos:
  - Raspberry Pi 4 (CPU, RAM, puertos, alimentación).
  - Tarjeta microSD.
  - HATs o placas de expansión para sensores.
  - Módem 4G / router 4G / WiFi.
  - Caja de protección (IP65 o similar) para entornos agrícolas.

### 2.2. Preparación hardware de la Raspberry Pi

- Lista de materiales:
  - Raspberry Pi 4 (modelo y especificaciones mínimas).
  - Fuente de alimentación adecuada.
  - Tarjeta microSD (capacidad recomendada).
  - Sensores de ejemplo (humedad de suelo, temperatura, etc.).
  - Interfaz 4G (módem USB o router externo).
- Esquema básico de conexión:
  - Sensores por I2C, 1-Wire, GPIO o UART.
  - Conexión a router 4G o punto de acceso WiFi.
- Buenas prácticas:
  - Identificación y etiquetado de cables.
  - Fijación mecánica y orden de cableado.
  - Consideraciones de protección eléctrica y ambiental.

### 2.3. Instalación y configuración del sistema operativo

- Elección de sistema operativo:
  - Raspberry Pi OS Lite (enfoque sin entorno gráfico).
- Instalación:
  - Uso de Raspberry Pi Imager (o herramienta equivalente).
  - Habilitar SSH y configuración básica en el primer arranque.
- Configuración inicial:
  - Cambio de contraseña por defecto.
  - Configuración de zona horaria y teclado.
  - Actualización del sistema (`apt update`, `apt upgrade`).
  - Activación de interfaces necesarias (I2C, 1-Wire, etc.).

### 2.4. Configuración de red: WiFi y 4G

- Configuración de WiFi:
  - Fichero de configuración (`wpa_supplicant.conf` o herramientas equivalentes).
  - Comprobación de IP y conectividad (`ip a`, `ping`).
- Introducción a 4G:
  - Opciones: módem USB 4G vs router 4G externo.
  - Configuración típica (APN, PIN, etc. según proveedor).
  - Verificación de conectividad 4G.
- Estrategias de redundancia:
  - Qué hacer si se pierde WiFi.
  - Pruebas de reconexión automática.
- Seguridad básica:
  - No exponer servicios innecesarios.
  - Actualizaciones periódicas.

### 2.5. Entorno de trabajo para adquisición y diagnóstico

- Preparación del entorno Python:
  - Instalación de Python y `pip` (si no vienen por defecto).
  - Creación de entorno virtual para el proyecto del nodo.
  - Instalación de librerías básicas:
    - `requests` (para APIs),
    - librería de sensores (según ejemplo que se use),
    - herramientas opcionales (p.ej. `gpiozero`).
- Organización del proyecto:
  - Estructura de carpetas recomendada (`/home/pi/naira_nodo/…`).
  - Ficheros de configuración (por ejemplo `config.yaml` o `.env` sencillo).

### 2.6. Lectura y diagnóstico de sensores de campo

- Comprobaciones de bajo nivel:
  - Detección de dispositivos I2C (`i2cdetect`).
  - Verificación de permisos para acceso a GPIO.
- Script sencillo de lectura de un sensor:
  - Leer un valor de ejemplo (temperatura, humedad,…).
  - Mostrar por pantalla, guardar en log o JSON.
- Validación básica de datos:
  - Rangos razonables (ej. temperatura 0–60 ºC, humedad 0–100 %).
  - Gestión de errores (sensor desconectado, lecturas nulas, etc.).

### 2.7. Monitorización y diagnóstico del nodo

- Indicadores de salud del sistema:
  - Uso de CPU y RAM (`top`, `htop`, `free -h`).
  - Espacio en disco (`df -h`).
  - Temperatura de la CPU (comando específico de Raspberry Pi).
- Creación de un script de diagnóstico:
  - Comprobar conectividad a Internet (p. ej. `ping` a una URL).
  - Consultar una API externa de prueba y reportar estado.
  - Generar un resumen en formato JSON con:
    - estado de red,
    - carga del sistema,
    - últimas lecturas de sensores.
- Opciones de automatización:
  - Ejecución periódica con `cron` o `systemd`.
  - Registro en fichero de log.

### 2.8. Acceso a una API desde el nodo

- Conceptos básicos:
  - Qué es una API REST.
  - Métodos principales (GET, POST).
  - Respuestas en formato JSON.
- Ejemplo práctico:
  - Consumir una API sencilla (por ejemplo, meteorología, hora mundial, etc.).
  - Parsear la respuesta y extraer campos relevantes.
  - Combinar datos de sensores con datos de la API en un mismo JSON.
- Aplicación al contexto NAIRA:
  - Uso de datos externos (meteorología, previsión de riego, etc.) para enriquecer la información del nodo.

### 2.9. Buenas prácticas y checklist de despliegue

- Checklist de nodo listo para campo:
  - OS actualizado, credenciales cambiadas.
  - Conectividad WiFi/4G verificada.
  - Sensores probados y con lecturas plausibles.
  - Scripts de diagnóstico funcionando.
- Documentación mínima:
  - Ficha del nodo (ID, ubicación, tipo de sensores).
  - Anotación de parámetros clave (APN, SSID, etc.).
- Recomendaciones para soporte y mantenimiento:
  - Cómo capturar información para soporte remoto.
  - Logs y ficheros útiles en caso de fallo.
