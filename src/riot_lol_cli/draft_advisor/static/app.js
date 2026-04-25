/* ============================================================================
   ADC Draft Advisor — Application Logic
   ============================================================================ */

// ==========================================================================
// State
// ==========================================================================

const state = {
  champions: [],        // Full champion list from API
  allies: [null, null, null, null],       // 4 ally slots
  enemies: [null, null, null, null, null], // 5 enemy slots
  poolMode: 'unrestricted',
  poolChampions: [],    // ADC IDs in user pool
  comfort: {},          // { champId: score 1-10 }
  modalTarget: null,    // { team: 'ally'|'enemy'|'pool', index: number }
  roleFilter: 'all',
  recommendation: null,
};

// ==========================================================================
// Init
// ==========================================================================

async function init() {
  try {
    // Fetch champions
    const res = await fetch('/api/v1/draft/champions');
    state.champions = await res.json();

    // Fetch telemetry for patch info
    const telemetry = await fetch('/api/v1/draft/meta/version-info');
    const info = await telemetry.json();
    document.getElementById('patch-badge').textContent = `Patch ${info.live_patch_label} (Data: ${info.static_data_version})`;

    renderChampionGrid();
  } catch (e) {
    console.error('Failed to init:', e);
    document.getElementById('patch-badge').textContent = 'Error loading data';
  }
}

// ==========================================================================
// Champion Picker Modal
// ==========================================================================

function openChampionPicker(team, index) {
  state.modalTarget = { team, index };
  const modal = document.getElementById('champion-modal');
  modal.classList.add('active');
  document.getElementById('champion-search').value = '';
  state.roleFilter = 'all';

  // Update role filter buttons
  document.querySelectorAll('.role-filter').forEach(b => {
    b.classList.toggle('active', b.dataset.role === 'all');
  });

  // If picking for pool, only show ADCs
  if (team === 'pool') {
    filterByRole('Bot');
    document.querySelectorAll('.role-filter').forEach(b => {
      b.classList.toggle('active', b.dataset.role === 'Bot');
    });
  }

  renderChampionGrid();
  setTimeout(() => document.getElementById('champion-search').focus(), 100);
}

function closeModal() {
  document.getElementById('champion-modal').classList.remove('active');
  state.modalTarget = null;
}

function getUsedChampionIds() {
  const used = new Set();
  state.allies.forEach(a => { if (a) used.add(a.id); });
  state.enemies.forEach(e => { if (e) used.add(e.id); });
  return used;
}

function renderChampionGrid() {
  const grid = document.getElementById('champion-grid');
  const search = document.getElementById('champion-search').value.toLowerCase();
  const used = getUsedChampionIds();

  let filtered = state.champions;

  // Role filter
  if (state.roleFilter !== 'all') {
    filtered = filtered.filter(c => c.primary_role === state.roleFilter);
  }

  // Search filter
  if (search) {
    filtered = filtered.filter(c =>
      c.display_name.toLowerCase().includes(search) ||
      c.id.toLowerCase().includes(search)
    );
  }

  // If pool mode, only show ADCs
  if (state.modalTarget && state.modalTarget.team === 'pool') {
    filtered = filtered.filter(c => c.is_adc);
  }

  grid.innerHTML = filtered.map(c => {
    const disabled = used.has(c.id) ? 'disabled' : '';
    const imgSrc = `/assets/splash_arts/${c.id}/${c.id}_Classic.jpg`;
    return `
      <div class="champion-option ${disabled}" onclick="selectChampion('${c.id}')" title="${c.display_name}">
        <img src="${imgSrc}" alt="${c.display_name}" loading="lazy"
             onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2280%22 height=%2280%22%3E%3Crect fill=%22%231a2035%22 width=%2280%22 height=%2280%22/%3E%3Ctext x=%2240%22 y=%2245%22 fill=%22%236b7280%22 text-anchor=%22middle%22 font-size=%2212%22%3E${c.id.slice(0,3)}%3C/text%3E%3C/svg%3E'">
        <div class="name">${c.display_name}</div>
      </div>
    `;
  }).join('');
}

