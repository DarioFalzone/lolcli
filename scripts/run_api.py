#!/usr/bin/env python
"""Wrapper para ejecutar el Meta Analyzer API desde el paquete instalado."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from riot_lol_cli.api_server import run

if __name__ == "__main__":
    run()
