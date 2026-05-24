"""
Dashboard Mejorado - HTML/JS con tabs avanzados para Meta Analyzer
Incluye: Dashboard, Matchups, Items, Raw Data con filtros y clicks interactivos
"""

ENHANCED_DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="/favicon.ico" type="image/svg+xml">
    <title>LOLCLI Meta Analyzer - Enhanced</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&family=Anton&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
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
            font-family: 'Inter', 'Segoe UI', sans-serif;
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
            font-family: 'Anton', sans-serif;
            font-style: italic;
            color: var(--arc-gold);
            margin-bottom: 10px;
            letter-spacing: 0.02em;
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

        .home-hub-link {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 16px;
            border-radius: 999px;
            border: 1px solid rgba(200, 155, 60, 0.28);
            background: rgba(200, 155, 60, 0.1);
            color: var(--light);
            text-decoration: none;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            transition: all 0.2s ease;
        }

        .home-hub-link:hover {
            transform: translateY(-1px);
            border-color: rgba(200, 155, 60, 0.45);
            background: rgba(200, 155, 60, 0.16);
            box-shadow: 0 8px 20px rgba(200, 155, 60, 0.14);
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

        /* Modal — overlay usa patterns.css .modal-overlay, content local */
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

        /* Mayor especificidad para ganarle a patterns.css */
        .modal-content .modal-close {
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
            margin-left: 0;
        }

        .modal-content .modal-close:hover {
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
    <link rel="stylesheet" href="/design-system/tokens.css?v=2">
    <link rel="stylesheet" href="/design-system/patterns.css?v=2">
</head>
<body class="app-shell">
    <!-- Hero -->
    <header class="hero hero-compact">
        <div class="hero-row" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:20px;">
            <div>
                <div class="hero-eyebrow">LOLCLI</div>
                <h1 class="hero-title">META ANALYZER</h1>
                <div class="hero-meta">Enhanced Dashboard</div>
            </div>
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
                <a class="home-hub-link" href="http://localhost:8080/">⌂ Home Hub</a>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <div class="container">
        <!-- Summary Stats -->
        <div class="stat-strip mb-20">
            <div class="stat">
                <div class="stat-value gold" id="stat-champions">0</div>
                <div class="stat-label">Campeones ADC</div>
            </div>
            <div class="stat">
                <div class="stat-value cyan" id="stat-matches">0</div>
                <div class="stat-label">Partidas Analizadas</div>
            </div>
            <div class="stat">
                <div class="stat-value warning" id="stat-anomalies">0</div>
                <div class="stat-label">Anomalías</div>
            </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
            <button class="tab active" onclick="switchTab(event, 'dashboard')">📊 Dashboard</button>
            <button class="tab" onclick="switchTab(event, 'matchups')">⚡ Matchups</button>
            <button class="tab" onclick="switchTab(event, 'items')">🛡️ Items</button>
            <button class="tab" onclick="switchTab(event, 'raw-data')">📋 Raw Data</button>
            <button class="tab" onclick="switchTab(event, 'jungle-research')">🌲 Jungla 360</button>
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

        <!-- Tab: Jungla 360 (Jungle Research) -->
        <div id="jungle-research" class="tab-content">
            <!-- Header del tab: freshness + patch + estado Riot API + gaps -->
            <div class="card" style="margin-bottom: 15px;">
                <div style="display:flex; flex-wrap:wrap; gap:20px; align-items:center; justify-content:space-between;">
                    <div>
                        <div style="font-size:11px; color: var(--arc-gold); text-transform:uppercase; letter-spacing:0.08em; font-weight:bold;">Jungla 360</div>
                        <div style="font-size:18px; font-family:'Anton', sans-serif; font-style:italic; color:#f0f0f0; letter-spacing:0.02em;">Knowledge Base de Jungla</div>
                    </div>
                    <div id="jr-header-meta" style="display:flex; flex-wrap:wrap; gap:14px; font-size:12px;">
                        <span>Último refresh: <strong id="jr-freshness">--</strong></span>
                        <span>Patch: <strong id="jr-patch">--</strong></span>
                        <span>Riot API: <strong id="jr-riot-key">--</strong></span>
                        <span>Gaps: <strong id="jr-gaps-count">--</strong></span>
                    </div>
                    <div style="display:flex; gap:8px; flex-wrap:wrap;">
                        <button onclick="jrRefresh('soloq')" style="padding:8px 14px; background:var(--arc-gold); color:#010a13; border:none; border-radius:4px; cursor:pointer; font-weight:bold; font-size:12px;">↻ Refrescar SoloQ</button>
                        <button onclick="jrRefresh('asia')" style="padding:8px 14px; background:transparent; color:var(--arc-gold); border:1px solid var(--arc-gold-dark); border-radius:4px; cursor:pointer; font-size:12px;">↻ Asia (V4)</button>
                        <button onclick="jrRefresh('riot_pros')" style="padding:8px 14px; background:transparent; color:var(--arc-gold); border:1px solid var(--arc-gold-dark); border-radius:4px; cursor:pointer; font-size:12px;">↻ Riot Pros</button>
                    </div>
                </div>
            </div>

            <!-- Sub-tabs internos -->
            <div class="tabs" style="margin-bottom:15px;">
                <button class="tab active" onclick="jrSwitchSubtab(event, 'jr-consensus')">🎯 Consenso</button>
                <button class="tab" onclick="jrSwitchSubtab(event, 'jr-sources')">🔗 Fuentes</button>
                <button class="tab" onclick="jrSwitchSubtab(event, 'jr-pros')">👤 Pros</button>
                <button class="tab" onclick="jrSwitchSubtab(event, 'jr-otps')">🏆 OTPs</button>
                <button class="tab" onclick="jrSwitchSubtab(event, 'jr-report')">📈 Reporte diario</button>
            </div>

            <!-- Sub-vista Consenso: tier list final -->
            <div id="jr-consensus" class="jr-subtab active">
                <div class="card">
                    <div class="card-title">Tier list final por consenso</div>
                    <p style="color:#aaa; font-size:12px; margin-bottom:12px;">
                        Score normalizado por percentil dentro de la cohorte (patch · region · elo · queue).
                        No copia ninguna tier list externa — agrega múltiples fuentes con pesos explícitos.
                    </p>
                    <div class="data-table">
                        <table id="jr-consensus-table">
                            <thead>
                                <tr>
                                    <th>Tier</th>
                                    <th>Campeón</th>
                                    <th>Score</th>
                                    <th>Confidence</th>
                                    <th>SoloQ</th>
                                    <th>Asia (V4)</th>
                                    <th>Pro presence</th>
                                    <th>Sources</th>
                                    <th>Warnings</th>
                                    <th>Explicación</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td colspan="10" class="loading">⏳ Cargando consenso...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Sub-vista Fuentes: registry con estado + telemetría runs -->
            <div id="jr-sources" class="jr-subtab" style="display:none;">
                <div class="card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:8px;">
                        <div class="card-title" style="margin:0; padding:0; border:0;">Registry de fuentes</div>
                        <button onclick="jrRefresh('soloq_extra')" style="padding:6px 12px; background:transparent; color:var(--arc-gold); border:1px solid var(--arc-gold-dark); border-radius:4px; cursor:pointer; font-size:11px;">↻ Probar adapters V3</button>
                    </div>
                    <p style="color:#aaa; font-size:12px; margin-bottom:12px;">
                        active = consumida en V1 · planned = registrada, sin scrape aún · gap = intentamos pero falla. La columna "Último run" se llena tras invocar al adapter (POST /refresh).
                    </p>
                    <div class="data-table">
                        <table id="jr-sources-table">
                            <thead>
                                <tr>
                                    <th>Estado</th>
                                    <th>ID</th>
                                    <th>Nombre</th>
                                    <th>Tipo</th>
                                    <th>Region</th>
                                    <th>Prioridad</th>
                                    <th>Último run</th>
                                    <th>URL</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td colspan="8" class="loading">⏳ Cargando fuentes...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Sub-vista Pros: cards del seed -->
            <div id="jr-pros" class="jr-subtab" style="display:none;">
                <div class="card">
                    <div class="card-title">Pro players seed</div>
                    <p style="color:#aaa; font-size:12px; margin-bottom:12px;">
                        Para resolver cuentas reales, agregar <code>riot_id</code> + <code>server</code> al seed y exportar <code>RIOT_API_KEY</code>.
                    </p>
                    <div id="jr-pros-cards" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:12px;">
                        <p class="loading">⏳ Cargando pros...</p>
                    </div>
                </div>
            </div>

            <!-- Sub-vista OTPs: V1 placeholder -->
            <div id="jr-otps" class="jr-subtab" style="display:none;">
                <div class="card">
                    <div class="card-title">Rankings OTP por campeón</div>
                    <div style="padding:20px; background:rgba(255, 153, 0, 0.08); border:1px solid var(--state-warning); border-radius:6px;">
                        <div style="font-weight:bold; color:var(--state-warning); margin-bottom:8px;">⚠ Pipeline planned (V1)</div>
                        <p style="font-size:13px; color:#ccc; line-height:1.5;">
                            El pipeline <code>otp_rankings</code> está registrado pero no implementado en V1.
                            Fuentes objetivo: Onetricks.gg, League of Graphs (rankings/summoners), PORO.GG Champion Masters.
                            Cuando se active, mostrará top jugadores por campeón meta detectado.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Sub-vista Reporte diario -->
            <div id="jr-report" class="jr-subtab" style="display:none;">
                <div class="card">
                    <div class="card-title">Reporte diario</div>
                    <div id="jr-report-content">
                        <p class="loading">⏳ Cargando reporte...</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal - Champion Details (modal-overlay = patterns.css toggle) -->
    <div id="champion-modal" class="modal-overlay">
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

        // ============================================================
        // Jungla 360 — sub-vistas + endpoints /api/v1/jungle-research/*
        // ============================================================

        const JR_BASE = `${API_BASE}/jungle-research`;
        let jrInitialized = false;

        function jrSwitchSubtab(event, subtabId) {
            const container = document.getElementById('jungle-research');
            container.querySelectorAll('.tabs .tab').forEach(t => t.classList.remove('active'));
            container.querySelectorAll('.jr-subtab').forEach(s => { s.classList.remove('active'); s.style.display = 'none'; });
            event.currentTarget.classList.add('active');
            const subtab = document.getElementById(subtabId);
            subtab.classList.add('active');
            subtab.style.display = 'block';
        }

        function jrFmtPct(v) { return (v === null || v === undefined) ? '--' : (v * 100).toFixed(0) + '%'; }
        function jrFmtScore(v) { return (v === null || v === undefined) ? '--' : Number(v).toFixed(2); }
        function jrFmtTimestamp(iso) {
            if (!iso) return '--';
            try { return new Date(iso).toLocaleString('es-AR'); } catch { return iso; }
        }
        function jrTierColor(tier) {
            const map = {S: '#ff4444', A: '#ff8c00', B: '#4ecdc4', C: '#38a169', D: '#999'};
            return map[tier] || '#666';
        }
        function jrEscape(s) {
            if (s === null || s === undefined) return '';
            return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
        }

        async function jrLoadAll() {
            await Promise.all([
                jrLoadOverview(),
                jrLoadConsensus(),
                jrLoadSources(),
                jrLoadPros(),
                jrLoadDailyReport()
            ]);
            jrInitialized = true;
        }

        async function jrLoadOverview() {
            try {
                const resp = await axios.get(`${JR_BASE}/overview`);
                const d = resp.data;
                document.getElementById('jr-freshness').textContent = jrFmtTimestamp(d.freshness);
                document.getElementById('jr-patch').textContent = d.patch || '--';
                document.getElementById('jr-riot-key').textContent = d.riot_api_key_present ? '✓ presente' : '✗ ausente';
                document.getElementById('jr-riot-key').style.color = d.riot_api_key_present ? 'var(--state-success)' : 'var(--state-warning)';
                document.getElementById('jr-gaps-count').textContent = (d.gaps || []).length;
            } catch (e) {
                console.error('jrLoadOverview error', e);
            }
        }

        async function jrLoadConsensus() {
            const tbody = document.querySelector('#jr-consensus-table tbody');
            try {
                const resp = await axios.get(`${JR_BASE}/current?limit=80`);
                const entries = resp.data.data || [];
                if (!entries.length) {
                    tbody.innerHTML = '<tr><td colspan="10" class="no-data">Sin tier list aún. Hacé click en "Refrescar SoloQ".</td></tr>';
                    return;
                }
                tbody.innerHTML = entries.map(e => {
                    const tier = e.final_tier || 'D';
                    const warnings = (e.warning_flags || []).map(w => `<span style="background:rgba(255,153,0,0.15); color:var(--state-warning); padding:2px 6px; border-radius:3px; font-size:10px; margin-right:4px;">${jrEscape(w)}</span>`).join('');
                    const asiaCell = e.asia_score
                        ? `<span style="color:var(--info); font-weight:bold;">${jrFmtScore(e.asia_score)}</span>`
                        : '<span style="color:#666;">—</span>';
                    // PR-C: badge "ES" (esports bridge) cuando pro_presence > 0.
                    // En V0 no diferenciamos fuente por entry; si > 0 asumimos esports
                    // (porque Riot match-v5 requiere RIOT_API_KEY que rara vez está).
                    const proCell = e.pro_soloq_score && e.pro_soloq_score > 0
                        ? `${jrFmtScore(e.pro_soloq_score)} <span title="Fuente: esports_research comfort" style="display:inline-block; padding:1px 5px; margin-left:4px; border:1px solid var(--arc-cyan, #5bc0de); color:var(--arc-cyan, #5bc0de); border-radius:3px; font-size:9px; font-weight:bold;">ES</span>`
                        : jrFmtScore(e.pro_soloq_score);
                    return `<tr>
                        <td><span style="display:inline-block; width:28px; height:28px; line-height:28px; text-align:center; border-radius:4px; background:${jrTierColor(tier)}; color:white; font-weight:bold;">${jrEscape(tier)}</span></td>
                        <td style="font-weight:bold; color:var(--arc-gold);">${jrEscape(e.champion_name)}</td>
                        <td>${jrFmtScore(e.final_score)}</td>
                        <td>${jrFmtScore(e.confidence)}</td>
                        <td>${jrFmtScore(e.soloq_score)}</td>
                        <td>${asiaCell}</td>
                        <td>${proCell}</td>
                        <td>${e.source_count || 0}</td>
                        <td>${warnings || '—'}</td>
                        <td style="font-size:11px; color:#aaa;">${jrEscape(e.explanation || '')}</td>
                    </tr>`;
                }).join('');
            } catch (e) {
                console.error('jrLoadConsensus error', e);
                tbody.innerHTML = '<tr><td colspan="10" class="text-danger">Error al cargar consenso</td></tr>';
            }
        }

        async function jrLoadSources() {
            const tbody = document.querySelector('#jr-sources-table tbody');
            try {
                const resp = await axios.get(`${JR_BASE}/sources`);
                const sources = resp.data.sources || [];
                if (!sources.length) {
                    tbody.innerHTML = '<tr><td colspan="8" class="no-data">Sin sources registradas</td></tr>';
                    return;
                }
                const statusColor = {active: 'var(--state-success)', planned: 'var(--state-warning)', gap: 'var(--state-error)'};
                const runColor = {ok: 'var(--state-success)', not_implemented: '#888', error: 'var(--state-error)', disabled: '#666'};
                tbody.innerHTML = sources.map(s => {
                    let lastRun = '<span style="color:#666; font-size:10px;">—</span>';
                    if (s.last_attempted_at) {
                        const status = s.last_run_status || 'unknown';
                        const color = runColor[status] || '#999';
                        const when = jrFmtTimestamp(s.last_attempted_at);
                        const tooltip = jrEscape((s.last_run_reason || '').substring(0, 200));
                        const countBadge = s.last_run_champion_count > 0
                            ? `<span style="margin-left:4px; font-size:10px; color:#aaa;">(${s.last_run_champion_count} champs)</span>`
                            : '';
                        lastRun = `<div title="${tooltip}">
                            <span style="color:${color}; font-size:11px; font-weight:bold;">${jrEscape(status)}</span>${countBadge}
                            <div style="font-size:10px; color:#888;">${when}</div>
                        </div>`;
                    }
                    return `<tr>
                        <td><span style="background:${statusColor[s.status] || '#666'}; color:white; padding:3px 8px; border-radius:3px; font-size:11px; font-weight:bold; text-transform:uppercase;">${jrEscape(s.status)}</span></td>
                        <td><code style="font-size:11px;">${jrEscape(s.id)}</code></td>
                        <td>${jrEscape(s.name)}</td>
                        <td><span style="font-size:10px; color:#aaa;">${jrEscape(s.source_type)}</span></td>
                        <td>${(s.region_focus || []).join(', ') || '—'}</td>
                        <td>${s.scrape_priority || 0}</td>
                        <td>${lastRun}</td>
                        <td><a href="${jrEscape(s.base_url)}" target="_blank" rel="noopener" style="color:var(--info); font-size:11px;">${jrEscape(s.base_url)}</a></td>
                    </tr>`;
                }).join('');
            } catch (e) {
                console.error('jrLoadSources error', e);
                tbody.innerHTML = '<tr><td colspan="8" class="text-danger">Error al cargar fuentes</td></tr>';
            }
        }

        const JR_SERVERS = ['KR', 'EUW', 'NA', 'EUNE', 'BR', 'LAN', 'LAS', 'JP', 'TR', 'RU', 'OCE', 'VN', 'TW', 'CN'];

        async function jrLoadPros() {
            const container = document.getElementById('jr-pros-cards');
            try {
                const resp = await axios.get(`${JR_BASE}/pros`);
                const rows = resp.data.data || [];
                const keyPresent = resp.data.riot_api_key_present;
                const keyBanner = keyPresent
                    ? ''
                    : `<div style="grid-column:1 / -1; padding:10px 14px; background:rgba(255,153,0,0.08); border:1px solid var(--state-warning); border-radius:6px; font-size:12px; color:#ccc;">
                        <strong style="color:var(--state-warning);">⚠ RIOT_API_KEY ausente.</strong> Podés cargar Riot IDs igual; la resolución a PUUID se hará cuando exportes la key y refresques.
                    </div>`;
                container.innerHTML = keyBanner + rows.map(p => jrProCard(p)).join('');
            } catch (e) {
                console.error('jrLoadPros error', e);
                container.innerHTML = '<p class="text-danger">Error al cargar pros</p>';
            }
        }

        function jrProCard(p) {
            const tierColors = {S: '#ff4444', A: '#ff8c00', B: '#4ecdc4'};
            const tierBadge = `<span style="display:inline-block; padding:2px 6px; border-radius:3px; background:${tierColors[p.priority_tier] || '#666'}; color:white; font-size:10px; font-weight:bold; margin-left:6px;">${jrEscape(p.priority_tier || '?')}</span>`;
            let stateBlock;
            if (p.puuid) {
                stateBlock = `<div style="margin-top:8px; padding:6px 8px; background:rgba(10,200,0,0.1); border-radius:4px; font-size:11px; color:var(--state-success);">
                    ✓ resuelto · <code style="color:#aaa; font-size:10px;">${jrEscape(p.puuid).substring(0, 16)}…</code>
                </div>`;
            } else if (p.gap_flag === 'no_riot_key') {
                stateBlock = `<div style="margin-top:8px; padding:6px 8px; background:rgba(255,153,0,0.1); border-radius:4px; font-size:10px; color:var(--state-warning);">⚠ no_riot_key — exportá RIOT_API_KEY</div>`;
            } else if (p.riot_id) {
                stateBlock = `<div style="margin-top:8px; padding:6px 8px; background:rgba(255,61,61,0.1); border-radius:4px; font-size:10px; color:var(--state-error);">✗ ${jrEscape(p.gap_flag || 'resolución pendiente')}</div>`;
            } else {
                stateBlock = `<div style="margin-top:8px; padding:6px 8px; background:rgba(255,153,0,0.1); border-radius:4px; font-size:10px; color:var(--state-warning);">⚠ needs_account_resolution</div>`;
            }
            const currentRiot = p.riot_id ? jrEscape(p.riot_id) : '';
            const currentServer = p.server || '';
            const serverOptions = JR_SERVERS.map(s => `<option value="${s}" ${s === currentServer ? 'selected' : ''}>${s}</option>`).join('');
            return `<div style="background:rgba(10, 30, 61, 0.6); border:1px solid var(--arc-gold-dark); border-radius:6px; padding:14px;">
                <div style="display:flex; justify-content:space-between; align-items:baseline;">
                    <div>
                        <div style="font-weight:bold; color:var(--arc-gold); font-size:14px;">${jrEscape(p.player_name)}${tierBadge}</div>
                        <div style="font-size:10px; color:#aaa; margin-top:2px;">${jrEscape(p.real_name || '')} · ${jrEscape(p.country || '?')}</div>
                    </div>
                </div>
                ${stateBlock}
                <details style="margin-top:10px; font-size:11px;">
                    <summary style="cursor:pointer; color:#aaa;">Editar cuenta</summary>
                    <div style="margin-top:8px; display:flex; flex-direction:column; gap:6px;">
                        <input type="text" id="jr-pro-rid-${jrEscape(p.player_name)}" placeholder="GameName#TAG" value="${currentRiot}" style="padding:6px; background:rgba(0,0,0,0.4); border:1px solid var(--arc-gold-dark); color:#f0f0f0; border-radius:3px; font-size:11px;">
                        <select id="jr-pro-srv-${jrEscape(p.player_name)}" style="padding:6px; background:rgba(0,0,0,0.4); border:1px solid var(--arc-gold-dark); color:#f0f0f0; border-radius:3px; font-size:11px;">
                            <option value="">— Server —</option>
                            ${serverOptions}
                        </select>
                        <div style="display:flex; gap:6px;">
                            <button onclick="jrSavePro('${jrEscape(p.player_name)}')" style="flex:1; padding:6px; background:var(--arc-gold); color:#010a13; border:none; border-radius:3px; cursor:pointer; font-size:11px; font-weight:bold;">Guardar</button>
                            <button onclick="jrClearPro('${jrEscape(p.player_name)}')" style="padding:6px 10px; background:transparent; color:#aaa; border:1px solid var(--arc-gold-dark); border-radius:3px; cursor:pointer; font-size:11px;">Limpiar</button>
                        </div>
                        <div id="jr-pro-msg-${jrEscape(p.player_name)}" style="font-size:10px; color:#aaa;"></div>
                    </div>
                </details>
            </div>`;
        }

        async function jrSavePro(name) {
            const ridInput = document.getElementById(`jr-pro-rid-${name}`);
            const srvSel = document.getElementById(`jr-pro-srv-${name}`);
            const msg = document.getElementById(`jr-pro-msg-${name}`);
            const riot_id = ridInput.value.trim() || null;
            const server = srvSel.value || null;
            if (riot_id && !riot_id.includes('#')) {
                msg.textContent = '✗ Formato: GameName#TAG';
                msg.style.color = 'var(--state-error)';
                return;
            }
            if (riot_id && !server) {
                msg.textContent = '✗ Elegí un server';
                msg.style.color = 'var(--state-error)';
                return;
            }
            msg.textContent = '⏳ Guardando…';
            msg.style.color = '#aaa';
            try {
                const resp = await axios.post(`${JR_BASE}/pros/${encodeURIComponent(name)}/account`, {riot_id, server});
                const d = resp.data;
                if (d.error) {
                    msg.textContent = `✗ ${d.error}`;
                    msg.style.color = 'var(--state-error)';
                    return;
                }
                if (d.resolved) {
                    msg.textContent = `✓ Resuelto · PUUID obtenido`;
                    msg.style.color = 'var(--state-success)';
                } else if (d.gap_flag) {
                    msg.textContent = `Guardado · ${d.gap_flag}`;
                    msg.style.color = 'var(--state-warning)';
                } else {
                    msg.textContent = '✓ Guardado';
                    msg.style.color = 'var(--state-success)';
                }
                // Refrescar la grilla.
                setTimeout(() => jrLoadPros(), 600);
            } catch (e) {
                console.error('jrSavePro error', e);
                msg.textContent = '✗ Error de red';
                msg.style.color = 'var(--state-error)';
            }
        }

        async function jrClearPro(name) {
            try {
                await axios.post(`${JR_BASE}/pros/${encodeURIComponent(name)}/account`, {riot_id: null, server: null});
                jrLoadPros();
            } catch (e) {
                console.error('jrClearPro error', e);
            }
        }

        async function jrLoadDailyReport() {
            const container = document.getElementById('jr-report-content');
            try {
                const resp = await axios.get(`${JR_BASE}/daily-report`);
                const data = resp.data.data;
                if (!data) {
                    container.innerHTML = `<div style="padding:14px; background:rgba(255,153,0,0.08); border:1px solid var(--state-warning); border-radius:6px; color:#ccc;">
                        ${(resp.data.gaps || ['Sin reporte aún. Hacé click en "Refrescar SoloQ" para generar la tier list base.']).join('<br>')}
                    </div>`;
                    return;
                }
                const movementHtml = (movements, label, color) => {
                    if (!movements || !movements.length) return '';
                    return `<div style="margin-top:14px;"><div style="font-weight:bold; color:${color}; margin-bottom:8px;">${label}</div>
                        <ul style="list-style:none; padding:0;">${movements.map(m => `
                            <li style="padding:4px 8px; border-bottom:1px solid rgba(200,155,60,0.1); font-size:13px;">
                                <strong>${jrEscape(m.champion_name)}</strong>
                                <span style="font-size:11px; color:#aaa;"> ${jrEscape(m.previous_tier || '?')} → ${jrEscape(m.current_tier)}</span>
                                <span style="float:right; color:${color};">${m.delta > 0 ? '+' : ''}${jrFmtScore(m.delta)}</span>
                            </li>`).join('')}</ul></div>`;
                };
                const contradictionsHtml = (data.contradictions || []).length === 0 ? '' : `
                    <div style="margin-top:14px;"><div style="font-weight:bold; color:var(--state-warning); margin-bottom:8px;">⚠ Contradicciones entre fuentes</div>
                        <ul style="list-style:none; padding:0;">${data.contradictions.map(c => `
                            <li style="padding:4px 8px; font-size:13px;">
                                <strong>${jrEscape(c.champion_name)}</strong>: spread WR ${jrFmtScore(c.spread)}pp
                                <span style="font-size:11px; color:#aaa; display:block;">${Object.entries(c.by_source || {}).map(([s, v]) => `${s}: ${v}%`).join(' · ')}</span>
                            </li>`).join('')}</ul></div>`;
                container.innerHTML = `
                    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:18px;">
                        <div>
                            <div style="font-weight:bold; color:var(--arc-gold); margin-bottom:8px;">Top junglers</div>
                            <ul style="list-style:none; padding:0;">${(data.top_junglers || []).slice(0, 10).map(t => `
                                <li style="padding:4px 8px; border-bottom:1px solid rgba(200,155,60,0.1); font-size:13px;">
                                    <span style="display:inline-block; width:22px; height:22px; line-height:22px; text-align:center; border-radius:3px; background:${jrTierColor(t.final_tier)}; color:white; font-weight:bold; font-size:11px; margin-right:8px;">${jrEscape(t.final_tier)}</span>
                                    <strong>${jrEscape(t.champion_name)}</strong>
                                    <span style="float:right; color:#aaa; font-size:11px;">${jrFmtScore(t.final_score)}</span>
                                </li>`).join('')}</ul>
                        </div>
                        <div>${movementHtml(data.risers, '📈 Risers', 'var(--state-success)')}${movementHtml(data.fallers, '📉 Fallers', 'var(--state-error)')}</div>
                        <div>${contradictionsHtml || '<div style="font-size:12px; color:#888;">Sin contradicciones detectadas.</div>'}</div>
                    </div>
                `;
            } catch (e) {
                console.error('jrLoadDailyReport error', e);
                container.innerHTML = '<p class="text-danger">Error al cargar reporte</p>';
            }
        }

        async function jrRefresh(mode) {
            try {
                const resp = await axios.post(`${JR_BASE}/refresh?mode=${encodeURIComponent(mode)}`);
                console.log('jrRefresh', mode, resp.data);
                await jrLoadAll();
            } catch (e) {
                console.error('jrRefresh error', e);
                alert('Refresh falló — revisá la consola.');
            }
        }

        // Hook: cargar Jungla 360 cuando el tab se active
        const _origSwitchTab = switchTab;
        switchTab = function(event, tabName) {
            _origSwitchTab(event, tabName);
            if (tabName === 'jungle-research' && !jrInitialized) {
                jrLoadAll();
            }
        };

        // Helper: activa primary + sub-tab directamente (sin simular clicks).
        // Evita el race condition donde switchTab() global toca también los .tab
        // de los sub-tabs y deja state inconsistente.
        function jrActivateView(primaryTabId, subtabId) {
            // Primary tabs: solo los del contenedor raíz (.container > .tabs).
            const rootTabsBar = document.querySelector('.container > .tabs');
            if (rootTabsBar) {
                rootTabsBar.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                const primaryBtn = rootTabsBar.querySelector(`button[onclick*="'${primaryTabId}'"]`);
                if (primaryBtn) primaryBtn.classList.add('active');
            }
            // Tab content principal.
            document.querySelectorAll('.container > .tab-content').forEach(c => c.classList.remove('active'));
            const primaryContent = document.getElementById(primaryTabId);
            if (primaryContent) primaryContent.classList.add('active');
            // Carga lazy de Jungla 360 si aplica.
            if (primaryTabId === 'jungle-research' && !jrInitialized) {
                jrLoadAll();
            }
            // Sub-tab si se pidió.
            if (subtabId && primaryContent) {
                primaryContent.querySelectorAll('.tabs .tab').forEach(t => t.classList.remove('active'));
                const subBtn = primaryContent.querySelector(`.tabs button[onclick*="'${subtabId}'"]`);
                if (subBtn) subBtn.classList.add('active');
                primaryContent.querySelectorAll('.jr-subtab').forEach(s => {
                    s.classList.remove('active');
                    s.style.display = 'none';
                });
                const subView = document.getElementById(subtabId);
                if (subView) {
                    subView.classList.add('active');
                    subView.style.display = 'block';
                }
            }
        }

        // Hook: hash #<tab>[/<subtab>] activa tabs anidados al cargar.
        // Útil para smoke visual: /dashboard-enhanced#jungle-research/jr-sources
        document.addEventListener('DOMContentLoaded', () => {
            const hash = window.location.hash.replace('#', '');
            if (!hash) return;
            const [primary, secondary] = hash.split('/');
            // Pequeño delay para dejar que initializeDashboard() arranque.
            setTimeout(() => jrActivateView(primary, secondary), 100);
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
