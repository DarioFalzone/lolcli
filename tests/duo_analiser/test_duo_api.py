from __future__ import annotations

import codecs
import json

from fastapi.testclient import TestClient

from riot_lol_cli.duo_analiser.api import _SYNERGIES_FILE, load_champions_list
from riot_lol_cli.duo_analiser.server import create_app

app = create_app()
client = TestClient(app)


def test_synergies_json_encoding_and_no_bom():
    """Verifica que data/duo_analiser/synergies.json exista, sea UTF-8 válido y no tenga BOM."""
    assert _SYNERGIES_FILE.exists(), f"Falta el archivo: {_SYNERGIES_FILE}"
    
    # Comprobar marca de orden de bytes (BOM)
    with open(_SYNERGIES_FILE, "rb") as f:
        raw = f.read(4)
        assert raw[:3] != codecs.BOM_UTF8, "El archivo synergies.json tiene BOM de UTF-8 indeseado."
    
    # Comprobar validez de decodificación JSON en UTF-8 puro
    with open(_SYNERGIES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data.get("schema_version") == "1.0"
        assert "Lux" in data.get("synergies", {})


def test_load_champions_list():
    """Valida la lectura y ordenado de la base de campeones general."""
    champs = load_champions_list()
    assert len(champs) > 0
    # Validar campos requeridos
    first = champs[0]
    assert "id" in first
    assert "display_name" in first
    assert "primary_role" in first
    assert "class" in first


def test_api_health_endpoint():
    """Verifica el health-check del servicio."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "duo_analiser"
    assert "champions_in_roster" in data


def test_api_get_champions_endpoint():
    """Valida la lista completa de campeones para el selector."""
    resp = client.get("/api/v1/duo/champions")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Lux debe estar en el catálogo
    lux_match = next((c for c in data if c["id"] == "Lux"), None)
    assert lux_match is not None
    assert lux_match["display_name"] == "Lux"


def test_api_get_synergies_curated_lux():
    """Valida las sinergias curadas estáticamente para Lux."""
    resp = client.get("/api/v1/duo/synergies/Lux")
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["champion_id"] == "Lux"
    assert data["display_name"] == "Lux"
    assert len(data["synergies"]) > 0
    
    # Nocturne debe ser una recomendación
    noc = next((s for s in data["synergies"] if s["jungler_id"] == "Nocturne"), None)
    assert noc is not None
    assert noc["jungler_name"] == "Nocturne"
    assert len(noc["advantages"]) == 3
    # Ventaja en español rioplatense
    assert "combo" in noc["advantages"][0] or "definitiva" in noc["advantages"][0] or "Lux" in noc["advantages"][0]


def test_api_get_synergies_fallback_dynamic():
    """Valida la generación fallback determinista para campeones no curados."""
    # Aatrox no está en la base curada estática
    resp = client.get("/api/v1/duo/synergies/Aatrox")
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["champion_id"] == "Aatrox"
    assert len(data["synergies"]) == 5  # Debe tener 5 junglers fallback
    
    # Comprobar determinismo: consultar de nuevo y verificar igualdad estadística
    resp2 = client.get("/api/v1/duo/synergies/Aatrox")
    data2 = resp2.json()
    assert data == data2


def test_api_get_synergies_invalid_champion():
    """Verifica que se devuelva 404 al consultar un campeón inexistente en el roster."""
    resp = client.get("/api/v1/duo/synergies/InvalidoChamp")
    assert resp.status_code == 404
    assert "no encontrado" in resp.json()["detail"].lower()
