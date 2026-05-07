/**
 * Meta Scraper — Dashboard Frontend Logic
 *
 * Consume la API local en localhost:8002 para mostrar la tier list
 * de soportes con filtros, panel de detalle y trigger de scraping.
 */

// --- State ---
const state = {
  data: null,          // Dataset normalizado completo
  champions: [],       // Lista filtrada actualmente visible
  activeTier: 'all',   // Filtro de tier activo
  searchQuery: '',     // Búsqueda por texto
  selectedChamp: null, // Campeón seleccionado para detalle
  isScraping: false,
  activeRole: 'support', // 'support' | 'adc'
};

// Data Dragon CDN para avatares de campeones
const DDRAGON_VERSION = '16.8.1';
const DDRAGON_BASE = `https://ddragon.leagueoflegends.com/cdn/${DDRAGON_VERSION}/img/champion`;

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
  loadData();
  // Poll health cada 10s para detectar cuando termina un scraping
  setInterval(pollHealth, 10000);
});

// --- Role Switching ---
function switchRole(role) {
  if (state.activeRole === role) return;
  state.activeRole = role;

  // Update tab styles
  document.querySelectorAll('.role-tab').forEach(tab => {
    tab.classList.toggle('role-tab--active', tab.dataset.role === role);
  });

  // Toggle climb_score column visibility via body class
  document.body.classList.toggle('role-adc', role === 'adc');

  // Reset filters and reload
  state.activeTier = 'all';
  state.searchQuery = '';
  document.getElementById('champion-search').value = '';
  document.querySelectorAll('.tier-pill').forEach(p => {
    p.classList.toggle('tier-pill--active', p.dataset.tier === 'all');
  });

  loadData();
}

// --- Data Loading ---
async function loadData() {
  const endpoint = state.activeRole === 'adc'
    ? '/api/v1/meta/adc/tier'
    : '/api/v1/meta/support/tier';

  try {
    const response = await fetch(endpoint);
    if (response.status === 404) {
      showEmptyState();
      return;
    }
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    state.data = await response.json();
    state.champions = state.data.champions || [];

    updateHeader(state.data);
    updateQuickStats(state.data);
    renderTierList(state.champions);
    hideEmptyState();
  } catch (err) {
    console.error('Error cargando datos:', err);
    showEmptyState();
  }
}

// --- Header ---
function updateHeader(data) {
  const patchBadge = document.getElementById('patch-badge');
  const timestamp = document.getElementById('scrape-timestamp');

  patchBadge.textContent = `Parche ${data.patch || '—'}`;

  if (data.scraped_at) {
    const date = new Date(data.scraped_at);
    timestamp.textContent = `Actualizado: ${date.toLocaleDateString('es-AR')} ${date.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' })}`;
  }
}

// --- Quick Stats ---
function updateQuickStats(data) {
  const champs = data.champions || [];

  document.getElementById('stat-total').textContent = champs.length;
  document.getElementById('stat-sources').textContent = (data.sources || []).join(' + ') || '—';

  // Mejor WR
  if (champs.length > 0) {
    const sorted = [...champs].sort((a, b) =>
      (b.stats?.win_rate || 0) - (a.stats?.win_rate || 0)
    );
    const best = sorted[0];
    document.getElementById('stat-best-wr').textContent = `${best.stats.win_rate}%`;
    document.getElementById('stat-best-name').textContent = best.display_name || best.id;

    // Más pickeado
    const byPick = [...champs].sort((a, b) =>
      (b.stats?.pick_rate || 0) - (a.stats?.pick_rate || 0)
    );
    const topPick = byPick[0];
    document.getElementById('stat-most-picked').textContent = `${topPick.stats.pick_rate}%`;
    document.getElementById('stat-picked-name').textContent = topPick.display_name || topPick.id;
  }
}