function filterChampions(value) {
  renderChampionGrid();
}

function filterByRole(role) {
  state.roleFilter = role;
  document.querySelectorAll('.role-filter').forEach(b => {
    b.classList.toggle('active', b.dataset.role === role);
  });
  renderChampionGrid();
}

function selectChampion(champId) {
  if (!state.modalTarget) return;
  const { team, index } = state.modalTarget;

  const champ = state.champions.find(c => c.id === champId);
  if (!champ) return;

  if (team === 'ally') {
    state.allies[index] = { id: champId, display_name: champ.display_name };
    renderSlots();
  } else if (team === 'enemy') {
    state.enemies[index] = { id: champId, display_name: champ.display_name };
    renderSlots();
  } else if (team === 'pool') {
    if (!state.poolChampions.includes(champId)) {
      state.poolChampions.push(champId);
      if (!state.comfort[champId]) state.comfort[champId] = 5;
      renderPool();
    }
  }

  closeModal();
}

// ==========================================================================
// Slot Rendering
// ==========================================================================

function renderSlots() {
  renderTeamSlots('ally', state.allies, 'ally-slots');
  renderTeamSlots('enemy', state.enemies, 'enemy-slots');
}

function renderTeamSlots(team, slots, containerId) {
  const container = document.getElementById(containerId);
  const slotElements = container.querySelectorAll('.champion-slot:not(.disabled)');

  slotElements.forEach((el, i) => {
    const champ = slots[i];
    if (champ) {
      const imgSrc = `/assets/splash_arts/${champ.id}/${champ.id}_Classic.jpg`;
      el.className = `champion-slot filled ${team}`;
      el.innerHTML = `
        <img class="slot-img" src="${imgSrc}" alt="${champ.display_name}"
             onerror="this.style.display='none'">
        <span class="slot-name">${champ.display_name}</span>
        <button class="remove-btn" onclick="event.stopPropagation(); removeChampion('${team}', ${i})">&times;</button>
      `;
      el.onclick = () => openChampionPicker(team, i);
    } else {
      el.className = 'champion-slot';
      el.innerHTML = '<span class="slot-placeholder">+</span>';
      el.onclick = () => openChampionPicker(team, i);
    }
  });
}

function removeChampion(team, index) {
  if (team === 'ally') {
    state.allies[index] = null;
  } else if (team === 'enemy') {
    state.enemies[index] = null;
  }
  renderSlots();
}

// ==========================================================================
// Pool Management
// ==========================================================================

function setPoolMode(mode) {
  state.poolMode = mode;
  document.querySelectorAll('#pool-toggle button').forEach(b => {
    b.classList.toggle('active', b.dataset.mode === mode);
  });
  document.getElementById('pool-config').style.display =
    mode === 'unrestricted' ? 'none' : 'block';
  renderPool();
}

function renderPool() {
  const container = document.getElementById('pool-champions');
  container.innerHTML = state.poolChampions.map(id => {
    const champ = state.champions.find(c => c.id === id);
    const name = champ ? champ.display_name : id;
    return `
      <span class="pool-chip">
        ${name}
        <span class="remove" onclick="removeFromPool('${id}')">&times;</span>
      </span>
    `;
  }).join('');

  // Comfort sliders
  const sliders = document.getElementById('comfort-sliders');
  sliders.innerHTML = state.poolChampions.map(id => {
    const champ = state.champions.find(c => c.id === id);
    const name = champ ? champ.display_name : id;
    const val = state.comfort[id] || 5;
    return `
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
        <span style="width:100px;font-size:0.8rem;color:var(--text-secondary)">${name}</span>
        <input type="range" min="1" max="10" value="${val}"
               style="flex:1;accent-color:var(--gold)"
               oninput="state.comfort['${id}']=parseInt(this.value);this.nextElementSibling.textContent=this.value">
        <span style="width:20px;font-size:0.8rem;font-weight:600;color:var(--gold);text-align:right">${val}</span>
      </div>
    `;
  }).join('');
}

function removeFromPool(champId) {
  state.poolChampions = state.poolChampions.filter(id => id !== champId);
  delete state.comfort[champId];
  renderPool();
}

// ==========================================================================
// Get Recommendation
// ==========================================================================

async function getRecommendation() {
  const btn = document.getElementById('recommend-btn');
  btn.classList.add('loading');
  btn.innerHTML = '<span class="spinner"></span> Analyzing...';

  try {
    const draftState = {
      allies: state.allies.filter(a => a !== null).map(a => ({ id: a.id })),
      enemies: state.enemies.filter(e => e !== null).map(e => ({ id: e.id })),
      bans: [],
      context: {
        pick_position: document.getElementById('pick-position').value,
        information_level: inferInfoLevel(),
        queue_type: document.getElementById('queue-type').value,
      },
      user_pool: {
        mode: state.poolMode,
        champions: state.poolChampions,
        comfort: state.comfort,
      },
    };

    const res = await fetch('/api/v1/draft/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(draftState),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'API error');
    }

    state.recommendation = await res.json();
    renderResults(state.recommendation);
  } catch (e) {
    console.error('Recommendation error:', e);
    alert('Error: ' + e.message);
  } finally {
    btn.classList.remove('loading');
    btn.innerHTML = 'Recommend ADC';
  }
}

function inferInfoLevel() {
  const enemies = state.enemies.filter(e => e !== null).length;
  if (enemies >= 4) return 'full';
  if (enemies >= 1) return 'partial';
  return 'none';
}

// ==========================================================================
// Render Results
// ==========================================================================

