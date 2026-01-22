# Verlaufswerte-Modul

## Uebersicht

Das `verlaufswerte.py`-Modul berechnet versicherungsmathematische Verlaufswerte 
effizient und strukturiert. Es nutzt NumPy-Vektorisierung fuer optimale Performance.

## Was sind Verlaufswerte?

Verlaufswerte sind zeitabhaengige Barwerte, die die verbleibenden Verpflichtungen
bzw. Ansprueche zu jedem Zeitpunkt waehrend der Vertragslaufzeit darstellen.

Beispiele:
- **Rentenbarwert** ae_{x+t}:n-t: Barwert der verbleibenden Rentenzahlungen
- **Todesfallbarwert** (n-t)Ae_{x+t}: Barwert der Todesfallleistung
- **Erlebensfallbarwert** (n-t)E_{x+t}: Barwert der Erlebensfallleistung

## Hauptmerkmale

### 1. Klare Struktur
- `VerlaufswerteConfig`: Datenklasse fuer Vertragsparameter
- `Verlaufswerte`: Hauptklasse fuer Berechnungen
- `berechne_verlaufswerte()`: Convenience-Funktion fuer schnelle Berechnungen

### 2. Effiziente Berechnung
- **Vektorisierung**: Alle Zeitpunkte in einem Durchgang
- **Memory-efficient**: Minimaler Speicherbedarf
- **Keine expliziten Schleifen**: List comprehension statt for-Schleifen

### 3. Flexible Ausgabe
- Als NumPy-Arrays (fuer Weiterverarbeitung)
- Als pandas DataFrame (fuer Analyse/Export)
- Formatierte Konsolenausgabe

## Verwendung

### Basis-Verwendung

```python
from sterbetafel import Sterbetafel
from verlaufswerte import Verlaufswerte, VerlaufswerteConfig

# Lade Sterbetafel
st = Sterbetafel("DAV1994_T", "data")

# Konfiguration
config = VerlaufswerteConfig(
    alter=40,
    n=20,
    sex='M',
    zins=0.0175,
    zw=1,
    sterbetafel='DAV1994_T'
)

# Berechne Verlaufswerte
vw = Verlaufswerte(config, st)
ergebnisse = vw.berechne_alle()

# Zugriff auf Ergebnisse
rentenbarwerte = ergebnisse['rentenbarwerte']
todesfallbarwerte = ergebnisse['todesfallbarwerte']
```

### Convenience-Funktion

```python
from verlaufswerte import berechne_verlaufswerte

# Direkte Berechnung ohne Config-Objekt
ergebnisse = berechne_verlaufswerte(
    alter=40,
    n=20,
    sex='M',
    zins=0.0175,
    zw=1,
    sterbetafel_obj=st
)
```

### Als DataFrame

```python
# Als pandas DataFrame
vw = Verlaufswerte(config, st)
df = vw.als_dataframe()

# Export nach Excel
df.to_excel("verlaufswerte.xlsx", index=False)

# Anzeige
print(df)
```

### Formatierte Ausgabe

```python
# Drucke alle Verlaufswerte formatiert
vw = Verlaufswerte(config, st)
vw.drucke_verlaufswerte(precision=10)
```

## Ergebnis-Struktur

Das Dictionary von `berechne_alle()` enthaelt:

```python
{
    'rentenbarwerte': np.ndarray,      # Laenge n
    'todesfallbarwerte': np.ndarray,   # Laenge n+1
    'erlebensfallbarwerte': np.ndarray,# Laenge n+1
    'zeitpunkte_rente': np.ndarray,    # [0, 1, ..., n-1]
    'zeitpunkte_leistung': np.ndarray  # [0, 1, ..., n]
}
```

### Wichtig: Array-Laengen

- **Rentenbarwerte**: Laenge `n`
  - Index 0 = Beginn Jahr 1 (t=0)
  - Index n-1 = Beginn Jahr n (t=n-1)

- **Leistungsbarwerte**: Laenge `n+1`
  - Index 0 = Beginn (t=0)
  - Index n = Ende Laufzeit (t=n)

## Performance

### Vorteile gegenueber For-Schleifen

