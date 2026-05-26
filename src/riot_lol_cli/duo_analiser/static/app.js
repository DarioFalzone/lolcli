/**
 * Duo Analiser — Control de Estado del Recomendador de Dúos
 * Vanilla JS SPA
 */

// Estado global de la aplicación
const state = {
    champions: [],         // Catálogo completo de campeones
    activeChampionId: "Lux", // Campeón bajo análisis actual
    activeRole: "all",     // Filtro de rol seleccionado (all, Top, Jungle, Mid, Bot, Support)
    searchQuery: "",       // Filtro de búsqueda textual
    loadingSynergies: false,
    ddVersion: "16.9.1"    // Versión DDragon, se resuelve al init
};

// URL del CDN de Data Dragon (dinámica, se resuelve en initApp)
function getDDragonUrl(championId) {
    return `https://ddragon.riotgames.com/cdn/${state.ddVersion}/img/champion/${championId}.png`;
}

/**
 * Inicialización al cargar la página
 */
document.addEventListener("DOMContentLoaded", () => {
    initApp();
});

async function initApp() {
    try {
        // 0. Resolver versión real de Data Dragon desde el CDN
        try {
            const vResp = await fetch("https://ddragon.leagueoflegends.com/api/versions.json");
            if (vResp.ok) {
                const versions = await vResp.json();
                if (versions.length > 0) {
                    state.ddVersion = versions[0];
                    // Actualizar el badge de patch
                    const patchBadge = document.getElementById("patch-badge-text");
                    if (patchBadge) patchBadge.textContent = `PATCH ${state.ddVersion}`;
                }
            }
        } catch (_) {
            // Fallback silencioso: usamos la versión hardcodeada
        }

        // 1. Cargar el catálogo completo de campeones para el grid izquierdo
        const resp = await fetch("/api/v1/duo/champions");
        if (!resp.ok) {
            throw new Error(`Error HTTP cargando catálogo: ${resp.status}`);
        }
        state.champions = await resp.json();

        // 2. Renderizar el listado inicial
        renderChampionSelector();

        // 3. Pre-seleccionar Lux por defecto y realizar la búsqueda de sinergias
        selectChampion("Lux");

    } catch (err) {
        console.error("Falla en la inicialización:", err);
        renderErrorSelector();
    }
}

/**
 * Renderiza el catálogo de campeones en el grid izquierdo con filtros aplicados
 */
function renderChampionSelector() {
    const grid = document.getElementById("champion-grid");
    if (!grid) return;

    grid.innerHTML = "";

    // Filtrar por rol y por nombre en tiempo real
    const filtered = state.champions.filter(champ => {
        const matchesRole = state.activeRole === "all" || champ.primary_role === state.activeRole;
        const matchesSearch = champ.display_name.toLowerCase().includes(state.searchQuery.toLowerCase());
        return matchesRole && matchesSearch;
    });

    if (filtered.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; padding: 24px; text-align: center; color: var(--text-secondary); font-size: 12px;">
                Ningún campeón coincide
            </div>
        `;
        return;
    }

    filtered.forEach(champ => {
        const item = document.createElement("div");
        item.className = `champ-item ${champ.id === state.activeChampionId ? 'active' : ''}`;
        item.setAttribute("role", "listitem");
        item.setAttribute("tabindex", "0");
        item.setAttribute("aria-label", `Elegir ${champ.display_name}`);
        item.onclick = () => selectChampion(champ.id);
        item.onkeydown = (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                selectChampion(champ.id);
            }
        };

        const portrait = document.createElement("div");
        portrait.className = "portrait";
        const img = document.createElement("img");
        img.src = getDDragonUrl(champ.id);
        img.alt = champ.display_name;
        // Fallback si la imagen no carga en CDN
        img.onerror = () => {
            img.src = "/static/favicon.svg";
        };
        portrait.appendChild(img);

        const name = document.createElement("span");
        name.className = "name";
        name.textContent = champ.display_name;

        item.appendChild(portrait);
        item.appendChild(name);
        grid.appendChild(item);
    });
}

function renderErrorSelector() {
    const grid = document.getElementById("champion-grid");
    if (grid) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; padding: 20px; text-align: center; color: var(--state-error);">
                Error al conectar con la API.
            </div>
        `;
    }
}