// --- Tier List Rendering ---
function renderTierList(champions) {
  const tbody = document.getElementById('tier-table-body');
  tbody.innerHTML = '';

  champions.forEach((champ, index) => {
    const wr = champ.stats?.win_rate || 0;
    const pr = champ.stats?.pick_rate || 0;
    const br = champ.stats?.ban_rate || 0;
    const tier = champ.stats?.tier || 'B';
    const sources = Object.keys(champ.source_breakdown || {});

    const row = document.createElement('tr');
    row.onclick = () => openDetail(champ);
    row.setAttribute('data-tier', tier);
    row.setAttribute('data-champion', (champ.display_name || champ.id).toLowerCase());

    // WR color class
    let wrClass = 'wr-mid';
    if (wr >= 52) wrClass = 'wr-high';
    else if (wr < 49) wrClass = 'wr-low';

    // WR bar width (mapped 45-55% → 0-100%)
    const wrBarWidth = Math.min(100, Math.max(0, (wr - 45) * 10));
    const prBarWidth = Math.min(100, pr * 5);
    const brBarWidth = Math.min(100, br * 4);

    // Avatar URL
    const avatarUrl = `${DDRAGON_BASE}/${champ.id}.png`;

    row.innerHTML = `
      <td class="td-rank">${index + 1}</td>
      <td>
        <div class="champion-cell">
          <img class="champion-avatar"
               src="${avatarUrl}"
               alt="${champ.display_name || champ.id}"
               onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 36 36%22><rect fill=%22%23091520%22 width=%2236%22 height=%2236%22/><text x=%2218%22 y=%2224%22 text-anchor=%22middle%22 fill=%22%23c89b3c%22 font-size=%2214%22>${(champ.display_name || champ.id).charAt(0)}</text></svg>'">
          <span class="champion-name">${champ.display_name || champ.id}</span>
        </div>
      </td>
      <td style="text-align:center">
        <span class="tier-badge tier-badge--${tier}">${tier}</span>
      </td>
      <td>
        <div class="stat-cell">
          <div class="stat-value-row">
            <span class="stat-number" style="color: ${wrColor(wr)}">${wr.toFixed(1)}</span>
            <span class="stat-suffix">%</span>
          </div>
          <div class="stat-bar">
            <div class="stat-bar-fill ${wrClass}" style="width: ${wrBarWidth}%"></div>
          </div>
        </div>
      </td>
      <td>
        <div class="stat-cell">
          <div class="stat-value-row">
            <span class="stat-number">${pr.toFixed(1)}</span>
            <span class="stat-suffix">%</span>
          </div>
          <div class="stat-bar">
            <div class="stat-bar-fill pr-bar" style="width: ${prBarWidth}%"></div>
          </div>
        </div>
      </td>
      <td>
        <div class="stat-cell">
          <div class="stat-value-row">
            <span class="stat-number">${br.toFixed(1)}</span>
            <span class="stat-suffix">%</span>
          </div>
          <div class="stat-bar">
            <div class="stat-bar-fill br-bar" style="width: ${brBarWidth}%"></div>
          </div>
        </div>
      </td>
      <td class="td-climb">
        ${champ.stats?.climb_score != null
          ? `<span class="stat-number" style="color:${climbColor(champ.stats.climb_score)}">${champ.stats.climb_score.toFixed(1)}</span>`
          : '<span style="color:var(--text-muted)">—</span>'}
      </td>
      <td>
        <div class="source-badges">
          ${sources.map(s => `<span class="source-badge source-badge--${s}">${s}</span>`).join('')}
        </div>
      </td>
    `;

    tbody.appendChild(row);
  });
}

function wrColor(wr) {
  if (wr >= 53) return '#2dcc70';
  if (wr >= 51) return '#0ac8b9';
  if (wr >= 49) return '#eef0f4';
  if (wr >= 47) return '#ff9a3c';
  return '#ff4655';
}

function climbColor(cs) {
  if (cs >= 80) return '#2dcc70';
  if (cs >= 65) return '#0ac8b9';
  if (cs >= 50) return '#eef0f4';
  if (cs >= 35) return '#ff9a3c';
  return '#ff4655';
}

