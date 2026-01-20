"""
Tests para la lectura de datos del puerto serie.

Prueba:
- Lectura raw de líneas
- Parsing de temperatura (temperature X.XX)
- Parsing de luz (light X.XX)
- Parsing de humedad suelo (moisture X)
- Manejo de líneas malformadas
- Validación de rangos
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from .collector import SerialCollector


class TestSerialReading:
    """Tests para lectura básica de puerto serie."""

    def test_read_line_returns_string(self):
        """Verifica que read_line devuelve string."""
        collector = SerialCollector()
        
        # Mock del puerto serie
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.readline.return_value = b"temperature 23.45\n"
        collector.ser = mock_serial
        
        line = collector.read_line()
        
        assert isinstance(line, str)
        assert line == "temperature 23.45"

    def test_read_line_handles_empty_line(self):
        """Verifica que read_line retorna None para línea vacía."""
        collector = SerialCollector()
        
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.readline.return_value = b"\n"
        collector.ser = mock_serial
        
        line = collector.read_line()
        
        assert line is None

    def test_read_line_handles_utf8_errors(self):
        """Verifica que read_line maneja errores de encoding."""
        collector = SerialCollector()
        
        mock_serial = MagicMock()
        mock_serial.is_open = True
        # Bytes inválidos UTF-8
        mock_serial.readline.return_value = b"temperature \xFF\xFE\n"
        collector.ser = mock_serial
        
        line = collector.read_line()
        
        # Debe ignorar errores y devolver lo que pueda
        assert isinstance(line, str)

    def test_read_line_returns_none_if_not_connected(self):
        """Verifica que read_line retorna None si no hay conexión."""
        collector = SerialCollector()
        collector.ser = None
        
        line = collector.read_line()
        
        assert line is None


class TestTemperatureParsing:
    """Tests para parsing de temperatura."""

    def test_parse_valid_temperature(self):
        """Parsea temperatura válida."""
        collector = SerialCollector()
        
        result = collector.parse_line("temperature 23.45")
        
        assert result is not None
        assert result["metric"] == "temp_aire"
        assert result["value"] == 23.45
        assert result["unit"] == "°C"
        assert result["source"] == "meteo"

    def test_parse_temperature_with_whitespace(self):
        """Parsea temperatura con espacios extras."""
        collector = SerialCollector()
        
        result = collector.parse_line("temperature  45.67")
        
        assert result is not None
        assert result["value"] == 45.67

    def test_parse_temperature_integer(self):
        """Parsea temperatura como entero."""
        collector = SerialCollector()
        
        result = collector.parse_line("temperature 20")
        
        assert result is not None
        assert result["value"] == 20.0

    def test_parse_temperature_malformed_returns_none(self):
        """Retorna None para temperatura malformada."""
        collector = SerialCollector()
        
        result = collector.parse_line("temperature abc")
        
        assert result is None

    def test_parse_temperature_missing_value_returns_none(self):
        """Retorna None si falta el valor."""
        collector = SerialCollector()
        
        result = collector.parse_line("temperature")
        
        assert result is None


class TestLightParsing:
    """Tests para parsing de luz/luminosidad."""

    def test_parse_valid_light(self):
        """Parsea luz válida."""
        collector = SerialCollector()
        
        result = collector.parse_line("light 5.00")
        
        assert result is not None
        assert result["metric"] == "luminosidad"
        assert result["value"] == 5.00
        assert result["unit"] == "lux"
        assert result["source"] == "meteo"

    def test_parse_light_integer(self):
        """Parsea luz como entero."""
        collector = SerialCollector()
        
        result = collector.parse_line("light 512")
        
        assert result is not None
        assert result["value"] == 512.0

    def test_parse_light_zero(self):
        """Parsea luz cero (sin luz)."""
        collector = SerialCollector()
        
        result = collector.parse_line("light 0")
        
        assert result is not None
        assert result["value"] == 0.0

    def test_parse_light_malformed_returns_none(self):
        """Retorna None para luz malformada."""
        collector = SerialCollector()
        
        result = collector.parse_line("light xyz")
        
        assert result is None


class TestMoistureParsing:
    """Tests para parsing de humedad del suelo."""

    def test_parse_valid_moisture(self):
        """Parsea humedad suelo válida."""
        collector = SerialCollector()
        
        result = collector.parse_line("moisture 800")
        
        assert result is not None
        assert result["metric"] == "humedad_suelo"
        assert result["value"] == 800.0
        assert result["unit"] == "%"
        assert result["source"] == "suelo"

    def test_parse_moisture_float(self):
        """Parsea humedad suelo como float."""
        collector = SerialCollector()
        
        result = collector.parse_line("moisture 650.5")
        
        assert result is not None
        assert result["value"] == 650.5

    def test_parse_moisture_dry(self):
        """Parsea humedad suelo seco (bajo)."""
        collector = SerialCollector()
        
        result = collector.parse_line("moisture 300")
        
        assert result is not None
        assert result["value"] == 300.0

    def test_parse_moisture_wet(self):
        """Parsea humedad suelo mojado (alto)."""
        collector = SerialCollector()
        
        result = collector.parse_line("moisture 950")
        
        assert result is not None
        assert result["value"] == 950.0

    def test_parse_moisture_malformed_returns_none(self):
        """Retorna None para humedad malformada."""
        collector = SerialCollector()
        
        result = collector.parse_line("moisture xxx")
        
        assert result is None


class TestUnknownSensor:
    """Tests para sensores desconocidos."""

    def test_parse_unknown_sensor_returns_none(self):
        """Retorna None para sensor desconocido."""
        collector = SerialCollector()
        
        result = collector.parse_line("pressure 1013.25")
        
        assert result is None

    def test_parse_malformed_line_returns_none(self):
        """Retorna None para línea sin separador."""
        collector = SerialCollector()
        
        result = collector.parse_line("temperature23.45")
        
        assert result is None

    def test_parse_empty_line_returns_none(self):
        """Retorna None para línea vacía."""
        collector = SerialCollector()
        
        result = collector.parse_line("")
        
        assert result is None


class TestQualityAssessment:
    """Tests para evaluación de calidad de datos."""

    def test_quality_ok_for_valid_temperature(self):
        """Temperatura válida tiene calidad 'ok'."""
        collector = SerialCollector()
        
        quality = collector._assess_quality("temp_aire", 25.0)
        
        assert quality == "ok"

    def test_quality_bad_for_temperature_too_low(self):
        """Temperatura muy baja tiene calidad 'bad'."""
        collector = SerialCollector()
        
        quality = collector._assess_quality("temp_aire", -50.0)
        
        assert quality == "bad"

    def test_quality_bad_for_temperature_too_high(self):
        """Temperatura muy alta tiene calidad 'bad'."""
        collector = SerialCollector()
        
        quality = collector._assess_quality("temp_aire", 100.0)
        
        assert quality == "bad"

    def test_quality_ok_for_valid_moisture(self):
        """Humedad suelo válida tiene calidad 'ok'."""
        collector = SerialCollector()
        
        quality = collector._assess_quality("humedad_suelo", 500.0)
        
        assert quality == "ok"

    def test_quality_bad_for_moisture_negative(self):
        """Humedad negativa tiene calidad 'bad'."""
        collector = SerialCollector()
        
        quality = collector._assess_quality("humedad_suelo", -10.0)
        
        assert quality == "bad"

    def test_quality_bad_for_moisture_out_of_range(self):
        """Humedad fuera de rango tiene calidad 'bad'."""
        collector = SerialCollector()
        
        quality = collector._assess_quality("humedad_suelo", 2000.0)
        
        assert quality == "bad"

    def test_quality_ok_for_valid_light(self):
        """Luz válida tiene calidad 'ok'."""
        collector = SerialCollector()
        
        quality = collector._assess_quality("luminosidad", 500.0)
        
        assert quality == "ok"

    def test_quality_bad_for_light_negative(self):
        """Luz negativa tiene calidad 'bad'."""
        collector = SerialCollector()
        
        quality = collector._assess_quality("luminosidad", -100.0)
        
        assert quality == "bad"

    def test_quality_ok_for_unknown_metric(self):
        """Métrica desconocida tiene calidad 'ok' (no validar)."""
        collector = SerialCollector()
        
        quality = collector._assess_quality("unknown_metric", 999999.0)
        
        assert quality == "ok"


class TestNormalization:
    """Tests para normalización de muestras."""

    def test_normalize_sample_structure(self):
        """Verifica estructura de muestra normalizada."""
        collector = SerialCollector()
        
        parsed = {
            "metric": "temp_aire",
            "value": 23.45,
            "unit": "°C",
            "source": "meteo"
        }
        
        normalized = collector.normalize_sample(parsed)
        
        # Verificar campos requeridos
        assert "ts" in normalized
        assert "node_id" in normalized
        assert "source" in normalized
        assert "metric" in normalized
        assert "value" in normalized
        assert "unit" in normalized
        assert "quality" in normalized
        
        # Verificar valores
        assert normalized["node_id"] == "naira-node-001"
        assert normalized["metric"] == "temp_aire"
        assert normalized["value"] == 23.45
        assert normalized["unit"] == "°C"

    def test_normalize_sample_quality_assessment(self):
        """Verifica que normalización incluye evaluación de calidad."""
        collector = SerialCollector()
        
        parsed = {
            "metric": "temp_aire",
            "value": -50.0,  # Fuera de rango
            "unit": "°C",
            "source": "meteo"
        }
        
        normalized = collector.normalize_sample(parsed)
        
        assert normalized["quality"] == "bad"

    def test_normalize_sample_with_valid_moisture(self):
        """Normaliza muestra de humedad suelo válida."""
        collector = SerialCollector()
        
        parsed = {
            "metric": "humedad_suelo",
            "value": 650,
            "unit": "%",
            "source": "suelo"
        }
        
        normalized = collector.normalize_sample(parsed)
        
        assert normalized["source"] == "suelo"
        assert normalized["quality"] == "ok"


class TestIntegration:
    """Tests de integración: parse → normalize."""

    def test_full_pipeline_temperature(self):
        """Pipeline completo: línea raw → normalizado (temperatura)."""
        collector = SerialCollector()
        
        # Raw line
        line = "temperature 18.96"
        
        # Parse
        parsed = collector.parse_line(line)
        assert parsed is not None
        
        # Normalize
        normalized = collector.normalize_sample(parsed)
        
        # Verify
        assert normalized["metric"] == "temp_aire"
        assert normalized["value"] == 18.96
        assert normalized["quality"] == "ok"

    def test_full_pipeline_moisture(self):
        """Pipeline completo: línea raw → normalizado (humedad)."""
        collector = SerialCollector()
        
        # Raw line
        line = "moisture 800"
        
        # Parse
        parsed = collector.parse_line(line)
        assert parsed is not None
        
        # Normalize
        normalized = collector.normalize_sample(parsed)
        
        # Verify
        assert normalized["metric"] == "humedad_suelo"
        assert normalized["value"] == 800
        assert normalized["source"] == "suelo"
        assert normalized["quality"] == "ok"

    def test_full_pipeline_light(self):
        """Pipeline completo: línea raw → normalizado (luz)."""
        collector = SerialCollector()
        
        # Raw line
        line = "light 5.00"
        
        # Parse
        parsed = collector.parse_line(line)
        assert parsed is not None
        
        # Normalize
        normalized = collector.normalize_sample(parsed)
        
        # Verify
        assert normalized["metric"] == "luminosidad"
        assert normalized["value"] == 5.00
        assert normalized["unit"] == "lux"
        assert normalized["quality"] == "ok"

    def test_multiple_samples_sequence(self):
        """Tests secuencia de múltiples muestras."""
        collector = SerialCollector()
        
        lines = [
            "moisture 800",
            "light 5.00",
            "temperature 18.96",
        ]
        
        samples = []
        for line in lines:
            parsed = collector.parse_line(line)
            if parsed:
                normalized = collector.normalize_sample(parsed)
                samples.append(normalized)
        
        assert len(samples) == 3
        assert samples[0]["metric"] == "humedad_suelo"
        assert samples[1]["metric"] == "luminosidad"
        assert samples[2]["metric"] == "temp_aire"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