/**
 * Filtro de búsqueda textual
 */
window.filterChampions = function(val) {
    state.searchQuery = val.trim();
    renderChampionSelector();
};

/**
 * Filtro por rol (Top, Jungle, Mid, Bot, Support)
 */
window.filterByRole = function(role) {
    state.activeRole = role;
    
    // Actualizar clase activa en la botonera
    const buttons = document.querySelectorAll(".role-filters button");
    buttons.forEach(btn => {
        const isTarget = btn.getAttribute("data-role") === role;
        btn.className = isTarget ? "active" : "";
        btn.setAttribute("aria-pressed", isTarget ? "true" : "false");
    });

    renderChampionSelector();
};

/**
 * Selecciona un campeón, refresca el grid izquierdo y carga sus sinergias a la derecha
 */
window.selectChampion = async function(championId) {
    if (state.loadingSynergies) return;

    state.activeChampionId = championId;
    
    // Refrescar clases del grid izquierdo
    const items = document.querySelectorAll(".champ-item");
    items.forEach(item => {
        // Obtenemos el nombre/id a partir del handler o texto
        const nameEl = item.querySelector(".name");
        if (nameEl) {
            // Buscamos si coincide con el catálogo
            const match = state.champions.find(c => c.id === championId);
            if (match && nameEl.textContent === match.display_name) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        }
    });

    // Cargar sinergias del lado derecho
    await fetchSynergies(championId);
};

/**
 * Realiza la petición asíncrona de sinergias al backend y las renderiza
 */
