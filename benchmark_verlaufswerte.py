"""
Benchmark-Skript: Standard vs. Vektorisierte Verlaufswerte

Vergleicht die Performance zwischen:
1. Standard-Implementation (mit Schleifen)
2. Vektorisierte Implementation
3. Ultra-optimierte Implementation

Demonstriert den massiven Performance-Gewinn durch Vektorisierung.
"""

import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# Imports (passe an deine Struktur an)
try:
    from barwerte.sterbetafel import Sterbetafel
    from barwerte import rentenbarwerte as rbw
    from barwerte import leistungsbarwerte as lbw
    
    # Versuche vektorisierte Funktionen zu importieren
    try:
        from barwerte.rentenbarwerte import ae_xn_verlauf_vec, ae_xn_verlauf_optimized
        from barwerte.leistungsbarwerte import nAe_x_verlauf_vec, nE_x_verlauf_optimized
        VECTORIZED_AVAILABLE = True
    except ImportError:
        VECTORIZED_AVAILABLE = False
        print("WARNUNG: Vektorisierte Funktionen nicht verfuegbar.")
    
except ImportError as e:
    print(f"Fehler beim Import: {e}")
    sys.exit(1)


# =============================================================================
# Benchmark-Konfiguration
# =============================================================================

BENCHMARK_CONFIG = {
    'alter': 40,
    'sex': 'M',
    'zins': 0.0175,
    'zw': 1,
    'tafel': 'DAV1994_T',
    'data_dir': 'data'
}

# Test verschiedene Laufzeiten
TEST_N_VALUES = [5, 10, 15, 20, 30, 50]


# =============================================================================
# Benchmark-Funktionen
# =============================================================================

def benchmark_standard(alter, n, sex, zins, zw, st, warmup=False):
    """Benchmark: Standard-Implementation mit Schleifen."""
    if warmup:
        # Warmup-Lauf (wird nicht gemessen)
        for i in range(min(3, n)):
            _ = rbw.ae_xn_k(alter + i, n - i, sex, zins, zw, st)
        return 0.0
    
    start = time.time()
    
    # Rentenbarwerte
    rentenbarwerte = []
    for i in range(n):
        bbw = rbw.ae_xn_k(alter + i, n - i, sex, zins, zw, st)
        rentenbarwerte.append(bbw)
    
    # Todesfallbarwerte
    todesfallbarwerte = []
    for i in range(n + 1):
        if n - i > 0:
            tdfall = lbw.nAe_x(alter + i, n - i, sex, zins, st)
        else:
            tdfall = 0.0
        todesfallbarwerte.append(tdfall)
    
    # Erlebensfallbarwerte
    erlebensfallbarwerte = []
    for i in range(n + 1):
        if n - i > 0:
            erleb = lbw.nE_x(alter + i, n - i, sex, zins, st)
        else:
            erleb = 1.0
        erlebensfallbarwerte.append(erleb)
    
    elapsed = time.time() - start
    
    return elapsed


def benchmark_vectorized(alter, n, sex, zins, zw, st, warmup=False):
    """Benchmark: Vektorisierte Implementation."""
    if not VECTORIZED_AVAILABLE:
        return None
    
    if warmup:
        # Warmup-Lauf
        _ = ae_xn_verlauf_vec(alter, min(3, n), sex, zins, zw, st)
        return 0.0
    
    start = time.time()
    
    # Alle Barwerte vektorisiert berechnen
    rentenbarwerte = ae_xn_verlauf_vec(alter, n, sex, zins, zw, st)
    todesfallbarwerte = nAe_x_verlauf_vec(alter, n, sex, zins, st)
    erlebensfallbarwerte = nE_x_verlauf_vec(alter, n, sex, zins, st)
    
    elapsed = time.time() - start
    
    return elapsed


def benchmark_optimized(alter, n, sex, zins, zw, st, warmup=False):
    """Benchmark: Ultra-optimierte Implementation."""
    if not VECTORIZED_AVAILABLE:
        return None
    
    if warmup:
        # Warmup-Lauf
        _ = ae_xn_verlauf_optimized(alter, min(3, n), sex, zins, zw, st)
        return 0.0
    
    start = time.time()
    
    # Alle Barwerte ultra-optimiert berechnen
    rentenbarwerte = ae_xn_verlauf_optimized(alter, n, sex, zins, zw, st)
    todesfallbarwerte = nAe_x_verlauf_vec(alter, n, sex, zins, st)
    erlebensfallbarwerte = nE_x_verlauf_optimized(alter, n, sex, zins, st)
    
    elapsed = time.time() - start
    
    return elapsed


# =============================================================================
# Hauptprogramm
# =============================================================================

