# Módulo 3 · Ejercicios

## Sesión 1 — Teórico-práctica

### Ejercicio 1 · Estructura de adquisición
**Objetivo:** crear la base del sistema de adquisición.

Tareas:
1. Crear la estructura de carpetas del módulo.
2. Definir el esquema común de datos.
3. Implementar un sensor simulado.

Entrega:
- Código funcional
- Lecturas generadas correctamente

---

### Ejercicio 2 · Almacenamiento en CSV
**Objetivo:** persistir datos de sensores.

Tareas:
1. Implementar un módulo de almacenamiento en CSV.
2. Guardar varias lecturas consecutivas.
3. Verificar el contenido del fichero.

Entrega:
- Archivo CSV generado
- Datos coherentes y bien formateados

---

## Sesión 2 — Repaso y caso práctico

### Ejercicio 3 · Persistencia en SQLite
**Objetivo:** usar una base de datos local.

Tareas:
1. Crear una base SQLite.
2. Insertar lecturas.
3. Consultar los últimos valores.

Entrega:
- Base de datos funcional
- Consulta ejecutada correctamente

---

### Ejercicio 4 · Modo real o simulación avanzada
**Objetivo:** gestionar errores y calidad del dato.

Tareas:
1. Leer datos reales o simulados con eventos.
2. Detectar fallos o valores anómalos.
3. Marcar la calidad del dato.

Entrega:
- Lecturas con campo `quality`
- Evidencia de gestión de errores

---

### Caso práctico final · Nodo de adquisición
Construir un nodo completo que:
- Lea varios sensores
- Funcione de forma periódica
- Almacene datos
- Genere un pequeño resumen de estado

Entrega final:
- Código
- Datos generados
- Explicación breve del funcionamiento
