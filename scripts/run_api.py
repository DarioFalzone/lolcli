#!/usr/bin/env python
"""
Wrapper para ejecutar el API correctamente
"""
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Ahora importar y levantar Uvicorn
import uvicorn
from riot_lol_cli.api_server import app

if __name__ == "__main__":
    print("🚀 Levantando API en http://localhost:8000")
    print("📚 Documentación en http://localhost:8000/docs")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )
