/* ============================================================
   Home Hub — app.js
   ============================================================
   Fetches service status from /api/v1/home/status and renders
   interactive service cards. Polls every 30s for live updates.
   ============================================================ */

(function () {
  'use strict';

  const POLL_INTERVAL_MS = 30_000;
  const STATUS_URL = '/api/v1/home/status';

  // --- DOM refs ---
  const $grid = document.getElementById('services-grid');
  const $versionPill = document.getElementById('version-pill');
  const $footerVersion = document.getElementById('footer-version');
  const $globalDot = document.getElementById('global-status-dot');
  const $statusText = document.getElementById('status-text');
  const $refreshBtn = document.getElementById('refresh-btn');

  // --- State ---
  let isFirstLoad = true;

  // --- Helpers ---

  function statusPillClass(status) {
    switch (status) {
      case 'online':  return 'pill-success';
      case 'offline': return 'pill-error';
      default:        return 'pill-neutral';
    }
  }

  function statusLabel(status) {
    switch (status) {
      case 'online':  return 'ONLINE';
      case 'offline': return 'OFFLINE';
      default:        return 'UNKNOWN';
    }
  }

  function dotClass(status) {
    switch (status) {
      case 'online':  return 'online';
      case 'offline': return 'offline';
      default:        return 'unknown';
    }
  }

  /**
   * Build a single service card HTML string.
   */
  function renderServiceCard(svc, index) {
    const url = `http://localhost:${svc.port}${svc.ui_path}`;
    const docsUrl = `http://localhost:${svc.port}/docs`;
    const delay = isFirstLoad ? `animation-delay: ${0.3 + index * 0.1}s;` : '';

    return `
      <div class="service-card" data-accent="${svc.accent}" data-service-id="${svc.id}" style="${delay}">
        <div class="card-accent-line"></div>
        <div class="card-top">
          <span class="service-icon">${svc.icon}</span>
          <div class="service-status">
            <div class="card-status-dot ${dotClass(svc.status)}"></div>
            <span class="pill ${statusPillClass(svc.status)} pill-sm">${statusLabel(svc.status)}</span>
          </div>
        </div>
        <div class="card-content">
          <h3 class="service-name">${svc.name}</h3>
          <p class="service-desc">${svc.description}</p>
        </div>
        <div class="card-footer">
          <span class="service-port">:${svc.port}</span>
          <div class="card-actions">
            <a href="${docsUrl}" target="_blank" rel="noopener" class="btn-docs-link" title="API Docs">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
              </svg>
              Docs
            </a>
            <a href="${url}" target="_blank" rel="noopener" class="btn-open">
              Abrir
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                <polyline points="15 3 21 3 21 9"/>
                <line x1="10" y1="14" x2="21" y2="3"/>
              </svg>
            </a>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Update global status indicator based on aggregate results.
   */
  function updateGlobalStatus(data) {
    // Version
    const version = `v${data.version}`;
    $versionPill.textContent = version;
    $footerVersion.textContent = version;

    // Global dot
    $globalDot.className = 'status-dot';
    if (data.online === data.total) {
      $globalDot.classList.add('status-dot--online');
      $statusText.textContent = `${data.online}/${data.total} online`;
    } else if (data.online > 0) {
      $globalDot.classList.add('status-dot--partial');
      $statusText.textContent = `${data.online}/${data.total} online`;
    } else {
      $globalDot.classList.add('status-dot--offline');
      $statusText.textContent = 'Todo offline';
    }
  }

  /**
   * Fetch status and render/update cards.
   */
  async function fetchAndRender() {
    try {
      const resp = await fetch(STATUS_URL);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();

      updateGlobalStatus(data);

      if (isFirstLoad) {
        // Full render on first load
        $grid.innerHTML = data.services.map(renderServiceCard).join('');
        isFirstLoad = false;
      } else {
        // Update existing cards in place (status only)
        data.services.forEach((svc) => {
          const card = $grid.querySelector(`[data-service-id="${svc.id}"]`);
          if (!card) return;

          const dot = card.querySelector('.card-status-dot');
          const pill = card.querySelector('.service-status .pill');

          if (dot) {
            dot.className = `card-status-dot ${dotClass(svc.status)}`;
          }
          if (pill) {
            pill.className = `pill ${statusPillClass(svc.status)} pill-sm`;
            pill.textContent = statusLabel(svc.status);
          }
        });
      }
    } catch (err) {
      console.error('[Home Hub] Error fetching status:', err);
      $globalDot.className = 'status-dot status-dot--offline';
      $statusText.textContent = 'Error de conexión';
    }
  }

  // --- Init ---

  // First load
  fetchAndRender();

  // Poll
  setInterval(fetchAndRender, POLL_INTERVAL_MS);

  // Manual refresh
  if ($refreshBtn) {
    $refreshBtn.addEventListener('click', () => {
      $refreshBtn.disabled = true;
      $refreshBtn.style.opacity = '0.5';
      fetchAndRender().finally(() => {
        setTimeout(() => {
          $refreshBtn.disabled = false;
          $refreshBtn.style.opacity = '1';
        }, 1000);
      });
    });
  }
})();