// --- Filtering ---
function filterByTier(tier) {
  state.activeTier = tier;

  // Update pill UI
  document.querySelectorAll('.tier-pill').forEach(pill => {
    pill.classList.remove('tier-pill--active');
    if (pill.dataset.tier === tier) pill.classList.add('tier-pill--active');
  });

  applyFilters();
}

function filterBySearch(query) {
  state.searchQuery = query.toLowerCase().trim();
  applyFilters();
}

function applyFilters() {
  if (!state.data) return;

  let filtered = state.data.champions || [];

  // Tier filter
  if (state.activeTier !== 'all') {
    filtered = filtered.filter(c => (c.stats?.tier || 'B') === state.activeTier);
  }

  // Search filter
  if (state.searchQuery) {
    filtered = filtered.filter(c =>
      (c.display_name || c.id).toLowerCase().includes(state.searchQuery) ||
      c.id.toLowerCase().includes(state.searchQuery)
    );
  }

  state.champions = filtered;
  renderTierList(filtered);
}

// --- Detail Panel ---
function openDetail(champ) {
  state.selectedChamp = champ;
  const panel = document.getElementById('detail-panel');
  const content = document.getElementById('detail-content');

  const wr = champ.stats?.win_rate || 0;
  const pr = champ.stats?.pick_rate || 0;
  const br = champ.stats?.ban_rate || 0;
  const tier = champ.stats?.tier || 'B';
  const games = champ.stats?.games_analyzed || 0;
  const climbScore = champ.stats?.climb_score ?? null;
  const sources = champ.source_breakdown || {};

  let sourcesHTML = '';
  for (const [platform, stats] of Object.entries(sources)) {
    sourcesHTML += `
      <div class="detail-source-item">
        <div class="detail-source-name">${platform}</div>
        <div class="detail-stat-row">
          <span class="detail-stat-label">Win Rate</span>
          <span class="detail-stat-value" style="color:${wrColor(stats.win_rate || 0)}">${(stats.win_rate || 0).toFixed(1)}%</span>
        </div>
        <div class="detail-stat-row">
          <span class="detail-stat-label">Pick Rate</span>
          <span class="detail-stat-value">${(stats.pick_rate || 0).toFixed(1)}%</span>
        </div>
        <div class="detail-stat-row">
          <span class="detail-stat-label">Ban Rate</span>
          <span class="detail-stat-value">${(stats.ban_rate || 0).toFixed(1)}%</span>
        </div>
        ${stats.games_analyzed ? `
        <div class="detail-stat-row">
          <span class="detail-stat-label">Partidas</span>
          <span class="detail-stat-value">${stats.games_analyzed.toLocaleString('es-AR')}</span>
        </div>` : ''}
      </div>
    `;
  }

  const avatarUrl = `${DDRAGON_BASE}/${champ.id}.png`;

  content.innerHTML = `
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
      <img src="${avatarUrl}" alt="${champ.display_name}" style="width:48px; height:48px; border-radius:50%; border:2px solid var(--gold);"
           onerror="this.style.display='none'">
      <div>
        <h2 style="margin:0">${champ.display_name || champ.id}</h2>
        <span class="tier-badge tier-badge--${tier}" style="margin-top:4px">${tier}</span>
      </div>
    </div>

    <div class="detail-section">
      <div class="detail-section-title">Estadísticas Promediadas</div>
      <div class="detail-stat-row">
        <span class="detail-stat-label">Win Rate</span>
        <span class="detail-stat-value" style="color:${wrColor(wr)}">${wr.toFixed(2)}%</span>
      </div>
      <div class="detail-stat-row">
        <span class="detail-stat-label">Pick Rate</span>
        <span class="detail-stat-value">${pr.toFixed(2)}%</span>
      </div>
      <div class="detail-stat-row">
        <span class="detail-stat-label">Ban Rate</span>
        <span class="detail-stat-value">${br.toFixed(2)}%</span>
      </div>
      ${games > 0 ? `
      <div class="detail-stat-row">
        <span class="detail-stat-label">Partidas analizadas</span>
        <span class="detail-stat-value">${games.toLocaleString('es-AR')}</span>
      </div>` : ''}
      ${climbScore !== null ? `
      <div class="detail-stat-row">
        <span class="detail-stat-label">Climb Score</span>
        <span class="detail-stat-value" style="color:${climbColor(climbScore)}">${climbScore.toFixed(1)}</span>
      </div>` : ''}
    </div>

    <div class="detail-section">
      <div class="detail-section-title">Desglose por Fuente</div>
      ${sourcesHTML || '<p style="color:var(--text-muted); font-size: 0.85rem;">Sin desglose disponible</p>'}
    </div>
  `;

  panel.style.display = 'block';

  // Highlight row
  document.querySelectorAll('.tier-table tbody tr').forEach(row => {
    row.classList.remove('is-selected');
    if (row.dataset.champion === (champ.display_name || champ.id).toLowerCase()) {
      row.classList.add('is-selected');
    }
  });
}

