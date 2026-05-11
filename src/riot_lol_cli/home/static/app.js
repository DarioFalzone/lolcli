/* ============================================================
   Home Hub — app.js (rediseño 2025)
   ============================================================
   • Polling cada 30s a /api/v1/home/status
   • Stats strip (online/total, offline, last update, uptime)
   • Tweaks: acento, densidad, layout grid/lista, partículas
   • Atajos: R = refresh, G = grid, L = list, 1–5 = abrir servicio
   ============================================================ */

(function () {
  'use strict';

  const POLL_INTERVAL_MS = 30_000;
  const STATUS_URL = '/api/v1/home/status';
  const LAUNCH_TIMEOUT_MS = 20_000;
  const LAUNCH_POLL_MS    = 1_000;

  // --- DOM refs ---
  const $body          = document.body;
  const $grid          = document.getElementById('services-grid');
  const $versionPill   = document.getElementById('version-pill');
  const $footerVersion = document.getElementById('footer-version');
  const $footerPort    = document.getElementById('footer-port');
  const $globalDot     = document.getElementById('global-status-dot');
  const $statusText    = document.getElementById('status-text');
  const $refreshBtn    = document.getElementById('refresh-btn');

  const $statOnline   = document.getElementById('stat-online');
  const $statTotal    = document.getElementById('stat-total');
  const $statOffline  = document.getElementById('stat-offline');
  const $statBarFill  = document.getElementById('stat-bar-fill');
  const $statLast     = document.getElementById('stat-last-update');
  const $statUptime   = document.getElementById('stat-uptime');

  const $viewGrid = document.getElementById('view-grid');
  const $viewList = document.getElementById('view-list');

  const $tweaksFab    = document.getElementById('tweaks-fab');
  const $tweaksPanel  = document.getElementById('tweaks-panel');
  const $tweaksClose  = document.getElementById('tweaks-close');
  const $tweakSegmentDensity = document.getElementById('tweak-density');
  const $tweakSegmentLayout  = document.getElementById('tweak-layout');
  const $tweakSwatches = document.getElementById('tweak-swatches');
  const $tweakParticles = document.getElementById('tweak-particles');

  // --- State ---
  let isFirstLoad = true;
  let lastServices = [];
  const launchingServices = new Set(); // service IDs currently being launched
  const sessionStart = Date.now();
  let uptimeTimer = null;

  // --- Tweaks (persisted via host postMessage) ---
  const tweaks = Object.assign({
    accent: 'gold',
    density: 'balanced',
    layout: 'grid',
    particles: true,
  }, window.__TWEAK_DEFAULTS || {});

  function applyTweaks() {
    $body.dataset.accentTheme = tweaks.accent;
    $body.dataset.density     = tweaks.density;
    $body.dataset.layout      = tweaks.layout;
    $body.dataset.particles   = tweaks.particles ? 'on' : 'off';

    // Reflect in panel UI
    setPressed($tweakSwatches, 'data-tweak-accent', tweaks.accent);
    setPressed($tweakSegmentDensity, 'data-tweak-density', tweaks.density);
    setPressed($tweakSegmentLayout,  'data-tweak-layout',  tweaks.layout);
    if ($tweakParticles) {
      $tweakParticles.setAttribute('aria-checked', tweaks.particles ? 'true' : 'false');
    }
    // Reflect in section view-toggle
    if ($viewGrid && $viewList) {
      $viewGrid.setAttribute('aria-pressed', tweaks.layout === 'grid' ? 'true' : 'false');
      $viewList.setAttribute('aria-pressed', tweaks.layout === 'list' ? 'true' : 'false');
    }
  }

  function setPressed(container, attr, value) {
    if (!container) return;
    container.querySelectorAll('[' + attr + ']').forEach((btn) => {
      btn.setAttribute('aria-pressed', btn.getAttribute(attr) === String(value) ? 'true' : 'false');
    });
  }

  function persistTweak(partial) {
    Object.assign(tweaks, partial);
    applyTweaks();
    try {
      window.parent.postMessage({ type: '__edit_mode_set_keys', edits: partial }, '*');
    } catch (_) { /* host may not be listening */ }
  }

  // --- Helpers ---

  function statusPillClass(status) {
    if (status === 'online')  return 'pill-success';
    if (status === 'offline') return 'pill-error';
    return 'pill-neutral';
  }

  function statusLabel(status) {
    if (status === 'online')  return 'ONLINE';
    if (status === 'offline') return 'OFFLINE';
    return 'UNKNOWN';
  }

  function dotClass(status) {
    if (status === 'online')  return 'online';
    if (status === 'offline') return 'offline';
    return 'unknown';
  }

  function escapeHtml(str) {
    return String(str ?? '').replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));
  }

  function fmtTime(date) {
    const h = String(date.getHours()).padStart(2, '0');
    const m = String(date.getMinutes()).padStart(2, '0');
    const s = String(date.getSeconds()).padStart(2, '0');
    return h + ':' + m + ':' + s;
  }

  function fmtUptime(ms) {
    const total = Math.floor(ms / 1000);
    const h = Math.floor(total / 3600);
    const m = Math.floor((total % 3600) / 60);
    const s = total % 60;
    if (h > 0) return String(h) + 'h ' + String(m).padStart(2, '0') + 'm';
    return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
  }

  const _OPEN_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>';

  async function fetchStatusSnapshot() {
    const resp = await fetch(STATUS_URL);
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    return resp.json();
  }

  // --- Empty / loading states ---

  function buildSkeletonCard(_, index) {
    const delay = 'animation-delay:' + (index * 0.08).toFixed(2) + 's';
    return '<article class="card service-card service-card--skeleton" style="' + delay + '" aria-hidden="true">'
      + '<div class="card-accent-line"></div>'
      + '<div class="card-top">'
      +   '<div class="skel skel-icon"></div>'
      +   '<div class="skel skel-pill"></div>'
      + '</div>'
      + '<div class="card-content">'
      +   '<div class="skel skel-name"></div>'
      +   '<div class="skel skel-desc"></div>'
      +   '<div class="skel skel-desc" style="width:65%"></div>'
      + '</div>'
      + '<div class="card-footer">'
      +   '<div class="skel skel-port"></div>'
      +   '<div class="skel skel-btn"></div>'
      + '</div>'
      + '</article>';
  }

  function renderGridSkeletons(count) {
    $grid.innerHTML = Array.from({ length: count }, buildSkeletonCard).join('');
  }

  function renderGridError() {
    $grid.innerHTML = '<div class="services-empty">'
      + '<svg class="services-empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
      +   '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>'
      + '</svg>'
      + '<p class="services-empty-title">Error al cargar servicios</p>'
      + '<p class="services-empty-desc">No se pudo conectar con el Hub. Verificá que el servidor esté corriendo.</p>'
      + '<button class="btn-retry" onclick="location.reload()">Reintentar</button>'
      + '</div>';
  }

  function renderGridEmpty() {
    $grid.innerHTML = '<div class="services-empty">'
      + '<svg class="services-empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
      +   '<circle cx="12" cy="12" r="10"/><line x1="8" y1="12" x2="16" y2="12"/>'
      + '</svg>'
      + '<p class="services-empty-title">Sin servicios configurados</p>'
      + '<p class="services-empty-desc">No hay subsistemas registrados en el Hub.</p>'
      + '</div>';
  }

  /** Build the "Abrir" / "Iniciando…" button for a service card. */
  function buildOpenButton(svc) {
    const url = 'http://localhost:' + svc.port + svc.ui_path;
    if (launchingServices.has(svc.id)) {
      return '<button class="btn-open btn-open--launching" disabled>⏳ Iniciando…</button>';
    }
    if (svc.status === 'online') {
      return '<a href="' + escapeHtml(url) + '" target="_blank" rel="noopener" class="btn-open">Abrir' + _OPEN_SVG + '</a>';
    }
    // offline / error → launch button
    return '<button class="btn-open btn-launch" data-svc-id="' + escapeHtml(svc.id) + '" data-svc-url="' + escapeHtml(url) + '">Abrir' + _OPEN_SVG + '</button>';
  }

  /**
   * Build a single service card HTML.
   * Mantiene contrato con el HTML existente:
   * .service-card[data-service-id], .card-status-dot, .service-status .pill
   */
  function renderServiceCard(svc, index) {
    const docsUrl = 'http://localhost:' + svc.port + '/docs';
    const delay = isFirstLoad ? 'animation-delay: ' + (0.1 + index * 0.06).toFixed(2) + 's;' : '';
    const accent = escapeHtml(svc.accent || 'gold');

    return ''
      + '<article class="card service-card" data-accent="' + accent + '" data-service-id="' + escapeHtml(svc.id) + '" data-shortcut="' + (index + 1) + '" style="' + delay + '">'
      +   '<div class="card-accent-line"></div>'
      +   '<div class="card-top">'
      +     '<div class="service-icon-wrap" aria-hidden="true">' + escapeHtml(svc.icon || '⚙') + '</div>'
      +     '<div class="service-status">'
      +       '<div class="card-status-dot ' + dotClass(svc.status) + '"></div>'
      +       '<span class="pill ' + statusPillClass(svc.status) + ' pill-sm">' + statusLabel(svc.status) + '</span>'
      +     '</div>'
      +   '</div>'
      +   '<div class="card-content">'
      +     '<h3 class="service-name">' + escapeHtml(svc.name) + '</h3>'
      +     '<p class="service-desc">' + escapeHtml(svc.description) + '</p>'
      +   '</div>'
      +   '<div class="card-footer">'
      +     '<span class="service-port">:' + escapeHtml(svc.port) + '</span>'
      +     '<div class="card-actions">'
      +       '<a href="' + docsUrl + '" target="_blank" rel="noopener" class="btn-docs-link" title="API Docs">'
      +         '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
      +           '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
      +           '<polyline points="14 2 14 8 20 8"/>'
      +         '</svg>'
      +         'Docs'
      +       '</a>'
      +       buildOpenButton(svc)
      +     '</div>'
      +   '</div>'
      + '</article>';
  }

  /**
   * Update global status indicator + stats strip.
   */
  function updateGlobalStatus(data) {
    const version = 'v' + data.version;
    if ($versionPill)   $versionPill.textContent   = version;
    if ($footerVersion) $footerVersion.textContent = version;

    // Global dot + text
    $globalDot.className = 'status-dot';
    if (data.online === data.total) {
      $globalDot.classList.add('status-dot--online');
      $statusText.textContent = data.online + '/' + data.total + ' online';
    } else if (data.online > 0) {
      $globalDot.classList.add('status-dot--partial');
      $statusText.textContent = data.online + '/' + data.total + ' online';
    } else {
      $globalDot.classList.add('status-dot--offline');
      $statusText.textContent = 'Todo offline';
    }

    // Stats strip
    if ($statOnline)  $statOnline.textContent  = data.online;
    if ($statTotal)   $statTotal.textContent   = data.total;
    if ($statOffline) $statOffline.textContent = data.offline;
    if ($statBarFill) {
      const pct = data.total > 0 ? (data.online / data.total) * 100 : 0;
      $statBarFill.style.width = pct + '%';
    }
    if ($statLast) {
      $statLast.textContent = fmtTime(new Date());
    }
  }

  /**
   * Fetch status and render/update cards.
   */
  async function fetchAndRender() {
    try {
      const data = await fetchStatusSnapshot();

      updateGlobalStatus(data);
      lastServices = data.services;

      if (isFirstLoad) {
        if (data.services.length === 0) {
          renderGridEmpty();
        } else {
          $grid.innerHTML = data.services.map(renderServiceCard).join('');
        }
        isFirstLoad = false;
      } else {
        // Update existing cards in place (status only, preserve launch buttons)
        data.services.forEach((svc) => {
          const card = $grid.querySelector('[data-service-id="' + svc.id + '"]');
          if (!card) return;
          const dot = card.querySelector('.card-status-dot');
          const pill = card.querySelector('.service-status .pill');
          if (dot)  dot.className  = 'card-status-dot ' + dotClass(svc.status);
          if (pill) {
            pill.className = 'pill ' + statusPillClass(svc.status) + ' pill-sm';
            pill.textContent = statusLabel(svc.status);
          }
          // Refresh button only if not currently launching
          if (!launchingServices.has(svc.id)) {
            refreshCardButton(svc.id);
          }
        });
      }
    } catch (err) {
      console.error('[Home Hub] Error fetching status:', err);
      $globalDot.className = 'status-dot status-dot--offline';
      $statusText.textContent = 'Error de conexión';
      if (isFirstLoad) {
        renderGridError();
        isFirstLoad = false;
      }
    }
  }

  // --- Launch service ---

  /** Replace the Abrir button in a card to reflect current launch state. */
  function refreshCardButton(svcId) {
    const card = $grid.querySelector('[data-service-id="' + svcId + '"]');
    if (!card) return;
    const actions = card.querySelector('.card-actions');
    if (!actions) return;
    const old = actions.querySelector('.btn-open, .btn-launch');
    if (!old) return;
    const svcDef = lastServices.find((s) => s.id === svcId);
    if (!svcDef) return;
    old.outerHTML = buildOpenButton(svcDef);
  }

  async function launchAndOpen(svcId, openUrl) {
    const pendingWindow = window.open('', '_blank');
    launchingServices.add(svcId);
    refreshCardButton(svcId);

    try {
      const resp = await fetch('/api/v1/home/launch/' + svcId, { method: 'POST' });
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      const data = await resp.json();
      if (data.status === 'already_online') {
        launchingServices.delete(svcId);
        refreshCardButton(svcId);
        if (pendingWindow && !pendingWindow.closed) {
          pendingWindow.location.replace(openUrl);
        } else {
          window.open(openUrl, '_blank', 'noopener');
        }
        return;
      }
    } catch (err) {
      console.error('[Home Hub] launch request failed:', err);
      launchingServices.delete(svcId);
      refreshCardButton(svcId);
      if (pendingWindow && !pendingWindow.closed) {
        pendingWindow.close();
      }
      return;
    }

    // Poll the Home Hub aggregate status to avoid cross-origin /health fetches.
    const deadline = Date.now() + LAUNCH_TIMEOUT_MS;

    const timer = setInterval(async () => {
      if (Date.now() > deadline) {
        clearInterval(timer);
        launchingServices.delete(svcId);
        refreshCardButton(svcId);
        console.warn('[Home Hub] launch timeout for', svcId);
        return;
      }
      try {
        const snapshot = await fetchStatusSnapshot();
        updateGlobalStatus(snapshot);
        lastServices = snapshot.services;

        const svcDef = snapshot.services.find((s) => s.id === svcId);
        if (svcDef && svcDef.status === 'online') {
          clearInterval(timer);
          launchingServices.delete(svcId);
          refreshCardButton(svcId);
          if (pendingWindow && !pendingWindow.closed) {
            pendingWindow.location.replace(openUrl);
          } else {
            window.open(openUrl, '_blank', 'noopener');
          }
          fetchAndRender(); // sync stats strip
        } else if (svcDef) {
          refreshCardButton(svcId);
        }
      } catch (_) { /* still starting */ }
    }, LAUNCH_POLL_MS);
  }

  // Delegated click handler for offline "Abrir" buttons.
  $grid.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-launch');
    if (!btn) return;
    const svcId = btn.dataset.svcId;
    if (!svcId || launchingServices.has(svcId)) return;
    launchAndOpen(svcId, btn.dataset.svcUrl);
  });

  // --- View toggle (grid/list) ---

  function setLayout(layout) {
    persistTweak({ layout: layout });
  }

  if ($viewGrid) $viewGrid.addEventListener('click', () => setLayout('grid'));
  if ($viewList) $viewList.addEventListener('click', () => setLayout('list'));

  // --- Refresh ---

  if ($refreshBtn) {
    $refreshBtn.addEventListener('click', () => {
      if ($refreshBtn.disabled) return;
      $refreshBtn.disabled = true;
      $refreshBtn.classList.add('is-refreshing');
      fetchAndRender().finally(() => {
        setTimeout(() => {
          $refreshBtn.disabled = false;
          $refreshBtn.classList.remove('is-refreshing');
        }, 600);
      });
    });
  }

  // --- Tweaks panel wiring ---

  function openTweaks()  { $body.dataset.tweaksOpen = 'true'; }
  function closeTweaks() {
    $body.dataset.tweaksOpen = 'false';
    try { window.parent.postMessage({ type: '__edit_mode_dismissed' }, '*'); } catch (_) {}
  }

  if ($tweaksFab)   $tweaksFab.addEventListener('click', () => {
    if ($body.dataset.tweaksOpen === 'true') closeTweaks(); else openTweaks();
  });
  if ($tweaksClose) $tweaksClose.addEventListener('click', closeTweaks);

  if ($tweakSwatches) {
    $tweakSwatches.querySelectorAll('[data-tweak-accent]').forEach((btn) => {
      btn.addEventListener('click', () => {
        persistTweak({ accent: btn.getAttribute('data-tweak-accent') });
      });
    });
  }
  if ($tweakSegmentDensity) {
    $tweakSegmentDensity.querySelectorAll('[data-tweak-density]').forEach((btn) => {
      btn.addEventListener('click', () => {
        persistTweak({ density: btn.getAttribute('data-tweak-density') });
      });
    });
  }
  if ($tweakSegmentLayout) {
    $tweakSegmentLayout.querySelectorAll('[data-tweak-layout]').forEach((btn) => {
      btn.addEventListener('click', () => {
        persistTweak({ layout: btn.getAttribute('data-tweak-layout') });
      });
    });
  }
  if ($tweakParticles) {
    $tweakParticles.addEventListener('click', () => {
      persistTweak({ particles: !tweaks.particles });
    });
  }

  // --- Host edit-mode protocol ---

  window.addEventListener('message', (e) => {
    const msg = e.data;
    if (!msg || typeof msg !== 'object') return;
    if (msg.type === '__activate_edit_mode') {
      $body.dataset.tweaksActive = 'true';
      openTweaks();
    } else if (msg.type === '__deactivate_edit_mode') {
      closeTweaks();
      $body.dataset.tweaksActive = 'false';
    }
  });
  // Announce availability so the host toolbar shows the toggle
  try {
    window.parent.postMessage({ type: '__edit_mode_available' }, '*');
  } catch (_) {}

  // --- Keyboard shortcuts ---

  document.addEventListener('keydown', (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const tag = (e.target && e.target.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA' || (e.target && e.target.isContentEditable)) return;

    const key = e.key.toLowerCase();
    if (key === 'r') {
      e.preventDefault();
      $refreshBtn && $refreshBtn.click();
    } else if (key === 'g') {
      e.preventDefault();
      setLayout('grid');
    } else if (key === 'l') {
      e.preventDefault();
      setLayout('list');
    } else if (/^[1-9]$/.test(key)) {
      const idx = parseInt(key, 10) - 1;
      const svc = lastServices[idx];
      if (svc) {
        e.preventDefault();
        const url = 'http://localhost:' + svc.port + svc.ui_path;
        window.open(url, '_blank', 'noopener');
      }
    } else if (key === '?' || (key === '/' && e.shiftKey)) {
      // future: open help overlay
    } else if (key === 'escape' && $body.dataset.tweaksOpen === 'true') {
      closeTweaks();
    }
  });

  // --- Uptime ticker ---
  function tickUptime() {
    if ($statUptime) $statUptime.textContent = fmtUptime(Date.now() - sessionStart);
  }
  tickUptime();
  uptimeTimer = setInterval(tickUptime, 1000);

  // --- Footer port ---
  if ($footerPort) $footerPort.textContent = location.port || '8080';

  // --- Init ---
  applyTweaks();
  renderGridSkeletons(5);   // show placeholders immediately, replaced on first fetch
  fetchAndRender();
  setInterval(fetchAndRender, POLL_INTERVAL_MS);
})();
