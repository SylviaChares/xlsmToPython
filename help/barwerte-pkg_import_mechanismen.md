# Import-Mechanismen im barwerte-Package

## Zusammenfassung

| Wo? | Import-Syntax | Zweck |
|-----|--------------|-------|
| **Innerhalb barwerte/** | `from .modul import funktion` | Relative Imports zwischen Modulen |
| **Außerhalb (Tests, Notebooks)** | `from barwerte import ...` | Absolute Imports von installiertem Package |

---

## 1. Innerhalb des barwerte-Packages

### ✅ So bleibt es (RICHTIG):

```python
# In barwerte/leistungsbarwerte.py
from .sterbetafel import Sterbetafel, MAX_ALTER
from .basisfunktionen import diskont, abzugsglied, npx, nqx
```

**Warum der Punkt (`.`)?**
- `.` = "aus dem gleichen Package"
- Relative Imports innerhalb eines Packages
- Standard-Praxis in Python-Packages

**Alternativen (funktionieren auch, aber nicht empfohlen):**

```python
# Absolute Imports (funktioniert, aber unüblich innerhalb Package)
from barwerte.sterbetafel import Sterbetafel
from barwerte.basisfunktionen import npx

# NICHT empfohlen innerhalb des Packages!
# Grund: Weniger flexibel bei Package-Umbenennung
```

---

## 2. Außerhalb des barwerte-Packages (Tests, Notebooks)

### Variante A: Einzelne Funktionen importieren (EMPFOHLEN)

```python
# In test_*.py oder Jupyter Notebooks
from barwerte import Sterbetafel, MAX_ALTER
from barwerte.basisfunktionen import npx, diskont
from barwerte.leistungsbarwerte import ae_xn_k

# Verwendung:
tafel = Sterbetafel("DAV2008_T")
wert = npx(40, 10, "M", "DAV2008_T")
```

**Vorteile:**
- ✅ Klar, welche Funktionen verwendet werden
- ✅ Kurze, lesbare Aufrufe
- ✅ IDE kann Auto-Complete anbieten
- ✅ Keine Namenskonflikte

### Variante B: Gesamtes Modul importieren

```python
# In test_*.py oder Jupyter Notebooks
import barwerte.basisfunktionen as bf
import barwerte.leistungsbarwerte as lb

# Verwendung:
wert = bf.npx(40, 10, "M", "DAV2008_T")
rente = lb.ae_xn_k(40, 20, "M", "DAV2008_T", 0.0175, 12)
```

**Vorteile:**
- ✅ Klar erkennbar, woher Funktion kommt
- ✅ Vermeidet Namenskonflikte (z.B. wenn npx mehrfach existiert)

**Nachteile:**
- ⚠️ Längere Schreibweise: `bf.npx()` statt `npx()`

### Variante C: Nur `import barwerte`

```python
# In test_*.py oder Jupyter Notebooks
import barwerte

# Verwendung:
tafel = barwerte.Sterbetafel("DAV2008_T")
wert = barwerte.basisfunktionen.npx(40, 10, "M", "DAV2008_T")
```

**Funktioniert das?**
- ⚠️ **NUR wenn Sie `__init__.py` entsprechend konfigurieren!**
- Standardmäßig: **NEIN**, Funktionen sind nicht direkt verfügbar

---

## 3. Die Rolle von `__init__.py`

Die `__init__.py` entscheidet, was bei `import barwerte` passiert.

### Aktuelle Situation (minimale __init__.py):

```python
# barwerte/__init__.py (aktuell)
from .sterbetafel import Sterbetafel, MAX_ALTER
```

**Ergebnis:**

```python
import barwerte

# ✅ Funktioniert:
tafel = barwerte.Sterbetafel("DAV2008_T")
print(barwerte.MAX_ALTER)

# ❌ Funktioniert NICHT:
barwerte.npx(40, 10, "M", "DAV2008_T")  # AttributeError!

# ✅ Funktioniert (voller Pfad):
barwerte.basisfunktionen.npx(40, 10, "M", "DAV2008_T")
```

### Erweiterte __init__.py (alle Funktionen direkt verfügbar):

```python
# barwerte/__init__.py (erweitert)
from .sterbetafel import Sterbetafel, MAX_ALTER
from .basisfunktionen import (
    diskont, abzugsglied, npx, nqx
)
from .leistungsbarwerte import (
    ae_x, ae_x_k, ae_xn, ae_xn_k, 
    n_ae_x_k, m_ae_xn_k,
    nAe_x, nE_x, ag_k
)

# Optional: Public API definieren
__all__ = [
    'Sterbetafel', 'MAX_ALTER',
    'diskont', 'abzugsglied', 'npx', 'nqx',
    'ae_x', 'ae_x_k', 'ae_xn', 'ae_xn_k',
    'n_ae_x_k', 'm_ae_xn_k',
    'nAe_x', 'nE_x', 'ag_k',
]
```

**Ergebnis:**

```python
import barwerte

# ✅ Jetzt funktioniert alles direkt:
tafel = barwerte.Sterbetafel("DAV2008_T")
wert = barwerte.npx(40, 10, "M", "DAV2008_T")
rente = barwerte.ae_xn_k(40, 20, "M", "DAV2008_T", 0.0175, 12)
```

---

## 4. Empfohlene Struktur für Ihr Projekt

### barwerte/__init__.py (empfohlen):

```python
"""
barwerte - Versicherungsmathematische Barwertfunktionen
=======================================================

Dieses Package stellt Funktionen zur Berechnung versicherungsmathematischer
Barwerte fuer Lebensversicherungen bereit.

Hauptkomponenten:
- Sterbetafel: Verwaltung von Sterbetafeln (DAV1994_T, DAV2008_T)
- Basisfunktionen: npx, nqx, diskont, abzugsglied
- Leistungsbarwerte: Leibrenten und Versicherungsleistungen
"""

# Version
__version__ = "0.1.0"

# Hauptklassen und Konstanten
from .sterbetafel import Sterbetafel, MAX_ALTER

# Basisfunktionen (optional: für direkten Zugriff)
from .basisfunktionen import (
    diskont, 
    abzugsglied, 
    npx, 
    nqx
)

# Leistungsbarwerte (optional: für direkten Zugriff)
from .leistungsbarwerte import (
    ae_x, ae_x_k, ae_xn, ae_xn_k,
    n_ae_x_k, m_ae_xn_k,
    nAe_x, nE_x, ag_k
)

# Public API definieren
__all__ = [
    # Kernklassen
    'Sterbetafel',
    'MAX_ALTER',
    # Basisfunktionen
    'diskont',
    'abzugsglied',
    'npx',
    'nqx',
    # Leistungsbarwerte
    'ae_x',
    'ae_x_k',
    'ae_xn',
    'ae_xn_k',
    'n_ae_x_k',
    'm_ae_xn_k',
    'nAe_x',
    'nE_x',
    'ag_k',
]
```

### In Tests und Notebooks:

```python
# Empfohlener Import-Stil
from barwerte import Sterbetafel, MAX_ALTER
from barwerte.basisfunktionen import npx, diskont
from barwerte.leistungsbarwerte import ae_xn_k

# Oder: Falls __init__.py erweitert (siehe oben)
import barwerte

tafel = barwerte.Sterbetafel("DAV2008_T")
wert = barwerte.npx(40, 10, "M", "DAV2008_T")
```

---

## 5. Best Practices

### ✅ DO - Empfohlene Imports:

```python
# Explizit und klar
from barwerte import Sterbetafel
from barwerte.basisfunktionen import npx, diskont
from barwerte.leistungsbarwerte import ae_xn_k

# Oder mit Alias
import barwerte.basisfunktionen as bf
import barwerte.leistungsbarwerte as lb
```

### ⚠️ AVOID - Nicht empfohlen:

```python
# Wildcard-Imports (schwer nachvollziehbar)
from barwerte import *
from barwerte.basisfunktionen import *

# Ausnahme: In interaktiven Sessions (Jupyter) manchmal OK
```

### ❌ DON'T - Vermeiden:

```python
# Innerhalb barwerte/: KEINE absoluten Imports
# In barwerte/leistungsbarwerte.py
from barwerte.sterbetafel import Sterbetafel  # ❌ Nicht innerhalb Package

# Stattdessen:
from .sterbetafel import Sterbetafel  # ✅ Relative Imports
```

---

## 6. Praktisches Beispiel

### Projektstruktur:

```
xlsmToPython/
├── setup.py
├── barwerte/
│   ├── __init__.py          # Definiert Public API
│   ├── sterbetafel.py       # Verwendet relative Imports
│   ├── basisfunktionen.py   # Verwendet relative Imports
│   └── leistungsbarwerte.py # Verwendet relative Imports
└── tests/
    └── test_leistungsbarwerte.py  # Verwendet absolute Imports
```

### In barwerte/leistungsbarwerte.py:

```python
# Relative Imports (innerhalb Package)
from .sterbetafel import Sterbetafel, MAX_ALTER
from .basisfunktionen import diskont, npx, nqx, abzugsglied

def ae_xn_k(alter, n, sex, tafel_name, zins, zw):
    """Temporaere Leibrente mit k Zahlungen p.a."""
    tafel = Sterbetafel(tafel_name)
    # ... Rest der Funktion
```

### In tests/test_leistungsbarwerte.py:

```python
# Absolute Imports (außerhalb Package)
import pytest
from barwerte import Sterbetafel, MAX_ALTER
from barwerte.leistungsbarwerte import ae_xn_k

def test_ae_xn_k():
    """Test temporaere Leibrente"""
    result = ae_xn_k(40, 20, "M", "DAV2008_T", 0.0175, 12)
    assert result > 0
```

### In Jupyter Notebook:

```python
# Variante 1: Explizite Imports (EMPFOHLEN für Produktionscode)
from barwerte import Sterbetafel
from barwerte.basisfunktionen import npx, diskont
from barwerte.leistungsbarwerte import ae_xn_k

tafel = Sterbetafel("DAV2008_T")
wert = npx(40, 10, "M", "DAV2008_T")
rente = ae_xn_k(40, 20, "M", "DAV2008_T", 0.0175, 12)

# Variante 2: Namespace-Import (EMPFOHLEN für Klarheit)
import barwerte as bw
import barwerte.basisfunktionen as bf

tafel = bw.Sterbetafel("DAV2008_T")
wert = bf.npx(40, 10, "M", "DAV2008_T")

# Variante 3: Wildcard (OK für interaktive Exploration)
from barwerte import *
from barwerte.basisfunktionen import *

tafel = Sterbetafel("DAV2008_T")
wert = npx(40, 10, "M", "DAV2008_T")
```

---

## 7. Zusammenfassung der Antworten

### Frage 1: Müssen relative Imports in .py-Dateien bleiben?

**Antwort: JA**

```python
# In barwerte/leistungsbarwerte.py - SO BLEIBT ES:
from .sterbetafel import Sterbetafel
from .basisfunktionen import npx
```

### Frage 2: Kann ich in Tests einzelne Funktionen importieren?

**Antwort: JA**

```python
# In test_*.py - BEIDE Varianten funktionieren:

# Alt (funktioniert weiterhin):
from barwerte import (
    Sterbetafel, diskont, npx, nqx, abzugsglied,
    ae_x, ae_x_k, ae_xn, ae_xn_k
)

# Neu (übersichtlicher bei vielen Funktionen):
from barwerte import Sterbetafel
from barwerte.basisfunktionen import npx, diskont
from barwerte.leistungsbarwerte import ae_xn_k
```

### Frage 3: Kann ich nur `import barwerte` schreiben?

**Antwort: JAIN - abhängig von __init__.py**

```python
import barwerte

# Funktioniert IMMER (Sub-Module explizit):
barwerte.basisfunktionen.npx(40, 10, "M", "DAV2008_T")

# Funktioniert NUR wenn in __init__.py importiert:
barwerte.npx(40, 10, "M", "DAV2008_T")

# Funktioniert IMMER (in __init__.py definiert):
barwerte.Sterbetafel("DAV2008_T")
```

**Empfehlung:** Erweitern Sie `__init__.py` wie oben gezeigt, dann funktioniert beides!

---

## 8. Cheat Sheet

```python
# ============================================
# INNERHALB barwerte/ (z.B. leistungsbarwerte.py)
# ============================================
from .sterbetafel import Sterbetafel          # ✅ Relative Imports
from .basisfunktionen import npx, diskont     # ✅

# ============================================
# AUSSERHALB barwerte/ (Tests, Notebooks)
# ============================================

# Variante 1: Explizit (am klarsten)
from barwerte import Sterbetafel
from barwerte.basisfunktionen import npx
from barwerte.leistungsbarwerte import ae_xn_k

# Variante 2: Mit Alias (bei Namenskonflikten)
import barwerte.basisfunktionen as bf
import barwerte.leistungsbarwerte as lb
wert = bf.npx(40, 10, "M", "DAV2008_T")

# Variante 3: Gesamtes Package (wenn __init__.py erweitert)
import barwerte
wert = barwerte.npx(40, 10, "M", "DAV2008_T")  # Nur wenn in __init__.py!

# Variante 4: Wildcard (nur für interaktive Sessions)
from barwerte import *
```
