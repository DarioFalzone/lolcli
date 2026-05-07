/* ============================================================
   Draft Advisor — Lógica de aplicación
   ============================================================ */

// ── Estado global ──────────────────────────────────────────
const state = {
  champions: [],
  allies:    [null, null, null, null],
  enemies:   [null, null, null, null, null],
  poolMode:  'unrestricted',
  poolChampions: [],
  comfort:   {},
  modalTarget: null,   // { team: 'ally'|'enemy', index: number }
  roleFilter: 'all',
  recommendation: null,
  targetRole: 'adc',
};

function formatLastUpdate(value) {
  if (!value || value === 'unknown') return 'sin fecha';
  const dateOnly = /^\d{4}-\d{2}-\d{2}$/.test(value);
  const parsed = new Date(dateOnly ? `${value}T00:00:00Z` : value);
  if (Number.isNaN(parsed.getTime())) return value;
  if (dateOnly) {
    return parsed.toLocaleDateString('es-AR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      timeZone: 'UTC',
    });
  }
  return parsed.toLocaleString('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'America/Argentina/Buenos_Aires',
  });
}

function formatDateTime(value) {
  if (!value || value === 'unknown') return 'sin fecha';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleDateString('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    timeZone: 'UTC',
  });
}

// ── Inicialización ─────────────────────────────────────────
async function init() {
  try {
    const [champsRes, telRes] = await Promise.all([
      fetch('/api/v1/draft/champions'),
      fetch('/api/v1/draft/meta/version-info'),
    ]);
    state.champions = await champsRes.json();
    const info = await telRes.json();
    const badge = document.getElementById('patch-badge');
    const lastUpdate = formatLastUpdate(info.last_verified_at);
    badge.innerHTML = `<span class="patch-dot"></span> Parche ${info.live_patch_label} &nbsp;·&nbsp; Data Dragon ${info.static_data_version} &nbsp;·&nbsp; Actualizado ${lastUpdate}`;
    renderChampionGrid();
  } catch (e) {
    console.error('Error al iniciar:', e);
    const badge = document.getElementById('patch-badge');
    if (badge) badge.textContent = 'Error al cargar datos';
  }
}

// ── Cambiar rol objetivo ───────────────────────────────────
function changeTargetRole(role) {
  state.targetRole = role;
  const lbl = document.getElementById('target-role-label');
  if (lbl) lbl.textContent = role === 'support' ? 'SUPP' : 'ADC';
  state.poolChampions = [];
  state.comfort = {};
}

// ── Limpiar tablero completo ───────────────────────────────
function clearBoard() {
  state.allies  = [null, null, null, null];
  state.enemies = [null, null, null, null, null];
  state.recommendation = null;
  renderSlots();

  // Ocultar resultados sin destruir el DOM interno
  const results = document.getElementById('results-section');
  const empty   = document.getElementById('results-empty');
  const altBlock = document.getElementById('alternatives-block');
  const summary  = document.getElementById('draft-summary');
  const topCard  = document.getElementById('top-pick-card');
  const altGrid  = document.getElementById('alternatives-grid');

  if (results)  results.classList.remove('visible');
  if (empty)    empty.style.display = '';
  if (altBlock) altBlock.style.display = 'none';
  // Limpiar contenido de los hijos, NO del contenedor padre
  if (summary)  summary.innerHTML = '';
  if (topCard)  topCard.innerHTML = '';
  if (altGrid)  altGrid.innerHTML = '';

  // Reiniciar el botón de análisis
  const btn = document.getElementById('recommend-btn');
  if (btn) {
    btn.classList.remove('loading');
    btn.innerHTML = '<span class="btn-analyze-icon">⚡</span><span>Analizar Draft</span>';
  }
}

// ── Modal: abrir selector ──────────────────────────────────
function openChampionPicker(team, index) {
  state.modalTarget = { team, index };
  const modal = document.getElementById('champion-modal');
  modal.classList.add('active');
  const input = document.getElementById('champion-search');
  input.value = '';
  state.roleFilter = 'all';
  document.querySelectorAll('.role-pill').forEach(b => {
    b.classList.toggle('role-pill--active', b.dataset.role === 'all');
    b.setAttribute('aria-pressed', b.dataset.role === 'all' ? 'true' : 'false');
  });
  renderChampionGrid();
  setTimeout(() => input.focus(), 80);
}

