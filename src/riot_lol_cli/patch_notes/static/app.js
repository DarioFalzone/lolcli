// Patch Notes V2.2 — hash-routed SPA, español-only, search + diff + sources tab
// + visual enrichment (champion icons desde Data Dragon).
const $app = document.getElementById("app");
const LOCALE = "es-es";
const DDRAGON_VERSION = "16.9.1"; // se sobrescribe desde manifest si está disponible

const state = {
  list: null,
  manifest: null,
  health: null,                // /health response cacheado
  patches: new Map(),          // key: `${version}` -> patch
  enrichments: new Map(),      // key: version -> {enrichments: [...]}
  diffs: new Map(),            // key: `${a}|${b}` -> diff
  ddragonVersion: DDRAGON_VERSION,
  championIndex: null,         // {nombre_normalizado: ID_canonico} para matching
};

async function fetchJson(url) {
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`${url} -> ${resp.status}`);
  return resp.json();
}

async function loadHealth() {
  if (state.health) return state.health;
  try {
    state.health = await fetchJson("/health");
  } catch (e) {
    state.health = { version: "?", patch_count: 0 };
  }
  return state.health;
}

async function loadList() {
  if (state.list) return state.list;
  const [list, manifest, health] = await Promise.all([
    fetchJson(`/api/v1/patch-notes/list?locale=${LOCALE}`),
    fetchJson("/api/v1/patch-notes/manifest"),
    loadHealth(),
  ]);
  state.list = list;
  state.manifest = manifest;
  state.health = health;
  // Si DDragon expone una versión más nueva, usarla para icons
  try {
    const ddragonStatus = (manifest.sources_status || {}).ddragon || {};
    if (ddragonStatus.last_success) {
      // El payload del enrichment global tiene `latest`. Lo fetcheamos lazy.
      fetchJson("/api/v1/patch-notes/sources/registry").catch(() => {});
    }
  } catch (_) {}
  loadChampionIndex().catch(() => {});
  return list;
}

async function loadPatch(version) {
  if (state.patches.has(version)) return state.patches.get(version);
  const patch = await fetchJson(`/api/v1/patch-notes/${encodeURIComponent(version)}?locale=${LOCALE}`);
  state.patches.set(version, patch);
  return patch;
}

async function loadSources(version) {
  if (state.enrichments.has(version)) return state.enrichments.get(version);
  const data = await fetchJson(`/api/v1/patch-notes/${encodeURIComponent(version)}/sources`);
  state.enrichments.set(version, data);
  return data;
}

async function loadDiff(aVersion, bVersion) {
  const key = `${aVersion}|${bVersion}`;
  if (state.diffs.has(key)) return state.diffs.get(key);
  const data = await fetchJson(
    `/api/v1/patch-notes/diff/${encodeURIComponent(aVersion)}/${encodeURIComponent(bVersion)}?locale=${LOCALE}`
  );
  state.diffs.set(key, data);
  return data;
}

async function runSearch(query) {
  if (!query || query.length < 2) return { hits: [], count: 0, query };
  return fetchJson(`/api/v1/patch-notes/search?q=${encodeURIComponent(query)}&locale=${LOCALE}&limit=30`);
}

// ============== VISUAL ENRICHMENT: CHAMPION ICONS ==============
// Cargamos la lista de campeones desde Data Dragon CDN para poder mapear
// títulos de sección (H3 = "Aatrox", "Bel'Veth", ...) a IDs canónicos para
// inyectar el icon al lado del título.

async function loadChampionIndex() {
  if (state.championIndex) return state.championIndex;
  const url = `https://ddragon.leagueoflegends.com/cdn/${state.ddragonVersion}/data/es_ES/champion.json`;
  try {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`DDragon champion.json HTTP ${resp.status}`);
    const data = await resp.json();
    const index = {};
    for (const key of Object.keys(data.data || {})) {
      const champ = data.data[key];
      // Indexar por id (key), name y nombre normalizado
      index[normalizeChampionName(key)] = champ;
      index[normalizeChampionName(champ.name)] = champ;
    }
    state.championIndex = index;
    return index;
  } catch (e) {
    console.warn("[patch_notes] No se pudo cargar champion.json:", e);
    state.championIndex = {};
    return state.championIndex;
  }
}

