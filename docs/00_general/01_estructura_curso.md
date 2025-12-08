
# Estructura del Curso
## Introducción a Edge Computing
### Objetivos
Entender por qué ciertos datos deben procesarse en el borde.
Diseñar el flujo sensor → Raspberry Pi → analítica → nube → agente IA.
### Contenido
  * Edge Computing: casos de uso en agricultura (humedad, clima, riego, diagnóstico).
  * Limitaciones reales: conectividad, energía, estabilidad, calor.
  * Integración con NAIRA: 
     * Estación Meteo
     * Suelo
     * Cultivo
     * Riego
     * Diagnóstico del nodo.
     * Sensores cableados + cámaras + MQTT + HTTP + buffer local.
### Práctica
  1. Diseñar el pipeline edge para cada tipo de sensor (suelo, clima, cultivo, riego).
  2. Crear el mapa de datos: frecuencia, tipo, criticidad, evento vs. continuo.

### Entrega
Esquema del nodo edge NAIRA con rutas de datos.

## Preparación y diagnóstico del nodo
### Objetivos
Configurar la RPi como nodo de computación para agricultura.
### Contenido
  * Raspberry Pi OS Lite, SSH, firewall, fail2ban.
  * Docker + contenedores para servicios edge.
  * Configuración de buses de sensores:
     * SPI → sensores hiperespectrales básicos.
     * Modbus RS485 → tensiómetro, caudalímetros.
  * Monitorización local:
     * Temperatura interna del nodo.
     * Voltaje de la batería.
### Práctica
  1. Script Python para lectura de temperatura del sistema + nivel de batería.
  2. Crear un servicio systemd que arranca la adquisición.

## Entrega
  * RPi operativa + diagnóstico funcionando.

## Adquisición de datos de sensores básicos
### Objetivos
Desarrollar scripts de adquisición modulares por familia de sensores.
### Contenido
  * Lectura de variables:
   * Temperatura y humedad del aire
   * Radiación solar (estación meteo o API)
   * Dirección y velocidad del viento (estación meteo o API)
   * Pluviómetro (estación meteo o API)
   * Humedad y temperatura del suelo (Sonda)
   * Tensiómetro (10/30 cm)
   * pH/CE (Opcional)
  * Variables internas  del nodo
  * Normalización de unidades, timestamps y frecuencia.
### Práctica
  1. Crear el módulo Python sensors/ con funciones de lectura reales o simuladas.
  2. Guardar datos en CSV/SQLite local cada 10–30 segundos.
### Entrega
Módulo unificado de adquisición con pruebas por sensor.

## Adquisición avanzada de datos
### Objetivos
Leer sensores más complejos y trabajar con imágenes.
### Contenido
  * Caudal/volumen de riego y acumulados.
  * Captura con cámara VGA/multiespectral.
  * Preprocesamiento mínimo de imágenes (compresión, resize).
  * Estructura de carpetas y almacenamiento multisensor.
### Práctica
  1. Script que captura imagen al detectar evento
  2. Lectura de caudalímetro y cálculo del volumen acumulado.
  3. Integración de todos los sensores del cultivo en un único script coordinado.
### Entrega
Pipeline de adquisición completo.

## Procesamiento local e IA ligera
### Objetivos
Construir analítica en el borde con los datos que se adquieren.
### Contenido
  * Filtros locales (media móvil, outliers).
  * Cálculo de indicadores:
     * Estrés hídrico
     * Balance hídrico con lluvia + riego
     * Condición del suelo (pH/CE + NPK)
     * Microclima (T/H + radiación)
  * TinyML: 
    * modelos ONNX pequeños para predicción de humedad,
    * clasificación simple: “estrés / no estrés”.
### Práctica
  1. Implementar un pipeline analytics.py con todas las funciones.
  2. Cargar un modelo ONNX y probar inferencias en la RPi.
### Entrega
Analítica local + IA funcionando.

## Publicación de datos
### Objetivos
Activar comunicaciones del nodo de forma robusta y eficiente.
### Contenido
  * MQTT para datos periódicos (clima, suelo, riego).
  * MQTT + evento para alertas (estrés hoja, tensiómetro, batería).
  * HTTP/REST para imágenes.
  * Compresión y envío batch cuando hay mala conexión.
  * Persistencia local cuando el nodo está offline.
### Práctica
  1. Enviar cada sensor a un tópico MQTT distinto (naira/suelo/humedad, …).
  2. Enviar imagen vía POST sólo cuando hay evento.
  3. Implementar buffer local + reenvío automático.
### Entrega
Nodo edge comunicando datos a la nube.

## Control local y automatización
### Objetivos
Cerrar el ciclo: actuadores y decisiones híbridas.
### Contenido
  * Control de relés, electroválvulas y bombas.
  * Reglas locales en Python:
    * humedad suelo < umbral → activar riego
    * humedad hoja alta + baja radiación → riesgo hongo
    * batería baja → modo ahorro
  * Integración con el agente IA del Curso 2 (decisión híbrida edge/cloud).
### Práctica
  1. Implementar un controlador actuadores.py.
  2. Prueba real: activar una válvula en función de la humedad.
### Entrega
Nodo edge capaz de actuar.

## Validación en campo
### Objetivos
Validar el sistema completo y documentarlo.
### Contenido
  * Integración total de sensores → analítica → MQTT → actuadores.
  * Escenarios realistas:
    * Falta de red de comunicaciones,
    * batería baja
    * lluvia intensa
    * estrés hídrico súbito.
  * Optimización energética del nodo.
### Práctica
  1. Generar un NAIRA Edge Node listo para despliegue.
  2. Crear documentación técnica mínima y dashboard de supervisión (Node-RED / Python).
### Entrega
Sistema final integrado 
