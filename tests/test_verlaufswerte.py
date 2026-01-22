"""
Test-Skript fuer Verlaufswerte-Modul

Demonstriert die Verwendung des Verlaufswerte-Moduls mit verschiedenen
Anwendungsfaellen und zeigt Performance-Vergleiche.

Verzeichnisstruktur:
    projekt/
    ├── data/
    │   ├── DAV1994_T.csv
    │   └── DAV2008_T.csv
    ├── barwerte/
    │   ├── __init__.py
    │   ├── sterbetafel.py
    │   ├── basisfunktionen.py
    │   ├── rentenbarwerte.py
    │   └── leistungsbarwerte.py
    ├── verlaufswerte.py          # <-- Dieses Modul
    ├── tests/
    │   ├── test_verlaufswerte.py     # <-- Dieses Skript
"""

import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path

# WICHTIG: Fuege Parent-Verzeichnis zum Python-Pfad hinzu
# Damit Python die Module barwerte/ und verlaufswerte.py findet
script_dir = Path(__file__).parent  # tests/
parent_dir = script_dir.parent       # projekt/
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Importiere Barwerte-Package und Verlaufswerte-Modul
try:
    from barwerte.sterbetafel import Sterbetafel
    from barwerte import rentenbarwerte as rbw
    from barwerte import leistungsbarwerte as lbw
    from verlaufswerte import (
        Verlaufswerte, 
        VerlaufswerteConfig, 
        berechne_verlaufswerte
    )
except ImportError as e:
    print(f"Fehler beim Import: {e}")
    print("\nStelle sicher, dass folgende Struktur vorhanden ist:")
    print("  projekt/")
    print("    ├── barwerte/          # Package")
    print("    ├── verlaufswerte.py   # Modul")
    print("    └── tests/")
    print("        └── test_verlaufswerte.py")
    print(f"\nAktuelles Verzeichnis: {Path.cwd()}")
    print(f"Script-Verzeichnis: {script_dir}")
    print(f"Parent-Verzeichnis: {parent_dir}")
    print(f"sys.path[0]: {sys.path[0]}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# =============================================================================
# Testparameter (wie im Excel-Tarifrechner)
# =============================================================================

# Berechne Pfad zum data/-Verzeichnis (relativ zum Projekt-Hauptverzeichnis)
DATA_DIR = parent_dir / "data"

CONFIG = {
    'alter': 40,
    'n': 20,
    'sex': 'M',
    'zins': 0.0175,
    'zw': 1,
    'tafel': 'DAV1994T',
    'data_dir': str(DATA_DIR)  # Absoluter Pfad zum data/-Verzeichnis
}


def test_basis_berechnung():
    """
    Test 1: Basis-Berechnung mit dem neuen Verlaufswerte-Modul
    """
    print("\n" + "=" * 80)
    print("TEST 1: BASIS-BERECHNUNG MIT VERLAUFSWERTE-MODUL")
    print("=" * 80)
    
    # Lade Sterbetafel
    st = Sterbetafel(CONFIG['tafel'], CONFIG['data_dir'])
    
    # Erstelle Config-Objekt
    config = VerlaufswerteConfig(
        alter=CONFIG['alter'],
        n=CONFIG['n'],
        sex=CONFIG['sex'],
        zins=CONFIG['zins'],
        zw=CONFIG['zw'],
        sterbetafel=CONFIG['tafel']
    )
    
    # Berechne Verlaufswerte
    vw = Verlaufswerte(config, st)
    ergebnisse = vw.berechne_alle()
    
    # Ausgabe
    vw.drucke_verlaufswerte(precision=10)
    
    # Zusaetzlich als DataFrame
    print("\nAls pandas DataFrame:")
    print("-" * 80)
    df = vw.als_dataframe()
    print(df.head(10))
    
    return vw, df


def test_convenience_funktion():
    """
    Test 2: Verwendung der Convenience-Funktion
    """
    print("\n" + "=" * 80)
    print("TEST 2: CONVENIENCE-FUNKTION")
    print("=" * 80)
    
    st = Sterbetafel(CONFIG['tafel'], CONFIG['data_dir'])
    
    # Direkter Aufruf ohne Config-Objekt
    ergebnisse = berechne_verlaufswerte(
        alter=CONFIG['alter'],
        n=CONFIG['n'],
        sex=CONFIG['sex'],
        zins=CONFIG['zins'],
        zw=CONFIG['zw'],
        sterbetafel_obj=st
    )
    
    print("\nRentenbarwerte (erste 5):")
    print(ergebnisse['rentenbarwerte'][:5])
    
    print("\nTodesfallbarwerte (erste 5):")
    print(ergebnisse['todesfallbarwerte'][:5])
    
    return ergebnisse


def test_performance_vergleich():
    """
    Test 3: Performance-Vergleich alte vs. neue Methode
    """
    print("\n" + "=" * 80)
    print("TEST 3: PERFORMANCE-VERGLEICH")
    print("=" * 80)
    
    st = Sterbetafel(CONFIG['tafel'], CONFIG['data_dir'])
    
    # --- ALTE METHODE: Sequentielle For-Schleife ---
    print("\n1) Alte Methode (sequentielle for-Schleife):")
    start_old = time.time()
    
    rentenbarwerte_old = []
    for i in range(CONFIG['n']):
        bbw = rbw.ae_xn_k(
            CONFIG['alter'] + i, 
            CONFIG['n'] - i, 
            CONFIG['sex'], 
            CONFIG['zins'], 
            CONFIG['zw'], 
            st
        )
        rentenbarwerte_old.append(bbw)
    
    zeit_old = time.time() - start_old
    print(f"   Zeit: {zeit_old:.4f} Sekunden")
    
    # --- NEUE METHODE: Verlaufswerte-Klasse ---
    print("\n2) Neue Methode (Verlaufswerte-Klasse):")
    start_new = time.time()
    
    config = VerlaufswerteConfig(
        alter=CONFIG['alter'],
        n=CONFIG['n'],
        sex=CONFIG['sex'],
        zins=CONFIG['zins'],
        zw=CONFIG['zw'],
        sterbetafel=CONFIG['tafel']
    )
    
    vw = Verlaufswerte(config, st)
    ergebnisse = vw.berechne_alle()
    rentenbarwerte_new = ergebnisse['rentenbarwerte']
    
    zeit_new = time.time() - start_new
    print(f"   Zeit: {zeit_new:.4f} Sekunden")
    
    # Speedup
    speedup = zeit_old / zeit_new if zeit_new > 0 else float('inf')
    print(f"\n3) Performance-Gewinn:")
    print(f"   Speedup: {speedup:.2f}x schneller")
    print(f"   Zeitersparnis: {(zeit_old - zeit_new):.4f} Sekunden "
          f"({100 * (zeit_old - zeit_new) / zeit_old:.1f}%)")
    
    # Validierung: Sind die Ergebnisse identisch?
    max_diff = np.max(np.abs(
        np.array(rentenbarwerte_old) - rentenbarwerte_new
    ))
    print(f"\n4) Validierung:")
    print(f"   Maximale Differenz: {max_diff:.2e}")
    print(f"   Ergebnisse identisch: {max_diff < 1e-10}")
    
    return rentenbarwerte_old, rentenbarwerte_new


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


def test_verschiedene_parameter():
    """
    Test 5: Verlaufswerte fuer verschiedene Parameterkombinationen
    """
    print("\n" + "=" * 80)
    print("TEST 5: VERSCHIEDENE PARAMETERKOMBINATIONEN")
    print("=" * 80)
    
    st = Sterbetafel(CONFIG['tafel'], CONFIG['data_dir'])
    
    # Test verschiedene Zahlungsweisen
    zahlungsweisen = [1, 2, 4, 12]
    
    print("\nVergleich verschiedener Zahlungsweisen:")
    print("(Rentenbarwert zu Beginn, t=0)\n")
    
    for zw in zahlungsweisen:
        config = VerlaufswerteConfig(
            alter=CONFIG['alter'],
            n=CONFIG['n'],
            sex=CONFIG['sex'],
            zins=CONFIG['zins'],
            zw=zw,
            sterbetafel=CONFIG['tafel']
        )
        
        vw = Verlaufswerte(config, st)
        ergebnisse = vw.berechne_alle()
        
        bbw_start = ergebnisse['rentenbarwerte'][0]
        print(f"  Zahlungsweise {zw:2d}x: ae_{CONFIG['alter']}:{CONFIG['n']} "
              f"= {bbw_start:.8f}")


def test_vergleich_mit_excel():
    """
    Test 6: Vergleich mit Excel-Referenzwerten
    
    Hier kannst du Referenzwerte aus deinem Excel-Tarifrechner einfuegen
    und gegen die Python-Implementierung validieren.
    """
    print("\n" + "=" * 80)
    print("TEST 6: VALIDIERUNG GEGEN EXCEL-REFERENZWERTE")
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
    ergebnisse = vw.berechne_alle()
    
    # HIER: Fuege Excel-Referenzwerte ein
    # Beispiel fuer t=0 (anpassen an deine Excel-Werte):
    excel_referenz = {
        'ae_xn_k': {
            0: 14.919192111,  # Beispielwert - durch echten Wert ersetzen
            1: 14.621204221,  # Beispielwert
            # ... weitere Werte ...
        },
        'nAe_x': {
            0: 0.043246001,  # Beispielwert
            1: 0.041708571,  # Beispielwert
            # ... weitere Werte ...
        }
    }
    
    print("\nVergleich Rentenbarwerte (erste 2 Zeitpunkte):")
    for t in [0, 1]:
        if t in excel_referenz['ae_xn_k']:
            python_wert = ergebnisse['rentenbarwerte'][t]
            excel_wert = excel_referenz['ae_xn_k'][t]
            diff = abs(python_wert - excel_wert)
            
            print(f"  t={t}:")
            print(f"    Python: {python_wert:.10f}")
            print(f"    Excel:  {excel_wert:.10f}")
            print(f"    Diff:   {diff:.2e}")
    
    print("\nHINWEIS: Bitte Excel-Referenzwerte im Code eintragen!")


# =============================================================================
# Hauptprogramm
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("VERLAUFSWERTE-MODUL - UMFASSENDER TEST")
    print("=" * 80)
    print(f"\nParameter:")
    for key, value in CONFIG.items():
        print(f"  {key:15s}: {value}")
    
    try:
        # Fuehre alle Tests aus
        vw, df = test_basis_berechnung()
        ergebnisse = test_convenience_funktion()
        old_vals, new_vals = test_performance_vergleich()
        df_export = test_export_excel()
        test_verschiedene_parameter()
        test_vergleich_mit_excel()
        
        print("\n" + "=" * 80)
        print("ALLE TESTS ERFOLGREICH ABGESCHLOSSEN")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n\nFEHLER bei Test-Ausfuehrung:")
        print(f"{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)