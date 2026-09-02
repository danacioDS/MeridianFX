FROM python:3.12-slim

WORKDIR /app

# Copiar requirements.txt y instalar dependencias
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar TODO el código de backend (incluyendo layer1, layer2, etc.)
COPY backend/ ./backend/

# Establecer PYTHONPATH para que Python encuentre los módulos
ENV PYTHONPATH=/app/backend

# Exponer puerto
EXPOSE 10000

# Comando para iniciar la aplicación
CMD ["uvicorn", "layer1.main:app", "--host", "0.0.0.0", "--port", "10000"]
