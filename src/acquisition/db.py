"""
Módulo de almacenamiento en SQLite para datos sensoriales.

Proporciona funciones para:
- Crear/inicializar base de datos
- Insertar muestras sensoriales
- Consultar datos históricos
- Exportar/sincronizar datos
"""

import sqlite3
import logging
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Optional

from .influx import get_influx_sink

logger = logging.getLogger(__name__)

# Ruta por defecto de la base de datos
DEFAULT_DB_PATH = "/home/naira/NAIRA/naira-edge/data/naira_sensors.db"


class SensorDatabase:
    """Gestor de base de datos SQLite para sensores NAIRA."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        """Inicializa el gestor de BD.
        
        Args:
            db_path: Ruta del archivo SQLite (se crea si no existe)
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()
        self.influx = get_influx_sink()

    def _initialize_db(self) -> None:
        """Crea tablas si no existen."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabla de muestras sensoriales
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sensor_samples (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts TEXT NOT NULL,
                        node_id TEXT NOT NULL,
                        source TEXT NOT NULL,
                        metric TEXT NOT NULL,
                        value REAL NOT NULL,
                        unit TEXT,
                        quality TEXT DEFAULT 'ok',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Índices para búsquedas rápidas
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_ts ON sensor_samples(ts)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_metric ON sensor_samples(metric)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_node ON sensor_samples(node_id)
                """)
                
                # Tabla de consolidaciones (para agregaciones diarias)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS daily_aggregates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        node_id TEXT NOT NULL,
                        metric TEXT NOT NULL,
                        value_min REAL,
                        value_max REAL,
                        value_avg REAL,
                        value_count INTEGER,
                        unit TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabla de estado del dispositivo
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS device_status (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts TEXT NOT NULL,
                        node_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        cpu_pct REAL,
                        ram_pct REAL,
                        disk_pct REAL,
                        temp_c REAL,
                        uptime_s REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info(f"Base de datos inicializada en {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error inicializando BD: {e}")
            raise

    def insert_sample(self, sample: Dict) -> int:
        """Inserta una muestra sensorial.
        
        Args:
            sample: Dict con estructura normalizada:
                {
                    "ts": "ISO8601-UTC",
                    "node_id": "naira-node-001",
                    "source": "meteo|suelo|riego",
                    "metric": "temp_aire|humedad_suelo",
                    "value": 23.45,
                    "unit": "°C|%",
                    "quality": "ok|suspect|bad"
                }
        
        Returns:
            ID de la fila insertada
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sensor_samples
                    (ts, node_id, source, metric, value, unit, quality)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sample.get("ts"),
                    sample.get("node_id"),
                    sample.get("source"),
                    sample.get("metric"),
                    sample.get("value"),
                    sample.get("unit"),
                    sample.get("quality", "ok")
                ))
                conn.commit()
                row_id = cursor.lastrowid
                logger.debug(f"Muestra insertada: ID={row_id}, metric={sample.get('metric')}")
                self._replicate_sample(sample)
                return row_id
        except sqlite3.Error as e:
            logger.error(f"Error insertando muestra: {e}")
            raise

    def insert_samples_batch(self, samples: List[Dict]) -> int:
        """Inserta múltiples muestras en una transacción.
        
        Args:
            samples: Lista de dicts de muestras
            
        Returns:
            Número de filas insertadas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                inserted = 0
                successful_samples: List[Dict] = []
                for sample in samples:
                    try:
                        cursor.execute("""
                            INSERT INTO sensor_samples
                            (ts, node_id, source, metric, value, unit, quality)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            sample.get("ts"),
                            sample.get("node_id"),
                            sample.get("source"),
                            sample.get("metric"),
                            sample.get("value"),
                            sample.get("unit"),
                            sample.get("quality", "ok")
                        ))
                        inserted += 1
                        successful_samples.append(sample)
                    except sqlite3.Error as e:
                        logger.warning(f"Error insertando muestra individual: {e}")
                        continue
                
                conn.commit()
                logger.info(f"Lote insertado: {inserted} de {len(samples)} muestras")
                self._replicate_samples(successful_samples)
                return inserted
        except sqlite3.Error as e:
            logger.error(f"Error en inserción por lotes: {e}")
            raise

    def insert_device_status(self, node_id: str, status_data: Dict) -> int:
        """Inserta estado del dispositivo.
        
        Args:
            node_id: ID del nodo
            status_data: Dict con métricas del sistema:
                {
                    "ts": "ISO8601-UTC",
                    "status": "ok|warning|error",
                    "cpu_pct": 45.2,
                    "ram_pct": 65.5,
                    "disk_pct": 42.1,
                    "temp_c": 52.3,
                    "uptime_s": 86400.5
                }
        
        Returns:
            ID de la fila insertada
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO device_status
                    (ts, node_id, status, cpu_pct, ram_pct, disk_pct, temp_c, uptime_s)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    status_data.get("ts", datetime.utcnow().isoformat() + "Z"),
                    node_id,
                    status_data.get("status", "ok"),
                    status_data.get("cpu_pct"),
                    status_data.get("ram_pct"),
                    status_data.get("disk_pct"),
                    status_data.get("temp_c"),
                    status_data.get("uptime_s")
                ))
                conn.commit()
                row_id = cursor.lastrowid
                self._replicate_device_status(node_id, status_data)
                return row_id
        except sqlite3.Error as e:
            logger.error(f"Error insertando estado: {e}")
            raise

    def get_samples(self, metric: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Obtiene muestras recientes.
        
        Args:
            metric: Filtrar por métrica (ej: "temp_aire")
            limit: Número máximo de filas
            
        Returns:
            Lista de dicts con las muestras
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if metric:
                    query = """
                        SELECT * FROM sensor_samples
                        WHERE metric = ?
                        ORDER BY ts DESC
                        LIMIT ?
                    """
                    cursor.execute(query, (metric, limit))
                else:
                    query = """
                        SELECT * FROM sensor_samples
                        ORDER BY ts DESC
                        LIMIT ?
                    """
                    cursor.execute(query, (limit,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo muestras: {e}")
            return []

    def get_samples_time_range(self, start_ts: str, end_ts: str, 
                               metric: Optional[str] = None) -> List[Dict]:
        """Obtiene muestras en un rango de tiempo.
        
        Args:
            start_ts: Timestamp inicio (ISO8601)
            end_ts: Timestamp fin (ISO8601)
            metric: Filtrar por métrica (opcional)
            
        Returns:
            Lista de dicts con las muestras
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if metric:
                    query = """
                        SELECT * FROM sensor_samples
                        WHERE ts BETWEEN ? AND ? AND metric = ?
                        ORDER BY ts
                    """
                    cursor.execute(query, (start_ts, end_ts, metric))
                else:
                    query = """
                        SELECT * FROM sensor_samples
                        WHERE ts BETWEEN ? AND ?
                        ORDER BY ts
                    """
                    cursor.execute(query, (start_ts, end_ts))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo rango de tiempo: {e}")
            return []

    def compute_daily_aggregate(self, date_str: str, metric: str, 
                                node_id: str = "naira-node-001") -> Dict:
        """Calcula agregación diaria para una métrica.
        
        Args:
            date_str: Fecha en formato YYYY-MM-DD
            metric: Métrica (ej: "temp_aire")
            node_id: ID del nodo
            
        Returns:
            Dict con agregaciones (min, max, avg, count)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Obtener muestras del día
                query = """
                    SELECT value, unit FROM sensor_samples
                    WHERE DATE(ts) = ? AND metric = ? AND node_id = ?
                """
                cursor.execute(query, (date_str, metric, node_id))
                rows = cursor.fetchall()
                
                if not rows:
                    logger.warning(f"No hay muestras para {metric} en {date_str}")
                    return {}
                
                values = [row[0] for row in rows]
                unit = rows[0][1] if rows else ""
                
                aggregate = {
                    "value_min": min(values),
                    "value_max": max(values),
                    "value_avg": sum(values) / len(values),
                    "value_count": len(values),
                    "unit": unit
                }
                
                # Insertar agregación en BD
                cursor.execute("""
                    INSERT INTO daily_aggregates
                    (date, node_id, metric, value_min, value_max, value_avg, value_count, unit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    date_str, node_id, metric,
                    aggregate["value_min"],
                    aggregate["value_max"],
                    aggregate["value_avg"],
                    aggregate["value_count"],
                    aggregate["unit"]
                ))
                conn.commit()
                
                logger.info(f"Agregación calculada: {metric} → {aggregate}")
                return aggregate
        except sqlite3.Error as e:
            logger.error(f"Error calculando agregación: {e}")
            return {}

    def get_stats(self) -> Dict:
        """Obtiene estadísticas de la base de datos.
        
        Returns:
            Dict con conteos y fechas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM sensor_samples")
                total_samples = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT metric) FROM sensor_samples")
                total_metrics = cursor.fetchone()[0]
                
                cursor.execute("SELECT MIN(ts), MAX(ts) FROM sensor_samples")
                result = cursor.fetchone()
                min_ts, max_ts = result if result else (None, None)
                
                return {
                    "total_samples": total_samples,
                    "total_metrics": total_metrics,
                    "earliest_ts": min_ts,
                    "latest_ts": max_ts,
                    "db_size_mb": self.db_path.stat().st_size / (1024 * 1024)
                }
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

    def delete_old_samples(self, days_old: int = 30) -> int:
        """Elimina muestras más antiguas de N días.
        
        Args:
            days_old: Número de días
            
        Returns:
            Número de filas eliminadas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM sensor_samples
                    WHERE ts < datetime('now', '-' || ? || ' days')
                """, (days_old,))
                conn.commit()
                deleted = cursor.rowcount
                logger.info(f"Eliminadas {deleted} muestras más antiguas de {days_old} días")
                return deleted
        except sqlite3.Error as e:
            logger.error(f"Error eliminando muestras antiguas: {e}")
            return 0

    def _replicate_sample(self, sample: Dict) -> None:
        if not self.influx:
            logger.debug("Replicación Influx omitida: sink no disponible")
            return
        try:
            logger.info("Replicando muestra a Influx: %s", sample.get("metric"))
            self.influx.write_sample(sample)
        except Exception as exc:
            logger.warning(
                "Replicación a Influx falló para %s: %s",
                sample.get("metric", "unknown"),
                exc,
            )

    def _replicate_samples(self, samples: List[Dict]) -> None:
        if not self.influx or not samples:
            return
        try:
            self.influx.write_samples(samples)
        except Exception as exc:
            logger.warning("Replicación en lote a Influx falló: %s", exc)

    def _replicate_device_status(self, node_id: str, status_data: Dict) -> None:
        if not self.influx:
            return
        try:
            self.influx.write_device_status(node_id, status_data)
        except Exception as exc:
            logger.warning("Replicación de estado a Influx falló: %s", exc)

    def close(self) -> None:
        """Cierra la conexión (si la hay abierta)."""
        pass


# Factory para crear instancia global
_db_instance: Optional[SensorDatabase] = None


def get_database(db_path: str = DEFAULT_DB_PATH) -> SensorDatabase:
    """Obtiene instancia global de la BD.
    
    Args:
        db_path: Ruta de la BD (usado solo en primera llamada)
        
    Returns:
        Instancia de SensorDatabase
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = SensorDatabase(db_path)
    return _db_instance


__all__ = ["SensorDatabase", "get_database"]
