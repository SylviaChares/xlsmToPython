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
print("VALIDIERUNGSTEST")
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
    from barwerte.sterbetafel import Sterbetafel, MAX_ALTER
    from barwerte import rentenbarwerte as rbw
    from barwerte import leistungsbarwerte as lbw    
    from barwerte import basisfunktionen as bf
    
    # Versuche vektorisierte Funktionen zu importieren
    try:
        from barwerte.rentenbarwerte import ae_xn_verlauf_vec, ae_xn_k, m_ae_xn_k
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
# Test-Funktionen
# =============================================================================

def test_1_berechnung(st: Sterbetafel):
    if st is None:
        print("\nTEST 1 uebersprungen (keine Sterbetafel)")
        return
    
    print("\n" + "=" * 80)
    print("Test 1: Test einzelner Funktionen mit Rückgabe einzelner Wert")
    print("=" * 80)    
    print(f"\nParameter: Alter={CONFIG.alter}, Sex={CONFIG.sex}, n={CONFIG.n}, t={CONFIG.t}, Tafel={CONFIG.tafel}, Zins={CONFIG.zins:.4%}")
        
#    # Test 
#    print(f"\n m_ae_xn_k_old:")
#    for zw in [1, 2, 4, 12]:
#        wert = rbw.m_ae_xn_k_old(CONFIG.alter, CONFIG.n, CONFIG.t, CONFIG.sex, CONFIG.zins, zw, st)
#        print(f"  wert = {wert:.12f}")
#
#    print(f"\n m_ae_xn_k:")
#    for zw in [1, 2, 4, 12]:
#        wert = (rbw.ae_xn_k(bf.verlaufswerte_setup(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.zins, st), zw) -
#            rbw.ae_xn_k(bf.verlaufswerte_setup(CONFIG.alter, CONFIG.t, CONFIG.sex, CONFIG.zins, st), zw))
#        print(f"  wert = {wert:.12f}")

    print(f"\n nqx alt:")
    wert = bf.nqx_old(CONFIG.alter, CONFIG.t, CONFIG.sex, st)
    print(f"  nqx alt = {wert:.12f}")
#
    print(f"\n nqx vec:")
    wert = bf.nqx(np.array([CONFIG.alter]), np.array([CONFIG.t]), CONFIG.sex, st)
    print(f"  nqx vec = {wert[0]:.12f}")
#
    print(f"\n nqx opt:")
    wert = bf.nqx_opt(CONFIG.alter, CONFIG.t, CONFIG.sex, st)
    print(f"  nqx opt = {wert[CONFIG.t]:.12f}")
#    
#    print(f"\n tpx_matrix:")
#    wert = bf.tpx_matrix(CONFIG.alter, CONFIG.n+1, CONFIG.sex, st)
#    #print(f"  tpx_matrix = {wert[1]:.12f}")
#    for m in range(CONFIG.n+1):
#        print(f"  m={m}: tpx_matrix = {wert[m]:.12f}")

    print("\n" + "=" * 80)
    print("Test 1: abgeschlossen")
    print("=" * 80)    


def test_2_berechnung(st: Sterbetafel) -> Dict[str, np.ndarray]:
    print("\n" + "=" * 80)
    print("Test 2: Test einzelner Funktionen mit Rückgabe Verktor")
    print("=" * 80)
    print(f"\nParameter: Alter={CONFIG.alter}, Sex={CONFIG.sex}, n={CONFIG.n}, t={CONFIG.t}, Tafel={CONFIG.tafel}, Zins={CONFIG.zins:.4%}")

    start_time = time.time()
    
    # Beitragsbarwerte

    rentenbarwerte = ae_xn_verlauf_vec(CONFIG.alter, CONFIG.t, CONFIG.sex, CONFIG.zins, CONFIG.zw, st)

    ae_xt_k_opt = rbw.ae_xn_k(CONFIG.alter, CONFIG.t, CONFIG.sex, CONFIG.zins, CONFIG.zw, st)
    ae_xn_k_opt = rbw.ae_xn_k(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.zins, CONFIG.zw, st)
    m_ae_xn_k_opt = rbw.m_ae_xn_k(CONFIG.alter, CONFIG.n, CONFIG.t, CONFIG.sex, CONFIG.zins, CONFIG.zw, st)

    elapsed = time.time() - start_time
    
    results = {
        'rentenbarwerte': rentenbarwerte,
        'ae_xn_k_opt': ae_xn_k_opt,
        'ae_xt_k_opt': ae_xt_k_opt,
        'm_ae_xn_k_opt': m_ae_xn_k_opt,
        'zeit': elapsed
    }
    
#    print(f"\n✓ Berechnung abgeschlossen")
#    print(f"  Berechnungszeit: {elapsed:.6f} Sekunden")
#    print(f"\n ae_xn_k:")
#    for m in range(min(5, CONFIG.t)):
#        print(f"  m={m}: ae_{{{CONFIG.alter+m}}}:{CONFIG.t-m} = {rentenbarwerte[m]:.12f}")
#
#    print(f"\n ae_xn_k_opt:")
#    for m in range(min(5, CONFIG.n)):
#        print(f"  m={m}: ae_{{{CONFIG.alter+m}}}:{CONFIG.n-m} = {ae_xn_k_opt[m]:.12f}")
#
#    print(f"\n ae_xt_k_opt:")
#    for m in range(min(5, CONFIG.t)):
#        print(f"  m={m}: ae_{{{CONFIG.alter+m}}}:{CONFIG.t-m} = {ae_xt_k_opt[m]:.12f}")
#
    print(f"\n m_ae_xn_k_opt:")
    print(f"  m_ae_xn_k_opt = {m_ae_xn_k_opt}")
#    for m in range(min(5, CONFIG.n)):
#        print(f"  m={m}: ae_{{{CONFIG.alter+m}}}:{CONFIG.n-m} = {m_ae_xn_k_opt[m]:.12f}")

    print("\n" + "=" * 80)
    print("Test 2: abgeschlossen")
    print("=" * 80)    
    
    return results

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
    #test_1_berechnung(st)
    standard_results = test_2_berechnung(st)
    
    


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
