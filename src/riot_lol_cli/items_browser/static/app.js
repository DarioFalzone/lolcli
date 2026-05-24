// Items Browser — vanilla SPA, filters by group + search + lang toggle
const GROUP_LABELS = {
  starter: "Starter",
  boots: "Botas",
  components: "Componentes",
  legendary: "Legendarios",
  consumables: "Consumibles",
  trinkets: "Trinkets",
  jungle_specific: "Jungla",
  deprecated: "Obsoletos",
};

const state = {
  items: [],
  groups: {},
  currentGroup: "all",
  searchQuery: "",
  showDeprecated: false,
  lang: "en",
  health: null,
};

const $ = (sel) => document.querySelector(sel);

async function fetchJson(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url} -> ${r.status}`);
  return r.json();
}

async function loadAll() {
  const [health, all, groups] = await Promise.all([
    fetchJson("/health"),
    fetchJson("/api/v1/items/all?include_deprecated=true"),
    fetchJson("/api/v1/items/groups"),
  ]);
  state.health = health;
  state.items = all.items;
  state.groups = groups.groups;
}

function init() {
  loadAll().then(() => {
    bindControls();
    renderTabs();
    renderHero();
    render();
  }).catch((err) => {
    $("#items-grid").innerHTML = `<div class="loader">Error: ${err.message}<br>Tip: ejecuta <code>python scripts/update_items_database.py</code> para regenerar la database.</div>`;
  });
}

function renderHero() {
  if (!state.health) return;
  $("[data-bind='version']").textContent = `DDragon v${state.health.version}`;
}

function bindControls() {
  $("#search-input").addEventListener("input", (e) => {
    state.searchQuery = e.target.value.trim().toLowerCase();
    render();
  });

  $("#show-deprecated").addEventListener("change", (e) => {
    state.showDeprecated = e.target.checked;
    renderTabs();
    render();
  });

  document.querySelectorAll(".lang-toggle button").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.lang = btn.dataset.lang;
      document.querySelectorAll(".lang-toggle button").forEach((b) => b.classList.toggle("active", b === btn));
      render();
    });
  });
}

function renderTabs() {
  const container = $("#group-tabs");
  container.innerHTML = "";

  const allTab = makeTab("all", "Todos", state.items.filter((i) => state.showDeprecated || !i.deprecated).length);
  container.appendChild(allTab);

  for (const [key, ids] of Object.entries(state.groups)) {
    if (key === "deprecated" && !state.showDeprecated) continue;
    if (ids.length === 0) continue;
    container.appendChild(makeTab(key, GROUP_LABELS[key] || key, ids.length));
  }
}

function makeTab(group, label, count) {
  const btn = document.createElement("button");
  btn.className = "tab group-tab";
  if (group === state.currentGroup) btn.classList.add("active");
  btn.innerHTML = `${label} <span class="badge">${count}</span>`;
  btn.addEventListener("click", () => {
    state.currentGroup = group;
    renderTabs();
    render();
  });
  return btn;
}

function filteredItems() {
  let items = state.items;

  if (!state.showDeprecated) items = items.filter((i) => !i.deprecated);

  if (state.currentGroup !== "all") {
    const ids = new Set(state.groups[state.currentGroup] || []);
    items = items.filter((i) => ids.has(i.id));
  }

  if (state.searchQuery) {
    const q = state.searchQuery;
    items = items.filter((i) => {
      const en = (i.name_en || "").toLowerCase();
      const es = (i.name_es || "").toLowerCase();
      return en.includes(q) || es.includes(q);
    });
  }

  return items;
}

function render() {
  const items = filteredItems();
  const grid = $("#items-grid");
  grid.innerHTML = "";

  $("[data-bind='counts']").textContent = `${items.length} items mostrados de ${state.items.length} totales`;

  if (items.length === 0) {
    grid.innerHTML = `<div class="state-block loader">Sin resultados para "${state.searchQuery || state.currentGroup}".</div>`;
    return;
  }

  for (const item of items.slice(0, 600)) {
    grid.appendChild(buildCard(item));
  }
}

function buildCard(item) {
  const card = document.createElement("div");
  card.className = "item-card";
  if (item.deprecated) card.classList.add("deprecated");
  card.title = `${item.name_en} (#${item.id})`;
  card.addEventListener("click", () => openModal(item));

  const wrap = document.createElement("div");
  wrap.className = "item-img";
  const img = document.createElement("img");
  img.src = `/items/${item.id}.png`;
  img.alt = item.name_en;
  img.loading = "lazy";
  img.onerror = () => { wrap.innerHTML = `<span style="font-size:0.65rem;color:var(--text-muted);display:flex;align-items:center;justify-content:center;height:100%;">#${item.id}</span>`; };
  wrap.appendChild(img);
  card.appendChild(wrap);

  const name = document.createElement("div");
  name.className = "item-name";
  name.textContent = state.lang === "es" ? item.name_es : item.name_en;
  card.appendChild(name);

  if (!item.deprecated && item.gold_total) {
    const gold = document.createElement("div");
    gold.className = "item-gold";
    gold.textContent = item.gold_total;
    card.appendChild(gold);
  }

  const id = document.createElement("div");
  id.className = "item-id";
  id.textContent = `#${item.id}`;
  card.appendChild(id);

  return card;
}

