#!/bin/bash

echo "🔧 Reemplazando .toFixed() por safeFormat()..."

# Lista de archivos críticos a modificar
FILES=(
  "src/pages/GlobalPage.tsx"
  "src/pages/PricePage.tsx"
  "src/pages/DriversPage.tsx"
  "src/pages/ModelComparisonPage.tsx"
  "src/components/global/RankingTable.tsx"
  "src/components/global/RankingCard.tsx"
  "src/components/forecast/SpotCard.tsx"
  "src/components/forecast/ForecastCard.tsx"
  "src/components/forecast/FanChart.tsx"
  "src/components/macro/MacroPanel.tsx"
)

for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "📝 Procesando $file..."
    # Añadir import si no existe
    if ! grep -q "from.*utils/format" "$file"; then
      sed -i '1iimport { safeFormat } from "../utils/format";' "$file"
    fi
    # Reemplazar .toFixed( con safeFormat(
    sed -i 's/\.toFixed(/safeFormat(/g' "$file"
  else
    echo "⚠️ $file no encontrado"
  fi
done

echo "✅ ¡Completado! Ahora ejecuta: npm run build"