def run_benchmarks():
    """Fuehrt alle Benchmarks aus und erstellt Vergleiche."""
    
    print("\n" + "=" * 80)
    print("PERFORMANCE-BENCHMARK: STANDARD VS. VEKTORISIERT")
    print("=" * 80)
    
    # Lade Sterbetafel
    st = Sterbetafel(BENCHMARK_CONFIG['tafel'], BENCHMARK_CONFIG['data_dir'])
    print(f"\nSterbetafel geladen: {st.name}")
    print(f"Konfiguration:")
    for key, value in BENCHMARK_CONFIG.items():
        print(f"  {key:15s}: {value}")
    
    # Ergebnis-Speicher
    results = {
        'n': [],
        'standard': [],
        'vectorized': [],
        'optimized': [],
        'speedup_vec': [],
        'speedup_opt': []
    }
    
    print("\n" + "=" * 80)
    print("BENCHMARK-LAEUFE")
    print("=" * 80)
    
    for n in TEST_N_VALUES:
        print(f"\n--- Laufzeit n = {n} ---")
        
        # Warmup-Laeufe
        benchmark_standard(
            BENCHMARK_CONFIG['alter'], n, BENCHMARK_CONFIG['sex'],
            BENCHMARK_CONFIG['zins'], BENCHMARK_CONFIG['zw'], st, warmup=True
        )
        
        if VECTORIZED_AVAILABLE:
            benchmark_vectorized(
                BENCHMARK_CONFIG['alter'], n, BENCHMARK_CONFIG['sex'],
                BENCHMARK_CONFIG['zins'], BENCHMARK_CONFIG['zw'], st, warmup=True
            )
            benchmark_optimized(
                BENCHMARK_CONFIG['alter'], n, BENCHMARK_CONFIG['sex'],
                BENCHMARK_CONFIG['zins'], BENCHMARK_CONFIG['zw'], st, warmup=True
            )
        
        # Eigentliche Messungen (mehrere Durchlaeufe fuer Stabilitaet)
        num_runs = 3 if n <= 20 else 1
        
        # Standard
        standard_times = []
        for _ in range(num_runs):
            t = benchmark_standard(
                BENCHMARK_CONFIG['alter'], n, BENCHMARK_CONFIG['sex'],
                BENCHMARK_CONFIG['zins'], BENCHMARK_CONFIG['zw'], st
            )
            standard_times.append(t)
        time_standard = np.mean(standard_times)
        
        # Vektorisiert
        if VECTORIZED_AVAILABLE:
            vec_times = []
            for _ in range(num_runs):
                t = benchmark_vectorized(
                    BENCHMARK_CONFIG['alter'], n, BENCHMARK_CONFIG['sex'],
                    BENCHMARK_CONFIG['zins'], BENCHMARK_CONFIG['zw'], st
                )
                vec_times.append(t)
            time_vec = np.mean(vec_times)
            
            # Optimiert
            opt_times = []
            for _ in range(num_runs):
                t = benchmark_optimized(
                    BENCHMARK_CONFIG['alter'], n, BENCHMARK_CONFIG['sex'],
                    BENCHMARK_CONFIG['zins'], BENCHMARK_CONFIG['zw'], st
                )
                opt_times.append(t)
            time_opt = np.mean(opt_times)
            
            speedup_vec = time_standard / time_vec if time_vec > 0 else 0
            speedup_opt = time_standard / time_opt if time_opt > 0 else 0
        else:
            time_vec = None
            time_opt = None
            speedup_vec = None
            speedup_opt = None
        
        # Speichere Ergebnisse
        results['n'].append(n)
        results['standard'].append(time_standard)
        results['vectorized'].append(time_vec)
        results['optimized'].append(time_opt)
        results['speedup_vec'].append(speedup_vec)
        results['speedup_opt'].append(speedup_opt)
        
        # Ausgabe
        print(f"  Standard:     {time_standard:.6f} s")
        if VECTORIZED_AVAILABLE:
            print(f"  Vektorisiert: {time_vec:.6f} s (Speedup: {speedup_vec:.1f}x)")
            print(f"  Optimiert:    {time_opt:.6f} s (Speedup: {speedup_opt:.1f}x)")
    
    # Erstelle Zusammenfassung
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)
    
    df = pd.DataFrame(results)
    print("\n", df.to_string(index=False))
    
    # Speichere als CSV
    df.to_csv("benchmark_results.csv", index=False)
    print("\nErgebnisse gespeichert: benchmark_results.csv")
    
    # Erstelle Visualisierung (wenn moeglich)
    try:
        create_benchmark_plots(df)
        print("Visualisierung gespeichert: benchmark_plots.png")
    except Exception as e:
        print(f"Konnte Visualisierung nicht erstellen: {e}")
    
    return df