// ── Modal: cerrar ──────────────────────────────────────────
function closeModal() {
  document.getElementById('champion-modal').classList.remove('active');
  state.modalTarget = null;
  document.getElementById('champion-search').value = '';
  updateSearchHint('');
}

// ── Buscar: keydown — Enter agrega el primer campeón ───────
function handleSearchKeydown(e) {
  if (e.key !== 'Enter') return;
  const grid = document.getElementById('champion-grid');
  const first = grid.querySelector('.champ-option:not(.champ-option--disabled)');
  if (first) {
    const champId = first.dataset.champId;
    selectChampion(champId);
  }
}

// ── Buscar: input ──────────────────────────────────────────
function filterChampions(value) {
  renderChampionGrid();
  updateSearchHint(value);
}

function updateSearchHint(value) {
  const hint = document.getElementById('search-hint');
  if (!hint) return;
  const grid = document.getElementById('champion-grid');
  const first = grid ? grid.querySelector('.champ-option:not(.champ-option--disabled)') : null;
  if (value.trim() && first) {
    const name = first.querySelector('.champ-name')?.textContent || '';
    hint.textContent = `↵ Agregar "${name}" al tablero`;
    hint.className = 'search-hint hint--ready';
  } else if (value.trim()) {
    hint.textContent = 'Sin coincidencias';
    hint.className = 'search-hint';
  } else {
    hint.textContent = 'Escribí un nombre o presioná ↵ para agregar el primero filtrado';
    hint.className = 'search-hint';
  }
}

// ── Filtrar por rol ────────────────────────────────────────
function filterByRole(role) {
  state.roleFilter = role;
  document.querySelectorAll('.role-pill').forEach(b => {
    const active = b.dataset.role === role;
    b.classList.toggle('role-pill--active', active);
    b.setAttribute('aria-pressed', active ? 'true' : 'false');
  });
  renderChampionGrid();
  updateSearchHint(document.getElementById('champion-search').value);
}

// ── Renderizar grilla de campeones ─────────────────────────
function getUsedIds() {
  const s = new Set();
  state.allies.forEach(a => a && s.add(a.id));
  state.enemies.forEach(e => e && s.add(e.id));
  return s;
}

function renderChampionGrid() {
  const grid   = document.getElementById('champion-grid');
  const search = document.getElementById('champion-search').value.toLowerCase().trim();
  const used   = getUsedIds();

  let list = state.champions;

  if (state.roleFilter !== 'all') {
    list = list.filter(c => c.primary_role === state.roleFilter);
  }
  if (search) {
    list = list.filter(c =>
      c.display_name.toLowerCase().includes(search) ||
      c.id.toLowerCase().includes(search)
    );
  }

  if (!list.length) {
    grid.innerHTML = '<p style="grid-column:1/-1;text-align:center;padding:24px;color:#4a5568;font-size:.82rem;">Sin resultados</p>';
    return;
  }

  grid.innerHTML = list.map((c, idx) => {
    const disabled  = used.has(c.id) ? 'champ-option--disabled' : '';
    const highlight = idx === 0 && search ? 'champ-option--highlighted' : '';
    const imgSrc    = `/assets/splash_arts/${c.id}/${c.id}_Classic.jpg`;
    const fallback  = `data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2280%22 height=%2280%22%3E%3Crect fill=%22%23060b14%22 width=%2280%22 height=%2280%22/%3E%3Ctext x=%2240%22 y=%2246%22 fill=%22%234a5568%22 text-anchor=%22middle%22 font-size=%2211%22 font-family=%22monospace%22%3E${encodeURIComponent(c.id.slice(0,4))}%3C/text%3E%3C/svg%3E`;
    return `<div class="champ-option ${disabled} ${highlight}" role="listitem" data-champ-id="${c.id}" onclick="selectChampion('${c.id}')" tabindex="0" aria-label="${c.display_name}${used.has(c.id) ? ' (ya seleccionado)' : ''}" onkeydown="if(event.key==='Enter'||event.key===' ')selectChampion('${c.id}')">
      <img src="${imgSrc}" alt="${c.display_name}" loading="lazy" onerror="this.src='${fallback}'">
      <div class="champ-name">${c.display_name}</div>
    </div>`;
  }).join('');
}