function normalizeChampionName(name) {
  return String(name || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/['\.\s&]+/g, "");
}

function getChampionByTitle(title) {
  if (!title || !state.championIndex) return null;
  const norm = normalizeChampionName(title);
  return state.championIndex[norm] || null;
}

function championIconUrl(champ) {
  if (!champ || !champ.id) return null;
  return `https://ddragon.leagueoflegends.com/cdn/${state.ddragonVersion}/img/champion/${champ.id}.png`;
}

function abilityKeyFromBlock(block) {
  // Detectar prefijo "Q -", "W -", "E -", "R -", "P -" (pasiva)
  if (!block) return null;
  const m = block.match(/^\s*([PQWER])\s*[-–—]/);
  return m ? m[1] : null;
}

async function loadChampionSpells(champ) {
  if (!champ || !champ.id) return null;
  if (champ._spells) return champ._spells;
  const url = `https://ddragon.leagueoflegends.com/cdn/${state.ddragonVersion}/data/es_ES/champion/${champ.id}.json`;
  try {
    const resp = await fetch(url);
    if (!resp.ok) return null;
    const data = await resp.json();
    const detail = data.data && data.data[champ.id];
    if (!detail) return null;
    champ._spells = {
      P: detail.passive || null,
      Q: detail.spells && detail.spells[0],
      W: detail.spells && detail.spells[1],
      E: detail.spells && detail.spells[2],
      R: detail.spells && detail.spells[3],
    };
    return champ._spells;
  } catch (e) {
    return null;
  }
}

function spellIconUrl(spell, isPassive) {
  if (!spell || !spell.image || !spell.image.full) return null;
  const folder = isPassive ? "passive" : "spell";
  return `https://ddragon.leagueoflegends.com/cdn/${state.ddragonVersion}/img/${folder}/${spell.image.full}`;
}

function formatDate(iso) {
  if (!iso) return null;
  try {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return null;
    const day = String(d.getDate()).padStart(2, "0");
    const month = d.toLocaleDateString("es-ES", { month: "short" }).toLowerCase();
    const hour = String(d.getHours()).padStart(2, "0");
    const min = String(d.getMinutes()).padStart(2, "0");
    return `${day} ${month}, ${hour}:${min}`;
  } catch {
    return null;
  }
}

function timeAgo(iso) {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return "—";
    const day = String(d.getDate()).padStart(2, "0");
    const month = d.toLocaleDateString("es-ES", { month: "short" }).toLowerCase();
    const hour = String(d.getHours()).padStart(2, "0");
    const min = String(d.getMinutes()).padStart(2, "0");
    return `${day} ${month}, ${hour}:${min}`;
  } catch {
    return "—";
  }
}

function freshnessLevel(iso) {
  if (!iso) return "cold";
  const diffH = (Date.now() - new Date(iso).getTime()) / (1000 * 60 * 60);
  if (diffH < 24) return "fresh";
  if (diffH < 24 * 7) return "stale";
  return "cold";
}

function escapeHtml(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function sectionSlug(text, idx) {
  const base = String(text || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 50);
  return base ? `${base}-${idx}` : `section-${idx}`;
}

// ============== ROUTER ==============

function parseRoute() {
  const hash = window.location.hash || "#overview";
  if (hash.startsWith("#patch/")) {
    // Aceptamos legacy hash `#patch/26.10|es-es` y nuevo `#patch/26.10`
    const rest = decodeURIComponent(hash.slice("#patch/".length));
    const version = rest.split("|")[0];
    return { name: "patch", version };
  }
  if (hash.startsWith("#search?")) {
    const params = new URLSearchParams(hash.slice("#search?".length));
    return { name: "search", query: params.get("q") || "" };
  }
  if (hash.startsWith("#diff/")) {
    const rest = hash.slice("#diff/".length);
    const [a, b] = rest.split("/");
    return { name: "diff", a: decodeURIComponent(a), b: decodeURIComponent(b) };
  }
  return { name: "overview" };
}

async function render() {
  const route = parseRoute();
  try {
    if (route.name === "patch") {
      const patch = await loadPatch(route.version);
      await renderPatchDetail(patch);
    } else if (route.name === "search") {
      const results = await runSearch(route.query);
      renderSearch(route.query, results);
    } else if (route.name === "diff") {
      const diff = await loadDiff(route.a, route.b);
      renderDiff(diff);
    } else {
      const list = await loadList();
      renderOverview(list);
    }
  } catch (err) {
    $app.innerHTML = `<div class="loader">Error: ${escapeHtml(err.message)}<br><a href="#overview">← Volver</a></div>`;
  }
  window.scrollTo({ top: 0, behavior: "instant" });
  // Reinit del scroll-to-top después de que el DOM cambió
  if (window.LOLCLI_ScrollToTop) window.LOLCLI_ScrollToTop.refresh();
}

window.addEventListener("hashchange", render);
window.addEventListener("DOMContentLoaded", render);

// ============== OVERVIEW ==============

function renderOverview(listPayload) {
  const tpl = document.getElementById("tpl-overview");
  const node = tpl.content.cloneNode(true);

  const items = listPayload.items || [];
  node.querySelector("[data-bind='patch_count']").textContent = String(items.length);
  node.querySelector("[data-bind='last_patch']").textContent = items[0]?.patch_version || "—";

  // Freshness chip
  const lastScrape = state.manifest?.last_scrape || null;
  const freshChip = node.querySelector("[data-bind='freshness_pill']");
  freshChip.textContent = timeAgo(lastScrape);
  freshChip.classList.add(`meta-chip--${freshnessLevel(lastScrape)}`);

  // Version pill (V2.5: visible en el hero)
  const versionPill = node.querySelector("[data-bind='app_version']");
  if (versionPill) {
    const version = state.health?.version || "?";
    versionPill.textContent = `v${version}`;
  }

  // Search form
  const searchForm = node.querySelector(".search-form");
  searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = (searchForm.querySelector("input[name='q']").value || "").trim();
    if (q.length >= 2) {
      window.location.hash = `#search?q=${encodeURIComponent(q)}`;
    }
  });

  // Cards
  const grid = node.querySelector("[data-bind='patch_cards']");
  const empty = node.querySelector("[data-bind='empty_state']");
  if (items.length === 0) {
    empty.hidden = false;
    grid.style.display = "none";
  } else {
    for (const item of items) {
      grid.appendChild(buildPatchCard(item));
    }
  }

  $app.innerHTML = "";
  $app.appendChild(node);
}

