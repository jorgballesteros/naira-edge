# Convenciones del repositorio

Este documento describe las **normas de organización, nombres y rutas** del repositorio del curso  
**“Edge Computing para la Gestión de Cultivos (NAIRA)”**.  
Su objetivo es que cualquier persona (docente o participante) pueda entender y extender el material sin perderse.

---

## 1. Estructura general del repositorio

Estructura de alto nivel:

```text
edge-cultivos-naira-curso3/
├─ README.md
├─ LICENSE
├─ docs/          → Documentación del curso (todo el contenido docente)
├─ data/          → Datos brutos y procesados para prácticas
├─ notebooks/     → Notebooks Jupyter de análisis y prototipado
├─ src/           → Código fuente del nodo edge y utilidades
├─ assets/        → Diagramas, esquemas e imágenes
├─ tools/         → Scripts auxiliares (simulación, pruebas, etc.)
└─ templates/     → Plantillas de informes y entregables
````

**Regla general:**

* Todo lo que sea **explicación, enunciado, ejercicio, guía o documentación** va en `docs/`.
* Todo lo que sea **código ejecutable** va en `src/` (y, si es de prototipado, en `notebooks/`).

---

## 2. Convenciones de nombres

### 2.1 Idioma y formato

* Nombres de archivos de documentación:

  * Idioma: **castellano**.
  * Formato: `nn_descripcion_corta.md`, en minúsculas, con guiones bajos.
  * Ejemplo: `01_contenidos_m3.md`, `04_ejercicios_m6.md`.

* Directorios de módulos:

  * Prefijo con **número de módulo** (dos dígitos) + nombre.
  * Ejemplo: `03_modulo3_adquisicion_sensores/`.

* Código fuente (Python):

  * snake_case para archivos y módulos.
  * Ejemplo: `meteo_reader.py`, `indicadores_hidricos.py`.

* Clases en Python:

  * `CamelCase`.
  * Ejemplo: `SensorReader`, `MQTTClient`, `IrrigationController`.

---

### 2.2 Prefijos de archivos en `docs/`

En cada carpeta de módulo se sigue el mismo patrón:

```text
01_contenidos_mX.md        → Qué se ve en el módulo (temario)
02_guion_docente_mX.md     → Guion para el formador
03_material_alumno_mX.md   → Versión limpia para el alumnado
04_ejercicios_mX.md        → Enunciado de ejercicios
05_sugerencias_solucion_mX.md → Pautas y soluciones
```

Ejemplo para el Módulo 4:

```text
docs/04_modulo4_procesamiento_ia_ligera/
├─ 01_contenidos_m4.md
├─ 02_guion_docente_m4.md
├─ 03_material_alumno_m4.md
├─ 04_ejercicios_m4.md
└─ 05_sugerencias_solucion_m4.md
```

---

## 3. Convenciones en `src/`

El código se organiza por **responsabilidades**:

```text
src/
├─ main.py                 # Punto de entrada del nodo edge
├─ config.py               # Carga/parsing de configuración
├─ acquisition/            # Lectura de sensores
├─ processing/             # Limpieza, filtros, indicadores
├─ models/                 # Modelos ligeros de IA
├─ comms/                  # MQTT, HTTP, etc.
├─ control/                # Actuadores y lógica de riego
└─ diagnostics/            # Salud del nodo y logging
```

Ejemplos de nombres:

* Lectura de sensores:

  * `acquisition/meteo_reader.py`
  * `acquisition/soil_reader.py`
  * `acquisition/irrigation_reader.py`
  * `acquisition/node_diagnostics_reader.py`

* Procesamiento:

  * `processing/filtros.py`
  * `processing/indicadores_hidricos.py`
  * `processing/event_detector.py`

* Comunicaciones:

  * `comms/mqtt_client.py`
  * `comms/http_client.py`

* Control:

  * `control/irrigation_controller.py`

* Diagnóstico:

  * `diagnostics/health_check.py`

**Reglas básicas de estilo:**

* Una responsabilidad clara por módulo (fichero) siempre que sea posible.
* Evitar lógica compleja en `main.py`; usarlo como “orquestador”.
* Añadir docstrings en funciones y clases clave.

---

## 4. Convenciones de rutas y referencias

* En documentación (`docs/`), las rutas hacia código se referencian de forma relativa desde la raíz del repo, por ejemplo:

  ```text
  src/acquisition/soil_reader.py
  src/comms/mqtt_client.py
  ```

* En los ejemplos dentro de los `.md` se asume que el repositorio se clona en un directorio de trabajo y se ejecuta desde la raíz:

  ```bash
  git clone <URL_REPO>
  cd edge-cultivos-naira-curso3
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

---

## 5. Uso recomendado del repositorio

### 5.1 Para docentes

* **Preparación**:

  * Revisar `docs/00_general/00_intro_curso.md` y `01_estructura_curso.md`.
  * Leer el módulo correspondiente en `docs/0X_moduloX_*/02_guion_docente_mX.md`.

* **Durante la sesión**:

  * Proyectar o compartir partes de `03_material_alumno_mX.md`.
  * Apoyarse en ejemplos de `notebooks/` y fragmentos de código en `src/`.

* **Seguimiento**:

  * Asignar ejercicios desde `04_ejercicios_mX.md`.
  * Usar `05_sugerencias_solucion_mX.md` como guía de corrección.

### 5.2 Para participantes

* Leer primero `README.md` y `docs/00_general/00_intro_curso.md`.
* Abrir los materiales del módulo que corresponda (dentro de `docs/0X_moduloX_*`).
* Clonar y trabajar siempre desde una rama propia, si se versiona con Git.

---

## 6. Nomenclatura de ramas (opcional)

Si se usa Git de forma colaborativa, se recomienda:

* `main` → versión “estable” del curso.
* `dev` → cambios en desarrollo.
* `feature/mX-nombre-corto` → rama para ampliar o corregir un módulo concreto.

  * Ejemplo: `feature/m3-sensores-suelo`.

---

## 7. Estilo de documentación

* Formato: **Markdown** (`.md`).
* Idioma: **castellano**, salvo fragmentos de código o nombres técnicos.
* Listas cortas y secciones claras (no texto en bloque).
* Incluir siempre contexto mínimo al inicio del archivo (qué es, para quién, cómo se usa).