"""Punto de entrada del nodo edge NAIRA.

Ejecuta una orquestación mínima que inicializa módulos de adquisición,
procesamiento, comunicaciones y control en modo de ejemplo/simulado.
"""

from __future__ import annotations

import argparse
import logging
import sys

from . import __version__

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="naira-edge-node")
    parser.add_argument("--sim", action="store_true", help="Modo simulación (no hardware)")
    parser.add_argument("--log", default="INFO", help="Nivel de logging (DEBUG, INFO, WARNING)")
    return parser.parse_args(argv)


def setup_logging(level: str) -> None:
    numeric = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(level=numeric, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    setup_logging(args.log)

    logging.getLogger(__name__).info("NAIRA Edge node starting (version=%s), sim=%s", __version__, args.sim)

    # Import modules lazily so the package can be imported without hardware.
    try:
        from .acquisition import stub as acquisition_stub
        from .processing import stub as processing_stub
        from .comms import stub as comms_stub
        from .control import stub as control_stub
        from .diagnostics import stub as diag_stub

        # Run a minimal orchestrated cycle
        data = acquisition_stub.read_sensor(sim=args.sim)
        processed = processing_stub.process_sample(data)
        comms_stub.publish_sample(processed)
        control_stub.apply_rules(processed)
        diag = diag_stub.health_check()

        logging.getLogger(__name__).info("Cycle finished — health=%s", diag)
    except Exception:
        logging.getLogger(__name__).exception("Error durante ejecución del nodo")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