function buildPatchCard(item) {
  const card = document.createElement("article");
  card.className = "patch-card";
  card.tabIndex = 0;
  const href = `#patch/${encodeURIComponent(item.patch_version)}`;
  const go = () => { window.location.hash = href; };
  card.addEventListener("click", go);
  card.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); }
  });

  const header = document.createElement("div");
  header.className = "patch-card-header";
  const versionEl = document.createElement("div");
  versionEl.className = "patch-card-version";
  versionEl.textContent = item.patch_version;
  header.appendChild(versionEl);

  const dateEl = document.createElement("div");
  dateEl.className = "patch-card-date";
  dateEl.textContent = formatDate(item.published_at) || item.source_locale.toUpperCase();
  header.appendChild(dateEl);
  card.appendChild(header);

  const title = document.createElement("div");
  title.className = "patch-card-title";
  title.textContent = item.title || `Versión ${item.patch_version}`;
  card.appendChild(title);

  const summary = document.createElement("div");
  summary.className = "patch-card-summary";
  summary.textContent = item.summary || "Sin resumen disponible.";
  card.appendChild(summary);

  const footer = document.createElement("div");
  footer.className = "patch-card-footer";
  const meta = document.createElement("div");
  meta.className = "patch-card-meta";
  meta.textContent = `${item.section_count} secciones · ${item.source_locale}`;
  footer.appendChild(meta);
  const cta = document.createElement("div");
  cta.className = "patch-card-cta";
  cta.textContent = "Ver detalle →";
  footer.appendChild(cta);
  card.appendChild(footer);

  return card;
}

