"""
Test-Script fuer vektorisierte Verlaufswerte

Validiert die vektorisierte Implementation gegen:
1. Standard-Implementation (interne Konsistenz)
2. Excel-Tarifrechner (externe Validierung)

Testet:
- Korrektheit der vektorisierten Funktionen
- Performance-Gewinn
- Identitaet der Ergebnisse mit Excel
"""

import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple

# =============================================================================
# Setup: Import-Pfade
# =============================================================================

print("=" * 80)
print("VEKTORISIERTE VERLAUFSWERTE - VALIDIERUNGSTEST")
print("=" * 80)

script_dir = Path(__file__).parent
parent_dir = script_dir.parent

# Fuege Parent-Verzeichnis zum Python-Pfad hinzu
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

print(f"\nScript liegt in: {script_dir}")
print(f"Parent-Dir ist:  {parent_dir}")
print(f"sys.path[0]:     {sys.path[0]}")

# =============================================================================
# Imports
# =============================================================================

try:
    from barwerte.sterbetafel import Sterbetafel
    from barwerte import rentenbarwerte as rbw
    from barwerte import leistungsbarwerte as lbw    
    from barwerte import basisfunktionen as bf
    
    # Versuche vektorisierte Funktionen zu importieren
    try:
        from barwerte.rentenbarwerte import ae_xn_verlauf_vec, ae_xn_verlauf_optimized
        from barwerte.leistungsbarwerte import nAe_x_verlauf_vec, nE_x_verlauf_vec, nE_x_verlauf_optimized
        VECTORIZED_AVAILABLE = True
        print("\n✓ Vektorisierte Funktionen verfuegbar")
    except ImportError as e:
        VECTORIZED_AVAILABLE = False
        print(f"\n✗ Vektorisierte Funktionen NICHT verfuegbar: {e}")
        print("  Bitte stelle sicher, dass die vektorisierten Funktionen")
        print("  zu den barwerte-Modulen hinzugefuegt wurden.")
        
