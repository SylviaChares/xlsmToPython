"""
Excel-Validierungstest fuer vektorisierte Verlaufswerte

Vereinfachter Test, der sich auf den Vergleich mit Excel-Werten konzentriert.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Setup
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
sys.path.insert(0, str(parent_dir))

from barwerte.sterbetafel import Sterbetafel
from barwerte import rentenbarwerte as rbw
from barwerte import leistungsbarwerte as lbw

# Versuche vektorisierte Funktionen zu importieren
try:
    from barwerte.rentenbarwerte import ae_xn_verlauf_optimized
    from barwerte.leistungsbarwerte import nAe_x_verlauf_vec, nE_x_verlauf_optimized
    VECTORIZED = True
except ImportError:
    VECTORIZED = False


# =============================================================================
# KONFIGURATION - MUSS MIT EXCEL UEBEREINSTIMMEN!
# =============================================================================

TEST_PARAMETER = {
    'alter': 40,
    'n': 20,
    'sex': 'M',
    'zins': 0.0175,
    'zw': 1,
    'tafel': 'DAV1994T',
    'data_dir': 'data'  # ANPASSEN!
}


# =============================================================================
# EXCEL-REFERENZWERTE - HIER DEINE WERTE EINTRAGEN!
# =============================================================================

# SCHRITT 1: Oeffne Excel-Tarifrechner
# SCHRITT 2: Stelle Parameter wie oben ein
# SCHRITT 3: Kopiere Verlaufswerte hierher

EXCEL_RENTENBARWERTE = {
    # Format: t: Wert
    # t=0: ae_{40}:20
    # t=1: ae_{41}:19
    # etc.
    0: None,  # <-- HIER EXCEL-WERT EINTRAGEN
    1: None,  # <-- HIER EXCEL-WERT EINTRAGEN
    2: None,
    3: None,
    4: None,
    # ... bis t=19
}

EXCEL_TODESFALLBARWERTE = {
    # Format: t: Wert
    # t=0: 20Ae_{40}
    # t=1: 19Ae_{41}
    # etc.
    0: None,  # <-- HIER EXCEL-WERT EINTRAGEN
    1: None,
    2: None,
    # ... bis t=20
}

EXCEL_ERLEBENSFALLBARWERTE = {
    # Format: t: Wert
    # t=0: 20E_{40}
    # t=1: 19E_{41}
    # etc.
    0: None,  # <-- HIER EXCEL-WERT EINTRAGEN
    1: None,
    2: None,
    # ... bis t=20
}


# =============================================================================
# HILFSFUNKTION: Excel-Spalte schnell formatieren
# =============================================================================

def formatiere_excel_spalte(werte_text: str) -> None:
    """
    Hilfsfunktion zum Formatieren von Excel-Werten.
    
    Verwendung:
    1. Kopiere Wertes-Spalte aus Excel (z.B. 20 Zellen)
    2. Fuege sie als String hier ein
    3. Funktion gibt formatierten Python-Code aus
    
    Beispiel:
        werte = '''
        14.919192111
        14.621204221
        14.311510421
        '''
        formatiere_excel_spalte(werte)
    """
    zeilen = [z.strip() for z in werte_text.strip().split('\n') if z.strip()]
    print("\nFormatiert fuer Python:")
    print("{")
    for i, wert in enumerate(zeilen):
        try:
            float(wert)  # Validiere, dass es eine Zahl ist
            print(f"    {i}: {wert},")
        except ValueError:
            print(f"    {i}: # FEHLER: '{wert}' ist keine Zahl")
    print("}")


# =============================================================================
# BERECHNUNG MIT PYTHON
# =============================================================================

def berechne_python_werte():
    """Berechnet Verlaufswerte mit Python."""
    print("\n" + "=" * 80)
    print("PYTHON-BERECHNUNG")
    print("=" * 80)
    
    # Lade Sterbetafel
    print(f"\nLade Sterbetafel: {TEST_PARAMETER['tafel']}")
    try:
        st = Sterbetafel(TEST_PARAMETER['tafel'], TEST_PARAMETER['data_dir'])
        print(f"✓ Sterbetafel geladen")
    except FileNotFoundError as e:
        print(f"✗ FEHLER: {e}")
        print(f"  Bitte passe 'data_dir' in TEST_PARAMETER an!")
        return None
    
    # Zeige Parameter
    print("\nParameter:")
    for key, value in TEST_PARAMETER.items():
        if key != 'data_dir':
            print(f"  {key:10s}: {value}")
    
    # Berechne mit bester verfuegbarer Methode
    if VECTORIZED:
        print("\n→ Nutze vektorisierte Funktionen")
        
        rentenbarwerte = ae_xn_verlauf_optimized(
            TEST_PARAMETER['alter'],
            TEST_PARAMETER['n'],
            TEST_PARAMETER['sex'],
            TEST_PARAMETER['zins'],
            TEST_PARAMETER['zw'],
            st
        )
        
        todesfallbarwerte = nAe_x_verlauf_vec(
            TEST_PARAMETER['alter'],
            TEST_PARAMETER['n'],
            TEST_PARAMETER['sex'],
            TEST_PARAMETER['zins'],
            st
        )
        
        erlebensfallbarwerte = nE_x_verlauf_optimized(
            TEST_PARAMETER['alter'],
            TEST_PARAMETER['n'],
            TEST_PARAMETER['sex'],
            TEST_PARAMETER['zins'],
            st
        )
    else:
        print("\n→ Nutze Standard-Funktionen (Schleifen)")
        
        n = TEST_PARAMETER['n']
        
        rentenbarwerte = np.array([
            rbw.ae_xn_k(
                TEST_PARAMETER['alter'] + t,
                n - t,
                TEST_PARAMETER['sex'],
                TEST_PARAMETER['zins'],
                TEST_PARAMETER['zw'],
                st
            )
            for t in range(n)
        ])
        
        todesfallbarwerte = np.array([
            lbw.nAe_x(
                TEST_PARAMETER['alter'] + t,
                n - t,
                TEST_PARAMETER['sex'],
                TEST_PARAMETER['zins'],
                st
            ) if n - t > 0 else 0.0
            for t in range(n + 1)
        ])
        
        erlebensfallbarwerte = np.array([
            lbw.nE_x(
                TEST_PARAMETER['alter'] + t,
                n - t,
                TEST_PARAMETER['sex'],
                TEST_PARAMETER['zins'],
                st
            ) if n - t > 0 else 1.0
            for t in range(n + 1)
        ])
    
    print(f"✓ Berechnung abgeschlossen")
    
    return {
        'rentenbarwerte': rentenbarwerte,
        'todesfallbarwerte': todesfallbarwerte,
        'erlebensfallbarwerte': erlebensfallbarwerte
    }


# =============================================================================
# VERGLEICH MIT EXCEL
# =============================================================================

def vergleiche_mit_excel(python_werte):
    """Vergleicht Python-Berechnungen mit Excel-Referenzwerten."""
    print("\n" + "=" * 80)
    print("VERGLEICH MIT EXCEL")
    print("=" * 80)
    
    # Pruefe, ob Excel-Werte eingetragen wurden
    excel_hat_daten = any(v is not None for v in EXCEL_RENTENBARWERTE.values())
    
    if not excel_hat_daten:
        print("\n✗ KEINE EXCEL-REFERENZWERTE EINGETRAGEN!")
        print("\nBitte trage Excel-Werte in die Dictionaries ein:")
        print("  - EXCEL_RENTENBARWERTE")
        print("  - EXCEL_TODESFALLBARWERTE")
        print("  - EXCEL_ERLEBENSFALLBARWERTE")
        print("\nSiehe Kommentare im Script oder ANLEITUNG_EXCEL_REFERENZWERTE.md")
        return False
    
    tolerance = 1e-8
    alle_ok = True
    
    # === RENTENBARWERTE ===
    print("\n1) Rentenbarwerte (ae_xn_k):")
    print("-" * 60)
    
    excel_count = 0
    max_diff = 0.0
    
    for t, excel_wert in EXCEL_RENTENBARWERTE.items():
        if excel_wert is None:
            continue
        
        if t >= len(python_werte['rentenbarwerte']):
            print(f"  t={t}: Excel vorhanden, aber t zu gross fuer Python-Array")
            continue
        
        python_wert = python_werte['rentenbarwerte'][t]
        diff = abs(python_wert - excel_wert)
        max_diff = max(max_diff, diff)
        excel_count += 1
        
        status = "✓" if diff < tolerance else "✗"
        
        if excel_count <= 10 or diff >= tolerance:  # Zeige erste 10 oder Fehler
            print(f"  t={t:2d} | Alter {TEST_PARAMETER['alter']+t}: "
                  f"Python={python_wert:.10f}, Excel={excel_wert:.10f}, "
                  f"Diff={diff:.2e} {status}")
    
    if excel_count > 10:
        print(f"  ... ({excel_count - 10} weitere Werte)")
    
    print(f"\n  Verglichene Werte: {excel_count}")
    print(f"  Maximale Differenz: {max_diff:.2e}")
    print(f"  Status: {'✓ OK' if max_diff < tolerance else '✗ FEHLER'}")
    
    if max_diff >= tolerance:
        alle_ok = False
    
    # === TODESFALLBARWERTE ===
    print("\n2) Todesfallbarwerte (nAe_x):")
    print("-" * 60)
    
    excel_count = 0
    max_diff = 0.0
    
    for t, excel_wert in EXCEL_TODESFALLBARWERTE.items():
        if excel_wert is None:
            continue
        
        if t >= len(python_werte['todesfallbarwerte']):
            continue
        
        python_wert = python_werte['todesfallbarwerte'][t]
        diff = abs(python_wert - excel_wert)
        max_diff = max(max_diff, diff)
        excel_count += 1
        
        status = "✓" if diff < tolerance else "✗"
        
        if excel_count <= 5 or diff >= tolerance:
            print(f"  t={t:2d}: Python={python_wert:.10f}, Excel={excel_wert:.10f}, "
                  f"Diff={diff:.2e} {status}")
    
    print(f"\n  Verglichene Werte: {excel_count}")
    print(f"  Maximale Differenz: {max_diff:.2e}")
    print(f"  Status: {'✓ OK' if max_diff < tolerance else '✗ FEHLER'}")
    
    if max_diff >= tolerance:
        alle_ok = False
    
    # === ERLEBENSFALLBARWERTE ===
    print("\n3) Erlebensfallbarwerte (nE_x):")
    print("-" * 60)
    
    excel_count = 0
    max_diff = 0.0
    
    for t, excel_wert in EXCEL_ERLEBENSFALLBARWERTE.items():
        if excel_wert is None:
            continue
        
        if t >= len(python_werte['erlebensfallbarwerte']):
            continue
        
        python_wert = python_werte['erlebensfallbarwerte'][t]
        diff = abs(python_wert - excel_wert)
        max_diff = max(max_diff, diff)
        excel_count += 1
        
        status = "✓" if diff < tolerance else "✗"
        
        if excel_count <= 5 or diff >= tolerance:
            print(f"  t={t:2d}: Python={python_wert:.10f}, Excel={excel_wert:.10f}, "
                  f"Diff={diff:.2e} {status}")
    
    print(f"\n  Verglichene Werte: {excel_count}")
    print(f"  Maximale Differenz: {max_diff:.2e}")
    print(f"  Status: {'✓ OK' if max_diff < tolerance else '✗ FEHLER'}")
    
    if max_diff >= tolerance:
        alle_ok = False
    
    return alle_ok


# =============================================================================
# EXPORT NACH EXCEL
# =============================================================================

def exportiere_vergleich(python_werte):
    """Erstellt Excel-Datei mit Python-Werten zum Vergleich."""
    print("\n" + "=" * 80)
    print("EXPORT NACH EXCEL")
    print("=" * 80)
    
    n = TEST_PARAMETER['n']
    
    # Erstelle DataFrame
    data = {
        't': list(range(n + 1)),
        'Alter': [TEST_PARAMETER['alter'] + t for t in range(n + 1)],
        'Restlaufzeit': [n - t for t in range(n + 1)]
    }
    
    # Python-Werte
    data['Python_ae_xn'] = np.append(python_werte['rentenbarwerte'], np.nan)
    data['Python_nAe_x'] = python_werte['todesfallbarwerte']
    data['Python_nE_x'] = python_werte['erlebensfallbarwerte']
    
    # Excel-Werte
    data['Excel_ae_xn'] = [EXCEL_RENTENBARWERTE.get(t) for t in range(n + 1)]
    data['Excel_nAe_x'] = [EXCEL_TODESFALLBARWERTE.get(t) for t in range(n + 1)]
    data['Excel_nE_x'] = [EXCEL_ERLEBENSFALLBARWERTE.get(t) for t in range(n + 1)]
    
    # Differenzen
    data['Diff_ae_xn'] = [
        abs(data['Python_ae_xn'][i] - data['Excel_ae_xn'][i])
        if data['Excel_ae_xn'][i] is not None and not np.isnan(data['Python_ae_xn'][i])
        else np.nan
        for i in range(n + 1)
    ]
    
    data['Diff_nAe_x'] = [
        abs(data['Python_nAe_x'][i] - data['Excel_nAe_x'][i])
        if data['Excel_nAe_x'][i] is not None
        else np.nan
        for i in range(n + 1)
    ]
    
    data['Diff_nE_x'] = [
        abs(data['Python_nE_x'][i] - data['Excel_nE_x'][i])
        if data['Excel_nE_x'][i] is not None
        else np.nan
        for i in range(n + 1)
    ]
    
    df = pd.DataFrame(data)
    
    # Speichere
    output_file = "excel_validierung_vergleich.xlsx"
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    print(f"\n✓ Vergleichstabelle erstellt: {output_file}")
    print(f"  Oeffne diese Datei, um Python- und Excel-Werte zu vergleichen")
    
    return df


# =============================================================================
# HAUPTPROGRAMM
# =============================================================================

def main():
    print("\n" + "=" * 80)
    print("EXCEL-VALIDIERUNGSTEST FUER VEKTORISIERTE VERLAUFSWERTE")
    print("=" * 80)
    
    # Berechne mit Python
    python_werte = berechne_python_werte()
    if python_werte is None:
        return False
    
    # Vergleiche mit Excel
    validierung_ok = vergleiche_mit_excel(python_werte)
    
    # Exportiere Vergleich
    df = exportiere_vergleich(python_werte)
    
    # Zusammenfassung
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)
    
    if validierung_ok:
        print("\n✓✓✓ VALIDIERUNG ERFOLGREICH! ✓✓✓")
        print("Python-Berechnungen stimmen mit Excel ueberein.")
    else:
        print("\n✗✗✗ VALIDIERUNG FEHLGESCHLAGEN ✗✗✗")
        print("Bitte pruefe:")
        print("  1. Sind TEST_PARAMETER identisch mit Excel?")
        print("  2. Wurden alle Excel-Werte korrekt eingetragen?")
        print("  3. Wird die richtige Sterbetafel verwendet?")
        print("\nSiehe 'excel_validierung_vergleich.xlsx' fuer Details.")
    
    return validierung_ok


if __name__ == "__main__":
    try:
        erfolg = main()
        sys.exit(0 if erfolg else 1)
    except Exception as e:
        print(f"\n\nFEHLER: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
