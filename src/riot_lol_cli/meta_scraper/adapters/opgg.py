"""
Adaptador para OP.GG.

Estrategia: Playwright (Capa 3) — OP.GG retorna 403 a requests HTTP
directos y usa rendering server-side con protección anti-bot.
Se usa un browser headless con stealth para extraer datos de la tabla HTML.

Datos extraídos de: https://www.op.gg/champions?position=support
DOM pattern: tabla con filas que contienen avatar, nombre, tier, WR, PR, BR.
"""

import logging
import re
from datetime import datetime, timezone

from riot_lol_cli.meta_scraper.messages import PLAYWRIGHT_UNAVAILABLE_MESSAGE

from .base import BaseAdapter

logger = logging.getLogger(__name__)

_TIERLIST_URL_TEMPLATE = "https://www.op.gg/champions?position={position}"

# OP.GG → ID canónico (casos especiales)
_OPGG_NAME_MAP = {
    "aurelion sol": "AurelionSol",
    "bel'veth": "Belveth",
    "dr. mundo": "DrMundo",
    "jarvan iv": "JarvanIV",
    "k'sante": "KSante",
    "kai'sa": "Kaisa",
    "kha'zix": "Khazix",
    "kog'maw": "KogMaw",
    "lee sin": "LeeSin",
    "master yi": "MasterYi",
    "miss fortune": "MissFortune",
    "rek'sai": "RekSai",
    "renata glasc": "Renata",
    "tahm kench": "TahmKench",
    "twisted fate": "TwistedFate",
    "vel'koz": "Velkoz",
    "wukong": "MonkeyKing",
    "xin zhao": "XinZhao",
    "cho'gath": "Chogath",
    "nunu & willump": "Nunu",
}


