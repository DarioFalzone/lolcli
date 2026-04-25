#!/usr/bin/env python3
"""
Script para obtener ADCs desde Data Dragon y actualizar el tracking
"""
import requests
import json
import os
import sys

def get_adc_champions():
    """Obtiene lista oficial de ADCs desde Data Dragon"""
    try:
        # Usar la versión más reciente disponible
        url = 'https://ddragon.leagueoflegends.com/cdn/14.1.1/data/en_US/champion.json'
        
        print("🔄 Conectando a Data Dragon...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        champions = response.json()['data']
        
        # ADCs son campeones con tag 'Marksman'
        adc_list = []
        for name, data in champions.items():
            tags = data.get('tags', [])
            if 'Marksman' in tags:
                adc_list.append(name)
        
        return sorted(adc_list)
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando a Data Dragon: {e}")
        print("\n⚠️ Usando lista hardcodeada de ADCs conocidos...")
        
        # Lista de ADCs conocida (fallback)
        return [
            'Ashe', 'Caitlyn', 'Corki', 'Draven', 'Ezreal', 'Graves', 
            'Jhin', 'Jinx', 'Kaisa', 'Kalista', 'KogMaw', 'Lucian', 
            'MissFortune', 'Samira', 'Senna', 'Seraphine', 'Sivir', 
            'Tristana', 'Twitch', 'Urgot', 'Vayne', 'Varus', 'Xayah'
        ]

def main():
    print("="*60)
    print("🎯 ADC TRACKER - Data Dragon Collector")
    print("="*60)
    print()
    
    # Obtener ADCs
    adcs = get_adc_champions()
    
    print(f"✅ Total ADCs encontrados: {len(adcs)}")
    print(f"\n📋 Lista de ADCs:")
    for i, adc in enumerate(adcs, 1):
        print(f"   {i:2}. {adc}")
    
    # Agregar Yasuo
    print(f"\n⚔️  Agregando Yasuo a la lista...")
    if 'Yasuo' not in adcs:
        adcs_with_yasuo = adcs + ['Yasuo']
    else:
        adcs_with_yasuo = adcs
    
    print(f"\n✅ Total con Yasuo: {len(adcs_with_yasuo)}")
    print(f"\n📋 Lista completa:")
    for i, adc in enumerate(sorted(adcs_with_yasuo), 1):
        print(f"   {i:2}. {adc}")
    
    # Guardar en archivo JSON
    output_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'adc_champions.json')
    output_data = {
        'adc_count': len(adcs),
        'adcs': adcs,
        'adcs_with_yasuo': sorted(adcs_with_yasuo),
        'total_with_yasuo': len(adcs_with_yasuo)
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Datos guardados en: {output_file}")
    print(f"\n🎯 Resumen:")
    print(f"   ADCs actuales: {len(adcs)}")
    print(f"   + Yasuo: 1")
    print(f"   Total tracked: {len(adcs_with_yasuo)}")
    
    return adcs_with_yasuo

if __name__ == "__main__":
    adcs = main()