function renderResults(result) {
  const section = document.getElementById('results-section');
  section.classList.add('visible');

  renderDraftSummary(result.draft_analysis);
  renderTopPick(result.top_pick);
  renderAlternatives(result.alternatives);

  // Scroll to results
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderDraftSummary(analysis) {
  const container = document.getElementById('draft-summary');
  const allied = analysis.allied_comp_profile;
  const enemy = analysis.enemy_comp_profile;

  const boolBadge = (val, label) =>
    `<span style="color:${val ? 'var(--green)' : 'var(--text-muted)'}">${val ? '&#10003;' : '&#10007;'} ${label}</span>`;

  container.innerHTML = `
    <div class="draft-summary-item">
      <div class="label">Allied Composition</div>
      <div class="value" style="display:flex;flex-wrap:wrap;gap:8px;font-size:0.8rem;">
        ${boolBadge(allied.has_frontline, 'Frontline')}
        ${boolBadge(allied.has_engage, 'Engage')}
        ${boolBadge(allied.has_peel, 'Peel')}
        ${boolBadge(allied.has_poke, 'Poke')}
      </div>
    </div>
    <div class="draft-summary-item">
      <div class="label">Teamfight Shape</div>
      <div class="value">${formatShape(allied.teamfight_shape)}</div>
    </div>
    <div class="draft-summary-item">
      <div class="label">ADC Threat Level</div>
      <div class="value" style="color:${threatColor(enemy.threat_level_to_adc)}">${enemy.threat_level_to_adc.toUpperCase()}</div>
    </div>
    <div class="draft-summary-item">
      <div class="label">Confidence</div>
      <div class="value">${analysis.confidence.toUpperCase()}</div>
    </div>
  `;
}

function renderTopPick(pick) {
  const card = document.getElementById('top-pick-card');
  const imgSrc = `/assets/splash_arts/${pick.id}/${pick.id}_Classic.jpg`;
  const raw = pick.score_breakdown.raw;

  const factors = [
    { label: 'Ally Synergy', key: 'ally_synergy' },
    { label: 'Enemy Matchup', key: 'enemy_matchup' },
    { label: 'Blind Safety', key: 'blind_pick_safety' },
    { label: 'Comp Gap Fill', key: 'comp_gap_fill' },
    { label: 'Solo Q Reliability', key: 'solo_queue_reliability' },
    { label: 'Scaling Fit', key: 'scaling_fit' },
  ];

  card.innerHTML = `
    <div class="top-pick-header">
      <div class="top-pick-portrait">
        <img src="${imgSrc}" alt="${pick.display_name}">
      </div>
      <div class="top-pick-info">
        <div class="top-pick-label">&#9733; Top Recommendation</div>
        <div class="top-pick-name">${pick.display_name}</div>
      </div>
      <div class="top-pick-score">
        <div class="score-value">${pick.total_score.toFixed(1)}</div>
        <div class="score-label">Score / 100</div>
      </div>
    </div>

    <div class="score-breakdown">
      ${factors.map(f => `
        <div class="score-factor">
          <span class="score-factor-label">${f.label}</span>
          <div class="score-bar-track">
            <div class="score-bar-fill" style="width:${raw[f.key]}%"></div>
          </div>
          <span class="score-factor-value">${raw[f.key].toFixed(0)}</span>
        </div>
      `).join('')}
    </div>

    <div class="explanation-grid">
      <div class="explanation-block">
        <h4 class="strengths">&#9650; Strengths</h4>
        <ul class="strengths-list">
          ${pick.strengths_in_this_draft.map(s => `<li>${s}</li>`).join('')}
        </ul>
      </div>
      <div class="explanation-block">
        <h4 class="risks">&#9888; Risks</h4>
        <ul class="risks-list">
          ${pick.risks_in_this_draft.map(r => `<li>${r}</li>`).join('')}
        </ul>
      </div>
      <div class="explanation-block">
        <h4 class="avoid">&#10007; Not Recommended When</h4>
        <ul class="avoid-list">
          ${pick.not_recommended_when.map(n => `<li>${n}</li>`).join('')}
        </ul>
      </div>
      <div class="explanation-block">
        <h4 class="pattern">&#9655; Play Pattern</h4>
        <p class="pattern-text">${pick.enabled_play_pattern}</p>
      </div>
    </div>
  `;
}

function renderAlternatives(alts) {
  const grid = document.getElementById('alternatives-grid');
  grid.innerHTML = alts.map(alt => {
    const imgSrc = `/assets/splash_arts/${alt.id}/${alt.id}_Classic.jpg`;
    return `
      <div class="alt-card">
        <div class="alt-header">
          <div class="alt-portrait">
            <img src="${imgSrc}" alt="${alt.display_name}">
          </div>
          <div class="alt-name">${alt.display_name}</div>
          <div class="alt-score">${alt.total_score.toFixed(1)}</div>
        </div>
        <div class="alt-reason">${alt.one_line_reason}</div>
        <div class="alt-compare">
          <div class="alt-pros">
            ${alt.advantages_over_top_pick.map(a => `<span>+ ${a}</span>`).join('')}
          </div>
          <div class="alt-cons">
            ${alt.disadvantages_vs_top_pick.map(d => `<span>- ${d}</span>`).join('')}
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// ==========================================================================
// Helpers
// ==========================================================================

function formatShape(shape) {
  const map = {
    'front_to_back': 'Front-to-Back',
    'dive': 'Dive',
    'poke_siege': 'Poke / Siege',
    'pick': 'Pick Comp',
    'split': 'Split Push',
    'mixed': 'Mixed / Flexible',
  };
  return map[shape] || shape;
}

function threatColor(level) {
  const map = {
    'critical': 'var(--red)',
    'high': 'var(--orange)',
    'medium': 'var(--gold)',
    'low': 'var(--green)',
    'minimal': 'var(--blue)',
  };
  return map[level] || 'var(--text-primary)';
}

// Close modal on escape
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
});

// Close modal on overlay click
document.getElementById('champion-modal').addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) closeModal();
});

// ==========================================================================
// Boot
// ==========================================================================
init();
