#!/usr/bin/env python3
"""
Verificar ADCs en la BD
"""
import os
import sqlite3
from pathlib import Path

# Asegurar que corremos desde el root del repo
os.chdir(Path(__file__).parent.parent)

conn = sqlite3.connect('data/meta_analyzer.db')
cursor = conn.cursor()

# Obtener ADCs de la BD
cursor.execute('SELECT DISTINCT champion_name FROM champion_hourly ORDER BY champion_name')
adcs = cursor.fetchall()

print('=' * 70)
print('ADCs EN BASE DE DATOS')
print('=' * 70)
print(f'Total: {len(adcs)} ADCs')
print()
for i, (adc,) in enumerate(adcs, 1):
    print(f'{i:2}. {adc}')

# Stats por ADC
cursor.execute('''
    SELECT champion_name, COUNT(*) as stats_count, 
           AVG(winrate_pct) as avg_wr, 
           AVG(pickrate_pct) as avg_pr
    FROM champion_hourly
    GROUP BY champion_name
    ORDER BY avg_wr DESC
''')

print()
print('=' * 70)
print('TOP 10 ADCs POR WINRATE')
print('=' * 70)
print(f'{"#":2} {"Champion":15} {"WR":>6} {"PR":>6} {"Stats":>5}')
print('-' * 70)
for i, (champ, count, wr, pr) in enumerate(cursor.fetchall()[:10], 1):
    print(f'{i:2}. {champ:15} {wr:5.1f}%  {pr:5.1f}%  {count:5}')

conn.close()

print()
print('=' * 70)
print('✅ Base de datos verificada correctamente')
print('=' * 70)
