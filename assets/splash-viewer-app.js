// Splash Arts Viewer App - League of Legends
const MANIFEST_URL = document.currentScript.dataset.manifestUrl || '../data/splash-manifest.json';
const ITEMS_PER_PAGE = 12;
const FAMILY_FILTERS = [
  'Pandemonium',
  'Demoncursed',
  'Maleficio Demoniaco',
  'Flora Fatalis',
  'Petricite',
  'Firecracker',
  'Winter Wonder',
  'Winterblessed',
  'Petals of Spring',
  'Sunken Shadows',
  'Warhound',
  'Battle Academia',
  'PROJECT',
  'Star Guardian',
  'K/DA',
  'Spirit Blossom'
];

const app = {
  data: {
    champions: [],
    images: [],
    championImages: {},
    meta: {}
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
    this.renderFamilyOptions();
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
        this.data.meta = inline || {};
        this.data.champions = inline.champions || [];
        this.data.images = inline.images || [];
        this.indexImages();
        return;
      }

      // 2) Si no hay inline, intentar fetch normal
      const resp = await fetch(MANIFEST_URL, { cache: 'no-store' });
      const data = await resp.json();
      this.data.meta = data || {};
      this.data.champions = data.champions || [];
      this.data.images = data.images || [];
      this.indexImages();
    } catch (e) {
      // 3) Fallback final: si existe inline aunque el fetch falle, usarlo
      if (window.__INLINE_MANIFEST__ && window.__INLINE_MANIFEST__.champions) {
        const data = window.__INLINE_MANIFEST__;
        this.data.meta = data || {};
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
    return this.imageSearchText(img).includes(this.normalizeText(this.state.familyFilter));
  },

  renderFamilyOptions() {
    const select = document.getElementById('family-filter');
    if (!select) return;

    const presentFamilies = FAMILY_FILTERS
      .filter(family => this.data.images.some(img => this.imageSearchText(img).includes(this.normalizeText(family))))
      .sort((a, b) => a.localeCompare(b, 'es', { sensitivity: 'base' }));

    select.innerHTML = [
      '<option value="">Familias: Todas</option>',
      ...presentFamilies.map(family => `<option value="${family}">${family}</option>`)
    ].join('');
    select.value = this.state.familyFilter || '';
  },

  // ========= Shuffle with seed =========
  seededRandom(seed) {
    // xorshift32 simple
    let x = 0;
    for (let i=0;i<seed.length;i++) x = (x ^ seed.charCodeAt(i)) >>> 0;
    if (x === 0) x = 0x9e3779b9;
    return () => {
      x ^= x << 13; x ^= x >>> 17; x ^= x << 5; x >>>= 0;
      return x / 0x100000000;
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

  normalizeText(value) {
    return String(value || '')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase();
  },

  championSearchText(champ) {
    return this.normalizeText([champ.id, champ.name, champ.nameEn].filter(Boolean).join(' '));
  },

  imageSearchText(img) {
    return this.normalizeText([img.skinName, img.skinNameEn, img.file].filter(Boolean).join(' '));
  },

  championMatchesQuery(champ, query) {
    return this.championSearchText(champ).includes(query);
  },

  imageMatchesQuery(img, query) {
    return this.imageSearchText(img).includes(query);
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
    this.saveStateToHash();
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
          <div class="champion-count">${this.getDisplayImagesForChampion(c).length} skins</div>
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
    const sortByName = (a, b) => (a.name || a.id).localeCompare(b.name || b.id, 'es', { sensitivity: 'base' });
    let filtered = this.data.champions;
    
    if (this.state.selectedLetter) {
      filtered = filtered.filter(c => c.name[0].toUpperCase() === this.state.selectedLetter);
    }
    
    if (this.state.searchQuery) {
      const q = this.normalizeText(this.state.searchQuery);
      filtered = filtered.filter(c => {
        if (this.championMatchesQuery(c, q)) return true;
        return (this.data.championImages[c.id] || []).some(img => this.imageMatchesQuery(img, q));
      });
    }

    filtered = filtered.filter(c => this.getDisplayImagesForChampion(c).length > 0);
    
    return filtered.slice().sort(sortByName);
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

  getDisplayImagesForChampion(champ) {
    const query = this.normalizeText(this.state.searchQuery);
    const championMatchesSearch = query ? this.championMatchesQuery(champ, query) : true;
    let images = this.data.championImages[champ.id] || [];

    images = images.filter(img => this.matchesFamily(img) && this.matchesBadge(img) && this.matchesColor(img));

    if (query && !championMatchesSearch) {
      images = images.filter(img => this.imageMatchesQuery(img, query));
    }

    if (this.state.favoritesOnly) {
      images = images.filter(img => this.state.favorites.has(this.keyFor(img)));
    }

    const bySkinNum = (a, b) => {
      const aNum = Number.isFinite(a.skinNum) ? a.skinNum : 999999;
      const bNum = Number.isFinite(b.skinNum) ? b.skinNum : 999999;
      if (aNum !== bNum) return aNum - bNum;
      return (a.skinName || a.file || '').localeCompare(b.skinName || b.file || '', 'es', { sensitivity: 'base' });
    };

    if (this.state.sortOrder === 'chrono') {
      images = images.slice().sort((a, b) => {
        const aYear = Number.isFinite(a.releaseYear) ? a.releaseYear : 999999;
        const bYear = Number.isFinite(b.releaseYear) ? b.releaseYear : 999999;
        if (aYear !== bYear) return aYear - bYear;
        return bySkinNum(a, b);
      });
    } else {
      images = images.slice().sort(bySkinNum);
    }

    if (this.state.shuffleSeed) {
      images = this.shuffleArraySeeded(images, this.state.shuffleSeed + ':' + champ.id);
    }

    return images;
  },

  renderChampionSection(champ) {
    const images = this.getDisplayImagesForChampion(champ);
    const visible = this.state.visibleCounts[champ.id] || ITEMS_PER_PAGE;
    const visibleImages = images.slice(0, visible);
    const hasMore = visible < images.length;
    
    return `
      <div class="champion-section" id="champ-${champ.id}">
        <div class="section-header" onclick="app.toggleSection('${champ.id}')">
          <div class="section-title">
            <span>${champ.name}</span>
            <span class="section-count">${images.length} skins</span>
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
    const champ = this.data.champions.find(c => c.id === champId);
    this.state.allImages = champ ? this.getDisplayImagesForChampion(champ) : [];
    this.state.currentIndex = Math.max(0, Math.min(idx, this.state.allImages.length - 1));
    
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
      this.saveStateToHash();
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
    if (this.state.badgeFilter) params.set('badge', this.state.badgeFilter);
    if (this.state.colorFilter) params.set('color', this.state.colorFilter);
    if (this.state.sortOrder !== 'default') params.set('sort', this.state.sortOrder);
    if (this.state.favoritesOnly) params.set('fav', '1');
    if (this.state.shuffleSeed) params.set('seed', this.state.shuffleSeed);
    
    const hash = params.toString() ? `#${params.toString()}` : '';
    if (window.location.hash !== hash) {
      window.location.hash = hash;
    }
  },
  
  restoreStateFromHash() {
    const params = new URLSearchParams(window.location.hash.slice(1));

    this.state.searchQuery = params.get('q') || '';
    this.state.selectedLetter = params.get('letter') || '';
    this.state.familyFilter = params.get('fam') || '';
    this.state.badgeFilter = params.get('badge') || '';
    this.state.colorFilter = params.get('color') || '';
    this.state.sortOrder = params.get('sort') || 'default';
    this.state.favoritesOnly = params.get('fav') === '1';
    this.state.shuffleSeed = params.get('seed') || '';
    this.state.currentChampion = params.get('champ') || null;

    const searchInput = document.getElementById('search-input');
    if (searchInput) searchInput.value = this.state.searchQuery;

    const familyFilter = document.getElementById('family-filter');
    if (familyFilter) familyFilter.value = this.state.familyFilter;

    const badgeFilter = document.getElementById('badge-filter');
    if (badgeFilter) badgeFilter.value = this.state.badgeFilter;

    const sortOrder = document.getElementById('sort-order');
    if (sortOrder) sortOrder.value = this.state.sortOrder;

    const favoritesBtn = document.getElementById('favorites-toggle');
    if (favoritesBtn) favoritesBtn.textContent = `★ Favoritos: ${this.state.favoritesOnly ? 'on' : 'off'}`;

    document.querySelectorAll('.color-chip').forEach(el => {
      el.classList.toggle('active', el.dataset.color === this.state.colorFilter);
    });

    this.renderChampionsList();
    this.renderMainContent();
    this.updateAlphabetUI();
    this.updateChampionListUI();
    this.updateBreadcrumbs();

    if (this.state.currentChampion) {
      if (params.has('idx')) {
        const idx = parseInt(params.get('idx'), 10);
        this.openFilmstrip(this.state.currentChampion, Number.isFinite(idx) ? idx : 0);
      } else {
        this.scrollToChampion(this.state.currentChampion);
      }
    }
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
  
  formatManifestDate(value) {
    if (!value) return 'N/D';

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;

    return date.toLocaleString('es-AR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  },

  updateStats() {
    const badge = document.getElementById('stats-badge');
    if (badge) {
      badge.textContent = `${this.data.champions.length} Campeones • ${this.data.images.length} Skins`;
    }

    const sourceBadge = document.getElementById('asset-source-badge');
    if (sourceBadge) {
      const patch = this.data.meta.ddragonVersion || 'N/D';
      const importedAt = this.formatManifestDate(this.data.meta.assetsImportedAt || this.data.meta.generatedAt);
      sourceBadge.textContent = `DDragon ${patch} • Importado ${importedAt}`;
    }
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
