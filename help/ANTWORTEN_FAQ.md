# Antworten auf Ihre Fragen

## 1. Was ist __init__.py und wo finde ich sie?

### Was ist __init__.py?

`__init__.py` ist eine **spezielle Datei**, die ein Verzeichnis zu einem **Python-Package** macht.

### Wo liegt die Datei?

```
Ihr Projekt/
├── barwerte/
│   ├── __init__.py          ← HIER! (direkt im barwerte-Ordner)
│   ├── sterbetafel.py
│   ├── basisfunktionen.py
│   ├── finanzmathematik.py
│   ├── rentenbarwerte.py
│   └── leistungsbarwerte.py
├── data/
│   ├── DAV1994T.csv
│   └── DAV2008T.csv
└── test_barwerte.py
```

### Was macht __init__.py?

**Ohne `__init__.py`:**
```python
# ❌ Funktioniert NICHT:
from barwerte import Sterbetafel
# Fehler: ModuleNotFoundError: No module named 'barwerte'

# Sie müssten schreiben:
from barwerte.sterbetafel import Sterbetafel  # Umständlich!
from barwerte.basisfunktionen import diskont
from barwerte.rentenbarwerte import ae_x
```

**Mit `__init__.py`:**
```python
# ✓ Funktioniert:
from barwerte import Sterbetafel, diskont, ae_x  # Einfach!
```

### Wie funktioniert __init__.py?

Die `__init__.py` definiert, was "nach außen" sichtbar ist:

```python
# In __init__.py:
from .sterbetafel import Sterbetafel
from .basisfunktionen import diskont, npx, nqx
from .rentenbarwerte import ae_x, ae_xn_k

# Jetzt können Sie schreiben:
from barwerte import Sterbetafel, diskont, ae_x
```

**Der Punkt (`.`) bedeutet:** "aus dem gleichen Package/Verzeichnis"

### Ihre aktuelle __init__.py

Sie haben bereits eine `__init__.py`, aber sie verwendet die **alten Funktionsnamen**:

```python
# Ihre alte __init__.py:
from .leibrenten import ax, axn  # ❌ Diese Funktionen heißen jetzt anders!

# Ihre neuen Funktionen:
from .rentenbarwerte import ae_x, ae_xn  # ✓ Neue Namen!
```

### Was müssen Sie tun?

**Option 1: Neue __init__.py mit Ihren neuen Namen**
→ Siehe Datei `__init___angepasst.py` 

**Option 2: Alte Namen als Aliase beibehalten (Abwärtskompatibilität)**
```python
# In __init__.py
from .rentenbarwerte import ae_x, ae_xn
# Alte Namen als Aliase:
ax = ae_x      # Für alte Scripts
axn = ae_xn    # Für alte Scripts
```

---

## 2. MAX_ALTER bei 121 belassen und nur bis dahin einlesen

### Ihre Anforderung:
- MAX_ALTER = 121 (für Berechnungen)
- CSV hat Zeilen 0-123, aber nur 0-121 laden

### Lösung:

Die neue `sterbetafel.py` filtert beim Laden:

```python
# In Sterbetafel.__init__():

# Lade komplette CSV
data_raw = pd.read_csv(csv_file, sep=';', decimal=',')

# Filtere nur Alter 0 bis MAX_ALTER (121)
self.data = data_raw[data_raw['Alter'] <= MAX_ALTER].copy()

# Info-Meldung
if len(data_raw) > len(self.data):
    print(f"Info: Von {len(data_raw)} Zeilen wurden {len(self.data)} geladen (Alter 0-{MAX_ALTER})")
```

### Test:

**Ihre CSV hat:**
```csv
Alter;qx;qy
0;...;...
1;...;...
...
121;...;...
122;...;...  ← Wird NICHT geladen
123;...;...  ← Wird NICHT geladen
```

**Beim Laden:**
```python
st = Sterbetafel("DAV1994T", data_dir="data")
# Ausgabe: Info: Von 124 Zeilen wurden 122 geladen (Alter 0-121)

print(st.max_alter)  # 121
print(len(st.data))  # 122 (Alter 0 bis 121 = 122 Zeilen)
```

### Vorteile:

