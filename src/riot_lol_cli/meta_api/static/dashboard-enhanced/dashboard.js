const API_BASE = "http://localhost:8000/api/v1";
let allChampions = [];
let currentModalChampion = null;

// Inicializar
document.addEventListener("DOMContentLoaded", async () => {
    await initializeDashboard();
    setInterval(updateLastUpdate, 1000);
});

async function initializeDashboard() {
    try {
        // Cargar lista de campeones desde raw-data
        const rawResp = await axios.get(`${API_BASE}/champions/all/raw-data?limit=200`);
        const rawRows = rawResp.data.data || [];
        const seen = new Set();
        allChampions = rawRows.map(r => r.champion).filter(c => c && !seen.has(c) && seen.add(c));

        // Cargar summary para el counter de anomalías
        try {
            const summaryResp = await axios.get(`${API_BASE}/dashboard/summary`);
            const summary = summaryResp.data.summary || {};
            document.getElementById("stat-anomalies").textContent = summary.active_anomalies ?? 0;
        } catch (_) { /* no bloquea el resto */ }

        // Llenar selects
        populateSelects();

        // Cargar datos iniciales
        await Promise.all([
            updateDashboard(),
            loadRawData()
        ]);

        setSystemStatus(true);
    } catch (error) {
        console.error("Error initializing:", error);
        setSystemStatus(false);
    }
}

function populateSelects() {
    const selects = [
        'matchup-champion-filter',
        'items-champion-filter',
        'raw-champion-filter'
    ];

    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        allChampions.forEach(champ => {
            const option = document.createElement('option');
            option.value = champ;
            option.textContent = champ;
            select.appendChild(option);
        });
    });
}

function switchTab(event, tabName) {
    // Remove active from all tabs
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

    // Add active to selected
    event.target.classList.add("active");
    document.getElementById(tabName).classList.add("active");
}

async function updateDashboard() {
    try {
        const response = await axios.get(`${API_BASE}/tier-list/current`);
        const raw = response.data;

        let html = '';
        let totalChamps = 0;

        const tierColors = {
            S: { bg: 'linear-gradient(135deg, #ff6b6b, #ff4444)', name: 'OP' },
            A: { bg: 'linear-gradient(135deg, #ffa500, #ff8c00)', name: 'Muy Bueno' },
            B: { bg: 'linear-gradient(135deg, #4ecdc4, #44b7aa)', name: 'Viable' },
            C: { bg: 'linear-gradient(135deg, #95e1d3, #38a169)', name: 'Aceptable' },
            D: { bg: 'linear-gradient(135deg, #cccccc, #999999)', name: 'Débil' }
        };

        // API devuelve tier_s / tier_a / tier_b / tier_c / tier_d con objetos {champion, winrate, pickrate, ...}
        [['tier_s','S'], ['tier_a','A'], ['tier_b','B'], ['tier_c','C'], ['tier_d','D']].forEach(([key, tier]) => {
            const champions = raw[key] || [];
            if (champions.length === 0) return;

            totalChamps += champions.length;
            const tierInfo = tierColors[tier] || { bg: '#666', name: tier };

            html += `
                <div class="mb-20">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 2px solid var(--arc-gold-dark);">
                        <div style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 4px; background: ${tierInfo.bg}; color: white; font-weight: bold; font-size: 20px;">${tier}</div>
                        <div><strong>Tier ${tier} - ${tierInfo.name}</strong> <span style="color: var(--arc-gold);">(${champions.length})</span></div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px;">
            `;

            champions.forEach(champ => {
                html += `
                    <div style="background: rgba(0, 0, 0, 0.3); border: 1px solid var(--arc-gold-dark); border-radius: 4px; padding: 10px; text-align: center; cursor: pointer; transition: all 0.3s ease;" onclick="showChampionDetails('${champ.champion}')">
                        <div style="font-weight: bold; color: var(--arc-gold); margin-bottom: 5px; font-size: 12px;">${champ.champion}</div>
                        <div style="font-size: 11px; color: #aaa;">
                            <div>WR: <span class="text-success">${champ.winrate?.toFixed(1)}%</span></div>
                            <div>PR: <span class="text-info">${champ.pickrate?.toFixed(1)}%</span></div>
                        </div>
                    </div>
                `;
            });

            html += '</div></div>';
        });

        document.getElementById("tier-list-content").innerHTML = html || '<p style="color:#aaa;">Sin datos de tier list</p>';
        document.getElementById("stat-champions").textContent = totalChamps;

    } catch (error) {
        console.error("Error updating dashboard:", error);
    }
}

