# Anleitung: Excel-Referenzwerte in Test eintragen

## Uebersicht

Diese Anleitung zeigt, wie du Referenzwerte aus deinem Excel-Tarifrechner
in das Test-Skript `test_verlaufswerte_vectorized.py` eintraegst.

## Warum Excel-Referenzwerte?

Die Excel-Referenzwerte dienen zur **externen Validierung**:
- Stellt sicher, dass Python dieselben Werte wie Excel berechnet
- Validiert die gesamte Berechnungskette
- Gibt Sicherheit fuer produktiven Einsatz

## Schritt 1: Excel-Werte ablesen

### 1.1 Konfiguration pruefen

Stelle sicher, dass die Testkonfiguration mit deinem Excel uebereinstimmt:

```python
# In test_verlaufswerte_vectorized.py
CONFIG = TestConfig(
    alter=40,
    sex='M',
    tafel='DAV1994_T',
    zins=0.0175,  # 1,75%
    n=20,         # Versicherungsdauer
    zw=1          # jaehrlich
)
```

### 1.2 Werte aus Excel kopieren

Oeffne deinen Excel-Tarifrechner und stelle die Parameter wie in CONFIG ein.

#### Rentenbarwerte

Verlaufswerte der Rentenbarwerte ae_{x+t}:n-t

```
t=0:  ae_{40}:20  = [Wert aus Excel]
t=1:  ae_{41}:19  = [Wert aus Excel]
t=2:  ae_{42}:18  = [Wert aus Excel]
...
t=19: ae_{59}:1   = [Wert aus Excel]
```

In Excel findest du diese ueblicherweise in einer Spalte.

**Tipp:** Wenn dein Excel Verlaufswerte berechnet, kopiere die gesamte
Spalte in einen Text-Editor und formatiere sie fuer Python.

#### Todesfallbarwerte

Verlaufswerte der Todesfallbarwerte (n-t)Ae_{x+t}

```
t=0:  20Ae_{40}   = [Wert aus Excel]
t=1:  19Ae_{41}   = [Wert aus Excel]
...
t=20: 0Ae_{60}    = 0.0  (immer 0, da keine Restlaufzeit)
```

#### Erlebensfallbarwerte

Verlaufswerte der Erlebensfallbarwerte (n-t)E_{x+t}

```
t=0:  20E_{40}    = [Wert aus Excel]
t=1:  19E_{41}    = [Wert aus Excel]
...
t=20: 0E_{60}     = 1.0  (immer 1.0, da Erleben sicher)
```

## Schritt 2: Werte in Python eintragen

### 2.1 Oeffne test_verlaufswerte_vectorized.py

Suche die Klasse `ExcelReferenzwerte`:

```python
class ExcelReferenzwerte:
    """Excel-Referenzwerte aus dem Tarifrechner."""
    
    rentenbarwerte = {
        0: 14.919192111,   # BEISPIELWERT - ERSETZEN!
        1: 14.621204221,   # BEISPIELWERT - ERSETZEN!
        # ...
    }
```

### 2.2 Trage deine Excel-Werte ein

**Methode A: Manuell** (fuer wenige Werte)

```python
rentenbarwerte = {
    0: 14.919192111,   # Wert aus Excel Zelle A1
    1: 14.621204221,   # Wert aus Excel Zelle A2
    2: 14.311510421,   # Wert aus Excel Zelle A3
    # ... weitere Werte
}
```

**Methode B: Aus Excel-Spalte generieren** (empfohlen!)

1. Kopiere die Werte-Spalte aus Excel (z.B. A1:A20)
2. Fuege sie in einen Text-Editor ein
3. Nutze folgenden Python-Code zum Formatieren:

```python
# Hilfsskript zum Formatieren von Excel-Werten
excel_werte_string = """
14.919192111
14.621204221
14.311510421
13.989383833
...
"""

# Konvertiere zu Python-Dictionary-Format
zeilen = [z.strip() for z in excel_werte_string.strip().split('\n') if z.strip()]
for i, wert in enumerate(zeilen):
    print(f"    {i}: {wert},")
```

