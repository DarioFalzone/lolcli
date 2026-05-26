"""
Adapters V4 - Asia meta (KR/CN/JP).

Foco: senal temprana del meta global. KR/CN historicamente se anticipan
1-2 patches al meta de las demas regiones. Implementar adapters de las
fuentes asiaticas para detectar tendencias antes que sean obvias.

Las 8 fuentes del set V4 viven en este modulo unico porque comparten
estado (stub) y patron en V1. Cuando alguna se active con extract real,
se puede extraer a su propio archivo si crece en complejidad.

Estrategias por fuente:

| Adapter | Tipo | Notas |
|---------|------|-------|
| OpGgKr/Jp/Cn | HTML/SPA | Misma estructura que opgg.py, distinto locale |
| PoroGg | HTML+JSON embebido | Stats KR, parse del SSR |
| FowKr | HTML | Stats historicos KR; encoding mixto UTF-8/EUC-KR |
| LolPs | SPA | Requiere Playwright, lang=ko forzado |
| DeepLol | HTML | Rankings KR jungle |
| Tencent101 | SPA + geolock | Sitio oficial CN |
| TencentRank | SPA + geolock | Ranking oficial CN, encoding GB18030 |

Todos retornan `status: not_implemented` con instrucciones claras hasta
que el operador active el extract real por adapter.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from .base import BaseAdapter

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class _AsiaStubAdapter(BaseAdapter):
    """Base stub para todos los adapters V4. Comparte el shape de respuesta."""

    source_url: str = ""
    note: str = "Adapter stub V4 (Asia)."

    def fetch_support_tier_list(self, patch: str = "latest", elo: str = "challenger") -> dict:
        return self._stub("support", patch, elo)

    def fetch_jungle_tier_list(self, patch: str = "latest", elo: str = "challenger") -> dict:
        return self._stub("jungle", patch, elo)

    def fetch_champion_detail(self, champion_id: str) -> dict:
        return {
            "platform": self.platform_name,
            "champion_id": champion_id,
            "status": "not_implemented",
            "reason": self.note,
            "scraped_at": _now_iso(),
        }

    def _stub(self, role: str, patch: str, elo: str) -> dict:
        logger.info("[%s] stub fetch_%s_tier_list (no scrape real aun)", self.platform_name, role)
        return {
            "platform": self.platform_name,
            "source_url": self.source_url,
            "role": role,
            "patch": patch,
            "elo": elo,
            "status": "not_implemented",
            "reason": self.note,
            "champions": [],
            "champion_count": 0,
            "scraped_at": _now_iso(),
        }


# ---------------------------------------------------------------------------
# OP.GG locales
# ---------------------------------------------------------------------------


class OpGgKrAdapter(_AsiaStubAdapter):
    platform_name = "opgg_kr"
    source_url = "https://op.gg/ko/lol/statistics/champions"
    note = (
        "Stub. Activar: reusar logica de meta_scraper/adapters/opgg.py "
        "cambiando locale ko + filtrar elo=challenger por defecto."
    )
    min_delay = 4.0
    max_delay = 8.0


class OpGgJpAdapter(_AsiaStubAdapter):
    platform_name = "opgg_jp"
    source_url = "https://op.gg/ja/lol/statistics/champions"
    note = "Stub. Activar: idem opgg_kr con locale ja."
    min_delay = 4.0
    max_delay = 8.0


class OpGgCnAdapter(_AsiaStubAdapter):
    platform_name = "opgg_cn"
    source_url = "https://op.gg/zh-cn/lol/statistics/champions"
    note = (
        "Stub. Activar: locale zh-cn. CUIDADO: posibles diferencias de payload "
        "vs locales latinos por dataset Tencent."
    )
    min_delay = 5.0
    max_delay = 10.0


# ---------------------------------------------------------------------------
# Korean stats sites
# ---------------------------------------------------------------------------


class PoroGgAdapter(_AsiaStubAdapter):
    platform_name = "porogg_champions"
    source_url = "https://poro.gg/champions"
    note = (
        "Stub. Activar: parse del SSR. Tiene JSON embebido en <script id=__NEXT_DATA__>. "
        "Preferible eso sobre scraping del DOM."
    )
    min_delay = 5.0
    max_delay = 10.0


class FowKrAdapter(_AsiaStubAdapter):
    platform_name = "fow_kr"
    source_url = "https://ss.fow.kr/statistics"
    note = (
        "Stub. Activar: parse HTML clasico. CUIDADO con encoding mixto UTF-8/EUC-KR "
        "en algunas paginas; usar response.encoding='utf-8' explicito y validar "
        "con tests/test_no_mojibake.py antes de persistir."
    )
    min_delay = 6.0
    max_delay = 12.0


class LolPsAdapter(_AsiaStubAdapter):
    platform_name = "lolps"
    source_url = "https://lol.ps/statistics?lang=ko"
    note = (
        "Stub. Activar: SPA, requiere Playwright. Forzar lang=ko en query string. "
        "Sospechar de XHR internos antes de ir a browser headless."
    )
    min_delay = 6.0
    max_delay = 12.0


class DeepLolKrAdapter(_AsiaStubAdapter):
    platform_name = "deeplol_kr_jungle"
    source_url = "https://www.deeplol.gg/ranking/KR/jungle"
    note = "Stub. Activar: parse HTML, ranking de jugadores KR jungle."
    min_delay = 5.0
    max_delay = 10.0


# ---------------------------------------------------------------------------
# Tencent (CN) - geolock probable
# ---------------------------------------------------------------------------


class Tencent101Adapter(_AsiaStubAdapter):
    platform_name = "tencent_101"
    source_url = "https://101.qq.com/"
    note = (
        "Stub. Activar: SPA, geolock probable desde fuera de CN. "
        "Considerar proxy o tratar como fuente opt-in geografica."
    )
    min_delay = 8.0
    max_delay = 15.0


class TencentRankAdapter(_AsiaStubAdapter):
    platform_name = "tencent_rank"
    source_url = "https://lol.qq.com/guides/rank.shtml"
    note = (
        "Stub. Activar: SPA. Encoding GB18030 (NO UTF-8). "
        "Geolock probable. Usar response.encoding='gb18030' explicito y "
        "convertir a UTF-8 antes de persistir para evitar romper "
        "tests/test_no_mojibake.py."
    )
    min_delay = 8.0
    max_delay = 15.0