async function loadMatchupData() {
    const champion = document.getElementById('matchup-champion-filter').value;
    if (!champion) {
        document.getElementById('matchup-table').querySelector('tbody').innerHTML =
            '<tr><td colspan="8" class="no-data">Selecciona un campeón</td></tr>';
        return;
    }

    try {
        const hours = document.getElementById('matchup-hours-filter').value;
        const limit = document.getElementById('matchup-limit-filter').value;

        const response = await axios.get(
            `${API_BASE}/champions/${champion}/matchups?limit=${limit}&hours=${hours}`
        );

        const data = response.data.data || [];
        const tbody = document.getElementById('matchup-table').querySelector('tbody');

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="no-data">Sin datos</td></tr>';
            return;
        }

        tbody.innerHTML = data.map(row => `
            <tr>
                <td>${new Date(row.hour_bucket).toLocaleString('es-ES')}</td>
                <td>${row.champion}</td>
                <td>${row.matches}</td>
                <td class="text-success">${row.wins}</td>
                <td class="text-danger">${row.losses}</td>
                <td class="text-info">${row.winrate?.toFixed(1)}%</td>
                <td class="trend-${row.trend?.toLowerCase() || 'stable'}">${row.trend || 'STABLE'}</td>
                <td><span class="source-badge">${row.source}</span></td>
            </tr>
        `).join('');

    } catch (error) {
        console.error("Error loading matchups:", error);
        document.getElementById('matchup-table').querySelector('tbody').innerHTML =
            '<tr><td colspan="8" class="text-danger">Error al cargar datos</td></tr>';
    }
}

async function loadItemsData() {
    const champion = document.getElementById('items-champion-filter').value;
    if (!champion) {
        document.getElementById('items-table').querySelector('tbody').innerHTML =
            '<tr><td colspan="4" class="no-data">Selecciona un campeón</td></tr>';
        return;
    }

    try {
        const limit = document.getElementById('items-limit-filter').value;
        const response = await axios.get(
            `${API_BASE}/champions/${champion}/items?limit=${limit}`
        );

        const data = response.data.data || [];
        const tbody = document.getElementById('items-table').querySelector('tbody');

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="no-data">Sin datos</td></tr>';
            return;
        }

        tbody.innerHTML = data.map(row => `
            <tr>
                <td>${row.item_id}</td>
                <td class="text-success">${row.frequency}</td>
                <td>${row.build_path || 'N/A'}</td>
                <td><span class="source-badge">${row.source}</span></td>
            </tr>
        `).join('');

    } catch (error) {
        console.error("Error loading items:", error);
        document.getElementById('items-table').querySelector('tbody').innerHTML =
            '<tr><td colspan="4" class="text-danger">Error al cargar datos</td></tr>';
    }
}

async function loadRawData() {
    try {
        const champion = document.getElementById('raw-champion-filter').value;
        const limit = document.getElementById('raw-limit-filter').value;

        let url = `${API_BASE}/champions/all/raw-data?limit=${limit}`;
        if (champion) url += `&champion=${champion}`;

        const response = await axios.get(url);
        const data = response.data.data || [];
        const tbody = document.getElementById('raw-table').querySelector('tbody');

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="no-data">Sin datos</td></tr>';
            return;
        }

        tbody.innerHTML = data.map((row, idx) => `
            <tr onclick="showChampionDetails('${row.champion}')">
                <td style="cursor: pointer; color: var(--arc-gold); font-weight: bold;">${row.champion}</td>
                <td>${new Date(row.hour_bucket).toLocaleString('es-ES')}</td>
                <td>${row.matches}</td>
                <td class="text-success">${row.winrate?.toFixed(1)}%</td>
                <td class="text-info">${row.pickrate?.toFixed(1)}%</td>
                <td><span class="source-badge">${row.source}</span></td>
            </tr>
        `).join('');

        document.getElementById("stat-matches").textContent = data.length;

    } catch (error) {
        console.error("Error loading raw data:", error);
        document.getElementById('raw-table').querySelector('tbody').innerHTML =
            '<tr><td colspan="6" class="text-danger">Error al cargar datos</td></tr>';
    }
}

