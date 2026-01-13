# Módulo 3 · Guion docente

## Enfoque general
Este módulo es **muy práctico**.  
La teoría debe servir únicamente para que el alumnado entienda **por qué** se estructura así un sistema de adquisición y **qué problemas reales resuelve**.

No profundizar en exceso en Modbus ni en electrónica: el foco es el **software y la arquitectura**.

---

## Sesión 1 (3 h) — Teórico-práctica

### 1. Introducción y contexto (15 min)
- Recordar el flujo completo del sistema IoT:
  sensor → adquisición → almacenamiento → análisis → decisión
- Explicar que este módulo construye la **base de todo lo demás**

### 2. Teoría esencial (45 min)
- Qué es una adquisición robusta:
  - timestamps coherentes
  - datos incompletos
  - sensores que fallan
- RS485 / Modbus RTU:
  - qué problema resuelve
  - por qué se usa en industria
- Concepto de modo simulado

👉 No entrar en tramas Modbus ni hexadecimales.

### 3. Ejercicio práctico 1 (45 min)
- Crear la estructura de carpetas del módulo
- Definir el esquema común de datos
- Implementar un primer sensor simulado

Acompañar paso a paso.

### 4. Ejercicio práctico 2 (45 min)
- Guardar datos en CSV
- Comprobar que los datos se generan correctamente
- Revisar errores típicos (rutas, formatos, timestamps)

---

## Sesión 2 (3 h) — Repaso, ejercicios y caso práctico

### 1. Repaso guiado (20–30 min)
- Revisar estructura y código del día anterior
- Analizar errores comunes detectados

### 2. Ejercicio práctico 1 (45 min)
- Persistencia en SQLite
- Inserción y consulta de datos
- Comparar CSV vs SQLite

### 3. Ejercicio práctico 2 (45 min)
- Modo real (si hay hardware) o simulación avanzada
- Introducir fallos y eventos
- Uso del campo `quality`

### 4. Caso práctico final (60 min)
- Nodo completo de adquisición
- Loop periódico
- Múltiples sensores
- Almacenamiento y resumen de estado
