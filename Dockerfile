FROM python:3.12-slim

WORKDIR /app

# Copiar requirements.txt
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY backend/ ./backend/

# Exponer puerto
EXPOSE 10000

# Comando para iniciar
CMD ["uvicorn", "backend.layer1.main:app", "--host", "0.0.0.0", "--port", "10000"]
