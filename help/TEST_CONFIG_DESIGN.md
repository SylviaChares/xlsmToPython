# Test-Konfiguration: Design-Entscheidung

## Problem
In der urspruenglichen Version wurden Testparameter in jeder Testfunktion einzeln definiert:

```python
def test_leibrenten(st: Sterbetafel):
    alter = 40
    sex = 'M'
    tafel = 'DAV1994_T'
    zins = 0.0175
    # ...
```

**Nachteile:**
- Parameter in jeder Funktion wiederholt
- Schwierig zu warten: Aenderungen muessen an vielen Stellen vorgenommen werden
- Inkonsistenzgefahr: Verschiedene Tests koennten unterschiedliche Werte verwenden
- Unuebersichtlich: Nicht sofort erkennbar, welche Testdaten verwendet werden

## Loesung: Zentrale TestConfig-Dataclass

### Implementation

```python
@dataclass
class TestConfig:
    """Zentrale Konfiguration fuer alle Tests."""
    alter: int = 40
    sex: str = 'M'
    tafel: str = 'DAV1994_T'
    zins: float = 0.0175
    laufzeit: int = 20
    laufzeit_lang: int = 30
    aufschub: int = 25
    zw: int = 12
    vs: float = 100000.00
    tafel_pfad: str = "C:/Users/chares/Documents/..."

# Globale Instanz
CONFIG = TestConfig()
```

### Verwendung in Tests

```python
def test_leibrenten(st: Sterbetafel):
    print(f"Parameter: Alter={CONFIG.alter}, Zins={CONFIG.zins:.4%}")
    ax_wert = ax(CONFIG.alter, CONFIG.sex, CONFIG.tafel, CONFIG.zins, st)
    # ...
```

## Vorteile dieser Loesung

### 1. Konsistenz
- Alle Tests verwenden identische Parameter
- Ergebnisse sind direkt vergleichbar
- Keine Abweichungen durch Tippfehler

### 2. Wartbarkeit
- Ein einziger Ort zum Aendern aller Testparameter
- Aenderungen wirken sich auf alle Tests aus
- Weniger Fehleranfaelligkeit

### 3. Dokumentation
- Testparameter sind am Dateianfang sofort sichtbar
- `__str__()` zeigt formatierte Uebersicht
- Klare Benennung der Parameter

### 4. Typsicherheit
- Type hints in der Dataclass
- IDE kann Fehler frueh erkennen
- Autocomplete funktioniert

### 5. Flexibilitaet
- Alternative Szenarien moeglich:
  ```python
  CONFIG_JUNG = TestConfig(alter=25, laufzeit=40)
  CONFIG_ALT = TestConfig(alter=60, laufzeit=10)
  ```

### 6. Erweiterbarkeit
- Neue Parameter koennen einfach hinzugefuegt werden
- Bestehende Tests bleiben kompatibel (Default-Werte)

## Alternativen und deren Bewertung

### Alternative 1: Globale Konstanten
```python
TEST_ALTER = 40
TEST_SEX = 'M'
# ...
```

**Pro:**
- Einfachste Implementierung
- Kein Import noetig

**Contra:**
- Keine Strukturierung
- Kein Type Hinting
- Kein IDE-Support
- Keine Gruppierung moeglich

### Alternative 2: Dictionary
```python
TEST_PARAMS = {
    'alter': 40,
    'sex': 'M',
    # ...
}
```

**Pro:**
- Einfach
- JSON-kompatibel

**Contra:**
- Keine Typsicherheit
- Tippfehler bei Keys erst zur Laufzeit erkannt
- Kein Autocomplete

### Alternative 3: Config-Datei (YAML/JSON)
```python
# config.yaml
test:
  alter: 40
  sex: M
  # ...
```

**Pro:**
- Externe Konfiguration
- Keine Code-Aenderung noetig

**Contra:**
- Zusaetzliche Dependency (PyYAML)
- Mehr Komplexitaet
- Schwieriger zu debuggen
- Overhead fuer kleine Test-Suite

## Fazit: Warum Dataclass?

Fuer diesen aktuariellen Anwendungsfall ist die **Dataclass-Loesung optimal**, weil:

1. **Aktuarielle Praxis**: Parameter gehoeren zusammen (Alter, Geschlecht, Tafel)
2. **Transparenz**: Sofort erkennbar, welche Werte getestet werden
3. **Professionell**: Type hints und Dokumentation entsprechen Python-Standards
4. **Pragmatisch**: Balance zwischen Einfachheit und Funktionalitaet
5. **Wartbar**: Ideal fuer langfristige Projektwartung

## Verwendung

### Standard-Tests ausfuehren
```bash
python test_barwerte.py
```

### Alternative Szenarien testen
```python
# In test_barwerte.py oder eigenem Script
CONFIG_JUNG = TestConfig(alter=25, laufzeit=40)
st = Sterbetafel(CONFIG_JUNG.tafel_pfad)
ax_wert = ax(CONFIG_JUNG.alter, CONFIG_JUNG.sex, CONFIG_JUNG.tafel, 
             CONFIG_JUNG.zins, st)
```

### Parameter anpassen
Einfach die Default-Werte in der TestConfig-Klasse aendern:

```python
@dataclass
class TestConfig:
    alter: int = 45  # <- geaendert
    zins: float = 0.02  # <- geaendert
    # ...
```

Alle Tests verwenden automatisch die neuen Werte.