// ── Seleccionar campeón ────────────────────────────────────
function selectChampion(champId) {
  if (!state.modalTarget) return;
  const { team, index } = state.modalTarget;
  const champ = state.champions.find(c => c.id === champId);
  if (!champ) return;

  if (team === 'ally') {
    state.allies[index] = { id: champId, display_name: champ.display_name };
  } else if (team === 'enemy') {
    state.enemies[index] = { id: champId, display_name: champ.display_name };
  }

  renderSlots();
  closeModal();
}

// ── Renderizar slots ───────────────────────────────────────
function renderSlots() {
  renderTeamSlots('ally',  state.allies,  'ally-slots',  4);
  renderTeamSlots('enemy', state.enemies, 'enemy-slots', 5);
}

function renderTeamSlots(team, slots, containerId, count) {
  const container = document.getElementById(containerId);
  const slotEls   = container.querySelectorAll('.champion-slot:not(.slot--role-locked)');

  slotEls.forEach((el, i) => {
    const champ = slots[i];
    if (champ) {
      const imgSrc  = `/assets/splash_arts/${champ.id}/${champ.id}_Classic.jpg`;
      const fallback = `data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2280%22 height=%2280%22%3E%3Crect fill=%22%23060b14%22 width=%2280%22 height=%2280%22/%3E%3C/svg%3E`;
      el.className  = `champion-slot slot--filled slot--${team}`;
      el.setAttribute('aria-label', `${champ.display_name}, slot ${team === 'ally' ? 'aliado' : 'enemigo'} ${i + 1}`);
      el.onclick    = () => openChampionPicker(team, i);
      el.innerHTML  = `
        <img class="slot-img" src="${imgSrc}" alt="${champ.display_name}" onerror="this.src='${fallback}'">
        <span class="slot-name">${champ.display_name}</span>
        <button class="remove-btn" onclick="event.stopPropagation();removeChampion('${team}',${i})" aria-label="Quitar ${champ.display_name}">×</button>
      `;
    } else {
      el.className  = 'champion-slot';
      el.setAttribute('aria-label', `Slot ${team === 'ally' ? 'aliado' : 'enemigo'} ${i + 1}, vacío`);
      el.onclick    = () => openChampionPicker(team, i);
      el.innerHTML  = '<span class="slot-plus">+</span>';
    }
  });
}

function removeChampion(team, index) {
  if (team === 'ally')  state.allies[index]  = null;
  if (team === 'enemy') state.enemies[index] = null;
  renderSlots();
}

// ── Obtener recomendación ──────────────────────────────────
async function getRecommendation() {
  const btn = document.getElementById('recommend-btn');
  btn.classList.add('loading');
  btn.innerHTML = '<span class="spinner"></span><span>Analizando…</span>';

  try {
    const payload = {
      allies:  state.allies.filter(Boolean).map(a => ({ id: a.id })),
      enemies: state.enemies.filter(Boolean).map(e => ({ id: e.id })),
      bans: [],
      context: {
        pick_position:     document.getElementById('pick-position').value,
        information_level: inferInfoLevel(),
        queue_type:        document.getElementById('queue-type').value,
      },
      user_pool: {
        mode:      state.poolMode,
        champions: state.poolChampions,
        comfort:   state.comfort,
      },
      target_role: state.targetRole,
    };

    const res = await fetch('/api/v1/draft/recommend', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Error del servidor');
    }

    state.recommendation = await res.json();
    renderResults(state.recommendation);
  } catch (e) {
    console.error('Error de recomendación:', e);
    alert('Error: ' + e.message);
  } finally {
    btn.classList.remove('loading');
    btn.innerHTML = '<span class="btn-analyze-icon">⚡</span><span>Analizar Draft</span>';
  }
}

function inferInfoLevel() {
  const n = state.enemies.filter(Boolean).length;
  if (n >= 4) return 'full';
  if (n >= 1) return 'partial';
  return 'none';
}

