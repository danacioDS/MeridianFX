#!/usr/bin/env python3
"""
Ejecuta benchmarks reales sobre los datos OOS de walk-forward.
"""
import numpy as np
import pandas as pd
from layer2.engine import DecisionEngine
from layer3.evaluation.walk_forward import WalkForwardEvaluator
from layer3.evaluation.benchmarks import BenchmarkEvaluator


def run_benchmarks():
    print("=" * 60)
    print("MERIDIAN FX — BENCHMARKS REALES")
    print("=" * 60)
    
    engine = DecisionEngine()
    xgb_model = engine.xgb_model
    
    if not xgb_model:
        print("❌ No hay modelo XGBoost cargado")
        return
    
    evaluator = WalkForwardEvaluator(data_provider=engine.data_provider)
    benchmark = BenchmarkEvaluator()
    
    # Ejecutar walk-forward
    result = evaluator.evaluate_expanding("USD/JPY", xgb_model, horizon=5,
                                          initial_train_years=3, test_years=1,
                                          step_years=1)
    
    windows = result.get('windows', [])
    
    if not windows:
        print("❌ No se obtuvieron ventanas")
        return
    
    print(f"\n📊 BENCHMARKS POR VENTANA")
    print("=" * 60)
    
    all_benchmarks = []
    
    for w in windows:
        future_returns = np.array(w.get('future_returns', []))
        y_pred = np.array(w.get('y_pred', []))
        
        if len(future_returns) == 0:
            print(f"\n⚠️ Window {w['window']}: Sin datos de retornos futuros")
            continue
        
        # Estrategia del modelo: 1 = LONG, -1 = SHORT
        model_positions = np.where(y_pred == 1, 1.0, -1.0)
        model_returns = model_positions * future_returns
        
        # Benchmarks
        benchmarks = {
            'Model': model_returns,
            'Always Long': benchmark.always_long(future_returns) * future_returns,
            'Always Short': benchmark.always_short(future_returns) * future_returns,
            'Random 50/50': benchmark.random_50_50(future_returns) * future_returns,
        }
        
        print(f"\n📈 WINDOW {w['window']}")
        print("-" * 50)
        print(f"  Train: {w['train_size']}, Test: {w['test_size']}")
        print(f"  Período: {w['test_start']} → {w['test_end']}")
        print()
        print(f"  {'Estrategia':<15} {'Sharpe':>10} {'PF':>10} {'Return':>10} {'MaxDD':>10}")
        print(f"  {'-'*15} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
        
        for name, returns in benchmarks.items():
            metrics = benchmark.evaluate_strategy(returns, horizon=5)
            print(f"  {name:<15} {metrics['Sharpe']:>10.3f} {metrics['ProfitFactor']:>10.3f} "
                  f"{metrics['NetReturn']:>10.3f} {metrics['MaxDD']:>10.3f}")
        
        all_benchmarks.append({
            'window': w['window'],
            'benchmarks': benchmarks,
            'metrics': {name: benchmark.evaluate_strategy(returns, horizon=5) 
                       for name, returns in benchmarks.items()}
        })
    
    # Agregado
    print("\n" + "=" * 60)
    print("📊 AGREGADO (TODAS LAS VENTANAS)")
    print("=" * 60)
    
    # Combinar todos los retornos de todas las ventanas
    combined = {}
    for entry in all_benchmarks:
        for name, returns in entry['benchmarks'].items():
            if name not in combined:
                combined[name] = []
            combined[name].extend(returns)
    
    print(f"\n  {'Estrategia':<15} {'Sharpe':>10} {'PF':>10} {'Return':>10} {'MaxDD':>10}")
    print(f"  {'-'*15} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
    
    for name, returns in combined.items():
        returns_arr = np.array(returns)
        metrics = benchmark.evaluate_strategy(returns_arr, horizon=5)
        print(f"  {name:<15} {metrics['Sharpe']:>10.3f} {metrics['ProfitFactor']:>10.3f} "
              f"{metrics['NetReturn']:>10.3f} {metrics['MaxDD']:>10.3f}")
    
    # Decisión
    model_metrics = benchmark.evaluate_strategy(np.array(combined.get('Model', [])), horizon=5)
    long_metrics = benchmark.evaluate_strategy(np.array(combined.get('Always Long', [])), horizon=5)
    
    print("\n" + "=" * 60)
    print("🔬 DECISIÓN")
    print("=" * 60)
    
    if model_metrics['Sharpe'] > long_metrics['Sharpe']:
        print("  ✅ Model supera a Always Long en Sharpe")
    else:
        print(f"  ❌ Model NO supera a Always Long (Model: {model_metrics['Sharpe']:.3f} vs Long: {long_metrics['Sharpe']:.3f})")
    
    if model_metrics['Sharpe'] > 0.3 and model_metrics['ProfitFactor'] > 1.2:
        print("  ✅ Research Gate: APPROVED")
    else:
        print(f"  ❌ Research Gate: REJECTED (Sharpe: {model_metrics['Sharpe']:.3f}, PF: {model_metrics['ProfitFactor']:.3f})")


if __name__ == "__main__":
    run_benchmarks()
