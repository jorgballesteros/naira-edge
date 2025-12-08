# Edge Computing para la Gestión de Cultivos

Este repositorio contiene los materiales, código, documentación y ejercicios del **Curso 3: Edge Computing para la Gestión de Cultivos**, desarrollado en el marco del proyecto **NAIRA – Sistema de inteligencia aplicada para la transformación circular del sector agroalimentario**.

El curso enseña a diseñar, desplegar y operar **nodos de computación en el borde (edge)** basados en Raspberry Pi para procesar datos agrícolas en tiempo real y soportar la toma de decisiones inteligente en cultivos.

---

## Objetivo del curso

Capacitar al alumnado para construir un **nodo edge funcional** capaz de:

- adquirir datos de sensores agrícolas (suelo, clima, cultivo, riego),
- procesar y analizar datos localmente,
- ejecutar modelos ligeros de IA,
- detectar eventos críticos en el cultivo,
- controlar actuadores (riego, ventilación, etc.),
- comunicarse con servicios NAIRA mediante MQTT/HTTP,
- operar de forma robusta y eficiente en campo.

---

## Contenidos del repositorio

    naira-edge/
    ├─ docs/ → Documentación del curso y materiales teóricos
    ├─ assets/ → Diagramas, imágenes y recursos visuales
    ├─ slides/ → Presentaciones por módulos
    ├─ data/ → Datos brutos y procesados para prácticas
    ├─ notebooks/ → EDA, indicadores agronómicos y modelos ligeros
    ├─ src/ → Código del nodo Raspberry Pi (producción)
    ├─ exercises/ → Ejercicios por módulo + proyecto final
    ├─ tools/ → Scripts auxiliares para simulación y tests
    └─ templates/ → Plantillas para informes y memorias

---

## Datos y sensores

El curso trabaja sobre datos reales/simulados provenientes de:

### **Estación meteorológica**
- Temperatura aire  
- Humedad aire  
- Radiación solar
- Pluviómetro
- Dirección y velocidad del viento

### **Suelo**
- Humedad de suelo  
- Temperatura de suelo
- pH y conductividad eléctrica (CE)  
- Tensiómetros a 10 y 30 cm (opcional)

### **Cultivo** 
- Cámara VGA (opcional)
- Sensor multiespectral (opcional)

### **Riego**
- Caudal / cantidad de agua  

### **Diagnóstico del nodo**
- Temperatura interna  
- Tensión de la batería (opcional)

Estos datos se utilizan para ejercicios de adquisición, analítica local e integración con IA.

---

## Estructura del curso

El curso se organiza en 7 módulos:

1. **Introducción al Edge Computing**  
2. **Preparación y diagnóstico del nodo**  
3. **Adquisición de datos de sensores**  
4. **Procesamiento local e IA ligera**  
5. **Comunicaciones y envío de datos**  
6. **Control y automatización de riego**  
7. **Validación en campo**  

---

## Código del nodo Edge

En la carpeta `src/` se incluye:

    src/
    ├─ main.py                 # Punto de entrada del nodo edge
    ├─ config.py               # Carga de configuración
    ├─ acquisition/            # Lectura de sensores
    ├─ processing/             # Filtros e indicadores
    ├─ models/                 # Modelos ligeros de IA
    ├─ comms/                  # MQTT, HTTP, etc.
    ├─ control/                # Actuadores y lógica de riego
    └─ diagnostics/            # Salud del nodo (T interna, batería)


Este módulo puede ejecutarse tanto en Raspberry Pi real como en modo simulado.

---

## Proyecto final

El alumnado desarrollará un **Nodo Edge NAIRA completo**, integrando:

- adquisición continua de sensores,
- cálculo de indicadores,
- IA ligera local,
- reglas de control de riego,
- envío de datos a la nube,
- panel básico de monitorización.

---

## Contribuciones

Este repositorio está diseñado como material docente y técnico del proyecto NAIRA.  
Mejoras, extensiones o materiales adicionales son bienvenidos mediante Pull Requests.

---

## Licencia

Este proyecto se distribuye bajo la licencia incluida en el archivo `LICENSE`.

---

## Contacto

Para dudas y soporte técnico del curso NAIRA:  
**Instructor:** Jorge Ballesteros (ITER)  
