// Splash Arts Viewer App - League of Legends
const MANIFEST_URL = document.currentScript.dataset.manifestUrl || '../data/splash-manifest.json';
const ITEMS_PER_PAGE = 12;

const app = {
  data: {
    champions: [],
    images: [],
    championImages: {}
  },
  
  state: {
    currentChampion: null,
    currentIndex: 0,
    allImages: [],
    searchQuery: '',
    selectedLetter: '',
    visibleCounts: {},
    uiHidden: false,
    familyFilter: '',
    favoritesOnly: false,
    favorites: new Set(),
    shuffleSeed: '',
    presenterTimer: null,
    presenterInterval: 3000,
    badgeFilter: '',
    colorFilter: '',
    sortOrder: 'default',
    compareSelection: new Set(),
    audioEnabled: false,
    audioVolume: 0.2
  },
  
  async init() {
    this.loadFavorites();
    await this.loadManifest();
    this.renderColorChips();
    this.renderAlphabet();
    this.renderChampionsList();
    this.renderMainContent();
    this.setupEventListeners();
    this.restoreStateFromHash();
    this.updateStats();
  },
  
  async loadManifest() {
    try {
      // 1) Priorizar manifest inline si existe (compatibilidad file://)
      const inline = window.__INLINE_MANIFEST__;
      if (inline && inline.champions && inline.images) {
        this.data.champions = inline.champions || [];
        this.data.images = inline.images || [];
        this.indexImages();
        return;
      }

      // 2) Si no hay inline, intentar fetch normal
      const resp = await fetch(MANIFEST_URL, { cache: 'no-store' });
      const data = await resp.json();
      this.data.champions = data.champions || [];
      this.data.images = data.images || [];
      this.indexImages();
    } catch (e) {
      // 3) Fallback final: si existe inline aunque el fetch falle, usarlo
      if (window.__INLINE_MANIFEST__ && window.__INLINE_MANIFEST__.champions) {
        const data = window.__INLINE_MANIFEST__;
        this.data.champions = data.champions || [];
        this.data.images = data.images || [];
        this.indexImages();
        return;
      }
      console.error('Error cargando manifest:', e);
      document.getElementById('main-content').innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">⚠</div>
          <div class="empty-title">Error al cargar</div>
          <div class="empty-desc">No se pudo cargar el manifest. Ejecutá: python src/riot_lol_cli/cli.py build-splash-manifest</div>
        </div>
      `;
    }
  },

  indexImages() {
    // Agrupar imágenes por campeón
    this.data.championImages = {};
    this.data.images.forEach(img => {
      if (!this.data.championImages[img.championId]) {
        this.data.championImages[img.championId] = [];
      }
      this.data.championImages[img.championId].push(img);
    });
    // Inicializar contadores de visibilidad
    this.state.visibleCounts = {};
    this.data.champions.forEach(c => {
      this.state.visibleCounts[c.id] = ITEMS_PER_PAGE;
    });
  },

  // ========= Favorites =========
  loadFavorites() {
    try {
      const raw = localStorage.getItem('splash_favorites');
      if (raw) this.state.favorites = new Set(JSON.parse(raw));
    } catch(e) {}
  },
  saveFavorites() {
    try {
      localStorage.setItem('splash_favorites', JSON.stringify(Array.from(this.state.favorites)));
    } catch(e) {}
  },
  keyFor(img) {
    return `${img.championId}::${img.file || img.relPath}`;
  },
  toggleFavorite(img, ev) {
    ev?.stopPropagation?.();
    const key = this.keyFor(img);
    if (this.state.favorites.has(key)) this.state.favorites.delete(key); else this.state.favorites.add(key);
    this.saveFavorites();
    // actualizar UI del botón
    if (ev && ev.currentTarget) {
      ev.currentTarget.classList.toggle('active');
      ev.currentTarget.innerText = ev.currentTarget.classList.contains('active') ? '★' : '☆';
    }
  },
  toggleFavoritesOnly() {
    this.state.favoritesOnly = !this.state.favoritesOnly;
    const btn = document.getElementById('favorites-toggle');
    if (btn) btn.textContent = `★ Favoritos: ${this.state.favoritesOnly ? 'on' : 'off'}`;
    this.renderMainContent();
    this.saveStateToHash();
  },

  // ========= Family filter =========
  setFamilyFilter(fam) {
    this.state.familyFilter = fam || '';
    this.renderMainContent();
    this.saveStateToHash();
  },
  matchesFamily(img) {
    if (!this.state.familyFilter) return true;
    const name = (img.skinName || '').toLowerCase();
    return name.includes(this.state.familyFilter.toLowerCase());
  },

  // ========= Shuffle with seed =========
  seededRandom(seed) {
    // xorshift32 simple
    let x = 0;
    for (let i=0;i<seed.length;i++) x = (x ^ seed.charCodeAt(i)) >>> 0;
    if (x === 0) x = 0x9e3779b9;
    return () => {
      x ^= x << 13; x ^= x >>> 17; x ^= x << 5; x >>>= 0;
      return (x & 0xffffffff) / 0x100000000;
    };
  },
  shuffleArraySeeded(arr, seed) {
    const rnd = this.seededRandom(seed);
    const a = arr.slice();
    for (let i=a.length-1;i>0;i--) {
      const j = Math.floor(rnd() * (i+1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  },
  shuffleNow() {
    if (!this.state.shuffleSeed) {
      this.state.shuffleSeed = Math.random().toString(36).slice(2,10);
    } else {
      // regenerate new seed
      this.state.shuffleSeed = Math.random().toString(36).slice(2,10);
    }
    this.renderMainContent();
    this.saveStateToHash();
  },

  // ========= Presenter mode =========
  togglePresenter() {
    if (this.state.presenterTimer) {
      clearInterval(this.state.presenterTimer);
      this.state.presenterTimer = null;
      const btn = document.getElementById('presenter-toggle');
      if (btn) btn.textContent = '▶ Reproducir';
    } else {
      const btn = document.getElementById('presenter-toggle');
      if (btn) btn.textContent = '⏸ Pausar';
      this.state.presenterTimer = setInterval(()=>{
        if (document.getElementById('filmstrip-modal').classList.contains('active')) {
          this.nextImage();
        }
      }, this.state.presenterInterval);
    }
  },
  setPresenterSpeed(ms) {
    const v = parseInt(ms,10) || 3000;
    this.state.presenterInterval = v;
    if (this.state.presenterTimer) {
      this.togglePresenter();
      this.togglePresenter();
    }
  },
  
  renderAlphabet() {
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
    const grid = document.getElementById('alphabet-grid');
    
    const champsByLetter = {};
    this.data.champions.forEach(c => {
      const first = c.name[0].toUpperCase();
      if (!champsByLetter[first]) champsByLetter[first] = [];
      champsByLetter[first].push(c);
    });
    
    grid.innerHTML = letters.map(l => {
      const hasChamps = champsByLetter[l] && champsByLetter[l].length > 0;
      return `<div class="alphabet-letter ${hasChamps ? '' : 'disabled'}" data-letter="${l}" onclick="app.filterByLetter('${l}')">${l}</div>`;
    }).join('');
  },
  
  filterByLetter(letter) {
    if (this.state.selectedLetter === letter) {
      this.state.selectedLetter = '';
      this.state.searchQuery = '';
    } else {
      this.state.selectedLetter = letter;
      this.state.searchQuery = '';
    }
    document.getElementById('search-input').value = this.state.searchQuery;
    this.renderChampionsList();
    this.renderMainContent();
    this.updateAlphabetUI();
    this.updateBreadcrumbs();
  },
  
  updateAlphabetUI() {
    document.querySelectorAll('.alphabet-letter').forEach(el => {
      el.classList.toggle('active', el.dataset.letter === this.state.selectedLetter);
    });
  },
  
  renderChampionsList() {
    const list = document.getElementById('champions-list');
    const filtered = this.getFilteredChampions();
    
    list.innerHTML = filtered.map(c => `
      <li class="champion-item" data-champion="${c.id}" onclick="app.scrollToChampion('${c.id}')">
        <div class="champion-avatar">${c.name[0]}</div>
        <div class="champion-info">
          <div class="champion-name">${c.name}</div>
          <div class="champion-count">${c.count} skins</div>
        </div>
      </li>
    `).join('');
    
    if (filtered.length === 0) {
      list.innerHTML = `
        <div class="empty-state" style="padding:40px 16px">
          <div class="empty-icon" style="font-size:32px">🔍</div>
          <div class="empty-desc">Sin resultados</div>
        </div>
      `;
    }
  },
  
  getFilteredChampions() {
    let filtered = this.data.champions;
    
    if (this.state.selectedLetter) {
      filtered = filtered.filter(c => c.name[0].toUpperCase() === this.state.selectedLetter);
    }
    
    if (this.state.searchQuery) {
      const q = this.state.searchQuery.toLowerCase();
      filtered = filtered.filter(c => c.name.toLowerCase().includes(q));
    }
    
    return filtered;
  },
  
  scrollToChampion(champId) {
    this.state.currentChampion = champId;
    const el = document.getElementById(`champ-${champId}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      // Abrir sección si está colapsada
      const header = el.querySelector('.section-header');
      if (header && header.classList.contains('collapsed')) {
        header.click();
      }
    }
    this.updateChampionListUI();
    this.saveStateToHash();
  },
  
  updateChampionListUI() {
    document.querySelectorAll('.champion-item').forEach(el => {
      el.classList.toggle('active', el.dataset.champion === this.state.currentChampion);
    });
  },
  
  renderMainContent() {
    const main = document.getElementById('main-content');
    const filtered = this.getFilteredChampions();
    
    if (filtered.length === 0) {
      main.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">🎨</div>
          <div class="empty-title">No hay resultados</div>
          <div class="empty-desc">Probá con otra búsqueda o letra</div>
        </div>
      `;
      return;
    }
    
    main.innerHTML = filtered.map(champ => this.renderChampionSection(champ)).join('');
  },
  
  renderChampionSection(champ) {
    let images = this.data.championImages[champ.id] || [];
    // aplicar filtros
    images = images.filter(img => this.matchesFamily(img) && this.matchesBadge(img) && this.matchesColor(img));
    if (this.state.favoritesOnly) {
      images = images.filter(img => this.state.favorites.has(this.keyFor(img)));
    }
    // ordenar cronológicamente si está activado
    if (this.state.sortOrder === 'chrono') {
      images = images.slice().sort((a,b) => (a.releaseYear || 9999) - (b.releaseYear || 9999));
    }
    // shuffle determinístico si hay seed
    if (this.state.shuffleSeed) {
      images = this.shuffleArraySeeded(images, this.state.shuffleSeed + ':' + champ.id);
    }
    const visible = this.state.visibleCounts[champ.id] || ITEMS_PER_PAGE;
    const visibleImages = images.slice(0, visible);
    const hasMore = visible < images.length;
    
    return `
      <div class="champion-section" id="champ-${champ.id}">
        <div class="section-header" onclick="app.toggleSection('${champ.id}')">
          <div class="section-title">
            <span>${champ.name}</span>
            <span class="section-count">${champ.count} skins</span>
          </div>
          <div class="section-toggle">▼</div>
        </div>
        <div class="section-content" id="content-${champ.id}">
          <div class="gallery-grid">
            ${visibleImages.map((img, idx) => this.renderSkinCard(img, champ, idx)).join('')}
          </div>
          ${hasMore ? `<button class="load-more-btn" onclick="app.loadMore('${champ.id}')">Cargar ${Math.min(ITEMS_PER_PAGE, images.length - visible)} más ↓</button>` : ''}
        </div>
      </div>
    `;
  },
  
  renderSkinCard(img, champ, idx) {
    const badges = (img.badges || []).map(b => `<span class="badge ${b}">${b}</span>`).join('');
    const isCompared = this.state.compareSelection.has(this.keyFor(img));
    return `
      <div class="skin-card" onclick="app.openFilmstrip('${champ.id}', ${idx})">
        <div class="skin-image-wrapper">
          <img class="skin-image" src="${img.relPath}" alt="${img.skinName}" loading="lazy">
          <input type="checkbox" class="compare-checkbox" ${isCompared ? 'checked' : ''} onclick="app.toggleCompare(${JSON.stringify(img).replace(/"/g,'&quot;')}, event)">
          <button class="fav-btn ${this.state.favorites.has(this.keyFor(img)) ? 'active' : ''}" onclick="app.toggleFavorite(${JSON.stringify(img).replace(/"/g,'&quot;')}, event)">${this.state.favorites.has(this.keyFor(img)) ? '★' : '☆'}</button>
        </div>
        <div class="skin-info">
          <div class="skin-name">${badges}${img.skinName}</div>
          <div class="skin-meta">${champ.name}${img.releaseYear ? ' • ' + img.releaseYear : ''}</div>
        </div>
      </div>
    `;
  },
  
  toggleSection(champId) {
    const header = document.querySelector(`#champ-${champId} .section-header`);
    const content = document.getElementById(`content-${champId}`);
    const toggle = header.querySelector('.section-toggle');
    
    const isCollapsed = content.classList.toggle('collapsed');
    toggle.classList.toggle('collapsed', isCollapsed);
    header.classList.toggle('collapsed', isCollapsed);
    
    if (isCollapsed) {
      content.style.maxHeight = '0';
    } else {
      content.style.maxHeight = content.scrollHeight + 'px';
    }
  },
  
  loadMore(champId) {
    this.state.visibleCounts[champId] = (this.state.visibleCounts[champId] || ITEMS_PER_PAGE) + ITEMS_PER_PAGE;
    const champ = this.data.champions.find(c => c.id === champId);
    if (champ) {
      const section = document.getElementById(`champ-${champId}`);
      section.outerHTML = this.renderChampionSection(champ);
    }
  },
  
  openFilmstrip(champId, idx) {
    this.state.currentChampion = champId;
    this.state.allImages = this.data.championImages[champId] || [];
    this.state.currentIndex = idx;
    
    document.getElementById('filmstrip-modal').classList.add('active');
    document.body.style.overflow = 'hidden';
    
    this.updateFilmstrip();
    this.renderThumbnails();
    this.saveStateToHash();
  },
  
  closeFilmstrip() {
    document.getElementById('filmstrip-modal').classList.remove('active');
    document.body.style.overflow = '';
  },
  
  updateFilmstrip() {
    const img = this.state.allImages[this.state.currentIndex];
    if (!img) return;
    
    const champ = this.data.champions.find(c => c.id === this.state.currentChampion);
    document.getElementById('filmstrip-title').textContent = `${champ?.name || ''} — ${img.skinName}`;
    document.getElementById('main-image').src = img.relPath;
    
    // Prefetch vecinos
    this.prefetchNeighbors();
    
    // Update thumbnails active state
    document.querySelectorAll('.thumbnail').forEach((th, i) => {
      th.classList.toggle('active', i === this.state.currentIndex);
    });
  },
  
  prefetchNeighbors() {
    const prev = this.state.currentIndex - 1;
    const next = this.state.currentIndex + 1;
    
    [prev, next].forEach(i => {
      if (i >= 0 && i < this.state.allImages.length) {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = this.state.allImages[i].relPath;
        document.head.appendChild(link);
      }
    });
  },
  
  renderThumbnails() {
    const track = document.getElementById('thumbnails-track');
    track.innerHTML = this.state.allImages.map((img, i) => `
      <div class="thumbnail ${i === this.state.currentIndex ? 'active' : ''}" onclick="app.goToImage(${i})">
        <img src="${img.relPath}" alt="${img.skinName}" loading="lazy">
      </div>
    `).join('');
  },
  
  prevImage() {
    if (this.state.currentIndex > 0) {
      this.state.currentIndex--;
      this.updateFilmstrip();
      this.saveStateToHash();
    }
  },
  
  nextImage() {
    if (this.state.currentIndex < this.state.allImages.length - 1) {
      this.state.currentIndex++;
      this.updateFilmstrip();
      this.saveStateToHash();
    }
  },
  
  goToImage(idx) {
    this.state.currentIndex = idx;
    this.updateFilmstrip();
    this.saveStateToHash();
  },
  
  toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  },
  
  toggleUI() {
    this.state.uiHidden = !this.state.uiHidden;
    document.body.classList.toggle('ui-hidden', this.state.uiHidden);
  },
  
  toggleHotkeys() {
    document.getElementById('hotkeys-overlay').classList.toggle('active');
  },
  
  setupEventListeners() {
    // Search input
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', (e) => {
      this.state.searchQuery = e.target.value;
      this.state.selectedLetter = '';
      this.renderChampionsList();
      this.renderMainContent();
      this.updateAlphabetUI();
      this.updateBreadcrumbs();
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      // Global shortcuts
      if (e.key === '?' || (e.key === '/' && e.shiftKey)) {
        e.preventDefault();
        this.toggleHotkeys();
      }
      
      if (e.key === 'Escape') {
        if (document.getElementById('hotkeys-overlay').classList.contains('active')) {
          this.toggleHotkeys();
        } else if (document.getElementById('filmstrip-modal').classList.contains('active')) {
          this.closeFilmstrip();
        }
      }
      
      // Filmstrip shortcuts
      if (document.getElementById('filmstrip-modal').classList.contains('active')) {
        if (e.key === 'ArrowLeft' || e.key === 'j' || e.key === 'J') {
          e.preventDefault();
          this.prevImage();
        }
        if (e.key === 'ArrowRight' || e.key === 'k' || e.key === 'K') {
          e.preventDefault();
          this.nextImage();
        }
        if (e.key === 'h' || e.key === 'H') {
          e.preventDefault();
          this.toggleUI();
        }
        if (e.key === 'f' || e.key === 'F') {
          e.preventDefault();
          this.toggleFullscreen();
        }
      }
    });
    
    // Hash change for back/forward
    window.addEventListener('hashchange', () => {
      this.restoreStateFromHash();
    });
  },
  
  saveStateToHash() {
    const params = new URLSearchParams();
    if (this.state.currentChampion) params.set('champ', this.state.currentChampion);
    if (this.state.searchQuery) params.set('q', this.state.searchQuery);
    if (this.state.selectedLetter) params.set('letter', this.state.selectedLetter);
    if (this.state.currentIndex > 0) params.set('idx', this.state.currentIndex);
    if (this.state.familyFilter) params.set('fam', this.state.familyFilter);
    if (this.state.favoritesOnly) params.set('fav', '1');
    if (this.state.shuffleSeed) params.set('seed', this.state.shuffleSeed);
    
    const hash = params.toString() ? `#${params.toString()}` : '';
    if (window.location.hash !== hash) {
      window.location.hash = hash;
    }
  },
  
  restoreStateFromHash() {
    const params = new URLSearchParams(window.location.hash.slice(1));
    
    if (params.has('q')) {
      this.state.searchQuery = params.get('q');
      document.getElementById('search-input').value = this.state.searchQuery;
    }
    
    if (params.has('letter')) {
      this.state.selectedLetter = params.get('letter');
      this.updateAlphabetUI();
    }
    if (params.has('fam')) {
      this.state.familyFilter = params.get('fam');
      const ff = document.getElementById('family-filter');
      if (ff) ff.value = this.state.familyFilter;
    }
    if (params.has('fav')) {
      this.state.favoritesOnly = params.get('fav') === '1';
      const btn = document.getElementById('favorites-toggle');
      if (btn) btn.textContent = `★ Favoritos: ${this.state.favoritesOnly ? 'on' : 'off'}`;
    }
    if (params.has('seed')) {
      this.state.shuffleSeed = params.get('seed');
    }
    
    if (params.has('champ')) {
      this.state.currentChampion = params.get('champ');
      this.updateChampionListUI();
      
      if (params.has('idx')) {
        const idx = parseInt(params.get('idx'), 10);
        this.openFilmstrip(this.state.currentChampion, idx);
      } else {
        this.scrollToChampion(this.state.currentChampion);
      }
    }
    
    this.updateBreadcrumbs();
    this.renderMainContent();
  },
  
  updateBreadcrumbs() {
    const current = document.getElementById('breadcrumb-current');
    const countSep = document.getElementById('breadcrumb-count-sep');
    const count = document.getElementById('breadcrumb-count');
    
    if (this.state.selectedLetter) {
      current.textContent = `Letra ${this.state.selectedLetter}`;
      const filtered = this.getFilteredChampions();
      count.textContent = `${filtered.length} campeones`;
      countSep.style.display = '';
      count.style.display = '';
    } else if (this.state.searchQuery) {
      current.textContent = `Búsqueda: "${this.state.searchQuery}"`;
      const filtered = this.getFilteredChampions();
      count.textContent = `${filtered.length} resultados`;
      countSep.style.display = '';
      count.style.display = '';
    } else if (this.state.currentChampion) {
      const champ = this.data.champions.find(c => c.id === this.state.currentChampion);
      if (champ) {
        current.textContent = champ.name;
        count.textContent = `${champ.count} skins`;
        countSep.style.display = '';
        count.style.display = '';
      }
    } else {
      current.textContent = '—';
      countSep.style.display = 'none';
      count.style.display = 'none';
    }
  },
  
  updateStats() {
    const badge = document.getElementById('stats-badge');
    badge.textContent = `${this.data.champions.length} Campeones • ${this.data.images.length} Skins`;
  },

  // ========= Phase 3: Color filter =========
  renderColorChips() {
    const container = document.getElementById('color-chips');
    if (!container) return;
    
    // Extraer colores únicos más comunes
    const colorCounts = {};
    this.data.images.forEach(img => {
      if (img.colors && img.colors.primary) {
        colorCounts[img.colors.primary] = (colorCounts[img.colors.primary] || 0) + 1;
      }
    });
    
    const topColors = Object.entries(colorCounts)
      .sort((a,b) => b[1] - a[1])
      .slice(0, 8)
      .map(([color]) => color);
    
    container.innerHTML = topColors.map(color => 
      `<div class="color-chip" style="background:${color}" data-color="${color}" onclick="app.setColorFilter('${color}')"></div>`
    ).join('');
  },

  setColorFilter(color) {
    this.state.colorFilter = this.state.colorFilter === color ? '' : color;
    document.querySelectorAll('.color-chip').forEach(el => {
      el.classList.toggle('active', el.dataset.color === this.state.colorFilter);
    });
    this.renderMainContent();
    this.saveStateToHash();
  },

  colorDistance(c1, c2) {
    const r1 = parseInt(c1.slice(1,3), 16);
    const g1 = parseInt(c1.slice(3,5), 16);
    const b1 = parseInt(c1.slice(5,7), 16);
    const r2 = parseInt(c2.slice(1,3), 16);
    const g2 = parseInt(c2.slice(3,5), 16);
    const b2 = parseInt(c2.slice(5,7), 16);
    return Math.sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2);
  },

  matchesColor(img) {
    if (!this.state.colorFilter) return true;
    if (!img.colors || !img.colors.primary) return false;
    return this.colorDistance(img.colors.primary, this.state.colorFilter) < 80;
  },

  // ========= Phase 3: Badge filter =========
  setBadgeFilter(badge) {
    this.state.badgeFilter = badge || '';
    this.renderMainContent();
    this.saveStateToHash();
  },

  matchesBadge(img) {
    if (!this.state.badgeFilter) return true;
    return img.badges && img.badges.includes(this.state.badgeFilter);
  },

  // ========= Phase 3: Sort order =========
  setSortOrder(order) {
    this.state.sortOrder = order || 'default';
    this.renderMainContent();
    this.saveStateToHash();
  },

  // ========= Phase 3: Comparator =========
  toggleCompare(img, ev) {
    ev?.stopPropagation?.();
    const key = this.keyFor(img);
    if (this.state.compareSelection.has(key)) {
      this.state.compareSelection.delete(key);
    } else {
      if (this.state.compareSelection.size >= 4) {
        alert('Máximo 4 skins para comparar');
        return;
      }
      this.state.compareSelection.add(key);
    }
    this.updateCompareButton();
    if (ev && ev.currentTarget) {
      ev.currentTarget.checked = this.state.compareSelection.has(key);
    }
  },

  updateCompareButton() {
    const btn = document.getElementById('compare-btn');
    const count = this.state.compareSelection.size;
    if (count > 0) {
      btn.style.display = '';
      btn.textContent = `⚖ Comparar (${count})`;
    } else {
      btn.style.display = 'none';
    }
  },

  openComparator() {
    if (this.state.compareSelection.size < 2) {
      alert('Seleccioná al menos 2 skins para comparar');
      return;
    }
    
    const modal = document.getElementById('comparator-modal');
    const grid = document.getElementById('comparator-grid');
    
    const selected = [];
    this.data.images.forEach(img => {
      if (this.state.compareSelection.has(this.keyFor(img))) {
        selected.push(img);
      }
    });
    
    grid.innerHTML = selected.map(img => {
      const champ = this.data.champions.find(c => c.id === img.championId);
      return `
        <div class="comparator-item">
          <img src="${img.relPath}" alt="${img.skinName}">
          <div class="comparator-item-title">${champ?.name} — ${img.skinName}</div>
        </div>
      `;
    }).join('');
    
    modal.classList.add('active');
  },

  closeComparator() {
    document.getElementById('comparator-modal').classList.remove('active');
  },

  // ========= Phase 3: Audio =========
  toggleAudio() {
    this.state.audioEnabled = !this.state.audioEnabled;
    const btn = document.getElementById('audio-toggle');
    if (btn) btn.textContent = this.state.audioEnabled ? '🔊 Audio' : '🔇 Audio';
    // Placeholder: implementar audio real con tracks
    if (this.state.audioEnabled) {
      console.log('Audio ambiente activado (placeholder)');
    } else {
      console.log('Audio ambiente desactivado');
    }
  }
};

// Init app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => app.init());
} else {
  app.init();
}
