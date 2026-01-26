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

# Setup: Import-Pfade
# Damit Python die Module barwerte/ und verlaufswerte_verctorized.py findet
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
    from verlaufswerte import (
        Verlaufswerte, 
        VerlaufswerteConfig, 
        berechne_verlaufswerte,
        berechne_reserve
    )        
except ImportError as e:
    print(f"\nFEHLER beim Import: {e}")
    print("\nStelle sicher, dass folgende Struktur vorhanden ist:")
    print("  projekt/")
    print("    ├── barwerte/                    # Package")
    print("    ├── verlaufswerte_vectorized.py  # Modul")
    print("    └── tests/")
    print("        └── test_verlaufswerte_vectorized.py")
    print(f"\nAktuelles Verzeichnis: {Path.cwd()}")
    print(f"Script-Verzeichnis: {script_dir}")
    print(f"Parent-Verzeichnis: {parent_dir}")
    print(f"sys.path[0]: {sys.path[0]}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

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
    script_dir = Path(__file__).parent      # tests/
    parent_dir = script_dir.parent          # projekt/
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

def test_barwerte(st: Sterbetafel) -> Dict[str, np.ndarray]:
    """
    Test 1: Berechnung Barwerte mit verlaufswerte_verctorized.py
    """
    print("\n" + "=" * 80)
    print("Test 1: Berechnung Barwerte")
    print()

    # Lade Sterbetafel
    st = Sterbetafel(CONFIG.tafel, CONFIG.data_dir)
    
    # Erstelle Config-Objekt
    config = VerlaufswerteConfig(
        alter=CONFIG.alter,
        n=CONFIG.n,
        t=CONFIG.t,
        sex=CONFIG.sex,
        zins=CONFIG.zins,
        zw=CONFIG.zw,
        sterbetafel=CONFIG.tafel
    )

    # Berechne Verlaufswerte
    vw = Verlaufswerte(config, st)
    ergebnisse = vw.berechne_alle()
    
    # Ausgabe
    #vw.drucke_verlaufswerte(precision=10)
    
    # Zusaetzlich als DataFrame
    print("\nAls pandas DataFrame:")
    print("-" * 80)
    df = vw.als_dataframe()
    print(df.head(10))
    
    return vw, df

def test_reserve(st: Sterbetafel) -> dict:
    """
    Test 1: Berechnung Reserve mit verlaufswerte_verctorized.py
    """
    print("\n" + "=" * 80)
    print("Test 2: Berechnung Reserve")
    print()

    # Lade Sterbetafel
    st = Sterbetafel(CONFIG.tafel, CONFIG.data_dir)

    # Berechne Verlaufswerte
    ergebnisse = berechne_reserve(CONFIG.alter, CONFIG.n, CONFIG.t, CONFIG.sex, CONFIG.zins, CONFIG.zw, st)
    
    # Ausgabe
    #vw.drucke_verlaufswerte(precision=10)
    
    # Zusaetzlich als DataFrame
    print(f"\nDK: {ergebnisse['DK'] * CONFIG.vs}")
    print("-" * 80)
    
    return ergebnisse


def test_3_optimierte_berechnung(st: Sterbetafel) -> Dict[str, np.ndarray]:
    """
    Berechnet Verlaufswerte
    """
    print("\n" + "=" * 80)
    print("Test: Verlaufswerte fuer n={CONFIG.n} Jahre")
        
    start_time = time.time()
    
    # Ultra-optimierte Berechnung
    rentenbarwerte = rbw.ae_xn_k(CONFIG.alter, CONFIG.t, CONFIG.sex, CONFIG.zins, CONFIG.zw, st)    
    todesfallbarwerte = lbw.nAe_x(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.zins, st)    
    erlebensfallbarwerte = lbw.nE_x(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.zins, st)
    
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


def test_export_excel():
    """
    Test 4: Export nach Excel
    """
    print("\n" + "=" * 80)
    print("TEST 4: EXPORT NACH EXCEL")
    print("=" * 80)
    
    st = Sterbetafel(CONFIG['tafel'], CONFIG['data_dir'])
    
    config = VerlaufswerteConfig(
        alter=CONFIG['alter'],
        n=CONFIG['n'],
        sex=CONFIG['sex'],
        zins=CONFIG['zins'],
        zw=CONFIG['zw'],
        sterbetafel=CONFIG['tafel']
    )
    
    vw = Verlaufswerte(config, st)
    df = vw.als_dataframe()
    
    # Export nach Excel
    output_file = "verlaufswerte_test.xlsx"
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    print(f"\nVerlaufswerte exportiert nach: {output_file}")
    print(f"Dateigröße: {Path(output_file).stat().st_size / 1024:.2f} KB")
    
    return df


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
    
    
    # Fuehre alle Tests aus
    vw, df = test_barwerte(st)

    dk = test_reserve(st)


    
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
    
#    print(f"{'✓' if excel_ok else '✗'} Excel-Vergleich: "
#          f"{'BESTANDEN' if excel_ok else 'FEHLER oder unvollstaendig'}")
    
   

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
