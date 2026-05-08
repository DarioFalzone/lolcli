// Jungle Meta SPA — hash routed, vanilla JS
const DDRAGON_VERSION = "16.9.1";
const TIER_ORDER = ["S", "A", "B", "C"];
const $app = document.getElementById("app");

const state = {
  data: null,
  categories: null,
  activeTier: "ALL",
};

const championIcon = (id) =>
  `https://ddragon.leagueoflegends.com/cdn/${DDRAGON_VERSION}/img/champion/${id}.png`;

const championSplash = (id) =>
  `https://ddragon.leagueoflegends.com/cdn/img/champion/splash/${id}_0.jpg`;

const itemIcon = (id) => `/items/${id}.png`;

const fmtPercent = (n) => (typeof n === "number" ? `${n.toFixed(1)}%` : "—");

const fmtDate = (iso) => {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return d.toLocaleString("es-AR", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
};

async function fetchJson(url) {
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`${url} -> ${resp.status}`);
  return resp.json();
}

async function loadAll() {
  if (state.data && state.categories) return;
  const [data, categories] = await Promise.all([
    fetchJson("/api/v1/jungle/tier-list"),
    fetchJson("/api/v1/jungle/categories"),
  ]);
  state.data = data;
  state.categories = categories;
}

// ============== ROUTER ==============
function parseRoute() {
  const hash = window.location.hash || "#overview";
  if (hash.startsWith("#champion/")) {
    return { name: "champion", id: decodeURIComponent(hash.slice("#champion/".length)) };
  }
  return { name: "overview" };
}

async function render() {
  const route = parseRoute();
  try {
    await loadAll();
  } catch (err) {
    $app.innerHTML = `<div class="loader">Error cargando datos: ${err.message}</div>`;
    return;
  }
  if (route.name === "champion") {
    renderChampionDetail(route.id);
  } else {
    renderOverview();
  }
  window.scrollTo({ top: 0, behavior: "instant" });
}

window.addEventListener("hashchange", render);
window.addEventListener("DOMContentLoaded", render);

// ============== OVERVIEW ==============
function renderOverview() {
  const tpl = document.getElementById("tpl-overview");
  const node = tpl.content.cloneNode(true);

  node.querySelector("[data-bind='patch']").textContent = state.data.patch;
  node.querySelector("[data-bind='date_updated']").textContent = fmtDate(state.data.date_updated);

  // Sidebar categories
  for (const key of ["overpowered", "low_elo_picks", "bans"]) {
    const container = node.querySelector(`[data-bind='${key}']`);
    const list = state.categories[key] || [];
    container.append(...list.map(buildCategoryThumb));
  }

  // Tier rows
  const tierRows = node.querySelector("[data-bind='tier_rows']");
  tierRows.append(...buildTierRows(state.activeTier));

  // Tier tabs
  const tabs = node.querySelectorAll(".tier-tab");
  tabs.forEach((btn) => {
    if (btn.dataset.tier === state.activeTier) btn.classList.add("active");
    else btn.classList.remove("active");
    btn.addEventListener("click", () => {
      state.activeTier = btn.dataset.tier;
      renderOverview();
    });
  });

  $app.innerHTML = "";
  $app.appendChild(node);
}

function buildCategoryThumb(champ) {
  const a = document.createElement("a");
  a.className = "cat-champ";
  a.href = `#champion/${encodeURIComponent(champ.id)}`;
  a.title = `${champ.display_name} — ${champ.tier} tier`;
  const img = document.createElement("img");
  img.src = championIcon(champ.id);
  img.alt = champ.display_name;
  img.onerror = () => { img.style.display = "none"; };
  a.appendChild(img);
  return a;
}

function buildTierRows(activeTier) {
  const champs = state.data.jungle_champions;
  const tiersToShow = activeTier === "ALL" ? TIER_ORDER : [activeTier];

  return tiersToShow.map((tier) => {
    const tierChamps = champs.filter((c) => c.tier === tier);
    const row = document.createElement("div");
    row.className = `tier-row tier-row--${tier.toLowerCase()}`;

    const label = document.createElement("div");
    label.className = "tier-label";
    label.textContent = tier;
    row.appendChild(label);

    const cards = document.createElement("div");
    cards.className = "tier-row-cards";
    cards.append(...tierChamps.map(buildExpandedCard));
    row.appendChild(cards);

    return row;
  });
}

