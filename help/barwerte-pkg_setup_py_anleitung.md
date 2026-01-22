# Setup.py - Speicherort und Funktionsweise

## Wo liegt setup.py?

Die `setup.py` muss im **Root-Verzeichnis Ihres Projekts** liegen, also:

```
C:\Users\chares\Documents\Notebooks\xlsmToPython\
├── setup.py                    # HIER!
├── barwerte\
│   ├── __init__.py
│   ├── sterbetafel.py
│   ├── basisfunktionen.py
│   └── ...
├── data\
└── tests\
```

**Nicht** irgendwo anders, denn die `setup.py` definiert, welche Packages sich **relativ zu ihr** befinden.

## Wie funktioniert das genau?

### 1. Was passiert bei `pip install -e .`?

```powershell
cd C:\Users\chares\Documents\Notebooks\xlsmToPython
pip install -e .
```

Der `.` bedeutet: "Installiere das Package aus dem aktuellen Verzeichnis"

**Editable Mode (`-e`):**
- Python erstellt einen **symbolischen Link** (Verweis) von Ihrer Python-Installation zu Ihrem Projekt-Ordner
- Änderungen an den .py-Dateien wirken sich **sofort** aus (kein Neuinstallieren nötig)
- Perfekt für Entwicklung!

### 2. Was macht `find_packages()`?

```python
packages=find_packages()
```

Diese Funktion sucht automatisch nach allen Ordnern mit `__init__.py`:
- Findet `barwerte/` → registriert als Package
- Später auch: `barwerte/leibrenten/` → als Sub-Package (falls gewünscht)

### 3. Danach funktioniert überall:

```python
# In jedem Jupyter Notebook, egal wo:
from barwerte import Sterbetafel
from barwerte.basisfunktionen import npx
```

Python findet das Package, weil es in `site-packages` registriert ist.

## Empfohlene setup.py für Ihr Projekt

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="barwerte",
    version="0.1.0",
    description="Versicherungsmathematische Barwertfunktionen",
    author="Sylvie",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.24.0',
        'pandas>=2.0.0',
        'openpyxl>=3.1.0',  # falls Sie Excel-Dateien lesen
    ],
    python_requires='>=3.11',
)
```

## Vorteile dieser Methode

### ✅ Für Ihre Situation ideal:

1. **Erweiterbarkeit**: Neue Module einfach zu `barwerte/` hinzufügen
   ```
   barwerte/
   ├── __init__.py
   ├── sterbetafel.py
   ├── basisfunktionen.py
   ├── leibrenten.py        # NEU
   └── versicherungen.py    # NEU
   ```

2. **Keine Pfad-Probleme mehr**: 
   - Funktioniert in Jupyter Notebooks
   - Funktioniert in Scripts
   - Funktioniert in Tests

3. **Professionelle Struktur**:
   - Ähnlich wie pandas, numpy installiert sind
   - Andere Aktuare können Ihr Package nutzen

4. **Versionierung möglich**:
   ```python
   version="0.2.0"  # Nach größeren Updates
   ```

## Alternative: Nur __init__.py (Ihre aktuelle Methode)

```python
# Ohne setup.py müssen Sie immer:
import sys
sys.path.append('C:\\Users\\chares\\Documents\\Notebooks\\xlsmToPython')
from barwerte import ...
```

**Nachteile:**
- Funktioniert nur, wenn Notebook im richtigen Ordner liegt
- Bei mehreren Notebooks: Code-Duplikation
- Pfad-Probleme bei Ordner-Verschiebung

## Empfehlung

**Ja, setup.py ergibt absolut Sinn für Ihr Projekt!**

Gründe:
1. Sie planen langfristige Erweiterung
2. Mehrere Notebooks/Scripts sollen das Package nutzen
3. Professioneller Ansatz (wie Sie es von R-Packages kennen)
4. Einfaches Deployment später möglich

## Installation - Schritt für Schritt

```powershell
# 1. Navigieren zum Projekt
cd C:\Users\chares\Documents\Notebooks\xlsmToPython

# 2. setup.py erstellen (siehe oben)

# 3. Editable Mode installieren
pip install -e .

# 4. Testen
python -c "from barwerte import Sterbetafel; print('Success!')"
```

## Was passiert bei Updates?

Wenn Sie neue Funktionen zu `barwerte/leibrenten.py` hinzufügen:

```python
# Kein Re-Install nötig wegen -e Flag!
# Sofort nutzbar:
from barwerte.leibrenten import axn_k
```

Nur bei Änderungen an `setup.py` selbst (z.B. neue Dependencies):
```powershell
pip install -e . --upgrade
```

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'barwerte'"

**Lösung:**
```powershell
# Prüfen, ob Package installiert ist
pip list | findstr barwerte

# Falls nicht gefunden, neu installieren
cd C:\Users\chares\Documents\Notebooks\xlsmToPython
pip install -e .
```

### Problem: Änderungen werden nicht übernommen

**Lösung:**
```python
# Jupyter Notebook: Kernel neu starten
# Oder: Modul neu laden
import importlib
import barwerte
importlib.reload(barwerte)
```

### Problem: Verschiedene Python-Versionen

**Lösung:**
```powershell
# Explizit Python-Version angeben
python3.11 -m pip install -e .
```
