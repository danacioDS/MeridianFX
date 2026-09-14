FROM python:3.12-slim

WORKDIR /app

# Copiar requirements.txt y instalar dependencias
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar TODO el código de backend (incluyendo layer1, layer2, etc.)
COPY backend/ ./backend/

# Copiar models/ a la raíz del contenedor.
# engine._load_canonical_model lee "models/canonical/*.joblib" relativo
# al CWD (/app), y StatusEngine lee "models/registry.json". Sin esta copia
# el canonical pipeline cae al fallback heurístico en producción.
COPY models/ ./models/

# Establecer PYTHONPATH para que Python encuentre los módulos
# /app permite resolver "models/..." desde la raíz del contenedor.
ENV PYTHONPATH=/app/backend:/app

# Exponer puerto
EXPOSE 10000

# Comando para iniciar la aplicación
CMD ["uvicorn", "layer1.main:app", "--host", "0.0.0.0", "--port", "10000"]
