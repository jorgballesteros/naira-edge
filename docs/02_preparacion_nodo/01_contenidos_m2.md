# Contenidos - Módulo 2. Preparación y diagnóstico del nodo
## Objetivos
Configurar la Raspberry Pi 4 como nodo edge NAIRA para agricultura.

## Contenido
  * Instalación Raspberry Pi OS Lite, SSH y seguridad básica (firewall + fail2ban).
  * Configuración de buses de sensores:
     * RS485/Modbus → tensiómetro, caudalímetro, PLC de riego.
     * I2C → tensiómetros digitales.
     * SPI → cámaras o sensores avanzados.
  * Conectividad en campo:
     * WiFi + 4G (failover).
     * Diagnóstico de red.
  * Monitorización local del nodo:
     * Temperatura interna del CPU.
     * Tensión de la batería/panel.
     * Logs y salud del sistema.
  * Servicios del nodo:
     * Python + entorno virtual.
     * Docker para servicios edge.
     * systemd para adquisición continua.

## Práctica
  1. Configurar la Raspberry Pi: SSH, actualización, servicios básicos.
  2. Detectar buses (I2C, UART, RS485) y leer un sensor sencillo.
  3. Crear un script de diagnóstico (CPU, RAM, disco, batería, red).
  4. Crear un servicio `systemd` que ejecuta la adquisición al arrancar.

## Entrega
  * Raspberry Pi operativa + diagnóstico funcionando.