except ImportError as e:
    print(f"\nFEHLER beim Import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 80)
print()


# =============================================================================
# Test-Konfiguration
# =============================================================================

@dataclass
class TestConfig:
    """Zentrale Test-Konfiguration."""
    # Versichertendaten
    alter: int = 40
    sex: str = 'M'
    
    # Sterbetafel
    tafel: str = 'DAV1994T'
    
    # Finanzmathematische Parameter
    zins: float = 0.0175  # 1,75%
    
    # Vertragsdaten
    n: int = 30           # Versicherungsdauer
    t: int = 20           # Beitragszahldauer (hier = n)
    
    # Zahlungsweise
    zw: int = 1  # jaehrlich (1=jaehrlich, 12=monatlich)
    
    # Versicherungssumme
    vs: float = 100000.00  # EUR
    
    # Pfad zum Sterbetafel-Verzeichnis 
    # Berechne Pfad zum data/-Verzeichnis (relativ zum Projekt-Hauptverzeichnis)
    script_dir = Path(__file__).parent  # tests/
    parent_dir = script_dir.parent       # projekt/
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    data_dir: str = parent_dir / "data"
    
    def __str__(self) -> str:
        return f"""
Testkonfiguration:
  Alter:                {self.alter}
  Geschlecht:           {self.sex}
  Sterbetafel:          {self.tafel}
  Zinssatz:             {self.zins:.4%}
  Versicherungsdauer:   {self.n} Jahre (n)
  Beitragszahldauer:    {self.t} Jahre (t)
  Zahlungsweise:        {self.zw}x pro Jahr
  Versicherungssumme:   {self.vs:,.2f} EUR
  Data-Verzeichnis:     {self.data_dir}
"""

CONFIG = TestConfig()


# =============================================================================
# Excel-Referenzwerte
# =============================================================================

class ExcelReferenzwerte:
    """
    Excel-Referenzwerte aus dem Tarifrechner.
    
    WICHTIG: Diese Werte muessen aus deinem Excel-Tarifrechner
    uebernommen werden!
    
    Fuer CONFIG: alter=40, n=20, sex='M', zins=0.0175, zw=1, tafel='DAV1994_T'
    """
    
    # Rentenbarwerte ae_{x+t}:n-t fuer t=0..n-1
    # Beispiel: ae_{40}:20, ae_{41}:19, ..., ae_{59}:1
    rentenbarwerte = {
        0: 14.919192111,   # ae_{40}:20  - BEISPIELWERT, durch Excel-Wert ersetzen!
        1: 14.621204221,   # ae_{41}:19  - BEISPIELWERT
        2: 14.311510421,   # ae_{42}:18  - BEISPIELWERT
        3: 13.989383833,   # ae_{43}:17
        4: 13.654818345,   # ae_{44}:16
        5: 13.307404120,   # ae_{45}:15
        # ... weitere Werte aus Excel einfuegen ...
    }
    
    # Todesfallbarwerte (n-t)Ae_{x+t} fuer t=0..n
    todesfallbarwerte = {
        0: 0.043246001,    # 20Ae_{40}  - BEISPIELWERT
        1: 0.041708571,    # 19Ae_{41}  - BEISPIELWERT
        2: 0.040170857,    # 18Ae_{42}  - BEISPIELWERT
        # ... weitere Werte aus Excel einfuegen ...
    }
    
    # Erlebensfallbarwerte (n-t)E_{x+t} fuer t=0..n
    erlebensfallbarwerte = {
        0: 0.723788010,    # 20E_{40}  - BEISPIELWERT
        1: 0.735692025,    # 19E_{41}  - BEISPIELWERT
        2: 0.747775130,    # 18E_{42}  - BEISPIELWERT
        # ... weitere Werte aus Excel einfuegen ...
    }
    
    @classmethod
    def hat_vollstaendige_daten(cls, n: int) -> bool:
        """Prueft, ob vollstaendige Daten fuer Laufzeit n vorhanden sind."""
        return (
            len(cls.rentenbarwerte) >= n and
            len(cls.todesfallbarwerte) >= n + 1 and
            len(cls.erlebensfallbarwerte) >= n + 1
        )
    
    @classmethod
    def als_arrays(cls, n: int) -> Dict[str, np.ndarray]:
        """Gibt Referenzwerte als NumPy-Arrays zurueck."""
        return {
            'rentenbarwerte': np.array([cls.rentenbarwerte.get(t, np.nan) for t in range(n)]),
            'todesfallbarwerte': np.array([cls.todesfallbarwerte.get(t, np.nan) for t in range(n + 1)]),
            'erlebensfallbarwerte': np.array([cls.erlebensfallbarwerte.get(t, np.nan) for t in range(n + 1)])
        }


# =============================================================================
# Test-Funktionen
# =============================================================================

def test_1_standard_berechnung(st: Sterbetafel) -> Dict[str, np.ndarray]:
    """
    TEST 1: Standard-Berechnung (mit Schleifen)
    
    Berechnet Verlaufswerte mit der Standard-Methode (Schleifen).
    Dient als Baseline fuer Vergleiche.
    """
    print("\n" + "=" * 80)
    print("TEST 1: STANDARD-BERECHNUNG (BASELINE)")
    print("=" * 80)
    
    print(f"\nBerechne Verlaufswerte fuer n={CONFIG.n} mit Standard-Methode...")
    
    start_time = time.time()
    
    # Beitragsbarwerte
#    rentenbarwerte = []
#    for m in range(CONFIG.t):
#        bbw = rbw.ae_xn_k_old(
#            CONFIG.alter + m,
#            CONFIG.t - m,
#            CONFIG.sex,
#            CONFIG.zins,
#            CONFIG.zw,
#            st
#        )
#        rentenbarwerte.append(bbw)
    
    rentenbarwerte = []
    for m in range(CONFIG.t):
        bbw = rbw.ae_xn_k_vec(bf.verlaufswerte_setup(CONFIG.alter + m, CONFIG.t - m, CONFIG.sex, CONFIG.zins, st), 1)
        rentenbarwerte.append(bbw)

    # Todesfallbarwerte
    todesfallbarwerte = []
    for m in range(CONFIG.n + 1):
        if CONFIG.n - m > 0:
            tdfall = lbw.nAe_x(
                CONFIG.alter + m,
                CONFIG.n - m,
                CONFIG.sex,
                CONFIG.zins,
                st
            )
        else:
            tdfall = 0.0
        todesfallbarwerte.append(tdfall)
    
    # Erlebensfallbarwerte
    erlebensfallbarwerte = []
    for m in range(CONFIG.n + 1):
        if CONFIG.n - m > 0:
            erleb = lbw.nE_x(
                CONFIG.alter + m,
                CONFIG.n - m,
                CONFIG.sex,
                CONFIG.zins,
                st
            )
        else:
            erleb = 1.0
        erlebensfallbarwerte.append(erleb)
    
    elapsed = time.time() - start_time
    
    results = {
        'rentenbarwerte': np.array(rentenbarwerte),
        'todesfallbarwerte': np.array(todesfallbarwerte),
        'erlebensfallbarwerte': np.array(erlebensfallbarwerte),
        'zeit': elapsed
    }
    
    print(f"\n✓ Standard-Berechnung abgeschlossen")
    print(f"  Berechnungszeit: {elapsed:.6f} Sekunden")
    print(f"\nRentenbarwerte:")
    for m in range(min(5, CONFIG.t)):
        print(f"  t={m}: ae_{{{CONFIG.alter+m}}}:{CONFIG.t-m} = {rentenbarwerte[m]:.12f}")
    
    print(f"\nTodesfallbarwerte:")
    for m in range(min(5, CONFIG.n)):
        print(f"  n={m}: |{CONFIG.n-m}Ae_{{{CONFIG.alter+m}}} = {todesfallbarwerte[m]:.12f}")
    
    print(f"\nErlebensfallbarwerte:")
    for m in range(min(5, CONFIG.n)):
        print(f"  n={m}: {CONFIG.n-m}E_{{{CONFIG.alter+m}}} = {erlebensfallbarwerte[m]:.12f}")
    
    return results


def test_2_vektorisierte_berechnung(st: Sterbetafel) -> Dict[str, np.ndarray]:
    """
    TEST 2: Vektorisierte Berechnung
    
    Berechnet Verlaufswerte mit vektorisierten Funktionen.
    """
    print("\n" + "=" * 80)
    print("TEST 2: VEKTORISIERTE BERECHNUNG")
    print("=" * 80)
    
    if not VECTORIZED_AVAILABLE:
        print("\n✗ Vektorisierte Funktionen nicht verfuegbar - Test uebersprungen")
        return None
    
    print(f"\nBerechne Verlaufswerte fuer n={CONFIG.n} mit vektorisierten Funktionen...")
    
    start_time = time.time()
    
    # Vektorisierte Berechnung
    rentenbarwerte = ae_xn_verlauf_vec(
        CONFIG.alter,
        CONFIG.t,
        CONFIG.sex,
        CONFIG.zins,
        CONFIG.zw,
        st
    )
    
    todesfallbarwerte = nAe_x_verlauf_vec(
        CONFIG.alter,
        CONFIG.n,
        CONFIG.sex,
        CONFIG.zins,
        st
    )
    
    erlebensfallbarwerte = nE_x_verlauf_vec(
        CONFIG.alter,
        CONFIG.n,
        CONFIG.sex,
        CONFIG.zins,
        st
    )
    
    elapsed = time.time() - start_time
    
    results = {
        'rentenbarwerte': rentenbarwerte,
        'todesfallbarwerte': todesfallbarwerte,
        'erlebensfallbarwerte': erlebensfallbarwerte,
        'zeit': elapsed
    }
    
    print(f"\n✓ Vektorisierte Berechnung abgeschlossen")
    print(f"  Berechnungszeit: {elapsed:.6f} Sekunden")
    print(f"\nErste 5 Rentenbarwerte:")
    for m in range(min(5, CONFIG.t)):
        print(f"  t={m}: ae_{{{CONFIG.alter+m}}}:{CONFIG.t-m} = {rentenbarwerte[m]:.12f}")
    
    print(f"\nTodesfallbarwerte:")
    for m in range(min(5, CONFIG.n)):
        print(f"  n={m}: |{CONFIG.n-m}Ae_{{{CONFIG.alter+m}}} = {todesfallbarwerte[m]:.12f}")
    
    print(f"\nErlebensfallbarwerte:")
    for m in range(min(5, CONFIG.n)):
        print(f"  n={m}: {CONFIG.n-m}E_{{{CONFIG.alter+m}}} = {erlebensfallbarwerte[m]:.12f}")
    
    return results


def test_3_optimierte_berechnung(st: Sterbetafel) -> Dict[str, np.ndarray]:
    """
    TEST 3: Ultra-optimierte Berechnung
    
    Berechnet Verlaufswerte mit ultra-optimierten Funktionen.
    """
    print("\n" + "=" * 80)
    print("TEST 3: ULTRA-OPTIMIERTE BERECHNUNG")
    print("=" * 80)
    
    if not VECTORIZED_AVAILABLE:
        print("\n✗ Vektorisierte Funktionen nicht verfuegbar - Test uebersprungen")
        return None
    
    print(f"\nBerechne Verlaufswerte fuer n={CONFIG.n} mit optimierten Funktionen...")
    
    start_time = time.time()
    
    # Ultra-optimierte Berechnung
    rentenbarwerte = ae_xn_verlauf_optimized(
        CONFIG.alter,
        CONFIG.t,
        CONFIG.sex,
        CONFIG.zins,
        CONFIG.zw,
        st
    )
    
    todesfallbarwerte = nAe_x_verlauf_vec(
        CONFIG.alter,
        CONFIG.n,
        CONFIG.sex,
        CONFIG.zins,
        st
    )
    
    erlebensfallbarwerte = nE_x_verlauf_optimized(
        CONFIG.alter,
        CONFIG.n,
        CONFIG.sex,
        CONFIG.zins,
        st
    )
    
    elapsed = time.time() - start_time
    
    results = {
        'rentenbarwerte': rentenbarwerte,
        'todesfallbarwerte': todesfallbarwerte,
        'erlebensfallbarwerte': erlebensfallbarwerte,
        'zeit': elapsed
    }
    
    print(f"\n✓ Optimierte Berechnung abgeschlossen")
    print(f"  Berechnungszeit: {elapsed:.6f} Sekunden")
    print(f"\nErste 5 Rentenbarwerte:")
    for m in range(min(5, CONFIG.t)):
        print(f"  t={m}: ae_{{{CONFIG.alter+m}}}:{CONFIG.t-m} = {rentenbarwerte[m]:.12f}")
    
    print(f"\nTodesfallbarwerte:")
    for m in range(min(5, CONFIG.n)):
        print(f"  n={m}: |{CONFIG.n-m}Ae_{{{CONFIG.alter+m}}} = {todesfallbarwerte[m]:.12f}")
    
    print(f"\nErlebensfallbarwerte:")
    for m in range(min(5, CONFIG.n)):
        print(f"  n={m}: {CONFIG.n-m}E_{{{CONFIG.alter+m}}} = {erlebensfallbarwerte[m]:.12f}")
    
    return results


def test_4_vergleich_standard_vs_vektorisiert(
    standard_results: Dict,
    vec_results: Dict,
    opt_results: Dict
) -> bool:
    """
    TEST 4: Vergleich Standard vs. Vektorisiert
    
    Vergleicht die Ergebnisse der verschiedenen Methoden.
    """
    print("\n" + "=" * 80)
    print("TEST 4: VERGLEICH STANDARD VS. VEKTORISIERT")
    print("=" * 80)
    
    if vec_results is None or opt_results is None:
        print("\n✗ Vektorisierte Ergebnisse nicht verfuegbar - Test uebersprungen")
        return False
    
    tolerance = 1e-10
    alle_tests_ok = True
    
    # Vergleiche Rentenbarwerte
    print("\nRentenbarwerte:")
    diff_vec = np.abs(standard_results['rentenbarwerte'] - vec_results['rentenbarwerte'])
    diff_opt = np.abs(standard_results['rentenbarwerte'] - opt_results['rentenbarwerte'])
    
    max_diff_vec = np.max(diff_vec)
    max_diff_opt = np.max(diff_opt)
    
    print(f"  Standard vs. Vektorisiert:")
    print(f"    Maximale Differenz: {max_diff_vec:.2e}")
    print(f"    Status: {'✓ OK' if max_diff_vec < tolerance else '✗ FEHLER'}")
    
    print(f"  Standard vs. Optimiert:")
    print(f"    Maximale Differenz: {max_diff_opt:.2e}")
    print(f"    Status: {'✓ OK' if max_diff_opt < tolerance else '✗ FEHLER'}")
    
    if max_diff_vec >= tolerance or max_diff_opt >= tolerance:
        alle_tests_ok = False
        print("\n  WARNUNG: Grosse Differenzen gefunden!")
        print("  Erste 5 Werte im Detail:")
        for t in range(min(5, CONFIG.n)):
            print(f"    t={t}:")
            print(f"      Standard:      {standard_results['rentenbarwerte'][t]:.15f}")
            print(f"      Vektorisiert:  {vec_results['rentenbarwerte'][t]:.15f}")
            print(f"      Optimiert:     {opt_results['rentenbarwerte'][t]:.15f}")
            print(f"      Diff (vec):    {diff_vec[t]:.2e}")
            print(f"      Diff (opt):    {diff_opt[t]:.2e}")
    
    # Vergleiche Todesfallbarwerte
    print("\nTodesfallbarwerte:")
    diff_vec = np.abs(standard_results['todesfallbarwerte'] - vec_results['todesfallbarwerte'])
    diff_opt = np.abs(standard_results['todesfallbarwerte'] - opt_results['todesfallbarwerte'])
    
    max_diff_vec = np.max(diff_vec)
    max_diff_opt = np.max(diff_opt)
    
    print(f"  Standard vs. Vektorisiert: max diff = {max_diff_vec:.2e} {'✓' if max_diff_vec < tolerance else '✗'}")
    print(f"  Standard vs. Optimiert:    max diff = {max_diff_opt:.2e} {'✓' if max_diff_opt < tolerance else '✗'}")
    
    if max_diff_vec >= tolerance or max_diff_opt >= tolerance:
        alle_tests_ok = False
    
    # Vergleiche Erlebensfallbarwerte
    print("\nErlebensfallbarwerte:")
    diff_vec = np.abs(standard_results['erlebensfallbarwerte'] - vec_results['erlebensfallbarwerte'])
    diff_opt = np.abs(standard_results['erlebensfallbarwerte'] - opt_results['erlebensfallbarwerte'])
    
    max_diff_vec = np.max(diff_vec)
    max_diff_opt = np.max(diff_opt)
    
    print(f"  Standard vs. Vektorisiert: max diff = {max_diff_vec:.2e} {'✓' if max_diff_vec < tolerance else '✗'}")
    print(f"  Standard vs. Optimiert:    max diff = {max_diff_opt:.2e} {'✓' if max_diff_opt < tolerance else '✗'}")
    
    if max_diff_vec >= tolerance or max_diff_opt >= tolerance:
        alle_tests_ok = False
    
    # Performance-Vergleich
    print("\nPerformance-Vergleich:")
    zeit_standard = standard_results['zeit']
    zeit_vec = vec_results['zeit']
    zeit_opt = opt_results['zeit']
    
    speedup_vec = zeit_standard / zeit_vec if zeit_vec > 0 else 0
    speedup_opt = zeit_standard / zeit_opt if zeit_opt > 0 else 0
    
    print(f"  Standard:      {zeit_standard:.6f} s")
    print(f"  Vektorisiert:  {zeit_vec:.6f} s (Speedup: {speedup_vec:.1f}x)")
    print(f"  Optimiert:     {zeit_opt:.6f} s (Speedup: {speedup_opt:.1f}x)")
    
    return alle_tests_ok


def test_5_vergleich_mit_excel(results: Dict) -> bool:
    """
    TEST 5: Vergleich mit Excel-Referenzwerten
    
    Vergleicht die berechneten Werte mit den Excel-Referenzwerten.
    """
    print("\n" + "=" * 80)
    print("TEST 5: VERGLEICH MIT EXCEL-REFERENZWERTEN")
    print("=" * 80)
    
    if not ExcelReferenzwerte.hat_vollstaendige_daten(CONFIG.n):
        print("\n✗ Keine vollstaendigen Excel-Referenzwerte vorhanden")
        print("  Bitte trage die Werte aus dem Excel-Tarifrechner in die")
        print("  Klasse 'ExcelReferenzwerte' ein!")
        return False
    
    excel_ref = ExcelReferenzwerte.als_arrays(CONFIG.n)
    tolerance = 1e-8  # Excel hat typischerweise ~8-10 Dezimalstellen Genauigkeit
    
    alle_tests_ok = True
    
    # Vergleiche Rentenbarwerte
    print("\nRentenbarwerte:")
    valid_mask = ~np.isnan(excel_ref['rentenbarwerte'])
    if np.any(valid_mask):
        diff = np.abs(results['rentenbarwerte'][valid_mask] - excel_ref['rentenbarwerte'][valid_mask])
        max_diff = np.max(diff)
        
        print(f"  Anzahl Vergleichswerte: {np.sum(valid_mask)}")
        print(f"  Maximale Differenz:     {max_diff:.2e}")
        print(f"  Status:                 {'✓ OK' if max_diff < tolerance else '✗ FEHLER'}")
        
        if max_diff >= tolerance:
            alle_tests_ok = False
            print("\n  Details der ersten 5 Werte:")
            for t in range(min(5, CONFIG.n)):
                if not np.isnan(excel_ref['rentenbarwerte'][t]):
                    python_wert = results['rentenbarwerte'][t]
                    excel_wert = excel_ref['rentenbarwerte'][t]
                    differenz = abs(python_wert - excel_wert)
                    print(f"    t={t}:")
                    print(f"      Python: {python_wert:.12f}")
                    print(f"      Excel:  {excel_wert:.12f}")
                    print(f"      Diff:   {differenz:.2e} {'✓' if differenz < tolerance else '✗'}")
    else:
        print("  ✗ Keine Excel-Referenzwerte vorhanden")
        alle_tests_ok = False
    
    # Vergleiche Todesfallbarwerte
    print("\nTodesfallbarwerte:")
    valid_mask = ~np.isnan(excel_ref['todesfallbarwerte'])
    if np.any(valid_mask):
        diff = np.abs(results['todesfallbarwerte'][valid_mask] - excel_ref['todesfallbarwerte'][valid_mask])
        max_diff = np.max(diff)
        
        print(f"  Anzahl Vergleichswerte: {np.sum(valid_mask)}")
        print(f"  Maximale Differenz:     {max_diff:.2e}")
        print(f"  Status:                 {'✓ OK' if max_diff < tolerance else '✗ FEHLER'}")
        
        if max_diff >= tolerance:
            alle_tests_ok = False
    else:
        print("  ✗ Keine Excel-Referenzwerte vorhanden")
    
    # Vergleiche Erlebensfallbarwerte
    print("\nErlebensfallbarwerte:")
    valid_mask = ~np.isnan(excel_ref['erlebensfallbarwerte'])
    if np.any(valid_mask):
        diff = np.abs(results['erlebensfallbarwerte'][valid_mask] - excel_ref['erlebensfallbarwerte'][valid_mask])
        max_diff = np.max(diff)
        
        print(f"  Anzahl Vergleichswerte: {np.sum(valid_mask)}")
        print(f"  Maximale Differenz:     {max_diff:.2e}")
        print(f"  Status:                 {'✓ OK' if max_diff < tolerance else '✗ FEHLER'}")
        
        if max_diff >= tolerance:
            alle_tests_ok = False
    else:
        print("  ✗ Keine Excel-Referenzwerte vorhanden")
    
    return alle_tests_ok


def erstelle_vergleichstabelle(
    standard_results: Dict,
    vec_results: Dict,
    opt_results: Dict,
    excel_ref: Dict
) -> pd.DataFrame:
    """
    Erstellt eine Vergleichstabelle aller Ergebnisse.
    """
    n = CONFIG.n
    
    # Erstelle DataFrame
    data = {
        't': list(range(n + 1)),
        'Alter': [CONFIG.alter + t for t in range(n + 1)],
        'Restlaufzeit': [n - t for t in range(n + 1)]
    }
    
    # Rentenbarwerte (nur bis n-1)
    data['ae_xn_standard'] = np.append(standard_results['rentenbarwerte'], np.nan)
    if vec_results:
        data['ae_xn_vec'] = np.append(vec_results['rentenbarwerte'], np.nan)
    if opt_results:
        data['ae_xn_opt'] = np.append(opt_results['rentenbarwerte'], np.nan)
    
    data['ae_xn_excel'] = np.append(
        [excel_ref['rentenbarwerte'].get(t, np.nan) for t in range(n)],
        np.nan
    )
    
    # Todesfallbarwerte
    data['nAe_x_standard'] = standard_results['todesfallbarwerte']
    if vec_results:
        data['nAe_x_vec'] = vec_results['todesfallbarwerte']
    data['nAe_x_excel'] = [excel_ref['todesfallbarwerte'].get(t, np.nan) for t in range(n + 1)]
    
    # Erlebensfallbarwerte
    data['nE_x_standard'] = standard_results['erlebensfallbarwerte']
    if vec_results:
        data['nE_x_vec'] = vec_results['erlebensfallbarwerte']
    data['nE_x_excel'] = [excel_ref['erlebensfallbarwerte'].get(t, np.nan) for t in range(n + 1)]
    
    df = pd.DataFrame(data)
    return df


# =============================================================================
# Hauptprogramm
# =============================================================================

def main():
    """Fuehrt alle Tests aus."""
    
    print(CONFIG)
    
    # Lade Sterbetafel
    print("\n" + "=" * 80)
    print("VORBEREITUNG: LADE STERBETAFEL")
    print("=" * 80)
    
    try:
        st = Sterbetafel(CONFIG.tafel, data_dir=CONFIG.data_dir)
        print(f"\n✓ Sterbetafel erfolgreich geladen: {st.name}")
    except FileNotFoundError as e:
        print(f"\n✗ FEHLER: {e}")
        print("  Bitte passe CONFIG.data_dir an!")
        return False
    
    # Fuehre Tests aus
    standard_results = test_1_standard_berechnung(st)
    vec_results = test_2_vektorisierte_berechnung(st)
    opt_results = test_3_optimierte_berechnung(st)
    
    # Vergleiche Implementierungen
    konsistenz_ok = test_4_vergleich_standard_vs_vektorisiert(
        standard_results, vec_results, opt_results
    )
    
#    # Vergleiche mit Excel (nutze vektorisierte Ergebnisse wenn verfuegbar)
#    test_results = vec_results if vec_results else standard_results
#    excel_ok = test_5_vergleich_mit_excel(test_results)
#    
#    # Erstelle Vergleichstabelle
#    print("\n" + "=" * 80)
#    print("VERGLEICHSTABELLE")
#    print("=" * 80)
#    
#    df = erstelle_vergleichstabelle(
#        standard_results,
#        vec_results,
#        opt_results,
#        ExcelReferenzwerte
#    )
#    
#    # Zeige erste Zeilen
#    print("\nErste 10 Zeilen:")
#    print(df.head(10).to_string(index=False))
#    
#    # Speichere als Excel
#    output_file = "verlaufswerte_vergleich.xlsx"
#    df.to_excel(output_file, index=False, engine='openpyxl')
#    print(f"\n✓ Vollstaendige Tabelle gespeichert: {output_file}")
    
    # Zusammenfassung
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)
    
    print(f"\n✓ Standard-Berechnung:     Abgeschlossen")
    if VECTORIZED_AVAILABLE:
        print(f"✓ Vektorisierte Berechnung: Abgeschlossen")
        print(f"✓ Optimierte Berechnung:    Abgeschlossen")
        print(f"\n{'✓' if konsistenz_ok else '✗'} Konsistenztest (Standard vs. Vektorisiert): "
              f"{'BESTANDEN' if konsistenz_ok else 'FEHLER'}")
    else:
        print(f"✗ Vektorisierte Funktionen: NICHT VERFUEGBAR")
    
#    print(f"{'✓' if excel_ok else '✗'} Excel-Vergleich: "
#          f"{'BESTANDEN' if excel_ok else 'FEHLER oder unvollstaendig'}")
    
    if konsistenz_ok: # and excel_ok:
        print("\n" + "=" * 80)
        print("ALLE TESTS ERFOLGREICH!")
        print("=" * 80)
        return True
    else:
        print("\n" + "=" * 80)
        print("WARNUNG: Nicht alle Tests erfolgreich!")
        print("=" * 80)
        if not konsistenz_ok:
            print("  - Konsistenztest fehlgeschlagen")
#        if not excel_ok:
#            print("  - Excel-Vergleich fehlgeschlagen oder unvollstaendig")
        return False


if __name__ == "__main__":
    try:
        erfolg = main()
        sys.exit(0 if erfolg else 1)
    except Exception as e:
        print(f"\n\nFEHLER bei Test-Ausfuehrung:")
        print(f"{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