Das gibt aus:
```python
    0: 14.919192111,
    1: 14.621204221,
    2: 14.311510421,
    3: 13.989383833,
    ...
```

Kopiere diese Ausgabe in die `rentenbarwerte = {}`

### 2.3 Vollstaendiges Beispiel

```python
class ExcelReferenzwerte:
    """Excel-Referenzwerte fuer CONFIG: alter=40, n=20, sex='M', zins=0.0175."""
    
    # Rentenbarwerte ae_{x+t}:n-t
    rentenbarwerte = {
        0: 14.919192111,
        1: 14.621204221,
        2: 14.311510421,
        3: 13.989383833,
        4: 13.654818345,
        5: 13.307404120,
        6: 12.946525589,
        7: 12.571554421,
        8: 12.181851255,
        9: 11.776767311,
        10: 11.355643089,
        11: 10.917808567,
        12: 10.462584156,
        13: 9.989280356,
        14: 9.497197878,
        15: 8.985627845,
        16: 8.453851234,
        17: 7.901139056,
        18: 7.326752489,
        19: 6.729943678,
    }
    
    # Todesfallbarwerte (n-t)Ae_{x+t}
    todesfallbarwerte = {
        0: 0.043246001,
        1: 0.041708571,
        2: 0.040170857,
        3: 0.038632845,
        # ... alle 21 Werte (t=0 bis t=20)
        20: 0.0,  # Immer 0 am Ende
    }
    
    # Erlebensfallbarwerte (n-t)E_{x+t}
    erlebensfallbarwerte = {
        0: 0.723788010,
        1: 0.735692025,
        2: 0.747775130,
        # ... alle 21 Werte
        20: 1.0,  # Immer 1.0 am Ende
    }
```

## Schritt 3: Test ausfuehren

### 3.1 Ersten Test-Lauf

```bash
cd tests
python test_verlaufswerte_vectorized.py
```

### 3.2 Output interpretieren

Der Test gibt aus:

```
TEST 5: VERGLEICH MIT EXCEL-REFERENZWERTEN
================================================================================

Rentenbarwerte:
  Anzahl Vergleichswerte: 20
  Maximale Differenz:     2.34e-11
  Status:                 ✓ OK

Todesfallbarwerte:
  Anzahl Vergleichswerte: 21
  Maximale Differenz:     1.45e-11
  Status:                 ✓ OK

...

ZUSAMMENFASSUNG
================================================================================

✓ Excel-Vergleich: BESTANDEN
```

**Erfolg:** Maximale Differenz < 1e-8 (typisch: 1e-10 bis 1e-12)

**Problem:** Grosse Differenzen (> 1e-6)
- Pruefe, ob Konfiguration in Python und Excel identisch ist
- Pruefe, ob richtige Sterbetafel verwendet wird
- Pruefe Excel-Werte auf Tippfehler

### 3.3 Vergleichstabelle pruefen

Der Test erstellt automatisch eine Excel-Datei:

```
verlaufswerte_vergleich.xlsx
```

Diese enthaelt:
- Alle berechneten Werte (Standard, Vektorisiert, Optimiert)
- Excel-Referenzwerte
- Differenzen

Oeffne diese Datei und pruefe visuell:
1. Sind Python- und Excel-Werte nah beieinander?
2. Wo sind die groessten Abweichungen?
3. Gibt es systematische Fehler?

## Schritt 4: Unterschiedliche Szenarien testen

### 4.1 Weitere Konfigurationen

Teste verschiedene Parameter-Kombinationen:

```python
# Scenario 1: Jaehrliche Zahlung
CONFIG_JAEHRLICH = TestConfig(
    alter=40, n=20, sex='M', zins=0.0175, zw=1, tafel='DAV1994_T'
)

# Scenario 2: Monatliche Zahlung
CONFIG_MONATLICH = TestConfig(
    alter=40, n=20, sex='M', zins=0.0175, zw=12, tafel='DAV1994_T'
)

# Scenario 3: Weiblich
CONFIG_WEIBLICH = TestConfig(
    alter=40, n=20, sex='F', zins=0.0175, zw=1, tafel='DAV1994_T'
)

# Scenario 4: Andere Tafel
CONFIG_DAV2008 = TestConfig(
    alter=40, n=20, sex='M', zins=0.0175, zw=1, tafel='DAV2008_T'
)
```

