"""
Orquestador de scraping multi-plataforma.

Coordina la ejecución de los adaptadores, gestiona rate-limiting global,
guarda datos raw por plataforma y dispara la normalización.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .adapters.base import BaseAdapter
from .normalizer import merge_platform_data, save_normalized, save_raw

logger = logging.getLogger(__name__)

_BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
_DATA_DIR = _BASE_DIR / "data" / "meta_scraper"
_MANIFEST_PATH = _DATA_DIR / "manifest.json"


class ScrapingOrchestrator:
    """
    Orquesta el scraping secuencial de múltiples plataformas.

    Ejecuta cada adapter, guarda raw, mergea datos y actualiza el manifest.
    """

    def __init__(self, adapters: list[BaseAdapter] | None = None) -> None:
        self.adapters: list[BaseAdapter] = adapters or []
        self._is_running = False

    def register_adapter(self, adapter: BaseAdapter) -> None:
        """Registra un nuevo adapter."""
        self.adapters.append(adapter)
        logger.info("Adapter registrado: %s", adapter.platform_name)

    @property
    def is_running(self) -> bool:
        """True si hay un scraping en curso."""
        return self._is_running

    def run_full_scrape(
        self,
        patch: str = "latest",
        elo: str = "emerald_plus",
        role: str = "support",
    ) -> dict:
        """
        Ejecuta un scraping completo de todas las plataformas registradas.

        Returns:
            El dataset normalizado y mergeado.
        """
        if self._is_running:
            raise RuntimeError("Ya hay un scraping en curso.")
        role = role.strip().lower()
        if role in {"bottom", "bot", "marksman"}:
            role = "adc"
        if role not in {"support", "adc"}:
            raise ValueError(f"Rol no soportado para scraping: {role}")

        self._is_running = True
        platform_datasets: dict[str, dict] = {}
        errors: list[dict] = []

        logger.info(
            "=== Iniciando scraping completo: %d plataformas ===",
            len(self.adapters),
        )

        try:
            for adapter in self.adapters:
                platform = adapter.platform_name
                logger.info("[%s] Iniciando scraping...", platform)

                try:
                    # Extraer tier list del rol solicitado.
                    if role == "adc":
                        tier_data = adapter.fetch_adc_tier_list(patch=patch, elo=elo)
                    else:
                        tier_data = adapter.fetch_support_tier_list(patch=patch, elo=elo)

                    if tier_data and tier_data.get("champions"):
                        # Guardar raw
                        save_raw(tier_data, platform, f"{role}_tier")
                        platform_datasets[platform] = tier_data
                        logger.info(
                            "[%s] ✓ %d campeones extraídos",
                            platform,
                            len(tier_data["champions"]),
                        )
                    else:
                        logger.warning("[%s] Sin datos de campeones.", platform)
                        errors.append(
                            {
                                "platform": platform,
                                "error": "Sin datos de campeones en la respuesta",
                            }
                        )

                except PermissionError as e:
                    logger.error("[%s] ✗ Bloqueado: %s", platform, e)
                    errors.append({"platform": platform, "error": str(e)})

                except Exception as e:
                    logger.error("[%s] ✗ Error: %s", platform, e, exc_info=True)
                    errors.append({"platform": platform, "error": str(e)})

                finally:
                    adapter.close()

            # Normalizar y mergear
            if platform_datasets:
                normalized = merge_platform_data(platform_datasets, role=role, elo_filter=elo)
                snapshot_path = save_normalized(normalized, role=role)
                self._update_manifest(normalized, snapshot_path)
                logger.info(
                    "=== Scraping completo: %d plataformas OK, %d errores ===",
                    len(platform_datasets),
                    len(errors),
                )

                # Añadir metadata de scraping al resultado
                normalized["_scrape_meta"] = {
                    "platforms_ok": list(platform_datasets.keys()),
                    "platforms_error": errors,
                    "duration_info": "completado",
                }
                return normalized
            else:
                logger.error("=== Scraping fallido: 0 plataformas OK ===")
                return {
                    "schema_version": "1.0",
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "error": "Ninguna plataforma respondió correctamente.",
                    "details": errors,
                    "champions": [],
                    "role": role,
                }

        finally:
            self._is_running = False

    def _update_manifest(self, data: dict, snapshot_path: Path) -> None:
        """Actualiza el manifest.json con el nuevo snapshot."""
        _DATA_DIR.mkdir(parents=True, exist_ok=True)

        manifest = {"last_scrape": None, "patch": None, "snapshots": []}
        if _MANIFEST_PATH.exists():
            try:
                with open(_MANIFEST_PATH, encoding="utf-8") as f:
                    manifest = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

        now = datetime.now(timezone.utc).isoformat()
        manifest["last_scrape"] = now
        manifest["patch"] = data.get("patch", "unknown")
        manifest.setdefault("latest_by_role", {})
        manifest["latest_by_role"][data.get("role", "support")] = {
            "timestamp": now,
            "patch": data.get("patch", "unknown"),
            "champion_count": data.get("champion_count", 0),
            "file": str(snapshot_path.relative_to(_DATA_DIR)),
        }
        manifest["snapshots"].append(
            {
                "timestamp": now,
                "role": data.get("role", "support"),
                "sources": data.get("sources", []),
                "champion_count": data.get("champion_count", 0),
                "file": str(snapshot_path.relative_to(_DATA_DIR)),
            }
        )

        # Mantener solo los últimos 50 snapshots en el manifest
        if len(manifest["snapshots"]) > 50:
            manifest["snapshots"] = manifest["snapshots"][-50:]

        with open(_MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        logger.info("Manifest actualizado: %s", _MANIFEST_PATH)
