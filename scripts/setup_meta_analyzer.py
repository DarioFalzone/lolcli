"""
Setup Script - Inicializa BD, carga datos, levanta API y dashboard
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import json

# Agregar root del repo al path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Imports del proyecto
from src.riot_lol_cli.database.models import DatabaseManager
from src.riot_lol_cli.dashboard import save_dashboard
from src.riot_lol_cli.dashboard_enhanced import save_enhanced_dashboard


def setup_database(db_path: str = "data/meta_analyzer.db"):
    """Inicializa la BD"""
    print("\n" + "="*60)
    print("📊 INICIALIZANDO BASE DE DATOS")
    print("="*60)
    
    db = DatabaseManager(db_path)
    db.init_db()
    print(f"✅ BD inicializada correctamente en: {db_path}")
    
    return db


def generate_demo_data(db: DatabaseManager):
    """Genera datos de demo para testing"""
    print("\n" + "="*60)
    print("📈 GENERANDO DATOS DE DEMO")
    print("="*60)
    
    from src.riot_lol_cli.database.models import (
        ChampionHourly, Anomaly, TierList, AnomalyTypeEnum, SeverityEnum, TierEnum
    )
    from datetime import datetime, timedelta
    
    session = db.get_session()
    
    try:
        # Limpiar datos anteriores si existen
        session.query(ChampionHourly).delete()
        session.commit()
        
        # Cargar ADCs de Data Dragon
        print("🔄 Cargando ADCs de Data Dragon...")
        try:
            with open(Path(__file__).parent / 'data' / 'adc_champions.json', 'r') as f:
                adc_data = json.load(f)
                adc_list = adc_data.get('adcs_with_yasuo', [])
        except FileNotFoundError:
            print("⚠️  Archivo adc_champions.json no encontrado. Usando lista predeterminada...")
            adc_list = [
                'Akshan', 'Aphelios', 'Ashe', 'Azir', 'Caitlyn', 'Corki', 'Draven',
                'Ezreal', 'Graves', 'Jayce', 'Jhin', 'Jinx', 'Kaisa', 'Kalista',
                'Kennen', 'Kindred', 'KogMaw', 'Lucian', 'MissFortune', 'Quinn',
                'Samira', 'Senna', 'Sivir', 'Teemo', 'Tristana', 'Twitch', 'Varus',
                'Vayne', 'Xayah', 'Yasuo', 'Zeri'
            ]
        
        print(f"✅ Trackeando {len(adc_list)} ADCs")
        
        # Crear datos demo para ADCs con variación de WR
        champions = []
        for i, adc in enumerate(adc_list):
            # Variar WR entre 45% y 55%
            wr = 45 + (i % 10) + (i / len(adc_list)) * 10
            pr = 3 + (i % 5) + (i / len(adc_list)) * 5
            champions.append({
                "name": adc,
                "wr": round(wr, 1),
                "pr": round(pr, 1)
            })
        
        # Insertar stats horarias (últimas 24h)
        now = datetime.utcnow()
        for hour_offset in range(0, 24, 3):
            hour_bucket = now - timedelta(hours=hour_offset)
            hour_bucket = hour_bucket.replace(minute=0, second=0, microsecond=0)
            
            for champ in champions:
                # Agregar variación
                wr_variance = (hour_offset * 0.3) % 5
                pr_variance = (hour_offset * 0.2) % 3
                
                hourly = ChampionHourly(
                    hour_bucket=hour_bucket,
                    champion_name=champ["name"],
                    total_matches=100 + hour_offset * 10,
                    total_wins=int((champ["wr"] / 100) * (100 + hour_offset * 10)),
                    total_losses=int((1 - champ["wr"] / 100) * (100 + hour_offset * 10)),
                    winrate_pct=champ["wr"] + wr_variance,
                    pickrate_pct=champ["pr"] + pr_variance,
                    banrate_pct=champ["pr"] * 0.5,
                    item_1_id=3089,
                    item_2_id=3156,
                    item_3_id=3001,
                    avg_kills=5.2 + (hour_offset * 0.1),
                    avg_deaths=3.1 + (hour_offset * 0.05),
                    avg_assists=8.5 + (hour_offset * 0.2),
                    avg_damage_dealt=18500 + (hour_offset * 100),
                    avg_gold_earned=12800 + (hour_offset * 50),
                    avg_vision_score=25 + hour_offset,
                )
                session.add(hourly)
        
        # Insertar anomalías
        anomaly_types = [
            AnomalyTypeEnum.WINRATE_SPIKE,
            AnomalyTypeEnum.ITEM_EMERGENCE,
            AnomalyTypeEnum.PICKRATE_SURGE,
        ]
        
        for i, champ in enumerate(champions[:3]):
            anomaly = Anomaly(
                detected_at=now - timedelta(hours=i),
                champion_name=champ["name"],
                anomaly_type=anomaly_types[i],
                previous_value=champ["wr"] - 2,
                current_value=champ["wr"],
                change_pct=2.5,
                z_score=2.1 + i * 0.1,
                confidence=0.87 + i * 0.05,
                severity=SeverityEnum.HIGH,
                description=f"{champ['name']} tiene tendencia al alza en el meta actual",
                acknowledged=False,
            )
            session.add(anomaly)
        
        # Insertar tier list
        tier_list_data = []
        for champ in champions:
            # Asignar tier basado en WR
            if champ["wr"] >= 51:
                tier = TierEnum.A
            elif champ["wr"] >= 48:
                tier = TierEnum.B
            elif champ["wr"] >= 46:
                tier = TierEnum.C
            else:
                tier = TierEnum.D
            
            tier_list_data.append({
                "champion": champ["name"],
                "tier": tier.value,
                "winrate": champ["wr"],
                "pickrate": champ["pr"],
                "banrate": champ["pr"] * 0.5,
                "trend": "RISING" if champ["wr"] > 50 else "STABLE",
                "reason": f"Campeón fuerte en el meta actual"
            })
        
        tier_list = TierList(
            snapshot_at=now,
            patch_version="14.3",
            total_matches_in_window=2400,
            tier_list_json=json.dumps(tier_list_data),
            tier_distribution=json.dumps({"S": 0, "A": 3, "B": 4, "C": 2, "D": 1}),
            active_anomalies_count=3,
        )
        session.add(tier_list)
        
        session.commit()
        print(f"✅ Datos de demo generados:")
        print(f"   - {len(champions)} ADCs trackeados")
        print(f"   - {len(champions) * 8} stats horarias (últimas 24h)")
        print(f"   - 3 anomalías detectadas")
        print(f"   - 1 tier list snapshot")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error generando datos: {e}")
    finally:
        session.close()


def generate_frontend(output_path: str = "outputs/meta-analyzer-dashboard.html"):
    """Genera el frontend dashboard"""
    print("\n" + "="*60)
    print("🎨 GENERANDO FRONTEND DASHBOARD")
    print("="*60)
    
    # Dashboard original
    save_dashboard(output_path)
    
    # Dashboard mejorado con tabs avanzados
    save_enhanced_dashboard("outputs/meta-analyzer-dashboard-enhanced.html")
    
    print(f"📱 Dashboards disponibles en:")
    print(f"   - Original: http://localhost:8000/dashboard")
    print(f"   - Enhanced: http://localhost:8000/dashboard-enhanced (RECOMENDADO)")

    

def setup_requirements():
    """Verifica e instala requerimientos"""
    print("\n" + "="*60)
    print("📦 VERIFICANDO REQUERIMIENTOS")
    print("="*60)
    
    required = ["sqlalchemy", "fastapi", "uvicorn"]
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"⚠️  Falta instalar: {package}")
            print(f"   pip install {package}")


def print_summary(db_path: str):
    """Imprime resumen del setup"""
    print("\n" + "="*60)
    print("✅ SETUP COMPLETADO")
    print("="*60)
    
    print("\n📊 Base de datos:")
    print(f"   Ubicación: {db_path}")
    print(f"   Tablas: 8 (raw_matches, champion_hourly, anomalies, tier_lists, etc)")
    
    print("\n🚀 API Backend:")
    print(f"   URL: http://localhost:8000")
    print(f"   Docs: http://localhost:8000/docs")
    print(f"   OpenAPI: http://localhost:8000/openapi.json")
    
    print("\n🎨 Frontend Dashboard:")
    print(f"   URL: http://localhost:3000 (o archivo local)")
    print(f"   Archivo: outputs/meta-analyzer-dashboard.html")
    
    print("\n📚 Endpoints principales:")
    print(f"   GET  /api/v1/tier-list/current")
    print(f"   GET  /api/v1/anomalies/high-confidence")
    print(f"   GET  /api/v1/stats/latest")
    print(f"   GET  /api/v1/dashboard/summary")
    
    print("\n🎯 Próximos pasos:")
    print(f"   1. Instalar dependencias: pip install -r requirements.txt")
    print(f"   2. LevantarAPI: python -m uvicorn src.riot_lol_cli.api_server:app --reload")
    print(f"   3. Abrir Dashboard: abre outputs/meta-analyzer-dashboard.html en navegador")
    print(f"   4. Recolectar datos: python main.py --collect-meta")
    

def main():
    parser = argparse.ArgumentParser(description="Setup LOLCLI Meta Analyzer")
    parser.add_argument("--db-path", default="data/meta_analyzer.db", help="Ruta BD")
    parser.add_argument("--demo", action="store_true", help="Generar datos demo")
    parser.add_argument("--no-frontend", action="store_true", help="No generar frontend")
    
    args = parser.parse_args()
    
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║     LOLCLI Meta Analyzer - Setup Completo               ║")
    print("║     [BD + API + Frontend]                               ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    # 1. Verificar requirements
    setup_requirements()
    
    # 2. Crear BD
    db = setup_database(args.db_path)
    
    # 3. Generar datos demo (opcional)
    if args.demo:
        generate_demo_data(db)
    
    # 4. Generar frontend
    if not args.no_frontend:
        generate_frontend()
    
    # 5. Resumen
    print_summary(args.db_path)
    
    print("\n✨ ¡Listo para usar!\n")


if __name__ == "__main__":
    main()
