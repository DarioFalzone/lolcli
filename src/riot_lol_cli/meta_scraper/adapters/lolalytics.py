"""
Adaptador para LoLalytics.

Estrategia: Playwright (Capa 3) — LoLalytics carga todo vía JS, no hay
endpoints JSON internos accesibles con httpx. Se usa un browser headless
para renderizar la página y extraer los datos del DOM.

Datos extraídos de: https://lolalytics.com/lol/tierlist/?lane=support
DOM pattern: cada fila es un div.flex con 15 hijos:
[0]=rank [1]=img/title [2]=name [3]=tier [4]=score [5]=WR+delta [6]=PR [7]=BR ...
Links de campeon: /lol/{name}/build/
"""

import logging
import re
from datetime import datetime, timezone

from .base import BaseAdapter

logger = logging.getLogger(__name__)

# URL base para tier list por lane en LoLalytics
_TIERLIST_URL_TEMPLATE = "https://lolalytics.com/lol/tierlist/?lane={lane}"
_CHAMPION_URL_TEMPLATE = "https://lolalytics.com/lol/{champion_id}/build/"

# LoLalytics → nuestro ID canónico (casos especiales)
_LOLALYTICS_NAME_MAP = {
    "aurelionsol": "AurelionSol",
    "belveth": "Belveth",
    "drmundo": "DrMundo",
    "jarvaniv": "JarvanIV",
    "kogmaw": "KogMaw",
    "leesin": "LeeSin",
    "masteryi": "MasterYi",
    "missfortune": "MissFortune",
    "monkeyking": "MonkeyKing",
    "reksai": "RekSai",
    "tahmkench": "TahmKench",
    "twistedfate": "TwistedFate",
    "xinzhao": "XinZhao",
    "kaisa": "Kaisa",
    "khazix": "Khazix",
    "chogath": "Chogath",
    "velkoz": "Velkoz",
    "renata": "Renata",
    "ksante": "KSante",
    "nunu": "Nunu",
}

_JS_EXTRACT = """() => {
    const results = [];
    const seen = new Set();

    // LoLalytics: cada fila es un div.flex con 15 hijos fijos.
    // El link al campeon esta en children[1] (o un hijo de el).
    // Layout de celdas:
    //   [0]=rank [1]=img+link [2]=name [3]=tier [4]=score
    //   [5]=WR(+delta) [6]=PR [7]=BR ...

    // Buscar todos los links de campeon
    const links = document.querySelectorAll('a[href*="/lol/"][href*="/build/"]');

    for (const link of links) {
        const href = link.getAttribute('href') || '';
        const match = href.match(/\\/lol\\/([a-z0-9'-]+)\\/build/i);
        if (!match) continue;

        const champId = match[1].toLowerCase();
        if (seen.has(champId)) continue;
        seen.add(champId);

        // La fila es el abuelo del link (link → div.my-auto → div.flex)
        const row = link.parentElement?.parentElement;
        if (!row || row.children.length < 8) continue;

        const cells = Array.from(row.children);

        const tier = (cells[3]?.textContent.trim() || 'B');

        // WR puede venir como "52.23+0.57" — tomar el primer numero
        const wrText = cells[5]?.textContent.trim() || '0';
        const wrMatch = wrText.match(/(\\d+\\.?\\d*)/);
        const winRate = wrMatch ? parseFloat(wrMatch[1]) : 0;

        const pickRate = parseFloat(cells[6]?.textContent.trim() || '0') || 0;
        const banRate = parseFloat(cells[7]?.textContent.trim() || '0') || 0;

        // Games: buscar el primer numero grande en el texto completo de la fila
        let games = 0;
        const fullText = row.textContent || '';
        const gameMatches = fullText.match(/(\\d[\\d,]{4,})/g);
        if (gameMatches) {
            for (const gm of gameMatches) {
                const val = parseInt(gm.replace(/,/g, ''));
                if (val > 10000) { games = val; break; }
            }
        }

        if (winRate > 0 && pickRate > 0) {
            results.push({
                id: champId,
                tier: tier,
                win_rate: winRate,
                pick_rate: pickRate,
                ban_rate: banRate,
                games_analyzed: games
            });
        }
    }
    return results;
}"""


class LolalyticsAdapter(BaseAdapter):
    """Adaptador para extraer datos de LoLalytics."""

    platform_name = "lolalytics"
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
        logger.info("[lolalytics] Browser Playwright iniciado")

    def fetch_support_tier_list(self, patch: str = "latest", elo: str = "emerald_plus") -> dict:
        """Extrae la tier list completa de soportes desde LoLalytics."""
        return self._fetch_tier_list(role="support", lane="support", patch=patch, elo=elo)

    def fetch_adc_tier_list(self, patch: str = "latest", elo: str = "emerald_plus") -> dict:
        """Extrae la tier list completa de ADC/bot lane desde LoLalytics."""
        return self._fetch_tier_list(role="adc", lane="bottom", patch=patch, elo=elo)

    def _fetch_tier_list(self, role: str, lane: str, patch: str, elo: str) -> dict:
        """
        Extrae una tier list por rol desde LoLalytics.

        Abre la página con Playwright, espera a que los datos carguen,
        y parsea el DOM para extraer stats por campeón.
        """
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
            logger.info("[lolalytics] Navegando a tier list de %s...", role)
            page.goto(_TIERLIST_URL_TEMPLATE.format(lane=lane), wait_until="domcontentloaded", timeout=60000)
            # Esperar a que los links de campeones aparezcan (JS rendering)
            page.wait_for_selector('a[href*="/build/"]', timeout=30000)
            # Dar tiempo extra al JS para renderizar todas las stats
            page.wait_for_timeout(5000)

            # Extraer el patch desde la página
            detected_patch = patch
            try:
                patch_text = page.text_content("h2, [class*='patch']") or ""
                patch_match = re.search(r"(\d+\.\d+)", patch_text)
                if patch_match:
                    detected_patch = patch_match.group(1)
            except Exception:
                pass

            champions_data = page.evaluate(_JS_EXTRACT)

            # Normalizar IDs
            normalized_champions = []
            seen = set()
            for champ in champions_data:
                raw_id = champ["id"].lower().replace("'", "").replace("-", "").replace(" ", "")
                canonical = _LOLALYTICS_NAME_MAP.get(raw_id) or _LOLALYTICS_NAME_MAP.get(
                    champ["id"].lower(), champ["id"].capitalize()
                )
                if canonical in seen:
                    continue
                seen.add(canonical)
                normalized_champions.append(
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
                "[lolalytics] Extraídos %d campeones (patch %s)",
                len(normalized_champions),
                detected_patch,
            )

            return {
                "platform": self.platform_name,
                "patch": detected_patch,
                "elo": elo,
                "role": role,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "champions": normalized_champions,
            }

        except Exception as e:
            logger.error("[lolalytics] Error durante scraping: %s", e, exc_info=True)
            raise

        finally:
            context.close()

    def fetch_champion_detail(self, champion_id: str) -> dict:
        """
        Extrae builds, runas y matchups de un soporte individual.

        (Implementación futura — por ahora devuelve placeholder)
        """
        logger.info(
            "[lolalytics] Detalle de %s — pendiente de implementación",
            champion_id,
        )
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
        logger.info("[lolalytics] Browser cerrado")
