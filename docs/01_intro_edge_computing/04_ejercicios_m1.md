# Ejercicios — Módulo 1. Introducción al Edge Computing

## **Ejercicio 1 — Identificar procesos que deben ejecutarse en el Edge**
En agricultura digital, no todos los procesos pueden depender de la nube.

### Tarea
Elige **un caso real** (riego, estrés hídrico, hongos, viento, temperatura, etc.) y clasifica:

1. Procesos que **deben ejecutarse en el Edge** (decisión inmediata).
2. Procesos que **pueden ejecutarse en la nube**.
3. Procesos que **deben ejecutarse en ambos** (modelo híbrido).

Justifica cada decisión.

---

## **Ejercicio 2 — Análisis de latencia**
Supongamos un cultivo donde:

- El sensor de humedad genera datos cada **10 segundos**.
- El enlace 4G tiene latencias de **200–700 ms**.
- Las decisiones de riego deben tomarse en **< 100 ms**.

### Tarea
1. Explica por qué un sistema “solo cloud” fallaría.  
2. Propón un flujo completo de procesamiento y actuación en el edge.  
3. Identifica qué información debe enviarse a la nube y con qué frecuencia.

---

## **Ejercicio 3 — Diseño básico de un nodo Edge**
Debes diseñar el esquema funcional de un nodo NAIRA (edge) para un cultivo de ejemplo.

### Incluir:
- Sensores utilizados.  
- Datos que adquiere el nodo.  
- Procesos que ejecuta localmente.  
- Eventos o alertas que genera.  
- Acciones directas sobre actuadores.  
- Qué información envía al servidor NAIRA y cuándo.

Puedes usar un diagrama (texto, flechas simples o mermaid).

---

## **Ejercicio 4 — Ventajas del modelo híbrido**
Analiza un escenario con:

- sensores de humedad,  
- tensiómetros,  
- estación meteo,  
- cámara VGA,  
- conectividad irregular.

### Tarea
Redacta un párrafo argumentando por qué un modelo híbrido (Edge + Cloud) es más eficiente que uno puramente cloud, incluyendo aspectos de:

- latencia,
- resiliencia,
- coste,
- sostenibilidad,
- calidad de datos,
- uso de IA.

---

## **Ejercicio 5 (opcional) — Interpretación del diagrama NAIRA**
Observa el diagrama del módulo e interpreta:

1. Qué ocurre en el nodo edge desde la lectura del sensor hasta el control del riego.  
2. Qué rol tiene el servidor NAIRA.  
3. Qué intercambian la IA ligera y la IA avanzada.  
4. Dónde fallaría el sistema si solo existiera la nube.

