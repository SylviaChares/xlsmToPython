# Sterbetafel-Klasse: CSV-Format und Verwendung

## CSV-Dateiformat

Die Sterbetafel-Klasse liest CSV-Dateien im **deutschen Format**:

### Format-Spezifikationen:
- **Trennzeichen**: Semikolon (`;`)
- **Dezimaltrennzeichen**: Komma (`,`)
- **Spalten**: `Alter;qx;qy`

### Beispiel (DAV1994T.csv):
```csv
Alter;qx;qy
0;0,011687;0,009003
1;0,001008;0,000867
2;0,000728;0,000624
3;0,000542;0,000444
...
122;0,995;0,995
123;1,0;1,0
```

### Spalten-Bedeutung:
- **Alter**: Alter in Jahren (0 bis 123)
- **qx**: Sterbewahrscheinlichkeit männlich
- **qy**: Sterbewahrscheinlichkeit weiblich

## Anpassung der Sterbetafel-Klasse

Die Klasse wurde angepasst, um das deutsche CSV-Format zu unterstützen:

```python
self.data = pd.read_csv(
    csv_file, 
    sep=';',         # Semikolon als Trennzeichen
    decimal=','      # Komma als Dezimaltrennzeichen
)
```

**Wichtig**: Diese Einstellung ist notwendig, da deutsche Excel-Exporte standardmäßig:
- Semikolon (`;`) als Feldtrennzeichen verwenden
- Komma (`,`) als Dezimaltrennzeichen verwenden

## Verwendung

### 1. Sterbetafel laden

```python
from barwerte import Sterbetafel

# Lade Sterbetafel aus CSV-Datei
st = Sterbetafel("DAV1994T", data_dir="C:/path/to/data")

# Die Klasse sucht automatisch nach: C:/path/to/data/DAV1994T.csv
```

### 2. Einzelne Sterbewahrscheinlichkeit abrufen

```python
# Männlich, Alter 40
qx_40_m = st.qx(40, 'M')
print(f"qx(40, M) = {qx_40_m:.8f}")

# Weiblich, Alter 40
qx_40_f = st.qx(40, 'F')
print(f"qx(40, F) = {qx_40_f:.8f}")
```

### 3. Vektor von Sterbewahrscheinlichkeiten

```python
# qx-Werte für Alter 40-44 (5 Jahre)
qx_vec = st.qx_vec(40, 5, 'M')
print(f"qx-Vektor: {qx_vec}")

# px-Werte (Überlebenswahrscheinlichkeiten)
px_vec = st.px_vec(40, 5, 'M')
print(f"px-Vektor: {px_vec}")
```

### 4. Informationen anzeigen

```python
# Detaillierte Informationen zur Tafel
print(st.info())

# Kurzform
print(st)  # Zeigt: Sterbetafel('DAV1994T', Alter: 0-123, Zeilen: 124)
```

## Vollständiges Beispiel

```python
from barwerte import Sterbetafel, nAx, nEx, axn_k

# Parameter
alter = 40
sex = 'M'
n = 30  # Versicherungsdauer
t = 20  # Beitragszahldauer
zins = 0.0175
zw = 12  # monatlich
vs = 100000.00

# Sterbetafel laden
st = Sterbetafel('DAV1994T', data_dir='C:/Users/.../data')

# Barwerte berechnen
Bxt = nAx(alter, n, sex, st, zins)  # Todesfall
Bxe = nEx(alter, n, sex, st, zins)  # Erlebensfall
Pxt = axn_k(alter, t, sex, st, zins, zw)  # Beitrag

# Prämie
praemie_jahres = (Bxt + Bxe) / Pxt * vs
praemie_monats = praemie_jahres / 12

print(f"Jahresprämie:  {praemie_jahres:,.2f} EUR")
print(f"Monatsprämie:  {praemie_monats:,.2f} EUR")
```

## Mehrere Tafeln verwenden

```python
from barwerte import Sterbetafel, ax

# Lade beide Tafeln
st_1994 = Sterbetafel('DAV1994T', data_dir='data')
st_2008 = Sterbetafel('DAV2008T', data_dir='data')

# Vergleich Leibrente
ax_1994 = ax(40, 'M', st_1994, 0.0175)
ax_2008 = ax(40, 'M', st_2008, 0.0175)

print(f"ax mit DAV1994T: {ax_1994:.6f}")
print(f"ax mit DAV2008T: {ax_2008:.6f}")
print(f"Differenz:       {ax_2008 - ax_1994:.6f}")
```

## CSV-Export aus Excel

Falls Sie neue Sterbetafeln aus Excel exportieren:

### In Excel:
1. Datei → Speichern unter
2. Dateityp: **CSV (Trennzeichen-getrennt) (*.csv)**
3. Wichtig: Excel verwendet automatisch:
   - Semikolon als Trennzeichen
   - Komma als Dezimaltrennzeichen

### Datenstruktur in Excel:

| Spalte A | Spalte B | Spalte C |
|----------|----------|----------|
| Alter    | qx       | qy       |
| 0        | 0,011687 | 0,009003 |
| 1        | 0,001008 | 0,000867 |
| ...      | ...      | ...      |

### Nach dem Export:
- Dateiname: `{TAFELNAME}.csv` (z.B. `DAV1994T.csv`)
- Speicherort: Im `data/` Verzeichnis

## Fehlerbehebung

### Fehler: "Sterbetafel nicht gefunden"
```
FileNotFoundError: Sterbetafel 'DAV1994T' nicht gefunden.
Erwarteter Pfad: C:/Users/.../data/DAV1994T.csv
```

**Lösung**: 
- Prüfen Sie, ob die CSV-Datei im angegebenen Verzeichnis existiert
- Prüfen Sie die Schreibweise des Tafelnamens (Groß-/Kleinschreibung!)

### Fehler: "CSV-Struktur nicht korrekt"
```
ValueError: CSV-Datei hat nicht die erwartete Struktur.
Erwartet: ['Alter', 'qx', 'qy']
```

**Lösung**:
- Erste Zeile muss Header sein: `Alter;qx;qy`
- Spaltennamen exakt so schreiben (Groß-/Kleinschreibung!)

### Fehler: Zahlen werden nicht korrekt gelesen
```
# qx-Werte sind viel zu groß oder NaN
```

**Lösung**:
- Prüfen Sie das Dezimaltrennzeichen in der CSV
- Deutsche CSV: Komma (`,`)
- Englische CSV: Punkt (`.`)
- Die Klasse ist auf deutsches Format eingestellt!

### Bei englischem CSV-Format:
Falls Ihre CSV-Dateien Punkt (`.`) als Dezimaltrennzeichen verwenden:

```python
# Ändern Sie in sterbetafel.py:
self.data = pd.read_csv(
    csv_file, 
    sep=';',
    decimal='.'  # Punkt statt Komma
)
```

## Zusammenfassung

Die Sterbetafel-Klasse:
- ✓ Lädt CSV-Dateien im deutschen Format (`;` und `,`)
- ✓ Cached geladene Daten für Performance
- ✓ Validiert Struktur beim Laden
- ✓ Bietet einfachen Zugriff auf qx/qy-Werte
- ✓ Unterstützt Vektoren für effiziente Berechnungen
- ✓ Zeigt Fehler mit hilfreichen Meldungen

**Empfehlung**: Belassen Sie CSV-Dateien im deutschen Excel-Format, da die Klasse bereits darauf optimiert ist.
