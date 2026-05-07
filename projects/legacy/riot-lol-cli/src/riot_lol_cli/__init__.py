import os
import json
from pathlib import Path

# Ruta al archivo de versión
VERSION_FILE = Path(__file__).parent.parent.parent / 'config' / 'version.json'

def get_version():
    """Obtiene la versión actual desde el archivo o usa la predeterminada."""
    if VERSION_FILE.exists():
        try:
            with open(VERSION_FILE, 'r') as f:
                data = json.load(f)
                return data.get('version', '1.0.0')
        except (json.JSONDecodeError, KeyError):
            pass
    return '1.0.0'

def increment_version():
    """Incrementa la versión y la guarda en el archivo."""
    current = get_version()
    try:
        # Incrementar el último número de versión (v1.0.X)
        parts = current.split('.')
        if len(parts) == 3:
            parts[2] = str(int(parts[2]) + 1)
            new_version = '.'.join(parts)
        else:
            new_version = current + '.1'
    except (ValueError, IndexError):
        new_version = current
    
    # Guardar la nueva versión
    with open(VERSION_FILE, 'w') as f:
        json.dump({'version': new_version}, f, indent=2)
    
    return new_version

# Versión actual
__version__ = get_version()

__all__ = [
    "regions",
    "api",
    "increment_version"
]