class OpggAdapter(BaseAdapter):
    """Adaptador para extraer datos de OP.GG."""

    platform_name = "opgg"
    min_delay = 5.0
    max_delay = 10.0

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
            raise ImportError(PLAYWRIGHT_UNAVAILABLE_MESSAGE) from e

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        logger.info("[opgg] Browser Playwright iniciado")

    def fetch_support_tier_list(self, patch: str = "latest", elo: str = "emerald_plus") -> dict:
        """Extrae la tier list de soportes desde OP.GG."""
        return self._fetch_tier_list(role="support", position="support", patch=patch, elo=elo)

    def fetch_adc_tier_list(self, patch: str = "latest", elo: str = "emerald_plus") -> dict:
        """Extrae la tier list de ADC/bot lane desde OP.GG."""
        return self._fetch_tier_list(role="adc", position="adc", patch=patch, elo=elo)

    def fetch_jungle_tier_list(self, patch: str = "latest", elo: str = "emerald_plus") -> dict:
        """Extrae la tier list de jungla desde OP.GG."""
        return self._fetch_tier_list(role="jungle", position="jungle", patch=patch, elo=elo)

    def _fetch_tier_list(self, role: str, position: str, patch: str, elo: str) -> dict:
        """
        Extrae una tier list por rol desde OP.GG.

        Abre la página con Playwright, espera la tabla de campeones,
        y parsea las filas para extraer stats.
        """
        self._ensure_playwright()
        context = self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            locale="en-US",
        )
        page = context.new_page()

        try:
            logger.info("[opgg] Navegando a tier list de %s...", role)
            page.goto(_TIERLIST_URL_TEMPLATE.format(position=position), wait_until="domcontentloaded", timeout=60000)

            # Esperar a que la tabla de campeones cargue
            page.wait_for_selector("table tbody tr", timeout=30000)
            # Dar tiempo extra para que carguen las stats
            page.wait_for_timeout(3000)

            # Extraer datos de la tabla via JS
            champions_data = page.evaluate("""() => {
                const results = [];
                const rows = document.querySelectorAll('table tbody tr');

                for (const row of rows) {
                    const cells = row.querySelectorAll('td');
                    if (cells.length < 4) continue;

                    // Nombre del campeón — buscar en links o texto
                    const nameLink = row.querySelector('a[href*="/champions/"]');
                    let name = '';
                    if (nameLink) {
                        // Extraer de href: /champions/thresh/...
                        const href = nameLink.getAttribute('href') || '';
                        const match = href.match(/\\/champions\\/([^/]+)/);
                        if (match) {
                            name = match[1];
                        } else {
                            name = nameLink.textContent.trim();
                        }
                    } else {
                        // Fallback: buscar texto en la fila
                        const textEls = row.querySelectorAll('strong, span, div');
                        for (const el of textEls) {
                            const t = el.textContent.trim();
                            if (t.length > 2 && t.length < 30 && !t.includes('%')) {
                                name = t;
                                break;
                            }
                        }
                    }

                    if (!name) continue;

                    // Extraer porcentajes del texto de las celdas
                    const fullText = row.textContent || '';
                    const percents = [];
                    const percentMatches = fullText.match(/(\\d+\\.\\d+)%/g) || [];
                    for (const m of percentMatches) {
                        percents.push(parseFloat(m));
                    }

                    // Extraer tier (badge con "Tier 1", "1", "S", etc.)
                    const tierEl = row.querySelector('[class*="tier"], [class*="Tier"]');
                    let tier = 'B';
                    if (tierEl) {
                        const tierText = tierEl.textContent.trim();
                        if (tierText.includes('1') || tierText.includes('S')) tier = 'S';
                        else if (tierText.includes('2') || tierText.includes('A')) tier = 'A';
                        else if (tierText.includes('3') || tierText.includes('B')) tier = 'B';
                        else if (tierText.includes('4') || tierText.includes('C')) tier = 'C';
                        else if (tierText.includes('5') || tierText.includes('D')) tier = 'C';
                    }

                    results.push({
                        name: name,
                        tier: tier,
                        win_rate: percents[0] || 0,
                        pick_rate: percents[1] || 0,
                        ban_rate: percents.length > 2 ? percents[2] : 0,
                    });
                }
                return results;
            }""")

            # Detectar patch
            detected_patch = patch
            try:
                page_text = page.text_content("body") or ""
                patch_match = re.search(r"Patch\s+(\d+\.\d+)", page_text, re.IGNORECASE)
                if patch_match:
                    detected_patch = patch_match.group(1)
            except Exception:
                pass

            # Normalizar nombres
            normalized_champions = []
            seen = set()
            for champ in champions_data:
                raw_name = champ["name"].strip().lower()
                canonical = _OPGG_NAME_MAP.get(
                    raw_name, champ["name"].strip().title().replace(" ", "").replace("'", "")
                )
                if canonical in seen:
                    continue
                seen.add(canonical)
                normalized_champions.append(
                    {
                        "id": canonical,
                        "display_name": champ["name"].strip().title(),
                        "win_rate": champ.get("win_rate", 0),
                        "pick_rate": champ.get("pick_rate", 0),
                        "ban_rate": champ.get("ban_rate", 0),
                        "games_analyzed": 0,  # OP.GG no siempre muestra games
                        "tier_raw": champ.get("tier", "B"),
                    }
                )

            logger.info(
                "[opgg] Extraídos %d soportes (patch %s)",
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
            logger.error("[opgg] Error durante scraping: %s", e, exc_info=True)
            raise

        finally:
            context.close()

    def fetch_champion_detail(self, champion_id: str) -> dict:
        """
        Extrae detalle de un soporte individual desde OP.GG.

        (Implementación futura)
        """
        logger.info(
            "[opgg] Detalle de %s — pendiente de implementación",
            champion_id,
        )
        return {
            "champion_id": champion_id,
            "platform": self.platform_name,
            "builds": {},
            "runes": {},
            "matchups": {},
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
        logger.info("[opgg] Browser cerrado")