Fuer jedes Szenario:
1. Stelle Excel entsprechend ein
2. Kopiere Referenzwerte
3. Erstelle neue `ExcelReferenzwerte_XXX`-Klasse
4. Fuehre Test aus

### 4.2 Mehrere Referenzwerte-Klassen

```python
class ExcelReferenzwerte_Jaehrlich:
    """Referenzwerte fuer zw=1."""
    rentenbarwerte = { ... }
    todesfallbarwerte = { ... }
    erlebensfallbarwerte = { ... }

class ExcelReferenzwerte_Monatlich:
    """Referenzwerte fuer zw=12."""
    rentenbarwerte = { ... }
    todesfallbarwerte = { ... }
    erlebensfallbarwerte = { ... }

# Im Test dann entsprechend verwenden
excel_ref = ExcelReferenzwerte_Monatlich  # oder _Jaehrlich
```

## Schritt 5: Automatisierung (Optional)

### 5.1 Excel-Export aus Python lesen

Falls dein Excel-Tarifrechner Ergebnisse exportieren kann:

```python
import pandas as pd

# Lies Excel-Export
excel_file = "tarifrechner_verlaufswerte_export.xlsx"
df_excel = pd.read_excel(excel_file)

# Extrahiere Werte
rentenbarwerte = dict(zip(df_excel['t'], df_excel['ae_xn']))
todesfallbarwerte = dict(zip(df_excel['t'], df_excel['nAe_x']))
# ...
```

### 5.2 Python-Script zum Konvertieren

```python
# convert_excel_to_test.py
import pandas as pd

def excel_spalte_zu_dict(excel_file, spalte, sheet='Sheet1'):
    """Konvertiert Excel-Spalte zu Python-Dictionary."""
    df = pd.read_excel(excel_file, sheet_name=sheet)
    result = {}
    for i, wert in enumerate(df[spalte]):
        if not pd.isna(wert):
            result[i] = float(wert)
    return result

# Verwendung
excel_file = "tarifrechner_export.xlsx"
rentenbarwerte = excel_spalte_zu_dict(excel_file, 'Rentenbarwerte')

# Ausgabe als Python-Code
print("rentenbarwerte = {")
for k, v in rentenbarwerte.items():
    print(f"    {k}: {v},")
print("}")
```

## Troubleshooting

### Problem 1: "Keine vollstaendigen Excel-Referenzwerte"

**Loesung:** Fuege alle Werte fuer t=0 bis t=n ein.

### Problem 2: "Maximale Differenz > 1e-6"

**Ursachen:**
1. Unterschiedliche Sterbetafeln in Python vs Excel
2. Unterschiedliche Zinssaetze
3. Unterschiedliche Rundungseinstellungen
4. Tippfehler beim Kopieren

**Loesung:** 
- Pruefe CONFIG vs. Excel-Einstellungen
- Kopiere Werte nochmals sorgfaeltig
- Nutze mehr Dezimalstellen aus Excel

### Problem 3: Test dauert sehr lange

**Loesung:** 
- Vektorisierte Funktionen noch nicht integriert
- Reduziere n fuer ersten Test
- Siehe INSTALLATION_VECTORIZED.md

## Zusammenfassung

✓ Stelle sicher, dass CONFIG mit Excel uebereinstimmt
✓ Kopiere Verlaufswerte aus Excel
✓ Trage Werte in ExcelReferenzwerte ein
✓ Fuehre Test aus
✓ Pruefe, dass max. Differenz < 1e-8
✓ Nutze verlaufswerte_vergleich.xlsx zur Analyse

**Bei Erfolg:** Deine Python-Implementation ist validiert! 🎉
