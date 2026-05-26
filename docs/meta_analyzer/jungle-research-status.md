# Jungla 360 — Estado Actual

**Última actualización**: 2026-05-25 (PR-D)  
**Versión subsistema**: V3.7 (METAsrc extraído real)  
**Patch meta**: 26.10  
**Riot API**: Verificable vía env var `RIOT_API_KEY`

---

## 📊 Metricas de cobertura

| Métrica | Valor | Estado |
|---------|-------|--------|
| Campeones totales analizados (SoloQ) | 164 | ✅ Activo |
| Fuentes activas (V1) | 4 | ✅ Operativo |
| Fuentes activadas (V3) | 1 (METAsrc) | ✅ En prueba |
| Snapshots diarios guardados | 23 | ✅ Acumulando |
| Asia score integrado | Sí | ✅ Operativo |
| High Elo presence | Sí | ✅ Operativo |
| Pro presence (esports) | Sí | ✅ Desde PR-C |
| Test coverage (jungle_research) | 97% | ✅ Alto |

---

## ✅ Features implementados (por fase)

### V1 (Inicial)
- [x] Tier list final por consenso (UGG + Lolalytics + Jungle Meta Local)
- [x] Registry de fuentes con estado (active/planned/gap)
- [x] Scoring con pesos explícitos (soloq, asia, high_elo)
- [x] Snapshot dailies automatizados
- [x] API `/jungle-research/*` endpoints
- [x] Dashboard Jungla 360 con tabs (Consenso, Fuentes, Pros, OTPs, Reporte)

### V2 (Mejorado)
- [x] Pro players seed management (Riot ID + server resolution)
- [x] PUUID resolution vía Riot Match API (si `RIOT_API_KEY` presente)
- [x] Daily report (risers, fallers, contradictions entre fuentes)
- [x] Drill-down expandible en tabla Consenso

### V3 (Adapters reales)
- [x] V3.7 METAsrc: SSR parse + tier/WR/PR/BR extract (con fixture + tests)
- [x] V3.8 LeagueOfGraphs: planned (selectores identificados)
- [ ] V3.9 Onetricks.gg: planned (OTP rankings)
- [ ] V4.0+ Riot API integración: planned (match-v5 con RIOT_API_KEY)

### Integraciones cruzadas
- [x] PR-C: Esports comfort → `pro_presence_score` (puente activo)
- [x] PR-D: HTML extraído a `/static/dashboard-enhanced/` + router hash

---

## 🗂️ Estructura de datos (final)

### Tier list JSON (latest snapshot)
```
data/meta_analyzer/jungle_research/final_jungle_tierlist/latest.json
├── meta:
│   ├── timestamp
│   ├── patch
│   ├── region_focus (KR)
│   └── source_count_total (≥4)
├── data:
│   └── [{
│       champion_name,
│       final_tier (S/A/B/C/D),
│       final_score,
│       confidence,
│       soloq_score,
│       asia_score,
│       high_elo_presence_score,
│       pro_soloq_score (desde esports),
│       source_count,
│       warning_flags [],
│       explanation
│   }]
```

### Adapter runs telemetry
```
data/meta_analyzer/jungle_research/adapter_runs.json
├── run_id (timestamp-based)
├── adapter_id (ugg_jungle, lolalytics_jungle, metasrc_jungle, etc.)
├── status (ok/not_implemented/error/disabled)
├── champion_count
├── attempted_at
├── run_reason (mensaje de error si aplica)
```

---

## 🔧 Decisiones arquitectónicas clave

1. **Storage final (Gold)**: JSON snapshots diarios en `data/`, no BD relacional  
   *Por qué*: Máxima auditabilidad, versionado simple vía git, backups automáticos

2. **Scraping policy**: SSR parse con BeautifulSoup, sin Playwright  
   *Por qué*: Rápido, bajo overhead, suficiente para tablas HTML estáticas

3. **Scoring**: Suma ponderada de cohortes (SoloQ 50% + Asia 20% + High Elo 15% + Pro 15%)  
   *Por qué*: Transparente, auditable, fácil de ajustar pesos por balance patch

4. **Pro presence**: Comfort de esports_research, sin resolver PUUID si no hay Riot key  
   *Por qué*: Decoupling de subsistemas, datos reales sin hard dependencies

---

## 🐛 Known gaps (bloqueados, no critical)

- **Onetricks OTP rankings (V3.9)**: Planned, no implementado (baja prioridad)
- **Match-v5 Riot API (V4.0)**: Bloqueado por `RIOT_API_KEY` env var no requerida
- **RLS (Regional League Series) integration**: No scope en V1-V3
- **Real-time updates**: Snapshots solo diarios (por eficiencia)

---

## 🚀 Próximas iteraciones (V4.0+)

Ver [`jungle-research-roadmap.md`](jungle-research-roadmap.md) para fases futuras.

---

## 📚 Referencias cruzadas

- [Decisiones arquitectónicas](jungle-research-decisions.md)
- [Roadmap futuro](jungle-research-roadmap.md)
- [`AGENTS.md`](../../AGENTS.md) — subsistema de jungle_research
- [Esports integration memory](../../.claude/projects/e--Desarrollos-LOLCLI/memory/project_esports_jungle_integration.md)