function buildExpandedCard(champ) {
  const a = document.createElement("a");
  a.className = "champ-card";
  a.href = `#champion/${encodeURIComponent(champ.id)}`;

  const img = document.createElement("img");
  img.src = championIcon(champ.id);
  img.alt = champ.display_name;
  img.onerror = () => { img.style.opacity = "0.3"; };
  a.appendChild(img);

  const name = document.createElement("div");
  name.className = "champ-name";
  name.textContent = champ.display_name;
  a.appendChild(name);

  const stats = document.createElement("div");
  stats.className = "champ-stats";
  stats.innerHTML = `WR <span>${champ.winrate}%</span> · PR <span>${champ.pickrate}%</span>`;
  a.appendChild(stats);

  return a;
}

// ============== CHAMPION DETAIL ==============
function renderChampionDetail(championId) {
  const champ = state.data.jungle_champions.find((c) => c.id.toLowerCase() === championId.toLowerCase());
  if (!champ) {
    $app.innerHTML = `<div class="loader">Champion '${championId}' not found. <a href="#overview">← back</a></div>`;
    return;
  }

  const tpl = document.getElementById("tpl-champion-detail");
  const node = tpl.content.cloneNode(true);

  node.querySelector("[data-bind='patch']").textContent = state.data.patch;
  node.querySelector("[data-bind='display_name']").textContent = champ.display_name;
  node.querySelector("[data-bind='reason_text']").textContent = champ.reason_text;
  node.querySelector("[data-bind='winrate']").textContent = fmtPercent(champ.winrate);
  node.querySelector("[data-bind='pickrate']").textContent = fmtPercent(champ.pickrate);
  node.querySelector("[data-bind='banrate']").textContent = fmtPercent(champ.banrate);
  node.querySelector("[data-bind='playstyle']").textContent = champ.playstyle;

  // Tier badge
  const tierBadge = node.querySelector("[data-bind='tier_badge']");
  tierBadge.textContent = champ.tier;
  tierBadge.classList.add(`tier-${champ.tier.toLowerCase()}`);

  // Splash bg
  const bg = node.querySelector("[data-bind='splash_bg']");
  bg.style.backgroundImage = `url('${championSplash(champ.id)}')`;

  // Portrait
  const portrait = node.querySelector("[data-bind='portrait_src']");
  portrait.src = championIcon(champ.id);
  portrait.alt = champ.display_name;

  // Rune
  const rune = champ.core_rune || {};
  node.querySelector("[data-bind='rune_name']").textContent = rune.name || "—";
  node.querySelector("[data-bind='rune_tree']").textContent = rune.tree ? `Árbol: ${rune.tree}` : "";

  // Builds
  const buildsContainer = node.querySelector("[data-bind='builds']");
  for (const build of champ.core_builds || []) {
    buildsContainer.appendChild(buildBuildBlock(build));
  }
  if (!champ.core_builds || champ.core_builds.length === 0) {
    buildsContainer.innerHTML = `<p style="color: var(--text-secondary); font-style: italic;">Sin builds registradas para este parche.</p>`;
  }

  $app.innerHTML = "";
  $app.appendChild(node);
}

function buildBuildBlock(build) {
  const div = document.createElement("div");
  div.className = "build";

  const label = document.createElement("div");
  label.className = "build-label";
  label.textContent = build.label || "Core Build";
  div.appendChild(label);

  const items = document.createElement("div");
  items.className = "build-items";
  build.items.forEach((id, idx) => {
    const wrap = document.createElement("div");
    wrap.className = "build-item";
    const img = document.createElement("img");
    img.src = itemIcon(id);
    img.alt = `Item ${id}`;
    img.title = `DDragon item ${id}`;
    img.onerror = () => {
      wrap.textContent = `#${id}`;
      wrap.style.fontSize = "0.7rem";
      wrap.style.display = "flex";
      wrap.style.alignItems = "center";
      wrap.style.justifyContent = "center";
      wrap.style.color = "var(--text-secondary)";
    };
    wrap.appendChild(img);
    items.appendChild(wrap);

    if (idx < build.items.length - 1) {
      const arrow = document.createElement("span");
      arrow.className = "build-arrow";
      arrow.textContent = "→";
      items.appendChild(arrow);
    }
  });
  div.appendChild(items);

  return div;
}