// ============== PATCH DETAIL ==============

async function renderPatchDetail(patch) {
  const tpl = document.getElementById("tpl-patch-detail");
  const node = tpl.content.cloneNode(true);

  node.querySelector("[data-bind='patch_version_pill']").textContent = `Versión ${patch.patch_version}`;
  node.querySelector("[data-bind='patch_date_pill']").textContent =
    formatDate(patch.published_at) || patch.source_locale.toUpperCase();
  const canonical = node.querySelector("[data-bind='canonical_link']");
  canonical.href = patch.canonical_url;

  const enrichCount = (patch.enrichments || []).length;
  const enrichPill = node.querySelector("[data-bind='enrichments_pill']");
  if (enrichCount > 0) {
    enrichPill.textContent = `${enrichCount} fuente${enrichCount === 1 ? "" : "s"}`;
  } else {
    enrichPill.style.display = "none";
  }

  node.querySelector("[data-bind='patch_title']").textContent = patch.title || `Versión ${patch.patch_version}`;
  const summary = node.querySelector("[data-bind='patch_summary']");
  if (patch.summary) summary.textContent = patch.summary;
  else summary.style.display = "none";

  // Official tab (TOC + article)
  fillOfficialPanel(node, patch);

  // Tab switching (sólo `official` y `sources` en V2.2 — locales removido)
  const tabs = node.querySelectorAll(".detail-tab");
  const panels = node.querySelectorAll(".tab-panel");
  tabs.forEach((tab) => {
    tab.addEventListener("click", async () => {
      tabs.forEach((t) => t.classList.toggle("active", t === tab));
      panels.forEach((p) => {
        const match = p.dataset.panel === tab.dataset.tab;
        p.hidden = !match;
        p.classList.toggle("active", match);
      });
      if (tab.dataset.tab === "sources") {
        await fillSourcesPanel($app.querySelector("[data-panel='sources']"), patch);
      }
    });
  });

  $app.innerHTML = "";
  $app.appendChild(node);

  // Visual enrichment async: cargar champion index y enriquecer headings post-render.
  loadChampionIndex().then(() => enrichChampionHeadings($app));
}

function fillOfficialPanel(node, patch) {
  const toc = node.querySelector("[data-bind='toc']");
  const article = node.querySelector("[data-bind='patch_sections']");
  const sections = patch.sections || [];
  if (sections.length === 0) {
    article.innerHTML = "<p class='loader'>Este parche no tiene secciones registradas.</p>";
    return;
  }
  sections.forEach((section, idx) => {
    const slug = sectionSlug(section.title || `section-${idx}`, idx);
    article.appendChild(buildSectionNode(section, slug));
    if (section.title) toc.appendChild(buildTocLink(section.title, slug, 2));
    // Subsection slugs must match what buildSectionNode generates internally:
    //   subSlug = sectionSlug(sub.title || "", `${parentSlug}-${idx}`)
    (section.subsections || []).forEach((sub, sIdx) => {
      const subSlug = sectionSlug(sub.title || "", `${slug}-${sIdx}`);
      if (sub.title) toc.appendChild(buildTocLink(sub.title, subSlug, 3));
    });
  });
}

function buildSectionNode(section, slug) {
  const wrap = document.createElement("section");
  wrap.className = "section-block";
  if (section.title) {
    const heading = document.createElement(section.heading_level === 2 ? "h2" : "h3");
    heading.id = slug;
    heading.textContent = section.title;
    wrap.appendChild(heading);
  }
  if (section.blocks && section.blocks.length) {
    const blocks = document.createElement("div");
    blocks.className = "patch-section-content";
    for (const text of section.blocks) {
      const p = document.createElement("p");
      p.textContent = text;
      blocks.appendChild(p);
    }
    wrap.appendChild(blocks);
  }
  if (section.subsections && section.subsections.length) {
    const subGroup = document.createElement("div");
    subGroup.className = "subsection-group";
    section.subsections.forEach((sub, idx) => {
      const subSlug = sectionSlug(sub.title || "", `${slug}-${idx}`);
      subGroup.appendChild(buildSectionNode(sub, subSlug));
    });
    wrap.appendChild(subGroup);
  }
  return wrap;
}

