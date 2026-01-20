#!/usr/bin/env python3
"""
Ejemplo de uso de la base de datos SQLite.

Muestra cómo:
- Insertar datos simulados
- Consultar muestras
- Generar agregaciones
- Exportar estadísticas
"""

import logging
from datetime import datetime, timedelta, UTC
from src.acquisition.db import get_database

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def example_insert_samples():
    """Inserta datos de ejemplo en la BD."""
    logger.info("=" * 60)
    logger.info("EJEMPLO 1: Insertar Muestras")
    logger.info("=" * 60)
    
    db = get_database()
    
    # Crear muestras de ejemplo
    samples = [
        {
            "ts": (datetime.now(UTC) - timedelta(hours=2)).isoformat().replace("+00:00", "") + "Z",
            "node_id": "naira-node-001",
            "source": "meteo",
            "metric": "temp_aire",
            "value": 22.5,
            "unit": "°C",
            "quality": "ok"
        },
        {
            "ts": (datetime.now(UTC) - timedelta(hours=1, minutes=30)).isoformat().replace("+00:00", "") + "Z",
            "node_id": "naira-node-001",
            "source": "meteo",
            "metric": "humedad_aire",
            "value": 65.2,
            "unit": "%",
            "quality": "ok"
        },
        {
            "ts": (datetime.now(UTC) - timedelta(hours=1)).isoformat().replace("+00:00", "") + "Z",
            "node_id": "naira-node-001",
            "source": "meteo",
            "metric": "luminosidad",
            "value": 512,
            "unit": "lux",
            "quality": "ok"
        },
        {
            "ts": datetime.now(UTC).isoformat().replace("+00:00", "") + "Z",
            "node_id": "naira-node-001",
            "source": "meteo",
            "metric": "temp_aire",
            "value": 24.10,
            "unit": "°C",
            "quality": "ok"
        },
    ]
    
    inserted = db.insert_samples_batch(samples)
    logger.info(f"✓ Insertadas {inserted} muestras de ejemplo\n")

def example_query_samples():
    """Consulta muestras de la BD."""
    logger.info("=" * 60)
    logger.info("EJEMPLO 2: Consultar Muestras")
    logger.info("=" * 60)
    
    db = get_database()
    
    # Obtener últimas muestras
    all_samples = db.get_samples(limit=10)
    logger.info(f"Últimas 10 muestras: {len(all_samples)} filas\n")
    
    for sample in all_samples:
        logger.info(
            f"  {sample['ts']} | {sample['metric']:15} = {sample['value']:7.2f} {sample['unit']} ({sample['quality']})"
        )
    
    # Filtrar por métrica
    temp_samples = db.get_samples(metric="temp_aire", limit=5)
    logger.info(f"\nÚltimas 5 muestras de temperatura: {len(temp_samples)} filas")
    for sample in temp_samples:
        logger.info(f"  {sample['ts']} | {sample['value']:.2f} {sample['unit']}")


def example_time_range():
    """Consulta muestras en rango de tiempo."""
    logger.info("=" * 60)
    logger.info("EJEMPLO 3: Consultar Rango de Tiempo")
    logger.info("=" * 60)
    
    db = get_database()
    
    now = datetime.now(UTC)
    start = (now - timedelta(hours=3)).isoformat().replace("+00:00", "") + "Z"
    end = now.isoformat().replace("+00:00", "") + "Z"
    
    samples = db.get_samples_time_range(start, end, metric="temp_aire")
    logger.info(f"Muestras de temperatura entre {start[:10]} y {end[:10]}: {len(samples)} filas\n")
    
    for sample in samples:
        logger.info(f"  {sample['ts']} | {sample['value']:.2f} {sample['unit']}")


def example_stats():
    """Obtiene estadísticas de la BD."""
    logger.info("=" * 60)
    logger.info("EJEMPLO 4: Estadísticas de la BD")
    logger.info("=" * 60)
    
    db = get_database()
    stats = db.get_stats()
    
    logger.info(f"Total de muestras:        {stats.get('total_samples', 0)}")
    logger.info(f"Métricas únicas:          {stats.get('total_metrics', 0)}")
    logger.info(f"Primera muestra:          {stats.get('earliest_ts', 'N/A')}")
    logger.info(f"Última muestra:           {stats.get('latest_ts', 'N/A')}")
    logger.info(f"Tamaño de BD (MB):        {stats.get('db_size_mb', 0):.2f}")


def example_device_status():
    """Inserta estado del dispositivo."""
    logger.info("=" * 60)
    logger.info("EJEMPLO 5: Insertar Estado del Dispositivo")
    logger.info("=" * 60)
    
    db = get_database()
    
    status = {
        "ts": datetime.now(UTC).isoformat().replace("+00:00", "") + "Z",
        "status": "ok",
        "cpu_pct": 45.2,
        "ram_pct": 65.5,
        "disk_pct": 42.1,
        "temp_c": 52.3,
        "uptime_s": 86400.5
    }
    
    row_id = db.insert_device_status("naira-node-001", status)
    logger.info(f"✓ Estado del dispositivo insertado (ID={row_id})")
    logger.info(f"  CPU: {status['cpu_pct']}%")
    logger.info(f"  RAM: {status['ram_pct']}%")
    logger.info(f"  Disco: {status['disk_pct']}%")
    logger.info(f"  Temp: {status['temp_c']}°C")


def example_export_json():
    """Exporta datos a JSON."""
    logger.info("=" * 60)
    logger.info("EJEMPLO 6: Exportar a JSON")
    logger.info("=" * 60)
    
    import json
    
    db = get_database()
    samples = db.get_samples(limit=5)
    
    json_str = json.dumps(samples, indent=2, ensure_ascii=False)
    logger.info("Muestras en formato JSON:\n")
    logger.info(json_str)


if __name__ == "__main__":
    # example_insert_samples()
    # example_query_samples()
    # example_time_range()
    example_stats()
    # example_device_status()
    # example_export_json()
    
    logger.info("=" * 60)
    logger.info("✓ Ejemplos completados")
    logger.info("=" * 60)