async function fetchSynergies(championId) {
    const tableBody = document.getElementById("synergies-table-body");
    if (!tableBody) return;

    state.loadingSynergies = true;
    tableBody.innerHTML = `
        <tr>
            <td colspan="8">
                <div class="loading-wrapper">
                    <span class="spinner" aria-hidden="true"></span>
                    <p style="margin-top: 12px; font-size: var(--font-body-xs); color: var(--text-secondary);">
                        Analizando sinergias de combate en SoloQ…
                    </p>
                </div>
            </td>
        </tr>
    `;

    try {
        const resp = await fetch(`/api/v1/duo/synergies/${championId}`);
        if (!resp.ok) {
            throw new Error(`Error API: ${resp.status}`);
        }
        const data = await resp.json();

        // 1. Actualizar Hero de Enfoque con metadata real
        const focusPortrait = document.getElementById("focus-portrait");
        const focusName = document.getElementById("focus-name");
        const focusRole = document.getElementById("focus-role");
        const focusTitle = document.getElementById("focus-title");
        const focusWinrate = document.getElementById("focus-winrate");

        if (focusPortrait) focusPortrait.src = getDDragonUrl(data.champion_id);
        if (focusName) focusName.textContent = data.display_name;
        if (focusRole) {
            focusRole.textContent = data.primary_role.toUpperCase();
            // Variar el color del pill según el rol
            focusRole.className = `focus-role-badge pill ${data.primary_role === 'Support' ? 'pill-gold' : 'pill-cyan'}`;
        }
        if (focusTitle) focusTitle.textContent = data.title;
        if (focusWinrate) focusWinrate.textContent = `${data.base_winrate.toFixed(2)}%`;

        // 2. Renderizar tabla de sinergias
        renderSynergiesTable(data.synergies);

    } catch (err) {
        console.error("Falla cargando sinergias:", err);
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" style="padding: 40px 0; text-align: center; color: var(--state-error);">
                    No se pudieron cargar las sinergias. Por favor reintentá en unos momentos.
                </td>
            </tr>
        `;
    } finally {
        state.loadingSynergies = false;
    }
}

/**
 * Renderiza dinámicamente las filas de la tabla de sinergias y configura el acordeón
 */
function renderSynergiesTable(synergies) {
    const tableBody = document.getElementById("synergies-table-body");
    if (!tableBody) return;

    tableBody.innerHTML = "";

    if (synergies.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" style="padding: 30px; text-align: center; color: var(--text-secondary);">
                    No se encontraron recomendaciones de jungla para este campeón.
                </td>
            </tr>
        `;
        return;
    }

    // Llevar un registro del acordeón activo actualmente
    let activeIndex = null;

    synergies.forEach((syn, index) => {
        const rank = index + 1;
        const synergySign = syn.synergy_factor >= 0 ? `+${syn.synergy_factor.toFixed(2)}%` : `${syn.synergy_factor.toFixed(2)}%`;
        const isSynergyGood = syn.synergy_factor >= 1.5;

        // Fila 1: Datos generales de la sinergia (interactiva)
        const row = document.createElement("tr");
        row.className = "interactive-row fade-in-up";
        row.style.animationDelay = `${index * 40}ms`;

        row.innerHTML = `
            <td class="cell-rank">${rank}</td>
            <td>
                <div class="cell-jungler">
                    <div class="cell-portrait">
                        <img src="${getDDragonUrl(syn.jungler_id)}" alt="${syn.jungler_name}" onerror="this.src='/static/favicon.svg'">
                    </div>
                    <span class="cell-name">${syn.jungler_name}</span>
                </div>
            </td>
            <td class="num cell-wr-value">${syn.jungle_winrate.toFixed(2)}%</td>
            <td class="num cell-duowr-value">${syn.duo_winrate.toFixed(2)}%</td>
            <td class="num">
                <span class="cell-synergy-pill ${isSynergyGood ? '' : 'warning'}">${synergySign}</span>
            </td>
            <td class="num cell-matches">${syn.matches.toLocaleString()}</td>
            <td class="col-tier" style="text-align: center;">
                <span class="tier-badge tier-${syn.tier.toLowerCase()}">${syn.tier}</span>
            </td>
            <td class="col-action" style="text-align: center;">
                <button class="btn-expand" aria-expanded="false">
                    <span>Ver</span> <span class="arrow">▼</span>
                </button>
            </td>
        `;

        // Fila 2: Ventajas tácticas (acordeón oculto por defecto)
        const advRow = document.createElement("tr");
        advRow.className = "advantage-row";
        
        const advCell = document.createElement("td");
        advCell.colSpan = 8;

        const advCard = document.createElement("div");
        advCard.className = "advantages-card";

        const advTitle = document.createElement("h4");
        advTitle.className = "advantages-title";
        advTitle.textContent = `VENTAJAS TÁCTICAS DE COMBATE (DÚO ${state.activeChampionId.toUpperCase()} + ${syn.jungler_name.toUpperCase()})`;

        const advList = document.createElement("ul");
        advList.className = "advantages-list";
        syn.advantages.forEach(advText => {
            const li = document.createElement("li");
            li.textContent = advText;
            advList.appendChild(li);
        });

        advCard.appendChild(advTitle);
        advCard.appendChild(advList);
        advCell.appendChild(advCard);
        advRow.appendChild(advCell);

        // Lógica de acordeón al hacer click
        const toggleAccordion = () => {
            const btn = row.querySelector(".btn-expand");
            const arrow = btn.querySelector(".arrow");

            if (activeIndex === index) {
                // Cerrar el actual
                row.classList.remove("active");
                advRow.classList.remove("active");
                btn.setAttribute("aria-expanded", "false");
                arrow.textContent = "▼";
                activeIndex = null;
            } else {
                // Cerrar cualquier otro que esté abierto
                const activeRows = tableBody.querySelectorAll(".interactive-row.active");
                const activeAdvs = tableBody.querySelectorAll(".advantage-row.active");
                activeRows.forEach(r => r.classList.remove("active"));
                activeAdvs.forEach(a => a.classList.remove("active"));
                
                const allBtns = tableBody.querySelectorAll(".btn-expand");
                allBtns.forEach(b => {
                    b.setAttribute("aria-expanded", "false");
                    const ar = b.querySelector(".arrow");
                    if (ar) ar.textContent = "▼";
                });

                // Abrir este acordeón
                row.classList.add("active");
                advRow.classList.add("active");
                btn.setAttribute("aria-expanded", "true");
                arrow.textContent = "▲";
                activeIndex = index;
            }
        };

        row.onclick = (e) => {
            // Evitar gatillo doble si hacen clic en el botón directo
            if (e.target.closest("button")) return;
            toggleAccordion();
        };

        const btn = row.querySelector(".btn-expand");
        btn.onclick = (e) => {
            e.stopPropagation();
            toggleAccordion();
        };

        tableBody.appendChild(row);
        tableBody.appendChild(advRow);
    });
}
