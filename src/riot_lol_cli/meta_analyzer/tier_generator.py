"""
Tier Generator - Genera tier lists basadas en estadísticas y anomalías
"""
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class Tier(Enum):
    """Tiers de campeones"""
    S = "S"  # OP, pick must
    A = "A"  # Muy bueno, pick frequently
    B = "B"  # Bueno, viable
    C = "C"  # Aceptable
    D = "D"  # Débil, avoid


@dataclass
class ChampionTierInfo:
    """Información de un campeón en tier list"""
    champion: str
    tier: Tier
    winrate: float
    pickrate: float
    banrate: float
    matches: int
    trend: Optional[str] = None      # "RISING", "STABLE", "FALLING"
    reason: Optional[str] = None     # Por qué está en este tier
    best_role: Optional[str] = None
    
    def to_dict(self) -> dict[str, Any]:
        return {
            'champion': self.champion,
            'tier': self.tier.value,
            'winrate': round(self.winrate, 2),
            'pickrate': round(self.pickrate, 2),
            'banrate': round(self.banrate, 2),
            'matches': self.matches,
            'trend': self.trend,
            'reason': self.reason,
            'best_role': self.best_role,
        }


class TierListGenerator:
    """Genera tier lists basadas en estadísticas"""
    
    # Umbrales de tier
    TIER_THRESHOLDS = {
        Tier.S: 54.0,
        Tier.A: 51.5,
        Tier.B: 48.5,
        Tier.C: 46.0,
        Tier.D: 0.0
    }
    
    # Ajustes
    MIN_MATCHES = 50        # Mínimo matches para validez
    PICKRATE_PENALTY = 2    # Reduce tier si pickrate < 2%
    BANRATE_BONUS = 0.3     # Sube tier si banrate alto
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data" / "meta"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_tier_list(
        self,
        stats: dict[str, Any],
        anomalies: Optional[list[Any]] = None
    ) -> list[ChampionTierInfo]:
        """
        Genera tier list desde estadísticas
        
        Args:
            stats: Estadísticas de campeones
            anomalies: Anomalías detectadas (para marcar tendencias)
        
        Returns:
            Lista de campeones con tier
        """
        
        tier_list = []
        anomalies = anomalies or []
        
        for champion, data in stats.items():
            # Validar sample size
            matches = data.get('matches', 0)
            if matches < self.MIN_MATCHES:
                continue
            
            # Determinar tier base
            winrate = data.get('winrate', 50.0)
            tier = self._get_tier_from_winrate(winrate)
            
            # Ajustes
            tier = self._apply_pickrate_penalty(tier, data.get('pickrate', 0))
            tier = self._apply_banrate_bonus(tier, data.get('banrate', 0))
            
            # Detectar tendencia
            trend = self._detect_trend(champion, anomalies)
            if trend == "RISING":
                tier = self._upgrade_tier(tier)
            elif trend == "FALLING":
                tier = self._downgrade_tier(tier)
            
            # Mejor rol
            best_role = self._get_best_role(data.get('roles', {}))
            
            # Razón del tier
            reason = self._generate_reason(champion, tier, winrate, trend)
            
            tier_info = ChampionTierInfo(
                champion=champion,
                tier=tier,
                winrate=winrate,
                pickrate=data.get('pickrate', 0),
                banrate=data.get('banrate', 0),
                matches=matches,
                trend=trend,
                reason=reason,
                best_role=best_role
            )
            
            tier_list.append(tier_info)
        
        # Sort: primero por tier, luego por winrate
        tier_list.sort(
            key=lambda x: (
                list(Tier).index(x.tier),
                -x.winrate
            )
        )
        
        return tier_list
    
    def _get_tier_from_winrate(self, winrate: float) -> Tier:
        """Asigna tier basado en winrate"""
        
        for tier in sorted(Tier, key=lambda t: self.TIER_THRESHOLDS[t], reverse=True):
            if winrate >= self.TIER_THRESHOLDS[tier]:
                return tier
        
        return Tier.D
    
    def _apply_pickrate_penalty(self, tier: Tier, pickrate: float) -> Tier:
        """
        Reduce tier si pickrate es muy baja
        (Pueden estar subestimados si no se juegan mucho)
        """
        if pickrate < 2.0 and tier != Tier.D:
            tier_index = list(Tier).index(tier)
            return list(Tier)[min(tier_index + 1, len(list(Tier)) - 1)]
        
        return tier
    
    def _apply_banrate_bonus(self, tier: Tier, banrate: float) -> Tier:
        """
        Sube tier si banrate es alta
        (Significa que es temido)
        """
        if banrate > 20.0 and tier != Tier.S:
            tier_index = list(Tier).index(tier)
            return list(Tier)[max(tier_index - 1, 0)]
        
        return tier
    
    def _upgrade_tier(self, tier: Tier) -> Tier:
        """Sube un tier"""
        tier_index = list(Tier).index(tier)
        return list(Tier)[max(tier_index - 1, 0)]
    
    def _downgrade_tier(self, tier: Tier) -> Tier:
        """Baja un tier"""
        tier_index = list(Tier).index(tier)
        return list(Tier)[min(tier_index + 1, len(list(Tier)) - 1)]
    
    def _detect_trend(self, champion: str, anomalies: list[Any]) -> Optional[str]:
        """Detecta tendencia del campeón basada en anomalías"""
        
        for anomaly in anomalies:
            if anomaly.get('champion') == champion or \
               anomaly.champion == champion if hasattr(anomaly, 'champion') else False:
                
                # Si hay spike de winrate, es RISING
                if 'WINRATE_SPIKE' in str(anomaly):
                    return "RISING"
                
                # Si hay drop de winrate, es FALLING
                if 'WINRATE_DROP' in str(anomaly):
                    return "FALLING"
        
        return None
    
    def _get_best_role(self, roles: dict[str, Any]) -> Optional[str]:
        """Determina mejor rol para el campeón"""
        
        if not roles:
            return None
        
        best_role = max(
            roles.items(),
            key=lambda x: x[1].get('winrate', 0)
        )
        
        return best_role[0] if best_role[1].get('matches', 0) > 20 else None
    
    def _generate_reason(
        self,
        champion: str,
        tier: Tier,
        winrate: float,
        trend: Optional[str]
    ) -> str:
        """Genera razón textual del tier"""
        
        reasons = {
            Tier.S: f"Dominante en el meta (WR: {winrate:.1f}%)",
            Tier.A: f"Muy fuerte ahora (WR: {winrate:.1f}%)",
            Tier.B: f"Viable y confiable (WR: {winrate:.1f}%)",
            Tier.C: f"Aceptable pero hay mejores (WR: {winrate:.1f}%)",
            Tier.D: f"Débil actualmente (WR: {winrate:.1f}%)"
        }
        
        reason = reasons.get(tier, "")
        
        if trend == "RISING":
            reason += " ↗ (Tendencia al alza)"
        elif trend == "FALLING":
            reason += " ↘ (Tendencia a la baja)"
        
        return reason
    
    def save_tier_list(
        self,
        tier_list: list[ChampionTierInfo],
        timestamp: Optional[str] = None
    ) -> Path:
        """Guarda tier list"""
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        filepath = self.data_dir / f"tier_list_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'timestamp': timestamp,
                'count': len(tier_list),
                'tier_list': [info.to_dict() for info in tier_list]
            }, f, indent=2, ensure_ascii=False)
        
        logger.info("Tier list guardada en %s", filepath)
        logger.info("Resumen:")
        
        tier_counts = {}
        for info in tier_list:
            tier_counts[info.tier.value] = tier_counts.get(info.tier.value, 0) + 1
        
        for tier in [Tier.S, Tier.A, Tier.B, Tier.C, Tier.D]:
            count = tier_counts.get(tier.value, 0)
            logger.info("  Tier %s: %3d campeones", tier.value, count)
        
        return filepath
    
    def get_tier_list_html(self, tier_list: list[ChampionTierInfo]) -> str:
        """Genera HTML para visualizar tier list"""
        
        html_rows = ""
        
        for info in tier_list:
            trend_icon = {
                "RISING": "📈",
                "FALLING": "📉",
                None: "➡️"
            }.get(info.trend, "")
            
            html_rows += f"""
            <tr class="tier-{info.tier.value}">
                <td class="tier-badge tier-{info.tier.value}">{info.tier.value}</td>
                <td class="champion-name">{info.champion}</td>
                <td class="wr">{info.winrate:.1f}%</td>
                <td class="pr">{info.pickrate:.1f}%</td>
                <td class="br">{info.banrate:.1f}%</td>
                <td class="matches">{info.matches}</td>
                <td class="trend">{trend_icon}</td>
                <td class="reason">{info.reason}</td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>LOL Meta - Tier List</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #0a0e27;
                    color: #c89b3c;
                    padding: 20px;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    background: #1a1f3a;
                    border: 1px solid #c89b3c;
                }}
                
                th {{
                    background: #0a0e27;
                    padding: 12px;
                    text-align: left;
                    border-bottom: 2px solid #c89b3c;
                    font-weight: bold;
                }}
                
                td {{
                    padding: 10px 12px;
                    border-bottom: 1px solid #333;
                }}
                
                .tier-S {{ background: #ff6b6b; color: white; }}
                .tier-A {{ background: #ffa94d; color: white; }}
                .tier-B {{ background: #74c0fc; color: white; }}
                .tier-C {{ background: #95e1d3; color: black; }}
                .tier-D {{ background: #888; color: white; }}
                
                .tier-badge {{
                    font-weight: bold;
                    padding: 5px 10px;
                    border-radius: 3px;
                    text-align: center;
                }}
                
                .champion-name {{ font-weight: bold; }}
                .wr {{ color: #4ecdc4; }}
                .pr {{ color: #95e1d3; }}
                .br {{ color: #feca57; }}
                .matches {{ color: #999; }}
                .reason {{ font-size: 12px; color: #aaa; }}
            </style>
        </head>
        <body>
            <h1>🎯 League of Legends Meta - Tier List</h1>
            <p>Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <table>
                <tr>
                    <th>Tier</th>
                    <th>Campeón</th>
                    <th>Winrate</th>
                    <th>Pickrate</th>
                    <th>Banrate</th>
                    <th>Matches</th>
                    <th>Tendencia</th>
                    <th>Razón</th>
                </tr>
                {html_rows}
            </table>
        </body>
        </html>
        """
        
        return html


if __name__ == "__main__":
    # Ejemplo
    generator = TierListGenerator()
    
    # Mock stats
    stats = {
        'Ekko': {
            'matches': 150,
            'winrate': 53.5,
            'pickrate': 8.5,
            'banrate': 5.2,
            'roles': {'MIDDLE': {'matches': 145, 'winrate': 53.7}}
        },
        'Ahri': {
            'matches': 120,
            'winrate': 49.2,
            'pickrate': 6.3,
            'banrate': 2.1,
            'roles': {'MIDDLE': {'matches': 115, 'winrate': 49.5}}
        },
        'Support': {
            'matches': 30,  # Too low
            'winrate': 55.0,
            'pickrate': 1.5,
            'banrate': 0.5,
        }
    }
    
    tier_list = generator.generate_tier_list(stats)
    
    logging.basicConfig(level=logging.INFO)
    logger.info("Generated Tier List:")
    for info in tier_list:
        logger.info("  [%s] %-20s WR:%5.1f%% PR:%5.1f%%", info.tier.value, info.champion, info.winrate, info.pickrate)
    
    # Save
    generator.save_tier_list(tier_list)