function closeDetail() {
  document.getElementById('detail-panel').style.display = 'none';
  state.selectedChamp = null;
  document.querySelectorAll('.tier-table tbody tr').forEach(row => {
    row.classList.remove('is-selected');
  });
}

// --- Scraping ---
async function triggerScrape() {
  if (state.isScraping) return;

  const btn = document.getElementById('btn-scrape');
  const text = document.getElementById('scrape-text');

  state.isScraping = true;
  btn.classList.add('is-scraping');
  btn.disabled = true;
  text.textContent = 'Scrapeando...';

  const scrapeEndpoint = state.activeRole === 'adc'
    ? '/api/v1/meta/scrape/adc'
    : '/api/v1/meta/scrape';

  try {
    const response = await fetch(scrapeEndpoint, { method: 'POST' });
    const data = await response.json();

    if (response.ok) {
      showToast('Scraping iniciado. Los datos se actualizarán en unos minutos.');
      // Poll más frecuente mientras scrapea
      const pollInterval = setInterval(async () => {
        const health = await (await fetch('/health')).json();
        if (!health.is_scraping) {
          clearInterval(pollInterval);
          state.isScraping = false;
          btn.classList.remove('is-scraping');
          btn.disabled = false;
          text.textContent = 'Actualizar';
          showToast('✓ Datos actualizados correctamente');
          loadData();
        }
      }, 3000);
    } else {
      showToast(`Error: ${data.detail || 'Error desconocido'}`);
      resetScrapeButton();
    }
  } catch (err) {
    showToast(`Error de red: ${err.message}`);
    resetScrapeButton();
  }
}

function resetScrapeButton() {
  const btn = document.getElementById('btn-scrape');
  const text = document.getElementById('scrape-text');
  state.isScraping = false;
  btn.classList.remove('is-scraping');
  btn.disabled = false;
  text.textContent = 'Actualizar';
}

// --- Health Polling ---
async function pollHealth() {
  try {
    const response = await fetch('/health');
    const health = await response.json();

    if (health.is_scraping && !state.isScraping) {
      // Alguien más inició un scrape
      state.isScraping = true;
      document.getElementById('btn-scrape').classList.add('is-scraping');
      document.getElementById('scrape-text').textContent = 'Scrapeando...';
    } else if (!health.is_scraping && state.isScraping) {
      resetScrapeButton();
      loadData();
    }
  } catch {
    // Silenciar errores de polling
  }
}

// --- UI Helpers ---
function showEmptyState() {
  document.getElementById('empty-state').style.display = 'flex';
  document.getElementById('tier-table').style.display = 'none';
}

function hideEmptyState() {
  document.getElementById('empty-state').style.display = 'none';
  document.getElementById('tier-table').style.display = 'table';
}

function showToast(message) {
  const existing = document.querySelector('.scrape-toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'scrape-toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}