def create_benchmark_plots(df):
    """Erstellt Visualisierung der Benchmark-Ergebnisse."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Absolute Zeiten
    ax1.plot(df['n'], df['standard'], 'o-', label='Standard', linewidth=2)
    if VECTORIZED_AVAILABLE:
        ax1.plot(df['n'], df['vectorized'], 's-', label='Vektorisiert', linewidth=2)
        ax1.plot(df['n'], df['optimized'], '^-', label='Optimiert', linewidth=2)
    
    ax1.set_xlabel('Laufzeit n (Jahre)', fontsize=12)
    ax1.set_ylabel('Berechnungszeit (Sekunden)', fontsize=12)
    ax1.set_title('Absolute Berechnungszeiten', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    
    # Plot 2: Speedup
    if VECTORIZED_AVAILABLE:
        ax2.plot(df['n'], df['speedup_vec'], 's-', label='Vektorisiert', linewidth=2)
        ax2.plot(df['n'], df['speedup_opt'], '^-', label='Optimiert', linewidth=2)
        ax2.axhline(y=1, color='r', linestyle='--', alpha=0.5, label='Baseline')
        
        ax2.set_xlabel('Laufzeit n (Jahre)', fontsize=12)
        ax2.set_ylabel('Speedup (x-fach schneller)', fontsize=12)
        ax2.set_title('Performance-Gewinn vs. Standard', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('benchmark_plots.png', dpi=150)
    print("\nVisualisierung erstellt: benchmark_plots.png")


# =============================================================================
# Validation: Pruefe Korrektheit der Ergebnisse
# =============================================================================

def validate_results():
    """
    Prueft, ob vektorisierte und Standard-Funktionen identische Ergebnisse liefern.
    """
    print("\n" + "=" * 80)
    print("VALIDIERUNG: KORREKTHEIT DER ERGEBNISSE")
    print("=" * 80)
    
    if not VECTORIZED_AVAILABLE:
        print("\nVektorisierte Funktionen nicht verfuegbar - Validierung uebersprungen.")
        return
    
    st = Sterbetafel(BENCHMARK_CONFIG['tafel'], BENCHMARK_CONFIG['data_dir'])
    n = 20
    alter = BENCHMARK_CONFIG['alter']
    sex = BENCHMARK_CONFIG['sex']
    zins = BENCHMARK_CONFIG['zins']
    zw = BENCHMARK_CONFIG['zw']
    
    print(f"\nTest mit n={n}, Alter={alter}, Sex={sex}, Zins={zins}, zw={zw}")
    
    # Berechne mit Standard-Methode
    print("\nBerechne mit Standard-Methode...")
    standard_renten = []
    for i in range(n):
        bbw = rbw.ae_xn_k(alter + i, n - i, sex, zins, zw, st)
        standard_renten.append(bbw)
    standard_renten = np.array(standard_renten)
    
    # Berechne mit vektorisierter Methode
    print("Berechne mit vektorisierter Methode...")
    vec_renten = ae_xn_verlauf_vec(alter, n, sex, zins, zw, st)
    
    # Berechne mit optimierter Methode
    print("Berechne mit optimierter Methode...")
    opt_renten = ae_xn_verlauf_optimized(alter, n, sex, zins, zw, st)
    
    # Vergleiche
    diff_vec = np.abs(standard_renten - vec_renten)
    diff_opt = np.abs(standard_renten - opt_renten)
    
    max_diff_vec = np.max(diff_vec)
    max_diff_opt = np.max(diff_opt)
    
    print(f"\nMaximale Abweichung (Vektorisiert): {max_diff_vec:.2e}")
    print(f"Maximale Abweichung (Optimiert):    {max_diff_opt:.2e}")
    
    tolerance = 1e-10
    
    if max_diff_vec < tolerance and max_diff_opt < tolerance:
        print("\n✓ VALIDIERUNG ERFOLGREICH: Alle Methoden liefern identische Ergebnisse!")
    else:
        print("\n✗ WARNUNG: Abweichungen gefunden!")
        print("\nErste 5 Werte im Vergleich:")
        for i in range(min(5, n)):
            print(f"  t={i}: Standard={standard_renten[i]:.12f}, "
                  f"Vec={vec_renten[i]:.12f}, "
                  f"Opt={opt_renten[i]:.12f}")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("PERFORMANCE-BENCHMARK: VERLAUFSWERTE")
    print("=" * 80)
    
    # Pruefe Verfuegbarkeit
    if not VECTORIZED_AVAILABLE:
        print("\nWARNUNG: Vektorisierte Funktionen nicht verfuegbar!")
        print("Bitte stelle sicher, dass die vektorisierten Module korrekt")
        print("in das barwerte-Package integriert wurden.")
        print("\nBenchmark wird trotzdem ausgefuehrt (nur Standard-Methode).")
    
    try:
        # Validierung
        validate_results()
        
        # Benchmarks
        results = run_benchmarks()
        
        print("\n" + "=" * 80)
        print("BENCHMARK ABGESCHLOSSEN")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n\nFEHLER: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
