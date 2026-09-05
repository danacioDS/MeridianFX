## 🚀 **CÓDIGOS PARA LEVANTAR BACKEND Y FRONTEND**

---

## 📦 **1. LEVANTAR BACKEND**

cd ~/repo_lab/MeridianFX/backend

# Activar entorno virtual
source venv/bin/activate

# Iniciar el backend
uvicorn layer1.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📦 **2. LEVANTAR FRONTEND**

cd ~/repo_lab/MeridianFX/frontend

# Iniciar el frontend
npm run dev

---

## 📦 **3. LEVANTAR AMBOS (COMANDO ÚNICO)**

```bash
#!/bin/bash
# Levantar Meridian FX completo

echo "=========================================="
echo "  🚀 LEVANTANDO MERIDIAN FX"
echo "=========================================="

# 1. Backend
echo "1. Iniciando backend..."
cd ~/repo_lab/MeridianFX/backend
source venv/bin/activate
uvicorn layer1.main:app --reload --host 0.0.0.0 --port 8000 &
sleep 3

# 2. Verificar backend
echo "2. Verificando backend..."
curl -s http://localhost:8000/health && echo " ✅ Backend OK" || echo " ❌ Backend FAILED"

# 3. Frontend
echo "3. Iniciando frontend..."
cd ~/repo_lab/MeridianFX/frontend
npm run dev &
sleep 3

# 4. Verificar frontend
echo "4. Verificando frontend..."
curl -s http://localhost:5174 > /dev/null && echo " ✅ Frontend OK (http://localhost:5174)" || echo " ❌ Frontend FAILED"

echo "=========================================="
echo "  ✅ MERIDIAN FX LEVANTADO"
echo "=========================================="
echo ""
echo "📊 Backend: http://localhost:8000"
echo "🎨 Frontend: http://localhost:5174"
echo "📝 API Docs: http://localhost:8000/docs"
echo ""
echo "Presiona Ctrl+C para detener"
```

---

## 📦 **4. DETENER LOS PROCESOS**

```bash
# Detener backend
pkill -9 -f uvicorn

# Detener frontend
pkill -9 -f vite

# Detener ambos
pkill -9 -f "uvicorn|vite"
```

---

## 📦 **5. VERIFICAR QUE ESTÁ CORRIENDO**

```bash
# Verificar backend
curl -s http://localhost:8000/health

# Verificar frontend
curl -s http://localhost:5174 | head -5

# Verificar procesos
ps aux | grep -E "uvicorn|vite" | grep -v grep
```

---

## 📦 **6. COMANDO RÁPIDO (COPIA Y PEGA)**

```bash
# Levantar backend
cd ~/repo_lab/MeridianFX/backend && source venv/bin/activate && uvicorn layer1.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
# Levantar frontend (en otra terminal)
cd ~/repo_lab/MeridianFX/frontend && npm run dev
```

---

## 📋 **RESUMEN**

| Componente | Comando | URL |
|------------|---------|-----|
| **Backend** | `cd ~/repo_lab/MeridianFX/backend && source venv/bin/activate && uvicorn layer1.main:app --reload --host 0.0.0.0 --port 8000` | http://localhost:8000 |
| **Frontend** | `cd ~/repo_lab/MeridianFX/frontend && npm run dev` | http://localhost:5174 |
| **API Docs** | - | http://localhost:8000/docs |

---

**¡Listo! El sistema está corriendo.** 🚀