async function showChampionDetails(championName) {
    currentModalChampion = championName;

    try {
        const response = await axios.get(
            `${API_BASE}/champions/${championName}/details`
        );

        const data = response.data;
        let html = '';

        if (data.champion_data) {
            const stats = data.champion_data;
            html += `
                <div class="modal-section">
                    <div class="modal-section-title">📊 Estadísticas Actuales</div>
                    <table style="width: 100%; margin-top: 10px;">
                        <tr>
                            <td style="padding: 5px;"><strong>Winrate:</strong></td>
                            <td class="text-success">${stats.winrate?.toFixed(1)}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px;"><strong>Pickrate:</strong></td>
                            <td class="text-info">${stats.pickrate?.toFixed(1)}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px;"><strong>Partidas:</strong></td>
                            <td>${stats.matches}</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px;"><strong>Tierrada:</strong></td>
                            <td style="color: var(--arc-gold);">${stats.tier || 'N/A'}</td>
                        </tr>
                    </table>
                </div>
            `;
        }

        if (data.anomalies && data.anomalies.length > 0) {
            html += `
                <div class="modal-section">
                    <div class="modal-section-title">⚠️ Anomalías Detectadas</div>
            `;

            data.anomalies.forEach(anom => {
                html += `
                    <div style="background: rgba(255, 153, 0, 0.1); border-left: 3px solid var(--state-warning); padding: 10px; margin-bottom: 10px; border-radius: 4px;">
                        <div><strong>${anom.type}</strong> - Confianza: <span class="text-warning">${(anom.confidence * 100).toFixed(0)}%</span></div>
                        <div style="margin-top: 5px; color: #ccc;">${anom.description}</div>
                    </div>
                `;
            });

            html += '</div>';
        }

        html += `
            <div class="modal-section">
                <div class="modal-section-title">Información</div>
                <div style="color: #aaa; font-size: 12px;">
                    <div><strong>Fuente de Datos:</strong> <span class="source-badge">${data.source}</span></div>
                    <div style="margin-top: 5px;"><strong>Última Actualización:</strong> ${new Date(data.timestamp).toLocaleString('es-ES')}</div>
                </div>
            </div>
        `;

        document.getElementById('modal-champion-name').textContent = championName;
        document.getElementById('modal-source').textContent = data.source;
        document.getElementById('modal-body').innerHTML = html;
        document.getElementById('champion-modal').classList.add('active');

    } catch (error) {
        console.error("Error loading champion details:", error);
        document.getElementById('modal-body').innerHTML =
            '<div class="text-danger">Error al cargar detalles del campeón</div>';
    }
}

function closeModal() {
    document.getElementById('champion-modal').classList.remove('active');
}

function sortTable(tableId, columnIndex) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const aVal = a.cells[columnIndex].textContent.trim();
        const bVal = b.cells[columnIndex].textContent.trim();

        const aNum = parseFloat(aVal);
        const bNum = parseFloat(bVal);

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return aNum - bNum;
        }

        return aVal.localeCompare(bVal);
    });

    rows.forEach(row => tbody.appendChild(row));
}

function setSystemStatus(isOnline) {
    const statusEl = document.getElementById('system-status');
    const dotEl = document.querySelector('.status-dot');

    if (isOnline) {
        statusEl.textContent = 'Conectado';
        dotEl.style.background = 'var(--state-success)';
    } else {
        statusEl.textContent = 'Desconectado';
        dotEl.style.background = 'var(--state-error)';
    }
}

function updateLastUpdate() {
    const now = new Date();
    document.getElementById('last-update').textContent = now.toLocaleTimeString('es-ES');
}

// Cerrar modal con ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Cerrar modal al hacer click fuera
document.getElementById('champion-modal').addEventListener('click', (e) => {
    if (e.target.id === 'champion-modal') {
        closeModal();
    }
});

const _origSwitchTab = switchTab;
switchTab = function(event, tabName) {
    _origSwitchTab(event, tabName);
    window.location.hash = `#${tabName}`;
    if (tabName === 'jungle-research' && !jrInitialized) {
        jrLoadAll();
    }
};

window.addEventListener('hashchange', () => {
    const hash = window.location.hash.replace('#', '');
    if (!hash) return;
    const [primary, secondary] = hash.split('/');
    setTimeout(() => jrActivateView(primary, secondary), 50);
});

document.addEventListener('DOMContentLoaded', () => {
    const hash = window.location.hash.replace('#', '');
    if (hash) {
        const [primary, secondary] = hash.split('/');
        setTimeout(() => jrActivateView(primary, secondary), 100);
    }
});