✅ MAX_ALTER bleibt bei 121  
✅ CSV kann mehr Zeilen haben (flexibel)  
✅ Keine manuellen Änderungen an CSV nötig  
✅ Klarheit in Berechnungen (Omega = 121)  

---

## Visuelle Übersicht: Package-Struktur

### Ihr Projekt:

```
Ihr_Projekt/
│
├── barwerte/                    ← Das ist das PACKAGE
│   │
│   ├── __init__.py              ← Macht barwerte/ zum Package
│   │                               Definiert: was ist "public"
│   │
│   ├── sterbetafel.py           ← Klasse Sterbetafel, MAX_ALTER
│   │
│   ├── basisfunktionen.py       ← diskont, npx, nqx, abzugsglied
│   │                               Import: from .sterbetafel import ...
│   │
│   ├── finanzmathematik.py      ← ag_k
│   │                               Import: from .basisfunktionen import ...
│   │
│   ├── rentenbarwerte.py        ← ae_x, ae_xn, ae_x_k, ae_xn_k, ...
│   │                               Import: from .basisfunktionen import ...
│   │
│   └── leistungsbarwerte.py     ← nAe_x, nE_x, Ae_xn
│                                   Import: from .basisfunktionen import ...
│
├── data/                         ← Sterbetafeln (CSV)
│   ├── DAV1994T.csv
│   └── DAV2008T.csv
│
└── test_barwerte.py              ← Test-Script
                                     Import: from barwerte import ...
```

### Import-Fluss:

```
test_barwerte.py
    ↓
from barwerte import Sterbetafel, ae_x
    ↓
barwerte/__init__.py  (liest alle Module ein)
    ↓
from .sterbetafel import Sterbetafel
from .rentenbarwerte import ae_x
    ↓
rentenbarwerte.py
    ↓
from .basisfunktionen import diskont, npx
    ↓
basisfunktionen.py
    ↓
from .sterbetafel import Sterbetafel
```

---

## Zusammenfassung: Was Sie tun müssen

### 1. __init__.py anpassen

**Ersetzen Sie Ihre aktuelle `barwerte/__init__.py` durch die neue Version.**

Die neue `__init__.py` exportiert:
- `ae_x` statt `ax`
- `ae_xn` statt `axn`
- `nAe_x` statt `nAx`
- `nE_x` statt `nEx`
- Neue Funktionen: `Ae_xn`, `m_ae_xn_k`

**Datei:** `__init___angepasst.py` (umbenennen zu `__init__.py`)

### 2. sterbetafel.py anpassen

**Ersetzen Sie Ihre `barwerte/sterbetafel.py` durch die neue Version.**

Änderungen:
- MAX_ALTER = 121
- Filtert CSV-Daten: nur Alter 0-121 werden geladen
- Info-Meldung beim Laden

**Datei:** `sterbetafel_MAX121.py` (umbenennen zu `sterbetafel.py`)

### 3. Alle anderen Module korrigieren

Siehe `KORREKTURANLEITUNG.md` für:
- Korrekte Imports (mit `.`)
- Entfernung des `tafel`-Parameters
- Entfernung von `zw = 1` im abzugsglied

### 4. Test-Scripts anpassen

```python
# Alte Test-Scripts:
from barwerte import ax, axn, nAx, nEx

# Neue Test-Scripts:
from barwerte import ae_x, ae_xn, nAe_x, nE_x
```

---

## Schnelltest

Nach den Änderungen sollte dies funktionieren:

```python
from barwerte import Sterbetafel, ae_x, nAe_x, nE_x, ae_xn_k

# Sterbetafel laden
st = Sterbetafel("DAV1994T", data_dir="data")
# Ausgabe: Info: Von 124 Zeilen wurden 122 geladen (Alter 0-121)

# Test
print(f"MAX_ALTER: {st.max_alter}")  # 121
print(f"qx(40,M): {st.qx(40, 'M'):.8f}")

# Rentenbarwert
ax_wert = ae_x(40, 'M', 0.0175, st)
print(f"ae_x(40): {ax_wert:.6f}")

# Leistungsbarwert
Ax_wert = nAe_x(40, 30, 'M', 0.0175, st)
print(f"nAe_x(40,30): {Ax_wert:.8f}")
```

Wenn das funktioniert, ist alles korrekt!
