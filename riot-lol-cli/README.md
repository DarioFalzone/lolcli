# riot-lol-cli

CLI simple en Python para consultar la API de League of Legends (Riot) y obtener:

- Nombre de invocador
- Nivel de invocador
- Historial de partidas (ids) y resumen por partida

Usa los endpoints Summoner-V4 y Match-V5.

Además permite exportar la información a HTML con plantillas bonitas (p. ej. "gpt5-medium").

## Requisitos
- Python 3.9+
- Una API Key vigente desde https://developer.riotgames.com/ (token de desarrollador personal, expira cada 24h)

## Instalación
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configurar API Key
Puedes pasarla por variable de entorno o por argumento:

- Variable de entorno:
  ```bash
  export RIOT_API_KEY="tu_api_key"
  ```
- O como argumento `--api-key` al ejecutar.

Opcionalmente, copia `.env.example` a `.env` y exporta manualmente.

## Uso
Ejemplos:
```bash
# Mostrar info y últimas 10 partidas (por defecto)
python main.py --platform la2 --summoner "TuNombre"

# Limitar a 5 partidas y pasar API key por argumento
python main.py --platform la2 --summoner "TuNombre" --count 5 --api-key "$RIOT_API_KEY"

# Usar Riot ID con tag (nombre#tag)
python main.py --platform la2 --summoner "nombre#tag" --count 10

# Último mes completo (ignora --count)
python main.py --platform la2 --summoner "nombre#tag" --last-month
```

- `--platform` es la ruta de plataforma (ej: `la2`, `la1`, `na1`, `br1`, `euw1`, `eun1`, `tr1`, `ru`, `kr`, `jp1`, `oc1`).
- Internamente se mapea a la ruta regional para Match-V5 (`americas`, `europe`, `asia`).

## Qué hace
1. Consulta Summoner-V4:
   - `GET https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}`
   - Extrae `name`, `summonerLevel` y `puuid`.
2. Consulta Match-V5 (ruta regional):
   - `GET https://{regional}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=N`
   - Para cada `matchId`, `GET https://{regional}.api.riotgames.com/lol/match/v5/matches/{matchId}` y resume tu desempeño.

Además, si pasas `nombre#tag`, resuelve primero via Account-V1:
- `GET https://{regional}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}` → `puuid`
- Luego Summoner-V4 por PUUID.

## Plataformas soportadas y región derivada
- americas: `na1`, `br1`, `la1`, `la2`, `oc1`
- europe: `euw1`, `eun1`, `tr1`, `ru`
- asia: `kr`, `jp1`

## Nota sobre límites de tasa (429)
Se implementa reintento básico con `Retry-After` cuando esté presente. Si recibes muchos 429, espera o reduce la frecuencia de consultas.

## Salida esperada (ejemplo)
```
Invocador: TuNombre (Nivel 123) - Plataforma la2
Últimas 5 partidas:
- 2025-10-08 18:12 | ARAM | Lux | 12/3/18 | Win | LA2_1234567890
- 2025-10-08 17:40 | CLASSIC | Ahri | 8/5/9 | Loss | LA2_0987654321
```

## Exportar a HTML
- Usa `--html-template` para generar un archivo HTML con una plantilla.
- El archivo se genera en `out/<plantilla>/<slug>-<plantilla>.html`.

Ejemplos:
```bash
# Plantilla gpt5-medium (admite variantes de nombre: "gpt 5 medium", "gpt-5-medium")
python main.py --platform la2 --summoner "nombre#tag" --count 10 --html-template "gpt 5 medium"

# Cambiar directorio de salida
python main.py --platform la2 --summoner "nombre#tag" --html-template gpt5-medium --out-dir export

# Combinar con último mes
python main.py --platform la2 --summoner "nombre#tag" --last-month --html-template gpt5-medium
```

Plantillas disponibles inicialmente:
- `gpt5-medium`

## Problemas comunes
- 401/403: API key inválida o expirada.
- 404: invocador no encontrado (verifica `--platform` y nombre exacto).
- 429: límite de tasa excedido; reintenta luego.
