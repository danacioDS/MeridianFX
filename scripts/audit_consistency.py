import requests
import json

BASE_URL = "http://localhost:8000"

def audit_pair(pair):
    print(f"\n🔍 AUDITANDO: {pair}")
    print("=" * 50)
    
    # 1. Forecast
    try:
        resp = requests.get(f"{BASE_URL}/v1/fx/{pair}/forecast", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            prob = data.get("prediction", {}).get("probability")
            direction = data.get("prediction", {}).get("direction")
            print(f"📊 /forecast    → {direction} (p={prob:.6f})")
        else:
            print(f"❌ /forecast    → HTTP {resp.status_code}")
    except Exception as e:
        print(f"❌ /forecast    → ERROR: {e}")

    # 2. Drivers
    try:
        resp = requests.get(f"{BASE_URL}/v1/fx/{pair}/drivers", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            prob = data.get("forecast", {}).get("probability")
            direction = data.get("forecast", {}).get("direction")
            model = data.get("model_type")
            print(f"🔍 /drivers     → {direction} (p={prob:.6f}) | model={model}")
        else:
            print(f"❌ /drivers     → HTTP {resp.status_code}")
    except Exception as e:
        print(f"❌ /drivers     → ERROR: {e}")

    # 3. Ranking
    try:
        resp = requests.get(f"{BASE_URL}/v1/fx/ranking", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("ranking", []):
                if item.get("pair") == pair:
                    prob = item.get("probability")
                    direction = item.get("direction")
                    print(f"🏆 /ranking     → {direction} (p={prob:.6f})")
                    break
        else:
            print(f"❌ /ranking     → HTTP {resp.status_code}")
    except Exception as e:
        print(f"❌ /ranking     → ERROR: {e}")

if __name__ == "__main__":
    pairs = ["USD/CNY", "EUR/USD", "USD/JPY", "USD/MXN"]
    for pair in pairs:
        audit_pair(pair)