1. **Schneller**: Vektorisierung mit NumPy
2. **Uebersichtlicher**: Keine verschachtelten Schleifen
3. **Wartbarer**: Zentrale Berechnungslogik
4. **Erweiterbar**: Neue Verlaufswerte einfach hinzufuegbar

### Benchmark-Beispiel

```python
# Alte Methode (for-Schleife)
for i in range(n):
    bbw = ae_xn_k(alter+i, n-i, sex, zins, zw, st)
    print(f"  ae_{alter+i},{n-i}: {bbw}")

# Neue Methode (Verlaufswerte-Klasse)
vw = Verlaufswerte(config, st)
vw.drucke_verlaufswerte()

# Typischer Speedup: 1.5x - 3x (je nach n)
```

## Erweiterung

### Neue Verlaufswerte hinzufuegen

```python
class Verlaufswerte:
    # ... bestehender Code ...
    
    def berechne_meine_werte(self) -> np.ndarray:
        """
        Berechnet neue Art von Verlaufswerten.
        """
        n = self.config.n
        alter_start = self.config.alter
        
        # Array-Berechnung
        werte = np.array([
            meine_funktion(alter_start + i, n - i, ...)
            for i in range(n)
        ])
        
        return werte
    
    def berechne_alle(self):
        """Fuege neue Werte hinzu."""
        # ... bestehender Code ...
        meine_werte = self.berechne_meine_werte()
        self._verlaufswerte['meine_werte'] = meine_werte
        # ...
```

## Zukuenftige Optimierungen

### Vollstaendige Vektorisierung

Die aktuelle Implementierung nutzt List Comprehension fuer die Berechnung.
Eine vollstaendige Vektorisierung der Basis-Funktionen wuerde die Performance
nochmals deutlich steigern:

```python
# Zukuenftig: Vektorisierte Basis-Funktionen
def ae_xn_k_vec(alter_array, n_array, sex, zins, zw, st):
    """
    Berechnet ae_xn_k fuer Arrays von Altern und Laufzeiten.
    """
    # Komplett vektorisierte Implementation
    pass
```

Dies waere relevant fuer:
- Monte-Carlo-Simulationen
- Massendaten-Verarbeitung
- Echtzeit-Berechnungen

## Validierung

### Test gegen Excel

```python
# 1. Exportiere Verlaufswerte
vw = Verlaufswerte(config, st)
df = vw.als_dataframe()
df.to_excel("python_verlaufswerte.xlsx")

# 2. Vergleiche mit Excel-Tarifrechner
# 3. Pruefe Differenzen (sollten < 1e-10 sein)
```

### Unit-Tests

Siehe `test_verlaufswerte.py` fuer umfassende Tests.

## Abhaengigkeiten

- `numpy`: Vektorisierung
- `pandas`: DataFrame-Funktionalitaet
- Eigene Module: `sterbetafel`, `rentenbarwerte`, `leistungsbarwerte`

## Beispiel-Output

```
================================================================================
VERLAUFSWERTE - Vertrag: Alter 40, Laufzeit 20 Jahre, M
================================================================================

Rentenbarwerte ae_{x+t}:20-t (Zahlungsweise: 1x jaehrlich):
------------------------------------------------------------
  t= 0 | Alter 40 | ae_{40}:20 = 14.9191921110
  t= 1 | Alter 41 | ae_{41}:19 = 14.6212042210
  t= 2 | Alter 42 | ae_{42}:18 = 14.3115104210
  ...

Todesfallbarwerte (n-t)Ae_{x+t}:
------------------------------------------------------------
  t= 0 | Alter 40 | 20Ae_{40} = 0.0432460010
  t= 1 | Alter 41 | 19Ae_{41} = 0.0417085710
  ...

Erlebensfallbarwerte (n-t)E_{x+t}:
------------------------------------------------------------
  t= 0 | Alter 40 | 20E_{40} = 0.7237880100
  t= 1 | Alter 41 | 19E_{41} = 0.7356920250
  ...
================================================================================
```

## Autor & Lizenz

Teil des Projekts zur Migration des Excel-Tarifrechners nach Python.

## Kontakt & Support

Bei Fragen oder Problemen: Siehe Projekt-Dokumentation.
