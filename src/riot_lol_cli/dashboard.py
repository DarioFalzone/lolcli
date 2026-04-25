"""
Frontend Dashboard - HTML/JS para Meta Analyzer
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LOLCLI Meta Analyzer Dashboard</title>
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
            --secondary: #785a28;
            --accent: #c89b3c;
            --success: #0ac800;
            --danger: #ff3d3d;
            --warning: #ff9900;
            --info: #00a8ff;
            --dark: #010a13;
            --light: #f0f0f0;
            --border-radius: 8px;
            --box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--dark) 0%, var(--primary) 100%);
            color: var(--light);
            min-height: 100vh;
        }

        /* Header */
        header {
            background: var(--primary);
            border-bottom: 3px solid var(--secondary);
            padding: 20px;
            box-shadow: var(--box-shadow);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        header h1 {
            font-size: 28px;
            color: var(--accent);
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
            background: var(--success);
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

        /* Grid */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .grid-2 {
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
        }

        /* Card */
        .card {
            background: rgba(10, 30, 61, 0.8);
            border: 1px solid var(--secondary);
            border-radius: var(--border-radius);
            padding: 20px;
            box-shadow: var(--box-shadow);
            backdrop-filter: blur(10px);
        }

        .card-title {
            font-size: 18px;
            color: var(--accent);
            margin-bottom: 15px;
            border-bottom: 2px solid var(--secondary);
            padding-bottom: 10px;
        }

        .card-content {
            color: var(--light);
        }

        /* Summary Stats */
        .summary-stat {
            text-align: center;
            padding: 15px;
        }

        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: var(--accent);
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 12px;
            color: #aaa;
            text-transform: uppercase;
        }

        /* Tier List */
        .tier-section {
            margin-bottom: 20px;
        }

        .tier-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--secondary);
        }

        .tier-letter {
            font-size: 24px;
            font-weight: bold;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            color: white;
        }

        .tier-s { background: linear-gradient(135deg, #ff6b6b, #ff4444); }
        .tier-a { background: linear-gradient(135deg, #ffa500, #ff8c00); }
        .tier-b { background: linear-gradient(135deg, #4ecdc4, #44b7aa); }
        .tier-c { background: linear-gradient(135deg, #95e1d3, #38a169); }
        .tier-d { background: linear-gradient(135deg, #cccccc, #999999); }

        .tier-count {
            color: var(--accent);
            font-weight: bold;
        }

        .champions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 10px;
        }

        .champion-card {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--secondary);
            border-radius: 4px;
            padding: 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .champion-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(200, 155, 60, 0.3);
        }

        .champion-name {
            font-weight: bold;
            color: var(--accent);
            margin-bottom: 5px;
            font-size: 12px;
        }

        .champion-stats {
            font-size: 11px;
            color: #aaa;
        }

        .stat-wr {
            color: var(--success);
        }

        .stat-pr {
            color: var(--info);
        }

        /* Anomalies */
        .anomaly-item {
            background: rgba(0, 0, 0, 0.3);
            border-left: 4px solid var(--warning);
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 4px;
        }

        .anomaly-type {
            display: inline-block;
            background: var(--warning);
            color: white;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            margin-right: 10px;
        }

        .anomaly-champion {
            color: var(--accent);
            font-weight: bold;
            font-size: 14px;
            margin: 5px 0;
        }

        .anomaly-confidence {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
        }

        .confidence-high {
            background: rgba(10, 200, 0, 0.3);
            color: var(--success);
        }

        .anomaly-description {
            font-size: 12px;
            color: #ccc;
            margin-top: 8px;
        }

        /* Charts */
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 15px;
        }

        /* Table */
        .table-responsive {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }

        th {
            background: rgba(0, 0, 0, 0.3);
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid var(--secondary);
            color: var(--accent);
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
        }

        td {
            padding: 10px 12px;
            border-bottom: 1px solid rgba(200, 155, 60, 0.1);
            color: var(--light);
        }

        tr:hover {
            background: rgba(200, 155, 60, 0.1);
        }

        /* Tabs */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid var(--secondary);
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
            color: var(--accent);
        }

        .tab.active {
            color: var(--accent);
            border-bottom-color: var(--accent);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        /* Loading */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(200, 155, 60, 0.3);
            border-radius: 50%;
            border-top-color: var(--accent);
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Responsivo */
        @media (max-width: 768px) {
            .grid-2 {
                grid-template-columns: 1fr;
            }

            .header-info {
                flex-direction: column;
                align-items: flex-start;
            }

            .champions-grid {
                grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
            }
        }

        /* Utility */
        .text-center { text-align: center; }
        .mt-20 { margin-top: 20px; }
        .mb-20 { margin-bottom: 20px; }
        .text-success { color: var(--success); }
        .text-danger { color: var(--danger); }
        .text-warning { color: var(--warning); }
        .text-info { color: var(--info); }
    </style>
</head>
<body>
    <!-- Header -->
    <header>
        <h1>⚔️ LOLCLI Meta Analyzer</h1>
        <div class="header-info">
            <div class="header-status">
                <div class="status-item">
                    <span class="status-dot"></span>
                    <span>Sistema: <strong id="system-status">Conectando...</strong></span>
                </div>
                <div class="status-item">
                    Última actualización: <strong id="last-update">--:--</strong>
                </div>
                <div class="status-item">
                    Partidas: <strong id="total-matches">0</strong>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <div class="container">
        <!-- Summary Stats -->
        <div class="card grid mb-20">
            <div class="summary-stat">
                <div class="stat-value" id="stat-anomalies">0</div>
                <div class="stat-label">Anomalías Activas</div>
            </div>
            <div class="summary-stat">
                <div class="stat-value" id="stat-champions">0</div>
                <div class="stat-label">Campeones Trackeados</div>
            </div>
            <div class="summary-stat">
                <div class="stat-value" id="stat-tier-s">0</div>
                <div class="stat-label">En Tier S</div>
            </div>
            <div class="summary-stat">
                <div class="stat-value" id="stat-tier-a">0</div>
                <div class="stat-label">En Tier A</div>
            </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
            <button class="tab active" onclick="switchTab('tier-list')">Tier List</button>
            <button class="tab" onclick="switchTab('anomalies')">Anomalías</button>
            <button class="tab" onclick="switchTab('charts')">Gráficos</button>
        </div>

        <!-- Tab: Tier List -->
        <div id="tier-list" class="tab-content active">
            <!-- Tier S -->
            <div class="card mb-20">
                <div class="tier-section">
                    <div class="tier-header">
                        <div class="tier-letter tier-s">S</div>
                        <div>
                            <strong>Tier S - OP</strong>
                            <span class="tier-count">(<span id="count-s">0</span>)</span>
                        </div>
                    </div>
                    <div class="champions-grid" id="tier-s-list">
                        <p style="color: #aaa;">Cargando...</p>
                    </div>
                </div>
            </div>

            <!-- Tier A -->
            <div class="card mb-20">
                <div class="tier-section">
                    <div class="tier-header">
                        <div class="tier-letter tier-a">A</div>
                        <div>
                            <strong>Tier A - Muy Bueno</strong>
                            <span class="tier-count">(<span id="count-a">0</span>)</span>
                        </div>
                    </div>
                    <div class="champions-grid" id="tier-a-list">
                        <p style="color: #aaa;">Cargando...</p>
                    </div>
                </div>
            </div>

            <!-- Tier B -->
            <div class="card mb-20">
                <div class="tier-section">
                    <div class="tier-header">
                        <div class="tier-letter tier-b">B</div>
                        <div>
                            <strong>Tier B - Viable</strong>
                            <span class="tier-count">(<span id="count-b">0</span>)</span>
                        </div>
                    </div>
                    <div class="champions-grid" id="tier-b-list">
                        <p style="color: #aaa;">Cargando...</p>
                    </div>
                </div>
            </div>

            <!-- Tier C -->
            <div class="card mb-20">
                <div class="tier-section">
                    <div class="tier-header">
                        <div class="tier-letter tier-c">C</div>
                        <div>
                            <strong>Tier C - Aceptable</strong>
                            <span class="tier-count">(<span id="count-c">0</span>)</span>
                        </div>
                    </div>
                    <div class="champions-grid" id="tier-c-list">
                        <p style="color: #aaa;">Cargando...</p>
                    </div>
                </div>
            </div>

            <!-- Tier D -->
            <div class="card mb-20">
                <div class="tier-section">
                    <div class="tier-header">
                        <div class="tier-letter tier-d">D</div>
                        <div>
                            <strong>Tier D - Débil</strong>
                            <span class="tier-count">(<span id="count-d">0</span>)</span>
                        </div>
                    </div>
                    <div class="champions-grid" id="tier-d-list">
                        <p style="color: #aaa;">Cargando...</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab: Anomalies -->
        <div id="anomalies" class="tab-content">
            <div class="card">
                <div class="card-title">Cambios Detectados en el Meta</div>
                <div id="anomalies-list">
                    <p style="color: #aaa; text-align: center;">Cargando anomalías...</p>
                </div>
            </div>
        </div>

        <!-- Tab: Charts -->
        <div id="charts" class="tab-content">
            <div class="grid grid-2">
                <div class="card">
                    <div class="card-title">Winrate Top 10</div>
                    <div class="chart-container">
                        <canvas id="winrate-chart"></canvas>
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Pickrate Top 10</div>
                    <div class="chart-container">
                        <canvas id="pickrate-chart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = "http://localhost:8000/api/v1";
        let chartsCache = {};

        // Inicializar
        document.addEventListener("DOMContentLoaded", () => {
            updateDashboard();
            setInterval(updateDashboard, 30000); // Actualizar cada 30s
        });

        async function updateDashboard() {
            try {
                await Promise.all([
                    updateSummary(),
                    updateTierList(),
                    updateAnomalies(),
                    updateCharts()
                ]);
                document.getElementById("system-status").textContent = "Conectado";
                document.querySelector(".status-dot").style.background = "var(--success)";
                updateLastUpdate();
            } catch (error) {
                console.error("Error updating dashboard:", error);
                document.getElementById("system-status").textContent = "Error";
                document.querySelector(".status-dot").style.background = "var(--danger)";
            }
        }

        async function updateSummary() {
            try {
                const response = await axios.get(`${API_BASE}/dashboard/summary`);
                const data = response.data.summary;
                
                document.getElementById("stat-anomalies").textContent = data.active_anomalies || 0;
                document.getElementById("stat-champions").textContent = data.champions_tracked || 0;
                document.getElementById("total-matches").textContent = data.total_matches || 0;
            } catch (error) {
                console.error("Error updating summary:", error);
            }
        }

        async function updateTierList() {
            try {
                const response = await axios.get(`${API_BASE}/tier-list/current`);
                const tiers = response.data;
                
                renderTier("s", tiers.tier_s || []);
                renderTier("a", tiers.tier_a || []);
                renderTier("b", tiers.tier_b || []);
                renderTier("c", tiers.tier_c || []);
                renderTier("d", tiers.tier_d || []);
                
                // Actualizar stats
                document.getElementById("stat-tier-s").textContent = (tiers.tier_s || []).length;
                document.getElementById("stat-tier-a").textContent = (tiers.tier_a || []).length;
            } catch (error) {
                console.error("Error updating tier list:", error);
            }
        }

        function renderTier(tier, champions) {
            const container = document.getElementById(`tier-${tier}-list`);
            const count = document.getElementById(`count-${tier}`);
            
            if (!champions || champions.length === 0) {
                container.innerHTML = '<p style="color: #aaa; grid-column: 1/-1;">Sin datos</p>';
                count.textContent = 0;
                return;
            }
            
            count.textContent = champions.length;
            container.innerHTML = champions.map(c => `
                <div class="champion-card">
                    <div class="champion-name">${c.champion || 'N/A'}</div>
                    <div class="champion-stats">
                        <div class="stat-wr">WR: ${(c.winrate || 0).toFixed(1)}%</div>
                        <div class="stat-pr">PR: ${(c.pickrate || 0).toFixed(1)}%</div>
                    </div>
                </div>
            `).join("");
        }

        async function updateAnomalies() {
            try {
                const response = await axios.get(`${API_BASE}/anomalies/high-confidence?min_confidence=0.85`);
                const anomalies = response.data.data || [];
                
                const container = document.getElementById("anomalies-list");
                if (!anomalies || anomalies.length === 0) {
                    container.innerHTML = '<p style="color: #aaa; text-align: center;">Sin anomalías detectadas</p>';
                    return;
                }
                
                container.innerHTML = anomalies.slice(0, 20).map(a => `
                    <div class="anomaly-item">
                        <div>
                            <span class="anomaly-type">${a.type || 'UNKNOWN'}</span>
                            <span class="anomaly-confidence confidence-high">
                                Confianza: ${(a.confidence * 100).toFixed(0)}%
                            </span>
                        </div>
                        <div class="anomaly-champion">${a.champion}</div>
                        <div class="anomaly-description">${a.description || 'Sin descripción'}</div>
                        <div class="anomaly-description" style="margin-top: 5px;">
                            Z-Score: ${(a.z_score || 0).toFixed(2)}σ | Cambio: ${(a.change_pct || 0).toFixed(2)}%
                        </div>
                    </div>
                `).join("");
            } catch (error) {
                console.error("Error updating anomalies:", error);
            }
        }

        async function updateCharts() {
            try {
                const response = await axios.get(`${API_BASE}/stats/latest?limit=100`);
                const stats = response.data.data || [];
                
                // Top 10 por Winrate
                const topWR = stats
                    .sort((a, b) => (b.winrate || 0) - (a.winrate || 0))
                    .slice(0, 10);
                
                const topPR = stats
                    .sort((a, b) => (b.pickrate || 0) - (a.pickrate || 0))
                    .slice(0, 10);
                
                renderChart("winrate-chart", topWR.map(s => s.champion_name), topWR.map(s => s.winrate || 0), "Winrate %");
                renderChart("pickrate-chart", topPR.map(s => s.champion_name), topPR.map(s => s.pickrate || 0), "Pickrate %");
            } catch (error) {
                console.error("Error updating charts:", error);
            }
        }

        function renderChart(canvasId, labels, data, label) {
            const ctx = document.getElementById(canvasId);
            if (!ctx) return;
            
            if (chartsCache[canvasId]) {
                chartsCache[canvasId].destroy();
            }
            
            chartsCache[canvasId] = new Chart(ctx, {
                type: "horizontalBar",
                data: {
                    labels,
                    datasets: [{
                        label,
                        data,
                        backgroundColor: "rgba(200, 155, 60, 0.6)",
                        borderColor: "rgba(200, 155, 60, 1)",
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: "y",
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            ticks: { color: "#aaa" },
                            grid: { color: "rgba(200, 155, 60, 0.1)" }
                        },
                        y: {
                            ticks: { color: "#aaa" }
                        }
                    }
                }
            });
        }

        function switchTab(tabName) {
            // Hide all
            document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
            document.querySelectorAll(".tab").forEach(el => el.classList.remove("active"));
            
            // Show selected
            document.getElementById(tabName).classList.add("active");
            event.target.classList.add("active");
        }

        function updateLastUpdate() {
            const now = new Date();
            document.getElementById("last-update").textContent = now.toLocaleTimeString("es-ES");
        }
    </script>
</body>
</html>
"""

def save_dashboard(output_path: str = "outputs/meta-analyzer-dashboard.html"):
    """Guarda el dashboard en archivo"""
    import logging
    from pathlib import Path
    _logger = logging.getLogger(__name__)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(DASHBOARD_HTML)
    _logger.info("Dashboard guardado en: %s", output_path)

if __name__ == "__main__":
    save_dashboard()
