-- ============================================================================
-- LOLCLI Meta Analyzer - Database Schema
-- ============================================================================
-- Purpose: Store real-time meta data for analysis and tier list generation
-- Window: Rolling 48-hour data retention
-- ============================================================================

-- ============================================================================
-- 1. RAW MATCHES - Datos crudos de partidas (ventana 48h)
-- ============================================================================
CREATE TABLE IF NOT EXISTS raw_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id TEXT NOT NULL UNIQUE,
    platform_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Información general
    match_duration_seconds INTEGER NOT NULL,
    game_mode TEXT NOT NULL,
    game_type TEXT NOT NULL,
    
    -- Participantes
    champion_id INTEGER NOT NULL,
    champion_name TEXT NOT NULL,
    summoner_name TEXT NOT NULL,
    summoner_id TEXT NOT NULL,
    
    -- Stats
    role TEXT,
    team_id INTEGER,
    
    -- Resultados
    win BOOLEAN NOT NULL,
    kills INTEGER,
    deaths INTEGER,
    assists INTEGER,
    damage_dealt REAL,
    damage_taken REAL,
    gold_earned REAL,
    minions_killed INTEGER,
    vision_score REAL,
    
    -- Items
    item_0 INTEGER,
    item_1 INTEGER,
    item_2 INTEGER,
    item_3 INTEGER,
    item_4 INTEGER,
    item_5 INTEGER,
    item_6 INTEGER,
    
    -- Runas
    rune_primary INTEGER,
    rune_secondary INTEGER,
    
    -- Metadata
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_champion_name (champion_name),
    INDEX idx_timestamp (timestamp),
    INDEX idx_match_id (match_id),
    INDEX idx_summoner (summoner_name)
);

-- Política de limpieza automática: DELETE FROM raw_matches WHERE timestamp < datetime('now', '-48 hours')

-- ============================================================================
-- 2. CHAMPION HOURLY - Estadísticas agregadas por hora
-- ============================================================================
CREATE TABLE IF NOT EXISTS champion_hourly (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hour_bucket DATETIME NOT NULL,  -- Truncado a hora
    champion_name TEXT NOT NULL,
    
    -- Agregaciones
    total_matches INTEGER NOT NULL DEFAULT 0,
    total_wins INTEGER NOT NULL DEFAULT 0,
    total_losses INTEGER NOT NULL DEFAULT 0,
    
    -- Porcentajes
    winrate_pct REAL,
    pickrate_pct REAL,
    banrate_pct REAL,
    
    -- Items principales (IDs)
    item_1_id INTEGER,
    item_2_id INTEGER,
    item_3_id INTEGER,
    
    -- Stats promedio
    avg_kills REAL,
    avg_deaths REAL,
    avg_assists REAL,
    avg_damage_dealt REAL,
    avg_damage_taken REAL,
    avg_gold_earned REAL,
    avg_minions_killed REAL,
    avg_vision_score REAL,
    avg_game_duration_seconds REAL,
    
    -- Por rol
    role_distribution TEXT,  -- JSON: {"MIDDLE": 0.6, "ADC": 0.3, "SUPPORT": 0.1}
    
    -- Metadata
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(hour_bucket, champion_name),
    INDEX idx_hour_bucket (hour_bucket),
    INDEX idx_champion_name (champion_name),
    INDEX idx_composite (hour_bucket, champion_name)
);

-- ============================================================================
-- 3. ANOMALIES - Cambios detectados en el meta
-- ============================================================================
CREATE TABLE IF NOT EXISTS anomalies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    detected_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    champion_name TEXT NOT NULL,
    
    -- Tipo de anomalía
    anomaly_type TEXT NOT NULL,  -- ENUM: WINRATE_SPIKE, WINRATE_DROP, ITEM_EMERGENCE, etc.
    
    -- Valores
    previous_value REAL,
    current_value REAL,
    change_pct REAL,
    z_score REAL,
    
    -- Confianza
    confidence REAL NOT NULL,  -- 0.0 a 1.0
    severity TEXT,  -- LOW, MEDIUM, HIGH, CRITICAL
    
    -- Detalles
    description TEXT,
    details TEXT,  -- JSON con detalles adicionales
    
    -- Seguimiento
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at DATETIME,
    acknowledged_by TEXT,
    
    -- Metadata
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_champion_name (champion_name),
    INDEX idx_detected_at (detected_at),
    INDEX idx_confidence (confidence),
    INDEX idx_anomaly_type (anomaly_type)
);

