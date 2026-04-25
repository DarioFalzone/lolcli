# 🎯 ADC TRACKER - Lista de Campeones

**Actualizado:** 11 de enero de 2026  
**Fuente:** Data Dragon (API oficial de Riot)  
**Total:** 31 ADCs + Yasuo

---

## 📊 Lista Completa de ADCs Trackeados

| # | Campeón | Rol | Estado |
|---|---------|-----|--------|
| 1 | Akshan | Marksman | ✅ Trackeado |
| 2 | Aphelios | Marksman | ✅ Trackeado |
| 3 | Ashe | Marksman | ✅ Trackeado |
| 4 | Azir | Marksman | ✅ Trackeado |
| 5 | Caitlyn | Marksman | ✅ Trackeado |
| 6 | Corki | Marksman | ✅ Trackeado |
| 7 | Draven | Marksman | ✅ Trackeado |
| 8 | Ezreal | Marksman | ✅ Trackeado |
| 9 | Graves | Marksman | ✅ Trackeado |
| 10 | Jayce | Marksman | ✅ Trackeado |
| 11 | Jhin | Marksman | ✅ Trackeado |
| 12 | Jinx | Marksman | ✅ Trackeado |
| 13 | Kaisa | Marksman | ✅ Trackeado |
| 14 | Kalista | Marksman | ✅ Trackeado |
| 15 | Kennen | Marksman | ✅ Trackeado |
| 16 | Kindred | Marksman | ✅ Trackeado |
| 17 | KogMaw | Marksman | ✅ Trackeado |
| 18 | Lucian | Marksman | ✅ Trackeado |
| 19 | MissFortune | Marksman | ✅ Trackeado |
| 20 | Quinn | Marksman | ✅ Trackeado |
| 21 | Samira | Marksman | ✅ Trackeado |
| 22 | Senna | Marksman | ✅ Trackeado |
| 23 | Sivir | Marksman | ✅ Trackeado |
| 24 | Teemo | Marksman | ✅ Trackeado |
| 25 | Tristana | Marksman | ✅ Trackeado |
| 26 | Twitch | Marksman | ✅ Trackeado |
| 27 | Varus | Marksman | ✅ Trackeado |
| 28 | Vayne | Marksman | ✅ Trackeado |
| 29 | Xayah | Marksman | ✅ Trackeado |
| 30 | Zeri | Marksman | ✅ Trackeado |
| 31 | Yasuo | Mid/ADC Híbrido | ✅ Trackeado |

---

## 📈 Estadísticas del Sistema

```
Total ADCs (Data Dragon):     30
ADCs Adicionales:              1 (Yasuo)
───────────────────────────────────
Total Trackeado:              31

Stats Horarias Generadas:     248 (8 por campeón)
Anomalías Detectadas:          3
Tier Lists Creadas:            1
```

---

## 🎮 Campeones por Categoría

### Top 10 Clásicos
1. Ashe
2. Caitlyn
3. Draven
4. Ezreal
5. Graves
6. Jinx
7. Lucian
8. Tristana
9. Twitch
10. Vayne

### Modernos/Actuales
- Akshan
- Aphelios
- Kaisa
- Samira
- Senna
- Xayah
- Zeri
- Yasuo (adición)

### Alternativos/Híbridos
- Azir (AP Carry)
- Corki (Hybrid)
- Jayce (Hybrid)
- Kennen (AP)
- Kindred (Jungler/ADC)
- KogMaw (AP/AD)
- Quinn (Mid/ADC)
- Teemo (Utility/AP)
- Varus (Hybrid)

---

## 🔄 Fuente de Datos

**API**: Data Dragon v14.1.1 (Oficialmente mantenida por Riot Games)  
**Endpoint**: `https://ddragon.leagueoflegends.com/cdn/14.1.1/data/en_US/champion.json`  
**Criterio**: Tag "Marksman" + Yasuo adicional

---

## 📊 Monitoreo Actual

El sistema ahora:
- ✅ Rastrea **winrate** de cada ADC
- ✅ Rastrea **pickrate** de cada ADC
- ✅ Rastrea **banrate** de cada ADC
- ✅ Detecta **anomalías** (spikes, nerfs, buffs)
- ✅ Genera **tier lists** automáticas
- ✅ Mantiene **histórico** de cambios meta

---

## 🚀 Próximos Pasos

1. **Integrar Riot API Real**
   - Reemplazar datos demo con matches reales
   - Ejecutar: `python main.py --collect-meta`

2. **Configurar Auto-Refresh**
   - Recolectar datos cada hora
   - Detectar cambios automáticamente

3. **Alertas y Notificaciones**
   - Discord webhook para cambios importantes
   - Slack integration
   - Email alerts

4. **Análisis Avanzado**
   - Correlacionar con parches
   - Machine Learning predictions
   - Historical trend analysis

---

## 📝 Archivo de Configuración

**Ubicación:** `adc_champions.json`

```json
{
  "adc_count": 30,
  "adcs": [
    "Akshan", "Aphelios", "Ashe", ... (30 total)
  ],
  "adcs_with_yasuo": [
    "Akshan", "Aphelios", "Ashe", ... (31 total con Yasuo)
  ],
  "total_with_yasuo": 31
}
```

---

## 💡 Notas Importantes

- **Yasuo** se agregó manualmente porque aunque tiene tag "Assassin", se juega frecuentemente de ADC
- **Teemo** está incluido porque Data Dragon lo clasifica como Marksman
- **Kindred** está incluida por ser jugable en bottom lane
- La lista se puede actualizar ejecutando: `python fetch_adc_champions.py`

---

## 🎯 Resumen

**Sistema configurado para trackear:**
- 30 ADCs oficiales de League of Legends
- 1 ADC alternativo (Yasuo)
- **31 campeones totales**

**Datos generados:**
- 248 registros de stats horarias
- Histórico de 24 horas
- Anomalías detectadas
- Tier list snapshot

**Listo para:**
- Análisis meta en tiempo real
- Detección de cambios
- Alertas automáticas
- Reportes de tendencias

---

**¡Sistema de tracking de ADCs completamente configurado! 🚀**
