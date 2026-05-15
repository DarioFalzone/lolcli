"""Smoke tests para los 7 adapters V2 — verifica que se instancian y exponen la interfaz."""

from __future__ import annotations

import pytest

from riot_lol_cli.patch_notes.adapters.base import PatchNotesAdapterBase


def _import_adapter(module: str, cls: str):
    """Importa un adapter y lo devuelve. None si Playwright no está disponible."""
    try:
        mod = __import__(f"riot_lol_cli.patch_notes.adapters.{module}", fromlist=[cls])
        return getattr(mod, cls)
    except ImportError:
        return None


ADAPTER_REGISTRY = [
    ("ddragon", "DDragonAdapter", "ddragon", False),  # no requiere playwright
    ("riot_calendar", "RiotCalendarAdapter", "riot_calendar", False),  # bs4
    ("lol_official", "LolOfficialAdapter", "lol_official", True),
    ("lol_dev", "LolDevAdapter", "lol_dev", True),
    ("lolalytics_patch", "LolalyticsPatchAdapter", "lolalytics_patch", True),
    ("ugg_patch", "UggPatchAdapter", "ugg_patch", True),
    ("opgg_patch", "OpggPatchAdapter", "opgg_patch", True),
    ("mobalytics_patch", "MobalyticsPatchAdapter", "mobalytics_patch", True),
]


@pytest.mark.parametrize("module,cls,platform,requires_playwright", ADAPTER_REGISTRY)
def test_adapter_class_imports(module: str, cls: str, platform: str, requires_playwright: bool) -> None:
    AdapterCls = _import_adapter(module, cls)
    assert AdapterCls is not None, f"{cls} debe poder importarse"
    assert issubclass(AdapterCls, PatchNotesAdapterBase), f"{cls} debe heredar PatchNotesAdapterBase"
    assert AdapterCls.platform_name == platform, f"platform_name esperado: {platform}"


@pytest.mark.parametrize("module,cls,platform,requires_playwright", ADAPTER_REGISTRY)
def test_adapter_instantiable(module: str, cls: str, platform: str, requires_playwright: bool) -> None:
    """Instanciar no debe fallar (Playwright se carga lazy en _ensure_playwright)."""
    AdapterCls = _import_adapter(module, cls)
    adapter = AdapterCls()
    assert adapter.platform_name == platform
    assert hasattr(adapter, "discover")
    assert hasattr(adapter, "extract")
    assert hasattr(adapter, "close")
    # close debe ser idempotente
    adapter.close()
    adapter.close()


def test_orchestrator_factory_registers_all_available() -> None:
    """create_default_orchestrator debe registrar todos los adapters importables."""
    from riot_lol_cli.patch_notes.orchestrator import create_default_orchestrator

    orchestrator = create_default_orchestrator()
    assert orchestrator is not None
    assert orchestrator.adapter is not None
    assert orchestrator.adapter.platform_name == "lol_official"
    # Al menos ddragon y riot_calendar (sin Playwright) tienen que estar
    assert "ddragon" in orchestrator.enrichment_adapters
    assert "riot_calendar" in orchestrator.enrichment_adapters
