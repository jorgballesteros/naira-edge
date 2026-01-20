#!/bin/bash
# Test runner para suite de tests del módulo acquisition
# Ubicación: src/acquisition/run_tests.sh
# Uso: bash src/acquisition/run_tests.sh [opción]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

cd "$PROJECT_ROOT"

# Detectar si estamos en un venv
if [ -f venv/bin/python ]; then
    PYTHON="venv/bin/python"
    PIP="venv/bin/pip"
else
    PYTHON="python3"
    PIP="pip3"
fi

# Función para mostrar ayuda
show_help() {
    echo "🧪 Test Runner - Acquisition Module"
    echo ""
    echo "Uso: bash src/acquisition/run_tests.sh [opción]"
    echo ""
    echo "Opciones:"
    echo "  all        - Ejecutar todos los tests (output quiet)"
    echo "  verbose    - Ejecutar todos los tests (verbose)"
    echo "  coverage   - Tests + reporte de cobertura (terminal)"
    echo "  html       - Tests + reporte HTML (htmlcov/index.html)"
    echo "  fast       - Tests rápidos (sin cobertura)"
    echo "  temperature - Solo tests de temperatura"
    echo "  moisture   - Solo tests de humedad"
    echo "  light      - Solo tests de luz"
    echo "  quality    - Solo tests de quality assessment"
    echo "  integration - Solo tests de integración"
    echo "  debug      - Con stack traces largos"
    echo "  help       - Mostrar esta ayuda"
    echo ""
}

# Procesar argumento
case "${1:-all}" in
    all)
        echo "✅ Running all tests..."
        $PYTHON -m pytest src/acquisition/test_serial_reader.py -q
        ;;
    verbose)
        echo "✅ Running all tests (verbose)..."
        $PYTHON -m pytest src/acquisition/test_serial_reader.py -v
        ;;
    coverage)
        echo "✅ Running tests with coverage (terminal)..."
        $PYTHON -m pytest src/acquisition/test_serial_reader.py \
            --cov=src.acquisition \
            --cov-report=term-missing \
            -v
        ;;
    html)
        echo "✅ Running tests with coverage (HTML)..."
        $PYTHON -m pytest src/acquisition/test_serial_reader.py \
            --cov=src.acquisition \
            --cov-report=html \
            -q
        echo "📊 Report saved to: htmlcov/index.html"
        ;;
    fast)
        echo "✅ Running tests (fast)..."
        $PYTHON -m pytest src/acquisition/test_serial_reader.py -q --tb=no
        ;;
    temperature)
        echo "✅ Running temperature tests..."
        $PYTHON -m pytest src/acquisition/test_serial_reader.py -v -k "temperature"
        ;;
    moisture)
        echo "✅ Running moisture tests..."
        $PYTHON -m pytest src/acquisition/test_serial_reader.py -v -k "moisture"
        ;;
    light)
        echo "✅ Running light tests..."
        $PYTHON -m pytest src/acquisition/test_serial_reader.py -v -k "light"
        ;;
    quality)
        echo "✅ Running quality assessment tests..."
        $PYTHON -m pytest src/acquisition/test_serial_reader.py -v -k "quality"
        ;;
    integration)
        echo "✅ Running integration tests..."
        $PYTHON -m pytest src/acquisition/test_serial_reader.py -v -k "integration"
        ;;
    debug)
        echo "✅ Running tests with full debug info..."
        $PYTHON -m pytest src/acquisition/test_serial_reader.py -vv --tb=long
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown option: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
