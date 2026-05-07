#!/bin/bash
# Mapa breve de documentacion canonica del repo.

cat << 'EOF'

LOLCLI - DOCUMENTACION CANONICA

1. Contexto maestro para agentes
   - AGENTS.md
   - .agent/rules/documentation-protocol.md

2. Indice general
   - docs/README.md
   - projects/README.md

3. Subsistemas activos
   - docs/meta_analyzer/README.md
   - docs/dashboard/README.md
   - docs/draft_advisor/
   - docs/splash-viewer.md

4. Archivo historico
   - _archive/README.md

Regla operativa:
Despues de cada iteracion significativa, revisar si AGENTS.md,
projects/README.md o docs/README.md necesitan quedar alineados.

EOF