function buildTocLink(label, slug, level) {
  const a = document.createElement("a");
  a.href = `#${slug}`;
  a.textContent = label;
  if (level === 3) a.classList.add("toc-level-3");
  a.addEventListener("click", (e) => {
    e.preventDefault();
    const target = document.getElementById(slug);
    if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
  });
  return a;
}

async function fillSourcesPanel(panel, patch) {
  if (panel.dataset.filled === "1") return;
  panel.dataset.filled = "1";
  const accordion = panel.querySelector("[data-bind='sources_accordion']");
  accordion.innerHTML = "<div class='loader'>Cargando fuentes...</div>";
  try {
    const data = await loadSources(patch.patch_version);
    accordion.innerHTML = "";
    const enrichments = data.enrichments || [];
    if (enrichments.length === 0) {
      accordion.innerHTML = `
        <div class='empty-state'>
          <h2>Sin fuentes adicionales</h2>
          <p>Este parche no tiene enrichments scrapeados todavía. Disparar:
          <code>POST /api/v1/patch-notes/scrape</code></p>
        </div>`;
      return;
    }
    for (const e of enrichments) {
      accordion.appendChild(buildSourceCard(e));
    }
  } catch (err) {
    accordion.innerHTML = `<div class='loader'>Error: ${escapeHtml(err.message)}</div>`;
  }
}

function buildSourceCard(enrichment) {
  const card = document.createElement("details");
  card.className = "source-card";
  if (enrichment.error) card.classList.add("source-card--error");

  const summary = document.createElement("summary");
  summary.className = "source-card-header";
  const label = document.createElement("span");
  label.className = "source-card-title";
  label.textContent = enrichment.label || enrichment.source;
  summary.appendChild(label);

  const stateChip = document.createElement("span");
  stateChip.className = `pill ${enrichment.error ? "pill-error" : "pill-success"}`;
  stateChip.textContent = enrichment.error ? "Error" : "OK";
  summary.appendChild(stateChip);

  const fetched = document.createElement("span");
  fetched.className = "source-card-meta";
  fetched.textContent = timeAgo(enrichment.fetched_at);
  summary.appendChild(fetched);

  card.appendChild(summary);

  const body = document.createElement("div");
  body.className = "source-card-body";

  if (enrichment.error) {
    const err = document.createElement("div");
    err.className = "source-error";
    err.textContent = enrichment.error;
    body.appendChild(err);
  }

  if (enrichment.source_url) {
    const link = document.createElement("a");
    link.href = enrichment.source_url;
    link.target = "_blank";
    link.rel = "noopener";
    link.className = "pill pill-cyan";
    link.textContent = "Ver fuente original ↗";
    body.appendChild(link);
  }

  // Renderizar contenido — si hay markdown, mostrar como texto; si no, JSON
  const payload = enrichment.payload || {};
  if (payload.content_markdown) {
    const contentBox = document.createElement("div");
    contentBox.className = "source-markdown-content";
    contentBox.style.cssText = "white-space: pre-wrap; font-family: monospace; font-size: 13px; line-height: 1.5; padding: 12px; border-radius: 4px; background: #1a1f2e; color: #a8b8d8; max-height: 600px; overflow: auto;";
    contentBox.textContent = payload.content_markdown;
    body.appendChild(contentBox);
  } else {
    const payloadBox = document.createElement("pre");
    payloadBox.className = "source-payload";
    try {
      payloadBox.textContent = JSON.stringify(payload, null, 2);
    } catch {
      payloadBox.textContent = "(payload no serializable)";
    }
    body.appendChild(payloadBox);
  }

  card.appendChild(body);
  return card;
}

// ============== VISUAL ENRICHMENT: post-render ==============

