"""
Dashboard Mejorado - HTML/JS con tabs avanzados para Meta Analyzer
Incluye: Dashboard, Matchups, Items, Raw Data con filtros y clicks interactivos
"""

ENHANCED_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LOLCLI Meta Analyzer - Enhanced</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #0a1e3d;
            --arc-gold-dark: #785a28;
            --arc-gold: #c89b3c;
            --state-success: #0ac800;
            --state-error: #ff3d3d;
            --state-warning: #ff9900;
            --info: #00a8ff;
            --forge-black: #010a13;
            --light: #f0f0f0;
            --border-radius: 8px;
            --box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--forge-black) 0%, var(--primary) 100%);
            color: var(--light);
            min-height: 100vh;
        }

        /* Header */
        header {
            background: var(--primary);
            border-bottom: 3px solid var(--arc-gold-dark);
            padding: 20px;
            box-shadow: var(--box-shadow);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        header h1 {
            font-size: 28px;
            color: var(--arc-gold);
            margin-bottom: 10px;
        }

        .header-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }

        .header-status {
            display: flex;
            gap: 20px;
            font-size: 14px;
        }

        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--state-success);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        /* Container */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        /* Card */
        .card {
            background: rgba(10, 30, 61, 0.8);
            border: 1px solid var(--arc-gold-dark);
            border-radius: var(--border-radius);
            padding: 20px;
            box-shadow: var(--box-shadow);
            backdrop-filter: blur(10px);
        }

        .card-title {
            font-size: 18px;
            color: var(--arc-gold);
            margin-bottom: 15px;
            border-bottom: 2px solid var(--arc-gold-dark);
            padding-bottom: 10px;
        }

        /* Tabs */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid var(--arc-gold-dark);
            flex-wrap: wrap;
        }

        .tab {
            padding: 10px 20px;
            background: none;
            border: none;
            color: var(--light);
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
            transition: all 0.3s ease;
        }

        .tab:hover {
            color: var(--arc-gold);
        }

        .tab.active {
            color: var(--arc-gold);
            border-bottom-color: var(--arc-gold);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        /* Filters */
        .filters {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            align-items: center;
        }

        .filter-group {
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .filter-group label {
            font-size: 12px;
            color: var(--arc-gold);
            font-weight: bold;
            text-transform: uppercase;
        }

        input[type="text"],
        input[type="number"],
        select {
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid var(--arc-gold-dark);
            color: var(--light);
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
        }

        input[type="text"]:focus,
        input[type="number"]:focus,
        select:focus {
            outline: none;
            border-color: var(--arc-gold);
            box-shadow: 0 0 8px rgba(200, 155, 60, 0.3);
        }

        /* Data Table */
        .data-table {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }

        thead {
            background: rgba(0, 0, 0, 0.3);
            position: sticky;
            top: 0;
        }

        th {
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid var(--arc-gold-dark);
            color: var(--arc-gold);
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
            cursor: pointer;
            user-select: none;
        }

        th:hover {
            background: rgba(200, 155, 60, 0.1);
        }

        td {
            padding: 10px 12px;
            border-bottom: 1px solid rgba(200, 155, 60, 0.1);
            color: var(--light);
            font-size: 13px;
        }

        tbody tr {
            cursor: pointer;
            transition: all 0.2s ease;
        }

        tbody tr:hover {
            background: rgba(200, 155, 60, 0.1);
            transform: scale(1.01);
        }

        /* Source Badge */
        .source-badge {
            display: inline-block;
            background: rgba(0, 168, 255, 0.2);
            color: var(--info);
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: bold;
            border: 1px solid var(--info);
        }

        /* Trend Badge */
        .trend-up {
            color: var(--state-success);
            font-weight: bold;
        }

        .trend-down {
            color: var(--state-error);
            font-weight: bold;
        }

        .trend-stable {
            color: var(--state-warning);
            font-weight: bold;
        }

        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(5px);
        }

        .modal.active {
            display: flex;
        }

        .modal-content {
            background: rgba(10, 30, 61, 0.95);
            border: 2px solid var(--arc-gold-dark);
            border-radius: 8px;
            padding: 30px;
            max-width: 900px;
            width: 95%;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
        }

        .modal-close {
            position: absolute;
            top: 10px;
            right: 10px;
            background: var(--state-error);
            color: white;
            border: none;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.2s ease;
        }

        .modal-close:hover {
            transform: rotate(90deg);
            background: #ff0000;
        }

        .modal-title {
            font-size: 24px;
            color: var(--arc-gold);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .modal-section {
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(200, 155, 60, 0.2);
            padding-bottom: 15px;
        }

        .modal-section-title {
            font-size: 16px;
            color: var(--arc-gold);
            font-weight: bold;
            margin-bottom: 10px;
        }

        /* Grid */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .summary-stat {
            text-align: center;
            padding: 15px;
        }

        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: var(--arc-gold);
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 12px;
            color: #aaa;
            text-transform: uppercase;
        }

        /* Utility */
        .loading {
            text-align: center;
            padding: 40px;
            color: var(--arc-gold);
        }

        .no-data {
            text-align: center;
            padding: 20px;
            color: #aaa;
        }

        .mb-20 { margin-bottom: 20px; }
        .mt-10 { margin-top: 10px; }
        .text-success { color: var(--state-success); }
        .text-danger { color: var(--state-error); }
        .text-warning { color: var(--state-warning); }
        .text-info { color: var(--info); }

        /* Responsivo */
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }

            .filters {
                flex-direction: column;
            }

            .filter-group {
                width: 100%;
            }

            input[type="text"],
            input[type="number"],
            select {
                width: 100%;
            }

            .modal-content {
                width: 98%;
                padding: 20px;
            }

            table {
                font-size: 11px;
            }

            td, th {
                padding: 8px;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header>
        <h1>⚔️ LOLCLI Meta Analyzer - Enhanced</h1>
        <div class="header-info">
            <div class="header-status">
                <div class="status-item">
                    <span class="status-dot"></span>
                    <span>Sistema: <strong id="system-status">Conectando...</strong></span>
                </div>
                <div class="status-item">
                    Última actualización: <strong id="last-update">--:--</strong>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <div class="container">
        <!-- Summary Stats -->
        <div class="card grid mb-20">
            <div class="summary-stat">
                <div class="stat-value" id="stat-champions">0</div>
                <div class="stat-label">Campeones ADC</div>
            </div>
            <div class="summary-stat">
                <div class="stat-value" id="stat-matches">0</div>
                <div class="stat-label">Partidas Analizadas</div>
            </div>
            <div class="summary-stat">
                <div class="stat-value" id="stat-anomalies">0</div>
                <div class="stat-label">Anomalías</div>
            </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
            <button class="tab active" onclick="switchTab(event, 'dashboard')">📊 Dashboard</button>
            <button class="tab" onclick="switchTab(event, 'matchups')">⚡ Matchups</button>
            <button class="tab" onclick="switchTab(event, 'items')">🛡️ Items</button>
            <button class="tab" onclick="switchTab(event, 'raw-data')">📋 Raw Data</button>
        </div>

        <!-- Tab: Dashboard (Tier List) -->
        <div id="dashboard" class="tab-content active">
            <div class="card">
                <div class="card-title">Tier List - ADCs Actuales</div>
                <p style="color: #aaa; margin-bottom: 15px;">Haz click en un campeón para ver más detalles</p>
                <div id="tier-list-content">
                    <p class="loading">⏳ Cargando tier list...</p>
                </div>
            </div>
        </div>

        <!-- Tab: Matchups -->
        <div id="matchups" class="tab-content">
            <div class="card">
                <div class="card-title">Historial de Matchups - Por Campeón</div>
                
                <!-- Filters -->
                <div class="filters">
                    <div class="filter-group">
                        <label>Campeón:</label>
                        <select id="matchup-champion-filter" onchange="loadMatchupData()">
                            <option value="">Seleccionar...</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Últimas (horas):</label>
                        <input type="number" id="matchup-hours-filter" value="24" min="1" max="240" onchange="loadMatchupData()">
                    </div>
                    <div class="filter-group">
                        <label>Límite:</label>
                        <input type="number" id="matchup-limit-filter" value="50" min="10" max="500" onchange="loadMatchupData()">
                    </div>
                </div>

                <!-- Table -->
                <div class="data-table">
                    <table id="matchup-table">
                        <thead>
                            <tr>
                                <th onclick="sortTable('matchup-table', 0)">Hora</th>
                                <th onclick="sortTable('matchup-table', 1)">Campeón Rival</th>
                                <th onclick="sortTable('matchup-table', 2)">Partidas</th>
                                <th onclick="sortTable('matchup-table', 3)">Victorias</th>
                                <th onclick="sortTable('matchup-table', 4)">Derrotas</th>
                                <th onclick="sortTable('matchup-table', 5)">WR %</th>
                                <th onclick="sortTable('matchup-table', 6)">Tendencia</th>
                                <th>Fuente</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="8" class="no-data">Selecciona un campeón para ver matchups</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Tab: Items -->
        <div id="items" class="tab-content">
            <div class="card">
                <div class="card-title">Construcción de Items - Por Campeón</div>
                
                <!-- Filters -->
                <div class="filters">
                    <div class="filter-group">
                        <label>Campeón:</label>
                        <select id="items-champion-filter" onchange="loadItemsData()">
                            <option value="">Seleccionar...</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Top Items:</label>
                        <input type="number" id="items-limit-filter" value="10" min="5" max="50" onchange="loadItemsData()">
                    </div>
                </div>

                <!-- Table -->
                <div class="data-table">
                    <table id="items-table">
                        <thead>
                            <tr>
                                <th onclick="sortTable('items-table', 0)">Item ID</th>
                                <th onclick="sortTable('items-table', 1)">Frecuencia</th>
                                <th onclick="sortTable('items-table', 2)">Ruta de Build</th>
                                <th>Fuente</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="4" class="no-data">Selecciona un campeón para ver items</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Tab: Raw Data -->
        <div id="raw-data" class="tab-content">
            <div class="card">
                <div class="card-title">Datos Sin Filtrar - Raw Data</div>
                
                <!-- Filters -->
                <div class="filters">
                    <div class="filter-group">
                        <label>Campeón (opcional):</label>
                        <select id="raw-champion-filter" onchange="loadRawData()">
                            <option value="">Todos</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Límite:</label>
                        <input type="number" id="raw-limit-filter" value="100" min="10" max="1000" onchange="loadRawData()">
                    </div>
                </div>

                <!-- Table -->
                <div class="data-table">
                    <table id="raw-table">
                        <thead>
                            <tr>
                                <th onclick="sortTable('raw-table', 0)">Campeón</th>
                                <th onclick="sortTable('raw-table', 1)">Hora</th>
                                <th onclick="sortTable('raw-table', 2)">Partidas</th>
                                <th onclick="sortTable('raw-table', 3)">WR %</th>
                                <th onclick="sortTable('raw-table', 4)">PR %</th>
                                <th>Fuente</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="6" class="loading">⏳ Cargando datos...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal - Champion Details -->
    <div id="champion-modal" class="modal">
        <div class="modal-content">
            <button class="modal-close" onclick="closeModal()">✕</button>
            <div class="modal-title">
                <span id="modal-champion-name"></span>
                <span class="source-badge" id="modal-source">data_dragon</span>
            </div>
            <div id="modal-body">
                <!-- Se llena con JavaScript -->
            </div>
        </div>
    </div>

    <script>
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
                // Cargar lista de campeones
                const response = await axios.get(`${API_BASE}/champions/list`);
                allChampions = response.data.champions || [];
                
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
                const tiers = response.data;
                
                let html = '';
                
                // Contar estadísticas
                let totalChamps = 0;
                let totalMatches = 0;
                let tierSCount = tiers.S?.length || 0;
                
                Object.keys(tiers).forEach(tier => {
                    const champions = tiers[tier] || [];
                    if (champions.length === 0) return;
                    
                    totalChamps += champions.length;
                    
                    const tierColors = {
                        S: { bg: 'linear-gradient(135deg, #ff6b6b, #ff4444)', name: 'OP' },
                        A: { bg: 'linear-gradient(135deg, #ffa500, #ff8c00)', name: 'Muy Bueno' },
                        B: { bg: 'linear-gradient(135deg, #4ecdc4, #44b7aa)', name: 'Viable' },
                        C: { bg: 'linear-gradient(135deg, #95e1d3, #38a169)', name: 'Aceptable' },
                        D: { bg: 'linear-gradient(135deg, #cccccc, #999999)', name: 'Débil' }
                    };
                    
                    const tierInfo = tierColors[tier] || { bg: '#666', name: tier };
                    
                    html += \`
                        <div class="mb-20">
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 2px solid var(--arc-gold-dark);">
                                <div style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 4px; background: \${tierInfo.bg}; color: white; font-weight: bold; font-size: 20px;">\${tier}</div>
                                <div><strong>Tier \${tier} - \${tierInfo.name}</strong> <span style="color: var(--arc-gold);">(\${champions.length})</span></div>
                            </div>
                            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px;">
                    \`;
                    
                    champions.forEach(champ => {
                        html += \`
                            <div style="background: rgba(0, 0, 0, 0.3); border: 1px solid var(--arc-gold-dark); border-radius: 4px; padding: 10px; text-align: center; cursor: pointer; transition: all 0.3s ease;" onclick="showChampionDetails('\${champ.name}')">
                                <div style="font-weight: bold; color: var(--arc-gold); margin-bottom: 5px; font-size: 12px;">\${champ.name}</div>
                                <div style="font-size: 11px; color: #aaa;">
                                    <div>WR: <span class="text-success">\${champ.winrate.toFixed(1)}%</span></div>
                                    <div>PR: <span class="text-info">\${champ.pickrate.toFixed(1)}%</span></div>
                                </div>
                            </div>
                        \`;
                    });
                    
                    html += '</div></div>';
                });
                
                document.getElementById("tier-list-content").innerHTML = html;
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
                    `\${API_BASE}/champions/\${champion}/matchups?limit=\${limit}&hours=\${hours}`
                );
                
                const data = response.data.data || [];
                const tbody = document.getElementById('matchup-table').querySelector('tbody');
                
                if (data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="8" class="no-data">Sin datos</td></tr>';
                    return;
                }
                
                tbody.innerHTML = data.map(row => \`
                    <tr>
                        <td>\${new Date(row.hour).toLocaleString('es-ES')}</td>
                        <td>\${row.champion}</td>
                        <td>\${row.matches}</td>
                        <td class="text-success">\${row.wins}</td>
                        <td class="text-danger">\${row.losses}</td>
                        <td class="text-info">\${row.winrate?.toFixed(1)}%</td>
                        <td class="trend-\${row.trend?.toLowerCase() || 'stable'}">\${row.trend || 'STABLE'}</td>
                        <td><span class="source-badge">\${row.source}</span></td>
                    </tr>
                \`).join('');
                
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
                    `\${API_BASE}/champions/\${champion}/items?limit=\${limit}`
                );
                
                const data = response.data.data || [];
                const tbody = document.getElementById('items-table').querySelector('tbody');
                
                if (data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="4" class="no-data">Sin datos</td></tr>';
                    return;
                }
                
                tbody.innerHTML = data.map(row => \`
                    <tr>
                        <td>\${row.item_id}</td>
                        <td class="text-success">\${row.frequency}</td>
                        <td>\${row.build_path || 'N/A'}</td>
                        <td><span class="source-badge">\${row.source}</span></td>
                    </tr>
                \`).join('');
                
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
                
                let url = `\${API_BASE}/champions/all/raw-data?limit=\${limit}`;
                if (champion) url += `&champion=\${champion}`;
                
                const response = await axios.get(url);
                const data = response.data.data || [];
                const tbody = document.getElementById('raw-table').querySelector('tbody');
                
                if (data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" class="no-data">Sin datos</td></tr>';
                    return;
                }
                
                tbody.innerHTML = data.map((row, idx) => \`
                    <tr onclick="showChampionDetails('\${row.champion}')">
                        <td style="cursor: pointer; color: var(--arc-gold); font-weight: bold;">\${row.champion}</td>
                        <td>\${new Date(row.hour).toLocaleString('es-ES')}</td>
                        <td>\${row.matches}</td>
                        <td class="text-success">\${row.winrate?.toFixed(1)}%</td>
                        <td class="text-info">\${row.pickrate?.toFixed(1)}%</td>
                        <td><span class="source-badge">\${row.source}</span></td>
                    </tr>
                \`).join('');
                
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
                    `\${API_BASE}/champions/\${championName}/details`
                );
                
                const data = response.data;
                let html = '';
                
                if (data.champion_data) {
                    const stats = data.champion_data;
                    html += \`
                        <div class="modal-section">
                            <div class="modal-section-title">📊 Estadísticas Actuales</div>
                            <table style="width: 100%; margin-top: 10px;">
                                <tr>
                                    <td style="padding: 5px;"><strong>Winrate:</strong></td>
                                    <td class="text-success">\${stats.winrate?.toFixed(1)}%</td>
                                </tr>
                                <tr>
                                    <td style="padding: 5px;"><strong>Pickrate:</strong></td>
                                    <td class="text-info">\${stats.pickrate?.toFixed(1)}%</td>
                                </tr>
                                <tr>
                                    <td style="padding: 5px;"><strong>Partidas:</strong></td>
                                    <td>\${stats.matches}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 5px;"><strong>Tierrada:</strong></td>
                                    <td style="color: var(--arc-gold);">\${stats.tier || 'N/A'}</td>
                                </tr>
                            </table>
                        </div>
                    \`;
                }
                
                if (data.anomalies && data.anomalies.length > 0) {
                    html += \`
                        <div class="modal-section">
                            <div class="modal-section-title">⚠️ Anomalías Detectadas</div>
                    \`;
                    
                    data.anomalies.forEach(anom => {
                        html += \`
                            <div style="background: rgba(255, 153, 0, 0.1); border-left: 3px solid var(--state-warning); padding: 10px; margin-bottom: 10px; border-radius: 4px;">
                                <div><strong>\${anom.type}</strong> - Confianza: <span class="text-warning">\${(anom.confidence * 100).toFixed(0)}%</span></div>
                                <div style="margin-top: 5px; color: #ccc;">\${anom.description}</div>
                            </div>
                        \`;
                    });
                    
                    html += '</div>';
                }
                
                html += \`
                    <div class="modal-section">
                        <div class="modal-section-title">ℹ️ Información</div>
                        <div style="color: #aaa; font-size: 12px;">
                            <div><strong>Fuente de Datos:</strong> <span class="source-badge">\${data.source}</span></div>
                            <div style="margin-top: 5px;"><strong>Última Actualización:</strong> \${new Date(data.timestamp).toLocaleString('es-ES')}</div>
                        </div>
                    </div>
                \`;
                
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
    </script>
</body>
</html>
"""

def save_enhanced_dashboard(output_path: str = "outputs/meta-analyzer-dashboard-enhanced.html"):
    """Guarda el dashboard mejorado en archivo"""
    import logging
    from pathlib import Path
    _logger = logging.getLogger(__name__)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ENHANCED_DASHBOARD_HTML)
    _logger.info("Dashboard mejorado guardado en: %s", output_path)

if __name__ == "__main__":
    save_enhanced_dashboard()