// ── Renderizar resultados ──────────────────────────────────
function renderResults(result) {
  const empty   = document.getElementById('results-empty');
  const section = document.getElementById('results-section');
  if (empty)   empty.style.display = 'none';
  if (!section) { console.error('results-section not found'); return; }
  section.classList.add('visible');

  renderDraftSummary(result.draft_analysis);
  renderTopPick(result.top_pick);
  renderAlternatives(result.alternatives);

  section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Resumen del draft ──────────────────────────────────────
function renderDraftSummary(analysis) {
  const container = document.getElementById('draft-summary');
  if (!container) return;
  const allied = analysis.allied_comp_profile;
  const enemy  = analysis.enemy_comp_profile;

  const badge = (val, label) =>
    `<span class="comp-badge ${val ? 'comp-badge--on' : 'comp-badge--off'}">${val ? '✓' : '—'} ${label}</span>`;

  container.innerHTML = `
    <div class="summary-card">
      <div class="summary-label">Composición Aliada</div>
      <div class="summary-value">
        <div class="comp-badges">
          ${badge(allied.has_frontline, 'Frente')}
          ${badge(allied.has_engage,   'Engage')}
          ${badge(allied.has_peel,     'Peel')}
          ${badge(allied.has_poke,     'Poke')}
        </div>
      </div>
    </div>
    <div class="summary-card">
      <div class="summary-label">Estilo de Pelea</div>
      <div class="summary-value">${formatShape(allied.teamfight_shape)}</div>
    </div>
    <div class="summary-card">
      <div class="summary-label">Amenaza Enemiga al ADC</div>
      <div class="summary-value threat--${enemy.threat_level_to_adc}">${threatEs(enemy.threat_level_to_adc)}</div>
    </div>
    <div class="summary-card">
      <div class="summary-label">Confianza del Análisis</div>
      <div class="summary-value">${confidenceEs(analysis.confidence)}</div>
    </div>
  `;
}

// ── Pick principal ─────────────────────────────────────────
function renderTopPick(pick) {
  const card   = document.getElementById('top-pick-card');
  if (!card) return;
  const imgSrc = `/assets/splash_arts/${pick.id}/${pick.id}_Classic.jpg`;
  const raw    = pick.score_breakdown.raw;

  const factors = [
    { label: 'Sinergia Aliada',       key: 'ally_synergy' },
    { label: 'Matchup Enemigo',       key: 'enemy_matchup' },
    { label: 'Seguridad a Ciegas',    key: 'blind_pick_safety' },
    { label: 'Cubre Huecos de Comp.', key: 'comp_gap_fill' },
    { label: 'Fiabilidad en SoloQ',   key: 'solo_queue_reliability' },
    { label: 'Ajuste de Escalado',    key: 'scaling_fit' },
  ];

  card.innerHTML = `
    <div class="top-pick-header">
      <div class="top-pick-portrait">
        <img src="${imgSrc}" alt="${pick.display_name}" onerror="this.style.background='#060b14'">
      </div>
      <div>
        <div class="pick-badge">★ Recomendación Principal</div>
        <div class="pick-name">${pick.display_name}</div>
        ${renderAdcContextChips(pick.adc_context)}
      </div>
      <div class="top-pick-score">
        <div class="score-number">${pick.total_score.toFixed(1)}</div>
        <div class="score-unit">Puntaje / 100</div>
      </div>
    </div>

    <div class="score-bars">
      ${factors.map(f => {
        const v = raw[f.key] ?? 0;
        return `<div class="score-row">
          <span class="score-lbl">${f.label}</span>
          <div class="bar-track"><div class="bar-fill" style="width:${v}%;background:${barGradient(v)}"></div></div>
          <span class="score-val">${v.toFixed(0)}</span>
        </div>`;
      }).join('')}
    </div>

    <div class="explain-grid">
      <div class="explain-block">
        <div class="explain-heading explain-heading--strength">▲ Fortalezas</div>
        <ul class="explain-list explain-list--strength">
          ${pick.strengths_in_this_draft.map(s => `<li>${s}</li>`).join('')}
        </ul>
      </div>
      <div class="explain-block">
        <div class="explain-heading explain-heading--risk">⚠ Riesgos</div>
        <ul class="explain-list explain-list--risk">
          ${pick.risks_in_this_draft.map(r => `<li>${r}</li>`).join('')}
        </ul>
      </div>
      <div class="explain-block">
        <div class="explain-heading explain-heading--avoid">✕ No recomendado cuando</div>
        <ul class="explain-list explain-list--avoid">
          ${pick.not_recommended_when.map(n => `<li>${n}</li>`).join('')}
        </ul>
      </div>
      <div class="explain-block">
        <div class="explain-heading explain-heading--pattern">▶ Plan de Juego</div>
        <p class="explain-text">${pick.enabled_play_pattern}</p>
      </div>
    </div>
  `;
}

// ── Alternativas ───────────────────────────────────────────
function renderAlternatives(alts) {
  const block = document.getElementById('alternatives-block');
  const grid  = document.getElementById('alternatives-grid');
  if (!block || !grid) return;

  if (!alts || !alts.length) { block.style.display = 'none'; return; }
  block.style.display = '';

  grid.innerHTML = alts.map(alt => {
    const imgSrc = `/assets/splash_arts/${alt.id}/${alt.id}_Classic.jpg`;
    const pros = alt.advantages_over_top_pick    || [];
    const cons = alt.disadvantages_vs_top_pick   || [];
    return `
      <div class="alt-card">
        <div class="alt-header">
          <div class="alt-portrait">
            <img src="${imgSrc}" alt="${alt.display_name}" onerror="this.style.background='#060b14'">
          </div>
          <div style="flex:1;min-width:0;">
            <div class="alt-name">${alt.display_name}</div>
            ${renderAdcContextChips(alt.adc_context, true)}
            <div class="alt-reason">${alt.one_line_reason}</div>
          </div>
          <div class="alt-score-num">${alt.total_score.toFixed(1)}</div>
        </div>
        ${(pros.length || cons.length) ? `
        <div class="alt-compare">
          ${pros.map(p => `<div class="alt-pro">+ ${p}</div>`).join('')}
          ${cons.map(c => `<div class="alt-con">− ${c}</div>`).join('')}
        </div>` : ''}
      </div>
    `;
  }).join('');
}

// ── Helpers ────────────────────────────────────────────────
function renderAdcContextChips(ctx, compact = false) {
  if (!ctx) return '';
  const chips = [];
  if (ctx.personal_tier) chips.push({ label: `Maestría ${ctx.personal_tier}`, mod: 'mastery' });
  if (ctx.meta_tier) chips.push({ label: `Meta ${ctx.meta_tier}`, mod: 'meta' });
  if (typeof ctx.meta_climb_score === 'number') {
    chips.push({ label: `Subida ${ctx.meta_climb_score.toFixed(1)}`, mod: 'score' });
  }
  if (ctx.meta_scraped_at && !compact) {
    chips.push({ label: `Scraping ${formatDateTime(ctx.meta_scraped_at)}`, mod: 'date' });
  }
  if (ctx.eligibility && ctx.eligibility.startsWith('fallback')) {
    chips.push({ label: 'Alternativa', mod: 'fallback' });
  }
  if (!chips.length) return '';
  return `<div class="adc-context-chips ${compact ? 'adc-context-chips--compact' : ''}">
    ${chips.map(chip => `<span class="adc-chip adc-chip--${chip.mod}" title="${ctx.eligibility_reason || ''}">${chip.label}</span>`).join('')}
  </div>`;
}

function formatShape(shape) {
  const map = {
    front_to_back: 'Teamfight frontal',
    dive:          'Dive',
    poke_siege:    'Poke / asedio',
    pick:          'Cazadas',
    split:         'Split push',
    mixed:         'Mixto / Flexible',
  };
  return map[shape] || shape;
}

function threatEs(level) {
  return { critical: 'Crítica', high: 'Alta', medium: 'Media', low: 'Baja', minimal: 'Mínima' }[level] || level;
}

function confidenceEs(level) {
  return { high: 'Alta', medium: 'Media', low: 'Baja' }[level] || level;
}

function barGradient(v) {
  if (v >= 70) return 'linear-gradient(90deg,#0ac8b9,#c89b3c)';
  if (v >= 45) return 'linear-gradient(90deg,#785a28,#c89b3c)';
  return 'linear-gradient(90deg,#d13639,#ff9a3c)';
}

// ── Eventos globales ───────────────────────────────────────
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
});

document.getElementById('champion-modal').addEventListener('click', e => {
  if (e.target === e.currentTarget) closeModal();
});

// ── Arranque ───────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const sel = document.getElementById('target-role');
  if (sel) changeTargetRole(sel.value);
  updateSearchHint('');
});
init();