function enrichChampionHeadings(root) {
  if (!root || !state.championIndex) return;

  // 1. H3 con nombre de campeón → inyectar avatar a la izquierda
  const h3List = root.querySelectorAll(".patch-article h3");
  h3List.forEach((h3) => {
    if (h3.dataset.enriched === "1") return;
    const title = (h3.textContent || "").trim();
    const champ = getChampionByTitle(title);
    if (!champ) return;
    const iconUrl = championIconUrl(champ);
    if (!iconUrl) return;

    const wrap = document.createElement("div");
    wrap.className = "champion-heading";
    const img = document.createElement("img");
    img.className = "champion-heading__icon";
    img.src = iconUrl;
    img.alt = champ.name || title;
    img.loading = "lazy";
    img.onerror = () => { img.style.display = "none"; };
    const txt = document.createElement("span");
    txt.className = "champion-heading__name";
    txt.textContent = title;
    wrap.appendChild(img);
    wrap.appendChild(txt);

    h3.classList.add("h3-enriched");
    h3.innerHTML = "";
    h3.appendChild(wrap);
    h3.dataset.enriched = "1";
    h3.dataset.championId = champ.id;

    // 2. Buscar subsecciones siguientes con "Q -", "W -", etc. y enriquecer
    const parentSection = h3.closest(".section-block");
    if (parentSection) {
      enrichAbilityHeadings(parentSection, champ);
    }
  });
}

function enrichAbilityHeadings(sectionEl, champ) {
  // En cada subsection-group descendiente, los H3 internos (subsubsections) tienen "Q -", "W -", etc.
  const subHeadings = sectionEl.querySelectorAll(".subsection-group h3, .subsection-group h4");
  if (!subHeadings.length) return;

  // Cargar spells del champion (async, sin bloquear)
  loadChampionSpells(champ).then((spells) => {
    if (!spells) return;
    subHeadings.forEach((node) => {
      if (node.dataset.enriched === "1") return;
      const text = (node.textContent || "").trim();
      const key = abilityKeyFromBlock(text);
      if (!key) return;
      const spell = spells[key];
      if (!spell) return;
      const isPassive = key === "P";
      const url = spellIconUrl(spell, isPassive);
      if (!url) return;

      const wrap = document.createElement("div");
      wrap.className = "ability-heading";
      const img = document.createElement("img");
      img.className = "ability-heading__icon";
      img.src = url;
      img.alt = spell.name || text;
      img.loading = "lazy";
      img.onerror = () => { img.style.display = "none"; };
      const txt = document.createElement("span");
      txt.className = "ability-heading__name";
      txt.textContent = text;
      wrap.appendChild(img);
      wrap.appendChild(txt);

      node.classList.add("ability-enriched");
      node.innerHTML = "";
      node.appendChild(wrap);
      node.dataset.enriched = "1";
    });
  });
}

// ============== SEARCH RESULTS ==============

function renderSearch(query, payload) {
  const tpl = document.getElementById("tpl-search-results");
  const node = tpl.content.cloneNode(true);

  node.querySelector("[data-bind='query']").textContent = query;
  const count = payload?.count ?? 0;
  node.querySelector("[data-bind='result_count']").textContent =
    `${count} resultado${count === 1 ? "" : "s"}`;

  const searchInput = node.querySelector("[data-bind='search_input']");
  searchInput.value = query;
  const searchForm = node.querySelector(".search-form");
  searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = (searchInput.value || "").trim();
    if (q.length >= 2) {
      window.location.hash = `#search?q=${encodeURIComponent(q)}`;
    }
  });

  const list = node.querySelector("[data-bind='hits']");
  const empty = node.querySelector("[data-bind='search_empty']");
  const hits = payload?.hits || [];
  if (hits.length === 0) {
    empty.hidden = false;
    list.style.display = "none";
  } else {
    for (const hit of hits) list.appendChild(buildSearchHit(hit, query));
  }

  $app.innerHTML = "";
  $app.appendChild(node);
}

