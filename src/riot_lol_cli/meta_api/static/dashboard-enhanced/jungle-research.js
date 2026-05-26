const JR_BASE = `${API_BASE}/jungle-research`;
let jrInitialized = false;

function jrSwitchSubtab(event, subtabId) {
    const container = document.getElementById('jungle-research');
    container.querySelectorAll('.tabs .tab').forEach(t => t.classList.remove('active'));
    container.querySelectorAll('.jr-subtab').forEach(s => { s.classList.remove('active'); s.style.display = 'none'; });
    event.currentTarget.classList.add('active');
    const subtab = document.getElementById(subtabId);
    subtab.classList.add('active');
    subtab.style.display = 'block';
}

function jrFmtPct(v) { return (v === null || v === undefined) ? '--' : (v * 100).toFixed(0) + '%'; }
function jrFmtScore(v) { return (v === null || v === undefined) ? '--' : Number(v).toFixed(2); }
function jrFmtTimestamp(iso) {
    if (!iso) return '--';
    try { return new Date(iso).toLocaleString('es-AR'); } catch { return iso; }
}
function jrTierColor(tier) {
    const map = {S: '#ff4444', A: '#ff8c00', B: '#4ecdc4', C: '#38a169', D: '#999'};
    return map[tier] || '#666';
}
function jrEscape(s) {
    if (s === null || s === undefined) return '';
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

async function jrLoadAll() {
    await Promise.all([
        jrLoadOverview(),
        jrLoadConsensus(),
        jrLoadSources(),
        jrLoadPros(),
        jrLoadDailyReport()
    ]);
    jrInitialized = true;
}

async function jrLoadOverview() {
    try {
        const resp = await axios.get(`${JR_BASE}/overview`);
        const d = resp.data;
        document.getElementById('jr-freshness').textContent = jrFmtTimestamp(d.freshness);
        document.getElementById('jr-patch').textContent = d.patch || '--';
        document.getElementById('jr-riot-key').textContent = d.riot_api_key_present ? '✓ presente' : '✗ ausente';
        document.getElementById('jr-riot-key').style.color = d.riot_api_key_present ? 'var(--state-success)' : 'var(--state-warning)';
        document.getElementById('jr-gaps-count').textContent = (d.gaps || []).length;
    } catch (e) {
        console.error('jrLoadOverview error', e);
    }
}

function jrToggleConsensusRow(idx) {
    const detailRow = document.getElementById(`jr-consensus-detail-${idx}`);
    const caret = document.getElementById(`jr-consensus-caret-${idx}`);
    if (!detailRow || !caret) return;
    const isOpen = detailRow.style.display !== 'none';
    detailRow.style.display = isOpen ? 'none' : 'table-row';
    caret.textContent = isOpen ? '▶' : '▼';
    caret.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
}

async function jrLoadConsensus() {
    const tbody = document.querySelector('#jr-consensus-table tbody');
    try {
        const resp = await axios.get(`${JR_BASE}/current?limit=80`);
        const entries = resp.data.data || [];
        if (!entries.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="no-data">Sin tier list aún. Hacé click en "Refrescar SoloQ".</td></tr>';
            return;
        }
        tbody.innerHTML = entries.map((e, idx) => {
            const tier = e.final_tier || 'D';
            const warnings = (e.warning_flags || []).map(w => `<span style="background:rgba(255,153,0,0.15); color:var(--state-warning); padding:2px 6px; border-radius:3px; font-size:10px; margin-right:4px;">${jrEscape(w)}</span>`).join('');
            const proCell = e.pro_soloq_score && e.pro_soloq_score > 0
                ? `<span title="Fuente: esports_research" style="background:rgba(0,200,255,0.15); color:#00c8ff; padding:2px 5px; border-radius:3px; font-size:9px; font-weight:bold;">ES ${jrFmtScore(e.pro_soloq_score)}</span>`
                : '';
            return `<tr class="jr-consensus-row" style="cursor:pointer; user-select:none;" onclick="jrToggleConsensusRow(${idx})">
                <td style="width:24px; text-align:center;"><span id="jr-consensus-caret-${idx}" aria-expanded="false" style="color:var(--arc-gold); font-size:12px;">▶</span></td>
                <td><span style="display:inline-block; width:28px; height:28px; line-height:28px; text-align:center; border-radius:4px; background:${jrTierColor(tier)}; color:white; font-weight:bold; font-size:12px;">${jrEscape(tier)}</span></td>
                <td style="font-weight:bold; color:var(--arc-gold);">${jrEscape(e.champion_name)}</td>
                <td style="text-align:right;">${jrFmtScore(e.final_score)}</td>
                <td style="text-align:right;">${jrFmtScore(e.confidence)} (${e.source_count || 0})</td>
            </tr>
            <tr id="jr-consensus-detail-${idx}" class="jr-consensus-detail" style="display:none; background:rgba(10,30,61,0.4);">
                <td colspan="5" style="padding:14px 18px;">
                    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:14px;">
                        <div><div style="color:var(--arc-gold); font-size:11px; text-transform:uppercase; font-weight:bold; margin-bottom:4px;">📊 SoloQ Score</div><div style="font-size:16px; color:#f0f0f0; font-weight:bold;">${jrFmtScore(e.soloq_score)}</div></div>
                        <div><div style="color:var(--arc-gold); font-size:11px; text-transform:uppercase; font-weight:bold; margin-bottom:4px;">🌏 Asia Score</div><div style="font-size:16px; color:#f0f0f0; font-weight:bold;">${jrFmtScore(e.asia_score)}</div></div>
                        <div><div style="color:var(--arc-gold); font-size:11px; text-transform:uppercase; font-weight:bold; margin-bottom:4px;">👑 High Elo</div><div style="font-size:16px; color:#f0f0f0; font-weight:bold;">${jrFmtScore(e.high_elo_presence_score)}</div></div>
                        <div><div style="color:var(--arc-gold); font-size:11px; text-transform:uppercase; font-weight:bold; margin-bottom:4px;">🎮 Pro Presence</div><div style="font-size:14px;">${proCell || '—'}</div></div>
                    </div>
                    ${warnings ? `<div style="margin-top:12px;"><div style="color:var(--state-warning); font-size:11px; text-transform:uppercase; font-weight:bold; margin-bottom:6px;">⚠️ Warnings</div><div style="display:flex; flex-wrap:wrap; gap:6px;">${warnings}</div></div>` : ''}
                    ${e.explanation ? `<div style="margin-top:12px;"><div style="color:var(--arc-gold); font-size:11px; text-transform:uppercase; font-weight:bold; margin-bottom:6px;">💬 Explicación</div><div style="font-size:12px; color:#bbb; line-height:1.4;">${jrEscape(e.explanation)}</div></div>` : ''}
                </td>
            </tr>`;
        }).join('');
    } catch (e) {
        console.error('jrLoadConsensus error', e);
        tbody.innerHTML = '<tr><td colspan="5" class="text-danger">Error al cargar consenso</td></tr>';
    }
}

async function jrLoadSources() {
    const tbody = document.querySelector('#jr-sources-table tbody');
    try {
        const resp = await axios.get(`${JR_BASE}/sources`);
        const sources = resp.data.sources || [];
        if (!sources.length) {
            tbody.innerHTML = '<tr><td colspan="8" class="no-data">Sin sources registradas</td></tr>';
            return;
        }
        const statusColor = {active: 'var(--state-success)', planned: 'var(--state-warning)', gap: 'var(--state-error)'};
        const runColor = {ok: 'var(--state-success)', not_implemented: '#888', error: 'var(--state-error)', disabled: '#666'};
        tbody.innerHTML = sources.map(s => {
            let lastRun = '<span style="color:#666; font-size:10px;">—</span>';
            if (s.last_attempted_at) {
                const status = s.last_run_status || 'unknown';
                const color = runColor[status] || '#999';
                const when = jrFmtTimestamp(s.last_attempted_at);
                const tooltip = jrEscape((s.last_run_reason || '').substring(0, 200));
                const countBadge = s.last_run_champion_count > 0
                    ? `<span style="margin-left:4px; font-size:10px; color:#aaa;">(${s.last_run_champion_count} champs)</span>`
                    : '';
                lastRun = `<div title="${tooltip}">
                    <span style="color:${color}; font-size:11px; font-weight:bold;">${jrEscape(status)}</span>${countBadge}
                    <div style="font-size:10px; color:#888;">${when}</div>
                </div>`;
            }
            return `<tr>
                <td><span style="background:${statusColor[s.status] || '#666'}; color:white; padding:3px 8px; border-radius:3px; font-size:11px; font-weight:bold; text-transform:uppercase;">${jrEscape(s.status)}</span></td>
                <td><code style="font-size:11px;">${jrEscape(s.id)}</code></td>
                <td>${jrEscape(s.name)}</td>
                <td><span style="font-size:10px; color:#aaa;">${jrEscape(s.source_type)}</span></td>
                <td>${(s.region_focus || []).join(', ') || '—'}</td>
                <td>${s.scrape_priority || 0}</td>
                <td>${lastRun}</td>
                <td><a href="${jrEscape(s.base_url)}" target="_blank" rel="noopener" style="color:var(--info); font-size:11px;">${jrEscape(s.base_url)}</a></td>
            </tr>`;
        }).join('');
    } catch (e) {
        console.error('jrLoadSources error', e);
        tbody.innerHTML = '<tr><td colspan="8" class="text-danger">Error al cargar fuentes</td></tr>';
    }
}

const JR_SERVERS = ['KR', 'EUW', 'NA', 'EUNE', 'BR', 'LAN', 'LAS', 'JP', 'TR', 'RU', 'OCE', 'VN', 'TW', 'CN'];

async function jrLoadPros() {
    const container = document.getElementById('jr-pros-cards');
    try {
        const resp = await axios.get(`${JR_BASE}/pros`);
        const rows = resp.data.data || [];
        const keyPresent = resp.data.riot_api_key_present;
        const keyBanner = keyPresent
            ? ''
            : `<div style="grid-column:1 / -1; padding:10px 14px; background:rgba(255,153,0,0.08); border:1px solid var(--state-warning); border-radius:6px; font-size:12px; color:#ccc;">
                <strong style="color:var(--state-warning);">⚠ RIOT_API_KEY ausente.</strong> Podés cargar Riot IDs igual; la resolución a PUUID se hará cuando exportes la key y refresques.
            </div>`;
        container.innerHTML = keyBanner + rows.map(p => jrProCard(p)).join('');
    } catch (e) {
        console.error('jrLoadPros error', e);
        container.innerHTML = '<p class="text-danger">Error al cargar pros</p>';
    }
}

function jrProCard(p) {
    const tierColors = {S: '#ff4444', A: '#ff8c00', B: '#4ecdc4'};
    const tierBadge = `<span style="display:inline-block; padding:2px 6px; border-radius:3px; background:${tierColors[p.priority_tier] || '#666'}; color:white; font-size:10px; font-weight:bold; margin-left:6px;">${jrEscape(p.priority_tier || '?')}</span>`;
    let stateBlock;
    if (p.puuid) {
        stateBlock = `<div style="margin-top:8px; padding:6px 8px; background:rgba(10,200,0,0.1); border-radius:4px; font-size:11px; color:var(--state-success);">
            ✓ resuelto · <code style="color:#aaa; font-size:10px;">${jrEscape(p.puuid).substring(0, 16)}…</code>
        </div>`;
    } else if (p.gap_flag === 'no_riot_key') {
        stateBlock = `<div style="margin-top:8px; padding:6px 8px; background:rgba(255,153,0,0.1); border-radius:4px; font-size:10px; color:var(--state-warning);">⚠ no_riot_key — exportá RIOT_API_KEY</div>`;
    } else if (p.riot_id) {
        stateBlock = `<div style="margin-top:8px; padding:6px 8px; background:rgba(255,61,61,0.1); border-radius:4px; font-size:10px; color:var(--state-error);">✗ ${jrEscape(p.gap_flag || 'resolución pendiente')}</div>`;
    } else {
        stateBlock = `<div style="margin-top:8px; padding:6px 8px; background:rgba(255,153,0,0.1); border-radius:4px; font-size:10px; color:var(--state-warning);">⚠ needs_account_resolution</div>`;
    }
    const currentRiot = p.riot_id ? jrEscape(p.riot_id) : '';
    const currentServer = p.server || '';
    const serverOptions = JR_SERVERS.map(s => `<option value="${s}" ${s === currentServer ? 'selected' : ''}>${s}</option>`).join('');
    return `<div style="background:rgba(10, 30, 61, 0.6); border:1px solid var(--arc-gold-dark); border-radius:6px; padding:14px;">
        <div style="display:flex; justify-content:space-between; align-items:baseline;">
            <div>
                <div style="font-weight:bold; color:var(--arc-gold); font-size:14px;">${jrEscape(p.player_name)}${tierBadge}</div>
                <div style="font-size:10px; color:#aaa; margin-top:2px;">${jrEscape(p.real_name || '')} · ${jrEscape(p.country || '?')}</div>
            </div>
        </div>
        ${stateBlock}
        <details style="margin-top:10px; font-size:11px;">
            <summary style="cursor:pointer; color:#aaa;">Editar cuenta</summary>
            <div style="margin-top:8px; display:flex; flex-direction:column; gap:6px;">
                <input type="text" id="jr-pro-rid-${jrEscape(p.player_name)}" placeholder="GameName#TAG" value="${currentRiot}" style="padding:6px; background:rgba(0,0,0,0.4); border:1px solid var(--arc-gold-dark); color:#f0f0f0; border-radius:3px; font-size:11px;">
                <select id="jr-pro-srv-${jrEscape(p.player_name)}" style="padding:6px; background:rgba(0,0,0,0.4); border:1px solid var(--arc-gold-dark); color:#f0f0f0; border-radius:3px; font-size:11px;">
                    <option value="">— Server —</option>
                    ${serverOptions}
                </select>
                <div style="display:flex; gap:6px;">
                    <button onclick="jrSavePro('${jrEscape(p.player_name)}')" style="flex:1; padding:6px; background:var(--arc-gold); color:#010a13; border:none; border-radius:3px; cursor:pointer; font-size:11px; font-weight:bold;">Guardar</button>
                    <button onclick="jrClearPro('${jrEscape(p.player_name)}')" style="padding:6px 10px; background:transparent; color:#aaa; border:1px solid var(--arc-gold-dark); border-radius:3px; cursor:pointer; font-size:11px;">Limpiar</button>
                </div>
                <div id="jr-pro-msg-${jrEscape(p.player_name)}" style="font-size:10px; color:#aaa;"></div>
            </div>
        </details>
    </div>`;
}

async function jrSavePro(name) {
    const ridInput = document.getElementById(`jr-pro-rid-${name}`);
    const srvSel = document.getElementById(`jr-pro-srv-${name}`);
    const msg = document.getElementById(`jr-pro-msg-${name}`);
    const riot_id = ridInput.value.trim() || null;
    const server = srvSel.value || null;
    if (riot_id && !riot_id.includes('#')) {
        msg.textContent = '✗ Formato: GameName#TAG';
        msg.style.color = 'var(--state-error)';
        return;
    }
    if (riot_id && !server) {
        msg.textContent = '✗ Elegí un server';
        msg.style.color = 'var(--state-error)';
        return;
    }
    msg.textContent = '⏳ Guardando…';
    msg.style.color = '#aaa';
    try {
        const resp = await axios.post(`${JR_BASE}/pros/${encodeURIComponent(name)}/account`, {riot_id, server});
        const d = resp.data;
        if (d.error) {
            msg.textContent = `✗ ${d.error}`;
            msg.style.color = 'var(--state-error)';
            return;
        }
        if (d.resolved) {
            msg.textContent = `✓ Resuelto · PUUID obtenido`;
            msg.style.color = 'var(--state-success)';
        } else if (d.gap_flag) {
            msg.textContent = `Guardado · ${d.gap_flag}`;
            msg.style.color = 'var(--state-warning)';
        } else {
            msg.textContent = '✓ Guardado';
            msg.style.color = 'var(--state-success)';
        }
        setTimeout(() => jrLoadPros(), 600);
    } catch (e) {
        console.error('jrSavePro error', e);
        msg.textContent = '✗ Error de red';
        msg.style.color = 'var(--state-error)';
    }
}

async function jrClearPro(name) {
    try {
        await axios.post(`${JR_BASE}/pros/${encodeURIComponent(name)}/account`, {riot_id: null, server: null});
        jrLoadPros();
    } catch (e) {
        console.error('jrClearPro error', e);
    }
}

async function jrLoadDailyReport() {
    const container = document.getElementById('jr-report-content');
    try {
        const resp = await axios.get(`${JR_BASE}/daily-report`);
        const data = resp.data.data;
        if (!data) {
            container.innerHTML = `<div style="padding:14px; background:rgba(255,153,0,0.08); border:1px solid var(--state-warning); border-radius:6px; color:#ccc;">
                ${(resp.data.gaps || ['Sin reporte aún. Hacé click en "Refrescar SoloQ" para generar la tier list base.']).join('<br>')}
            </div>`;
            return;
        }
        const movementHtml = (movements, label, color) => {
            if (!movements || !movements.length) return '';
            return `<div style="margin-top:14px;"><div style="font-weight:bold; color:${color}; margin-bottom:8px;">${label}</div>
                <ul style="list-style:none; padding:0;">${movements.map(m => `
                    <li style="padding:4px 8px; border-bottom:1px solid rgba(200,155,60,0.1); font-size:13px;">
                        <strong>${jrEscape(m.champion_name)}</strong>
                        <span style="font-size:11px; color:#aaa;"> ${jrEscape(m.previous_tier || '?')} → ${jrEscape(m.current_tier)}</span>
                        <span style="float:right; color:${color};">${m.delta > 0 ? '+' : ''}${jrFmtScore(m.delta)}</span>
                    </li>`).join('')}</ul></div>`;
        };
        const contradictionsHtml = (data.contradictions || []).length === 0 ? '' : `
            <div style="margin-top:14px;"><div style="font-weight:bold; color:var(--state-warning); margin-bottom:8px;">⚠ Contradicciones entre fuentes</div>
                <ul style="list-style:none; padding:0;">${data.contradictions.map(c => `
                    <li style="padding:4px 8px; font-size:13px;">
                        <strong>${jrEscape(c.champion_name)}</strong>: spread WR ${jrFmtScore(c.spread)}pp
                        <span style="font-size:11px; color:#aaa; display:block;">${Object.entries(c.by_source || {}).map(([s, v]) => `${s}: ${v}%`).join(' · ')}</span>
                    </li>`).join('')}</ul></div>`;
        container.innerHTML = `
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:18px;">
                <div>
                    <div style="font-weight:bold; color:var(--arc-gold); margin-bottom:8px;">Top junglers</div>
                    <ul style="list-style:none; padding:0;">${(data.top_junglers || []).slice(0, 10).map(t => `
                        <li style="padding:4px 8px; border-bottom:1px solid rgba(200,155,60,0.1); font-size:13px;">
                            <span style="display:inline-block; width:22px; height:22px; line-height:22px; text-align:center; border-radius:3px; background:${jrTierColor(t.final_tier)}; color:white; font-weight:bold; font-size:11px; margin-right:8px;">${jrEscape(t.final_tier)}</span>
                            <strong>${jrEscape(t.champion_name)}</strong>
                            <span style="float:right; color:#aaa; font-size:11px;">${jrFmtScore(t.final_score)}</span>
                        </li>`).join('')}</ul>
                </div>
                <div>${movementHtml(data.risers, '📈 Risers', 'var(--state-success)')}${movementHtml(data.fallers, '📉 Fallers', 'var(--state-error)')}</div>
                <div>${contradictionsHtml || '<div style="font-size:12px; color:#888;">Sin contradicciones detectadas.</div>'}</div>
            </div>
        `;
    } catch (e) {
        console.error('jrLoadDailyReport error', e);
        container.innerHTML = '<p class="text-danger">Error al cargar reporte</p>';
    }
}

async function jrRefresh(mode) {
    try {
        const resp = await axios.post(`${JR_BASE}/refresh?mode=${encodeURIComponent(mode)}`);
        console.log('jrRefresh', mode, resp.data);
        await jrLoadAll();
    } catch (e) {
        console.error('jrRefresh error', e);
        alert('Refresh falló — revisá la consola.');
    }
}

function jrActivateView(primaryTabId, subtabId) {
    const rootTabsBar = document.querySelector('.container > .tabs');
    if (rootTabsBar) {
        rootTabsBar.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        const primaryBtn = rootTabsBar.querySelector(`button[onclick*="'${primaryTabId}'"]`);
        if (primaryBtn) primaryBtn.classList.add('active');
    }
    document.querySelectorAll('.container > .tab-content').forEach(c => c.classList.remove('active'));
    const primaryContent = document.getElementById(primaryTabId);
    if (primaryContent) primaryContent.classList.add('active');
    if (primaryTabId === 'jungle-research' && !jrInitialized) {
        jrLoadAll();
    }
    if (subtabId && primaryContent) {
        primaryContent.querySelectorAll('.tabs .tab').forEach(t => t.classList.remove('active'));
        const subBtn = primaryContent.querySelector(`.tabs button[onclick*="'${subtabId}'"]`);
        if (subBtn) subBtn.classList.add('active');
        primaryContent.querySelectorAll('.jr-subtab').forEach(s => {
            s.classList.remove('active');
            s.style.display = 'none';
        });
        const subView = document.getElementById(subtabId);
        if (subView) {
            subView.classList.add('active');
            subView.style.display = 'block';
        }
    }
}