-- ============================================================================
-- 4. TIER LISTS - Snapshots de tier lists generados
-- ============================================================================
CREATE TABLE IF NOT EXISTS tier_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_at DATETIME NOT NULL,  -- Cuándo se generó
    
    -- Información del snapshot
    patch_version TEXT,
    total_matches_in_window INTEGER,
    
    -- Tier list completa (JSON)
    tier_list_json TEXT NOT NULL,  -- JSON array: [{champion, tier, wr, pr, br, trend, reason}]
    
    -- Summary
    tier_distribution TEXT,  -- JSON: {"S": 5, "A": 12, "B": 18, "C": 35, "D": 25}
    
    -- Anomalies activas
    active_anomalies_count INTEGER,
    
    -- Metadata
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_snapshot_at (snapshot_at),
    INDEX idx_patch_version (patch_version)
);

-- ============================================================================
-- 5. CHAMPION STATS HISTORICAL - Para análisis histórico (último mes)
-- ============================================================================
CREATE TABLE IF NOT EXISTS champion_stats_historical (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_bucket DATE NOT NULL,  -- Día
    champion_name TEXT NOT NULL,
    
    -- Stats del día
    matches INTEGER,
    wins INTEGER,
    losses INTEGER,
    winrate_pct REAL,
    pickrate_pct REAL,
    banrate_pct REAL,
    
    -- Trending info
    tier_assigned TEXT,  -- S/A/B/C/D
    trend TEXT,  -- RISING/STABLE/FALLING
    
    -- Metadata
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(date_bucket, champion_name),
    INDEX idx_date_bucket (date_bucket),
    INDEX idx_champion_name (champion_name)
);

-- ============================================================================
-- 6. META EVENTS - Eventos importantes en meta
-- ============================================================================
CREATE TABLE IF NOT EXISTS meta_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,  -- PATCH, ITEM_RELEASE, CHAMPION_REWORK, etc.
    event_date DATETIME NOT NULL,
    patch_version TEXT,
    
    -- Cambios principales
    description TEXT NOT NULL,
    affected_champions TEXT,  -- JSON: ["Ekko", "Zed", "Yasuo"]
    affected_items TEXT,      -- JSON: [3089, 3156, 3001]
    
    -- Metadata
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_event_date (event_date),
    INDEX idx_patch_version (patch_version)
);

-- ============================================================================
-- 7. ANALYSIS LOGS - Para auditoría y debugging
-- ============================================================================
CREATE TABLE IF NOT EXISTS analysis_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_type TEXT NOT NULL,  -- HOURLY_ANALYSIS, ANOMALY_DETECTION, TIER_GENERATION
    
    -- Ejecución
    started_at DATETIME NOT NULL,
    completed_at DATETIME,
    status TEXT,  -- RUNNING, COMPLETED, FAILED
    
    -- Resultados
    matches_processed INTEGER,
    anomalies_detected INTEGER,
    tier_list_generated BOOLEAN,
    
    -- Logs
    log_message TEXT,
    error_message TEXT,
    
    -- Metadata
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_started_at (started_at),
    INDEX idx_analysis_type (analysis_type),
    INDEX idx_status (status)
);

-- ============================================================================
-- INDICES y CONSTRAINTS adicionales
-- ============================================================================

-- Tabla de sincronización para control de races
CREATE TABLE IF NOT EXISTS sync_control (
    lock_name TEXT PRIMARY KEY,
    locked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    locked_by TEXT
);

-- ============================================================================
-- VIEWS útiles
-- ============================================================================

-- View: Últimas estadísticas de cada campeón (últimas 24h)
CREATE VIEW IF NOT EXISTS v_latest_champion_stats AS
SELECT 
    champion_name,
    (SELECT winrate_pct FROM champion_hourly 
     WHERE champion_hourly.champion_name = ch.champion_name 
     ORDER BY hour_bucket DESC LIMIT 1) AS current_winrate,
    (SELECT pickrate_pct FROM champion_hourly 
     WHERE champion_hourly.champion_name = ch.champion_name 
     ORDER BY hour_bucket DESC LIMIT 1) AS current_pickrate,
    (SELECT hour_bucket FROM champion_hourly 
     WHERE champion_hourly.champion_name = ch.champion_name 
     ORDER BY hour_bucket DESC LIMIT 1) AS last_updated
FROM (SELECT DISTINCT champion_name FROM champion_hourly) ch
ORDER BY current_winrate DESC;

-- View: Anomalías de alto nivel
CREATE VIEW IF NOT EXISTS v_high_confidence_anomalies AS
SELECT 
    id,
    detected_at,
    champion_name,
    anomaly_type,
    confidence,
    description,
    current_value,
    z_score
FROM anomalies
WHERE confidence >= 0.85
ORDER BY detected_at DESC;

-- ============================================================================
-- TRIGGERS para mantenimiento automático
-- ============================================================================

-- Trigger: Limpiar matches antiguos (cada 24h idealmente vía cron)
-- Nota: SQLite no tiene job scheduler, usar Python/cron externo

-- ============================================================================
-- Fin del schema
-- ============================================================================