function buildSearchHit(hit, query) {
  const li = document.createElement("li");
  li.className = "search-hit";

  const header = document.createElement("div");
  header.className = "search-hit-header";
  const verPill = document.createElement("span");
  verPill.className = "pill pill-gold";
  verPill.textContent = hit.patch_version;
  header.appendChild(verPill);
  const localePill = document.createElement("span");
  localePill.className = "pill pill-neutral";
  localePill.textContent = hit.source_locale.toUpperCase();
  header.appendChild(localePill);
  const path = document.createElement("span");
  path.className = "search-hit-path";
  path.textContent = (hit.section_path || []).join(" / ") || "(general)";
  header.appendChild(path);
  li.appendChild(header);

  const snippet = document.createElement("p");
  snippet.className = "search-hit-snippet";
  snippet.innerHTML = highlightSnippet(hit.snippet || "", query);
  li.appendChild(snippet);

  const linkRow = document.createElement("div");
  linkRow.className = "search-hit-cta";
  const link = document.createElement("a");
  link.href = `#patch/${encodeURIComponent(hit.patch_version)}`;
  link.className = "btn-pill btn-pill--gold";
  link.textContent = "Ver parche →";
  linkRow.appendChild(link);
  li.appendChild(linkRow);

  return li;
}

function highlightSnippet(snippet, query) {
  const escaped = escapeHtml(snippet);
  if (!query) return escaped;
  const tokens = query.split(/\s+/).filter((t) => t.length >= 2);
  let out = escaped;
  for (const tok of tokens) {
    const safeTok = tok.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    out = out.replace(new RegExp(safeTok, "gi"), (m) => `<mark>${m}</mark>`);
  }
  return out;
}

// ============== DIFF ==============

function renderDiff(diff) {
  const tpl = document.getElementById("tpl-diff");
  const node = tpl.content.cloneNode(true);

  node.querySelector("[data-bind='a_pill']").textContent = diff.a_version;
  node.querySelector("[data-bind='b_pill']").textContent = diff.b_version;
  const sum = diff.summary || {};
  node.querySelector("[data-bind='diff_summary']").textContent =
    `+${sum.added || 0} / −${sum.removed || 0} / ~${sum.modified || 0}`;

  const grid = node.querySelector("[data-bind='diff_sections']");
  for (const section of (diff.sections || [])) {
    grid.appendChild(buildDiffSection(section));
  }

  $app.innerHTML = "";
  $app.appendChild(node);
}

function buildDiffSection(section) {
  const card = document.createElement("article");
  card.className = `diff-section diff-section--${section.change_type}`;

  const header = document.createElement("header");
  header.className = "diff-section-header";
  const badge = document.createElement("span");
  badge.className = `diff-badge diff-badge--${section.change_type}`;
  badge.textContent = changeTypeLabel(section.change_type);
  header.appendChild(badge);
  const title = document.createElement("h2");
  title.textContent = section.title;
  header.appendChild(title);
  card.appendChild(header);

  if (section.change_type !== "unchanged") {
    const columns = document.createElement("div");
    columns.className = "diff-columns";

    const aCol = document.createElement("div");
    aCol.className = "diff-col diff-col--a";
    const aLabel = document.createElement("div");
    aLabel.className = "diff-col-label";
    aLabel.textContent = "Antes";
    aCol.appendChild(aLabel);
    for (const block of section.a_blocks || []) {
      const p = document.createElement("p");
      p.textContent = block;
      aCol.appendChild(p);
    }

    const bCol = document.createElement("div");
    bCol.className = "diff-col diff-col--b";
    const bLabel = document.createElement("div");
    bLabel.className = "diff-col-label";
    bLabel.textContent = "Después";
    bCol.appendChild(bLabel);
    for (const block of section.b_blocks || []) {
      const p = document.createElement("p");
      p.textContent = block;
      bCol.appendChild(p);
    }

    columns.appendChild(aCol);
    columns.appendChild(bCol);
    card.appendChild(columns);
  }

  if (section.sub_diffs && section.sub_diffs.length) {
    const sub = document.createElement("div");
    sub.className = "diff-subs";
    for (const child of section.sub_diffs) sub.appendChild(buildDiffSection(child));
    card.appendChild(sub);
  }
  return card;
}

function changeTypeLabel(t) {
  return { added: "+ Agregado", removed: "− Eliminado", modified: "~ Modificado", unchanged: "= Sin cambios" }[t] || t;
}
