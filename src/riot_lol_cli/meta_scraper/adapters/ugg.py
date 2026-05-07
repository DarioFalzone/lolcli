"""
Adaptador para U.GG.

Estrategia: Playwright — U.GG usa React y carga datos via JS.
URL: https://u.gg/lol/tier-list?role={role}

DOM pattern: tabla React (.rt-tr) con celdas .rt-td indexadas:
[0]=rank [1]=img [2]=name [3]=tier [4]=WR% [5]=PR% [6]=BR% [7]=link [8]=games
Links de campeon: /lol/champions/{slug}/build/{role}
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

from .base import BaseAdapter

logger = logging.getLogger(__name__)

_TIERLIST_URL_TEMPLATE = "https://u.gg/lol/tier-list?role={role}"

# U.GG usa slugs con guiones → ID canónico
_UGG_NAME_MAP = {
    "aurelion-sol": "AurelionSol",
    "bel-veth": "Belveth",
    "dr-mundo": "DrMundo",
    "jarvan-iv": "JarvanIV",
    "k-sante": "KSante",
    "kai-sa": "Kaisa",
    "kha-zix": "Khazix",
    "kog-maw": "KogMaw",
    "lee-sin": "LeeSin",
    "master-yi": "MasterYi",
    "miss-fortune": "MissFortune",
    "rek-sai": "RekSai",
    "renata-glasc": "Renata",
    "tahm-kench": "TahmKench",
    "twisted-fate": "TwistedFate",
    "vel-koz": "Velkoz",
    "wukong": "MonkeyKing",
    "xin-zhao": "XinZhao",
    "cho-gath": "Chogath",
    "nunu-willump": "Nunu",
    "nunu": "Nunu",
}

_JS_EXTRACT = """() => {
    const results = [];
    const seen = new Set();

    // U.GG: tabla React con filas .rt-tr
    // Celdas: [0]=rank [1]=img [2]=name [3]=tier [4]=WR% [5]=PR% [6]=BR% [7]=link [8]=games
    const rows = document.querySelectorAll('.rt-tr');

    for (const row of rows) {
        const link = row.querySelector('a[href*="/lol/champions/"][href*="/build/"]');
        if (!link) continue;

        const href = link.getAttribute('href') || '';
        const match = href.match(/\\/lol\\/champions\\/([a-z0-9-]+)\\/build/i);
        if (!match) continue;

        const slug = match[1].toLowerCase();
        if (seen.has(slug)) continue;
        seen.add(slug);

        const cells = Array.from(row.querySelectorAll('.rt-td'));
        if (cells.length < 7) continue;

        const tier = (cells[3]?.textContent.trim() || 'B').replace(/\\s+/g, '');
        const winRate = parseFloat((cells[4]?.textContent.trim() || '0').replace('%', '')) || 0;
        const pickRate = parseFloat((cells[5]?.textContent.trim() || '0').replace('%', '')) || 0;
        const banRate = parseFloat((cells[6]?.textContent.trim() || '0').replace('%', '')) || 0;

        let games = 0;
        if (cells.length > 8) {
            games = parseInt((cells[8]?.textContent.trim() || '0').replace(/,/g, '')) || 0;
        }

        if (winRate > 0) {
            results.push({
                id: slug,
                tier: tier || 'B',
                win_rate: winRate,
                pick_rate: pickRate,
                ban_rate: banRate,
                games_analyzed: games
            });
        }
    }
    return results;
}"""


def _slug_to_id(slug: str) -> str:
    """Convierte slug U.GG a ID canónico: 'miss-fortune' → 'MissFortune'."""
    if slug in _UGG_NAME_MAP:
        return _UGG_NAME_MAP[slug]
    return "".join(part.capitalize() for part in slug.split("-"))


class UggAdapter(BaseAdapter):
    """Adaptador para extraer datos de U.GG."""

    platform_name = "ugg"
    min_delay = 4.0
    max_delay = 8.0

    def __init__(self) -> None:
        super().__init__()
        self._browser = None
        self._playwright = None

    def _ensure_playwright(self):
        """Inicializa Playwright si no está activo."""
        if self._browser is not None:
            return

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as e:
            raise ImportError(
                "Playwright no está instalado. Ejecutá:\n  pip install playwright\n  playwright install chromium"
            ) from e

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        logger.info("[ugg] Browser Playwright iniciado")

    def fetch_support_tier_list(self, patch: str = "latest", elo: str = "emerald_plus") -> dict:
        """Extrae la tier list de soportes desde U.GG."""
        return self._fetch_tier_list(role="support", patch=patch, elo=elo)

    def fetch_adc_tier_list(self, patch: str = "latest", elo: str = "emerald_plus") -> dict:
        """Extrae la tier list de ADC desde U.GG."""
        return self._fetch_tier_list(role="adc", patch=patch, elo=elo)

    def _fetch_tier_list(self, role: str, patch: str, elo: str) -> dict:
        self._ensure_playwright()
        context = self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        try:
            url = _TIERLIST_URL_TEMPLATE.format(role=role)
            logger.info("[ugg] Navegando a tier list de %s: %s", role, url)
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Esperar a que los links de campeones estén en el DOM
            page.wait_for_selector('a[href*="/lol/champions/"][href*="/build/"]', timeout=30000)
            # Dar tiempo extra al React para renderizar stats
            page.wait_for_timeout(5000)

            # Detectar patch desde texto de la página
            detected_patch = patch
            try:
                page_text = page.text_content("body") or ""
                patch_match = re.search(r"Patch\s+(\d+\.\d+)", page_text, re.IGNORECASE)
                if patch_match:
                    detected_patch = patch_match.group(1)
            except Exception:
                pass

            champions_data = page.evaluate(_JS_EXTRACT)

            normalized = []
            seen_ids: set[str] = set()
            for champ in champions_data:
                canonical = _slug_to_id(champ["id"])
                if canonical in seen_ids:
                    continue
                seen_ids.add(canonical)
                normalized.append(
                    {
                        "id": canonical,
                        "display_name": canonical,
                        "win_rate": champ.get("win_rate", 0),
                        "pick_rate": champ.get("pick_rate", 0),
                        "ban_rate": champ.get("ban_rate", 0),
                        "games_analyzed": champ.get("games_analyzed", 0),
                        "tier_raw": champ.get("tier", "B"),
                    }
                )

            logger.info(
                "[ugg] Extraídos %d campeones (rol=%s, patch=%s)",
                len(normalized),
                role,
                detected_patch,
            )

            return {
                "platform": self.platform_name,
                "patch": detected_patch,
                "elo": elo,
                "role": role,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "champions": normalized,
            }

        except Exception as e:
            logger.error("[ugg] Error durante scraping: %s", e, exc_info=True)
            raise

        finally:
            context.close()

    def fetch_champion_detail(self, champion_id: str) -> dict:
        """Detalle de campeón — pendiente de implementación."""
        logger.info("[ugg] Detalle de %s — pendiente de implementación", champion_id)
        return {
            "champion_id": champion_id,
            "platform": self.platform_name,
            "builds": {},
            "runes": {},
            "matchups": {},
            "synergies": {},
        }

    def close(self) -> None:
        """Cierra el browser de Playwright."""
        super().close()
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        logger.info("[ugg] Browser cerrado")