function openModal(item) {
  const modal = $("#item-modal");
  const content = $("#modal-content");
  content.innerHTML = "";

  const close = document.createElement("button");
  close.className = "modal-close";
  close.textContent = "x";
  close.addEventListener("click", closeModal);
  content.appendChild(close);

  if (item.deprecated) {
    const banner = document.createElement("div");
    banner.className = "modal-deprecated-banner";
    banner.textContent = "OBSOLETO — este item no existe en la version actual de Data Dragon. Probable removido del juego.";
    content.appendChild(banner);
  }

  const header = document.createElement("div");
  header.className = "modal-header";
  const img = document.createElement("img");
  img.src = `/items/${item.id}.png`;
  img.alt = item.name_en;
  img.onerror = () => { img.style.display = "none"; };
  header.appendChild(img);
  const names = document.createElement("div");
  names.className = "modal-names";
  names.innerHTML = `<span class="modal-name-en">${item.name_en}</span><span class="modal-name-es">${item.name_es}</span>`;
  header.appendChild(names);
  content.appendChild(header);

  const meta = document.createElement("div");
  meta.className = "modal-meta";
  if (item.gold_total) meta.innerHTML += `<span><b>Gold:</b>${item.gold_total} (sell ${item.gold_sell || 0})</span>`;
  meta.innerHTML += `<span><b>Depth:</b>${item.depth}</span>`;
  meta.innerHTML += `<span><b>Purchasable:</b>${item.purchasable ? "yes" : "no"}</span>`;
  meta.innerHTML += `<span><b>Maps:</b>${(item.maps || []).join(", ") || "—"}</span>`;
  content.appendChild(meta);

  if (item.tags && item.tags.length) {
    const tags = document.createElement("div");
    tags.className = "modal-tags";
    item.tags.forEach((t) => {
      const span = document.createElement("span");
      span.className = "tag";
      span.textContent = t;
      tags.appendChild(span);
    });
    content.appendChild(tags);
  }

  if (item.stats && Object.keys(item.stats).length) {
    const stats = document.createElement("div");
    stats.className = "modal-stats";
    for (const [k, v] of Object.entries(item.stats)) {
      const row = document.createElement("div");
      row.className = "stat-row";
      row.innerHTML = `<b>${humanStat(k)}:</b> ${v}`;
      stats.appendChild(row);
    }
    content.appendChild(stats);
  }

  if (item.plaintext_en) {
    const sec = document.createElement("div");
    sec.className = "modal-section";
    sec.innerHTML = `<h3>EN</h3><p>${item.plaintext_en}</p>`;
    content.appendChild(sec);
  }
  if (item.plaintext_es) {
    const sec = document.createElement("div");
    sec.className = "modal-section";
    sec.innerHTML = `<h3>ES</h3><p>${item.plaintext_es}</p>`;
    content.appendChild(sec);
  }

  modal.classList.add("active");
}

function closeModal() {
  $("#item-modal").classList.remove("active");
}

document.addEventListener("click", (e) => {
  if (e.target.matches("[data-close]")) closeModal();
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});

function humanStat(key) {
  return key
    .replace(/^Flat/, "")
    .replace(/^Percent/, "%")
    .replace(/Mod$/, "")
    .replace(/Pool$/, "")
    .replace(/HP/, "HP")
    .replace(/MP/, "MP")
    .replace(/PhysicalDamage/, "AD")
    .replace(/MagicDamage/, "AP")
    .replace(/MovementSpeed/, "MS")
    .replace(/AttackSpeed/, "AS")
    .replace(/CritChance/, "Crit")
    .replace(/SpellBlock/, "MR")
    .replace(/Armor/, "Armor")
    .replace(/LifeSteal/, "LS");
}

init();
