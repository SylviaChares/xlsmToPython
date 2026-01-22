# Integration von verlaufswerte.py in dein Projekt

## Schritt 1: Verzeichnisstruktur pruefen

Deine aktuelle Struktur sollte so aussehen:

```
C:\Users\chares\Documents\Notebooks\xlsmToPython\
├── data/
│   ├── DAV1994_T.csv
│   └── DAV2008_T.csv
├── barwerte/
│   ├── __init__.py
│   ├── sterbetafel.py
│   ├── basisfunktionen.py
│   ├── finanzmathematik.py
│   ├── rentenbarwerte.py
│   └── leistungsbarwerte.py
└── test_barwerte_adj.py
```

## Schritt 2: verlaufswerte.py platzieren

Kopiere `verlaufswerte.py` ins **Hauptverzeichnis** (NICHT in barwerte/):

```
C:\Users\chares\Documents\Notebooks\xlsmToPython\
├── data/
├── barwerte/
├── verlaufswerte.py          # <-- HIER
├── test_barwerte_adj.py
└── test_verlaufswerte.py     # <-- Optional: Test-Skript
```

**NICHT so:**
```
barwerte/
└── verlaufswerte.py          # <-- FALSCH!
```

## Schritt 3: Warum diese Struktur?

### barwerte/ = Package (mehrere zusammenhaengende Module)
- sterbetafel.py
- basisfunktionen.py
- rentenbarwerte.py
- leistungsbarwerte.py
- Alle arbeiten zusammen fuer Basis-Barwerte

### verlaufswerte.py = Einzelnes Modul
- Nutzt die barwerte-Module
- Baut darauf auf (naechste Ebene)
- Eigenstaendige Funktionalitaet

### Analogie:
```
numpy/          # Package mit vielen Modulen
scipy/          # Package mit vielen Modulen
matplotlib.py   # Einzelnes Modul (vereinfacht)
```

## Schritt 4: Verwendung in deinem Code

### A) In Jupyter Notebook / Python-Skript

```python
# Imports (wie gewohnt)
from barwerte.sterbetafel import Sterbetafel
from barwerte import rentenbarwerte as rbw
from barwerte import leistungsbarwerte as lbw

# NEU: Import von verlaufswerte
from verlaufswerte import Verlaufswerte, VerlaufswerteConfig

# Verwendung
st = Sterbetafel("DAV1994_T", "data")

config = VerlaufswerteConfig(
    alter=40,
    n=20,
    sex='M',
    zins=0.0175,
    zw=1,
    sterbetafel='DAV1994_T'
)

vw = Verlaufswerte(config, st)
ergebnisse = vw.berechne_alle()

# Zugriff auf Ergebnisse
print(ergebnisse['rentenbarwerte'])
print(ergebnisse['todesfallbarwerte'])

# Als DataFrame
df = vw.als_dataframe()
print(df)
```

### B) Integration in bestehenden Code (test_barwerte_adj.py)

Am Ende deiner aktuellen Datei kannst du hinzufuegen:

```python
# Am Anfang der Datei, bei den anderen Imports:
from verlaufswerte import Verlaufswerte, VerlaufswerteConfig

# Dann im Code:
print("\n" + "=" * 80)
print("VERLAUFSWERTE")
print("=" * 80)

config_vw = VerlaufswerteConfig(
    alter=CONFIG.alter,
    n=CONFIG.n,
    sex=CONFIG.sex,
    zins=CONFIG.zins,
    zw=CONFIG.zw,
    sterbetafel=CONFIG.tafel
)

vw = Verlaufswerte(config_vw, st)
vw.drucke_verlaufswerte(precision=10)

# Optional: Export nach Excel
df = vw.als_dataframe()
df.to_excel("verlaufswerte_output.xlsx", index=False)
```

## Schritt 5: Test ausfuehren

```bash
# Im Hauptverzeichnis (xlsmToPython/)
python test_verlaufswerte.py
```

Oder in Jupyter:

```python
%run test_verlaufswerte.py
```

## Haeufige Fehler und Loesungen

### Fehler: "ModuleNotFoundError: No module named 'barwerte'"

**Problem:** Du bist im falschen Verzeichnis.

**Loesung:** Wechsle ins Hauptverzeichnis:
```bash
cd C:\Users\chares\Documents\Notebooks\xlsmToPython
python test_verlaufswerte.py
```

### Fehler: "ModuleNotFoundError: No module named 'verlaufswerte'"

**Problem:** verlaufswerte.py liegt nicht im richtigen Verzeichnis.

**Loesung:** Stelle sicher, dass verlaufswerte.py im HAUPTVERZEICHNIS liegt 
(nicht in barwerte/).

### Fehler: Imports funktionieren nicht in Jupyter

**Problem:** Jupyter findet die Module nicht.

**Loesung:** 
```python
import sys
from pathlib import Path

# Fuege Projekt-Verzeichnis zum Python-Pfad hinzu
projekt_dir = Path("C:/Users/chares/Documents/Notebooks/xlsmToPython")
if str(projekt_dir) not in sys.path:
    sys.path.insert(0, str(projekt_dir))

# Jetzt sollten die Imports funktionieren
from barwerte.sterbetafel import Sterbetafel
from verlaufswerte import Verlaufswerte
```

## Zukuenftige Erweiterungen

Falls verlaufswerte.py spaeter sehr komplex wird (z.B. mit Analyse-, 
Visualisierungs- und Export-Funktionen), koenntest du es als Package 
strukturieren:

```
verlaufswerte/
├── __init__.py
├── core.py              # Haupt-Klasse
├── analyse.py           # Analyse-Funktionen
└── visualisierung.py    # Plotting
```

Aber **aktuell** ist das einzelne Modul die richtige Wahl.

## Zusammenfassung

✓ verlaufswerte.py ins Hauptverzeichnis
✓ NICHT in barwerte/ verschieben
✓ Import: `from verlaufswerte import Verlaufswerte`
✓ verlaufswerte.py nutzt barwerte-Package
✓ Analog zu deinem bisherigen Workflow

Bei Fragen: Melde dich!
