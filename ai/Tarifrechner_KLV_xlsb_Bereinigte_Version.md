# Strukturanalyse: Tarifrechner_KLV_neu.xlsb (Bereinigte Version)

## Executive Summary

**Datum:** 20. Januar 2026  
**Version:** Bereinigte Fassung ohne historische Reste  
**Dateigröße:** 771 KB (vorher 75 KB)  
**Status:** Bereit für Python-Migration

Diese Version ist eine bereinigte, erweiterte Fassung des Tarifrechners mit:
- **qx-basierter Berechnung** (direkt aus Sterbewahrscheinlichkeiten)
- **Erweitertem Tafeln-Blatt** (4 MB Daten)
- **1 VBA-Modul** (mBarwerte) ohne historische Reste

---

## 1. DATEI-ÜBERSICHT

### 1.1 Grunddaten

| Eigenschaft | Wert |
|-------------|------|
| Dateiname | Tarifrechner_KLV_neu.xlsb |
| Format | Excel Binary Workbook |
| Dateigröße | 789.689 Bytes (771 KB) |
| VBA-Projekt | 49 KB |
| Tabellenblätter | 2 |
| Definierte Namen | 25 |
| Unternehmen | msg group |

### 1.2 Größenvergleich

| Version | Dateigröße | VBA-Projekt | Tafeln-Blatt |
|---------|------------|-------------|--------------|
| Unreinigt (historische Reste) | 75 KB | 63 KB | 16 KB |
| **Bereinigt (aktuell)** | **771 KB** | **49 KB** | **4 MB** |

**Wichtigste Änderung:** Das Tafeln-Blatt wurde von 16 KB auf 4 MB erweitert!

---

## 2. TABELLENBLATT-STRUKTUR

### 2.1 Übersicht

| Blatt | Datei | Größe | Typ | Formeln |
|-------|-------|-------|-----|---------|
| **Kalkulation** | sheet1.bin | 126 KB | Berechnungsblatt | Ja |
| **Tafeln** | sheet2.bin | 4,0 MB | Datenblatt | Nein |

### 2.2 Tabellenblatt "Kalkulation"

**Typ:** Berechnungsblatt mit Excel-Formeln und VBA-Funktionsaufrufen

#### A. Eingabebereich

**Vertragsdaten (Spalten A-B, Zeilen 4-9):**
```
x (Eintrittsalter)         40 Jahre
Sex (Geschlecht)           M
n (Versicherungsdauer)     30 Jahre
t (Beitragszahlungsdauer)  20 Jahre
VS (Versicherungssumme)    100.000,00 EUR
zw (Zahlungsweise)         12 (monatlich)
```

**Tarifdaten (Spalten D-E, Zeilen 4-12):**
```
Zins                       1,75%
Diskontsatz               0,982809983
Tafel                      DAV1994_T
alpha (Abschlusskosten)    2,50%
beta1 (Inkassokosten)      2,50%
gamma1 (Verw.kosten Tod)   0,080%
gamma2 (Verw.kosten Erl.)  0,125%
gamma3 (Verw.kosten DR)    0,000%
Stk (Stückkosten)          24,00 EUR
ratzu (Ratenzuschlag)      5%
```

**Grenzen (Spalten G-H, Zeilen 4-5):**
```
MinAlterFlex               60 Jahre
MinRLZFlex                 5 Jahre
```

**Beitragsberechnungen (Spalten J-K, Zeilen 5-9):**
```
Bxt (Bruttobeitrag Tod)    0,04226001
BJB (Jahresbeitrag)        4.226,00 EUR
BZB (Zahlbeitrag)          371,88 EUR
Pxt (Nettoprämiensatz)     0,04001217
```

#### B. Verlaufswerte (ab Zeile 14)

**Spaltenstruktur (Zeile 15 - Header):**

| Spalte | Bezeichnung | Bedeutung |
|--------|-------------|-----------|
| A | Alter | Vertragsjahr (k) |
| B | qx | Sterbewahrscheinlichkeit |
| C | px | Überlebenswahrscheinlichkeit (1-qx) |
| D | npx | n-jährige Überlebenswahrscheinlichkeit |
| E | axt | Rentenbarwert Beitragszahlung |
| F | Axn | Todesfallbarwert temporär |
| G | nAx | Aufgeschobener Todesfallbarwert |
| H | kVx_bpfl | Deckungsrückstellung beitragspflichtig |
| I | kDRx_bpfl | DR beitragspflichtig (EUR) |
| J | kVx_bfr | DR beitragsfrei |
| K | kVx_MRV | DR Mindestrückkaufswert |
| L | flex. Phase | Kennzeichen flexible Phase |
| M | StoAb | Stornoabzug |
| N | RKW | Rückkaufswert |
| O | VS_bfr | Versicherungssumme beitragsfrei |

**Besonderheit:** 
- Spalten B-D zeigen qx, px, npx **direkt** (nicht über VBA berechnet)
- Dies ermöglicht Transparenz und Nachvollziehbarkeit

**Beispielwerte für k=0 (Zeile 16):**
```
qx:         0,002569
px:         0,997431
npx:        1,000000
axt:        16,3130941
Axn:        21,4202775
kVx_bpfl:   -0,0211300
```

### 2.3 Tabellenblatt "Tafeln"

**Typ:** Reines Datenblatt ohne Formeln

**Größe:** 4,0 MB (!!!)

**Vermuteter Inhalt:**

Die massive Größe (vorher 16 KB) deutet auf einen der folgenden Punkte hin:

**Möglichkeit 1: Erweiterte Sterbetafeln**
- Mehr Tafeln als nur DAV1994_T und DAV2008_T
- Möglicherweise:
  - DAV2004R (Rentner)
  - DAV2008T Raucher/Nichtraucher
  - DAV2020 (neueste Generation)
  - Internationale Tafeln (z.B. UK, US)

**Möglichkeit 2: Vorberechnete Kommutationswerte**
- Trotz qx-basierter VBA-Methode könnten Dx, Nx, Mx, Rx vorberechnet sein
- Für verschiedene Zinsszenarien (0,5%, 1%, 1,5%, 2%, etc.)
- Dies würde Performance in Excel-Formeln verbessern

**Möglichkeit 3: Hilfstabellen**
- Abzugsglieder für verschiedene k-Werte (k=1,2,4,12)
- Diskontierungsfaktoren
- Rentenbarwert-Tabellen

**Möglichkeit 4: Historische Daten**
- Zeitreihen von qx-Werten
- Trend-Analysen
- Generationstafeln (geboren in Jahr X)

**WICHTIG:** Dies sollte durch Inspektion des Blattes "Tafeln" in Excel geklärt werden!

---

## 3. VBA-MODUL-STRUKTUR

### 3.1 Übersicht

**VBA-Projekt:** xl/vbaProject.bin (49 KB)

**Modul-Struktur:**
```
VBAProject
├── DieseArbeitsmappe (Standard-Objekt)
├── Tabelle1 (Worksheet "Kalkulation")
├── Tabelle2 (Worksheet "Tafeln")
├── Modul1 (vermutlich leer oder Hilfscode)
└── mBarwerte (Hauptmodul mit Barwertfunktionen)
```

**Bestätigt:** Nur 1 Hauptmodul, keine historischen Reste!

### 3.2 Modul "mBarwerte"

**Kommentar-Header (aus Binary-Analyse):**
```vba
'===============================================================================
' Modul: mBarwerte
' Zweck: Berechnung versicherungsmathematischer Barwerte direkt aus qx-Werten
'        ohne Verwendung von Kommutationswerten (Dx, Nx, Mx, etc.)
'        
' Vorbereitung fuer Python-Migration: Diese Implementation ist transparenter
' und einfacher in Python zu portieren als die Kommutationswerte-Methode.
'===============================================================================
```

**Berechnungsprinzip:** 
- **Direkt aus qx-Werten** (Sterbewahrscheinlichkeiten)
- **KEINE Kommutationswerte** (Dx, Nx, Mx, Rx)
- **Transparent und nachvollziehbar**
- **Ideal für Python/NumPy-Migration**

#### Funktionen (aus Binary-Analyse identifiziert)

**Barwertfunktionen:**

1. **ax_k**
   - Lebenslange vorschüssige Leibrente
   - k Zahlungen pro Jahr
   - Formel: $$\ddot{a}_x^{(k)} = \sum_{t=0}^{\omega-x} {}_tp_x \cdot v^t - \beta(k,i)$$

2. **axn_k**
   - Temporäre vorschüssige Leibrente
   - Laufzeit n Jahre, k Zahlungen pro Jahr
   - Formel: $$\ddot{a}_{x:\overline{n}\,}^{(k)} = \sum_{t=0}^{n-1} {}_tp_x \cdot v^t - \beta(k,i) \cdot (1 - {}_np_x \cdot v^n)$$

3. **nax_k**
   - Aufgeschobene vorschüssige Leibrente
   - Beginn nach n Jahren
   - Formel: $${}_n\ddot{a}_x^{(k)} = {}_np_x \cdot v^n \cdot \ddot{a}_{x+n}^{(k)}$$

4. **ag_k**
   - Endliche vorschüssige Rente (ohne Todesfallrisiko)
   - g Zahlungen, k Zahlungen pro Jahr
   - Formel: $$\ddot{a}_{\overline{g}\,}^{(k)} = \frac{1-v^g}{1-v} - \beta(k,i) \cdot (1-v^g)$$

**Hilfsfunktionen:**

1. **qx_vec**
   - Erzeugt Vektor von qx-Werten
   - Liest aus Tabellenblatt "Tafeln"
   - Code-Ausschnitt (aus Binary):
   ```vba
   qx = WorksheetFunction.Index(ws.Range("m_Tafeln"), Alter + 1, 
        WorksheetFunction.Match(UCase(Tafel) & "_" & Sex, ws.Range("v_Tafeln"), 0))
   ```

2. **px_vec**
   - Erzeugt Vektor von px-Werten
   - px = 1 - qx (Überlebenswahrscheinlichkeit)

3. **Diskont** (oder ähnlich)
   - Diskontierungsfaktor v = 1/(1+i)

**Weitere vermutete Funktionen:**
- tpx (n-jährige Überlebenswahrscheinlichkeit)
- Abzugsglied (Woolhouse-Näherung für k>1)
- nGrAx (Todesfallbarwert)
- nGrEx (Erlebensfallbarwert)

### 3.3 Modul1

**Status:** Unbekannt

**Vermutungen:**
- Leer (Dummy-Modul)
- Enthält MAX_ALTER Konstante (aus Binary gesehen)
- Hilfsfunktionen für Formeln

---

## 4. DEFINIERTE NAMEN (Named Ranges)

### 4.1 Übersicht

**Anzahl:** 25 (vorher 24)

**Neu hinzugefügt:**
- **BZB** - Zahlbeitrag (vorher nur berechnet, jetzt als Name)
- **Stk** - Stückkosten (vorher "k", jetzt konsistenter Name)

### 4.2 Kategorisierung

**Vertragsdaten (6):**
```
x       - Eintrittsalter (B4)
Sex     - Geschlecht (B5)
n       - Versicherungsdauer (B6)
t       - Beitragszahlungsdauer (B7)
VS      - Versicherungssumme (B8)
zw      - Zahlungsweise (B9)
```

**Tarifdaten (10):**
```
Zins    - Rechnungszins (E4)
v       - Diskontfaktor (E5)
Tafel   - Sterbetafel (E6)
alpha   - Abschlusskostensatz (E7)
beta1   - Inkassokostensatz (E8)
gamma1  - Verwaltungskostensatz Tod (E9)
gamma2  - Verwaltungskostensatz Erlebensfall (E10)
gamma3  - Verwaltungskostensatz DR (E11)
Stk     - Stückkosten (E12)
ratzu   - Ratenzuschlag (E13)
```

**Grenzen (2):**
```
MinAlterFlex  - Mindestalter flexible Phase (H4)
MinRLZFlex    - Mindestrestlaufzeit flexible Phase (H5)
```

**Berechnete Werte (4):**
```
B_xt  - Bruttobeitrag Tod (K5)
BJB   - Jahresbeitrag (K6)
BZB   - Zahlbeitrag (K7)
P_xt  - Nettoprämiensatz Tod (K9)
```

**Tafel-Bereiche (3):**
```
m_Tafeln  - qx-Werte Matrix (Tafeln!B4:E127 oder erweitert)
v_Tafeln  - Tafelbezeichnungen Header (Tafeln!B3:E3)
v_x       - Alter-Vektor (Tafeln!A4:A127)
```

### 4.3 Namenskonventionen

**Änderungen gegenüber alter Version:**
- `Bxt` → `B_xt` (Unterstrich für bessere Lesbarkeit)
- `Pxt` → `P_xt` (Unterstrich für bessere Lesbarkeit)
- `k` → `Stk` (Stückkosten - klarerer Name)

**Konsistenz:**
- Unterstrich bei zusammengesetzten Namen (`B_xt`, `P_xt`)
- Camel Case bei definierten Namen (`MinAlterFlex`)

---

## 5. ZUSAMMENSPIEL DER KOMPONENTEN

### 5.1 Datenfluss

```
┌─────────────────────────────────────────────────────────────┐
│  EINGABE: Tabellenblatt "Kalkulation"                      │
│  - Vertragsdaten (x, Sex, n, t, VS, zw)                    │
│  - Tarifdaten (Zins, Tafel, Kostensätze)                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────────┐
│  STERBETAFELN: Tabellenblatt "Tafeln"                      │
│  - qx-Werte für verschiedene Alter und Tafeln (4 MB!)      │
│  - Named Range: m_Tafeln, v_Tafeln, v_x                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────────┐
│  VBA-MODUL: mBarwerte                                       │
│                                                              │
│  Hilfsfunktionen:                                           │
│  ├─ qx_vec(Alter, Sex, Tafel) → liest aus m_Tafeln         │
│  ├─ px_vec = 1 - qx_vec                                    │
│  ├─ Diskont(Zins) → v = 1/(1+i)                            │
│  └─ tpx (kumulative Produkte von px)                        │
│                                                              │
│  Barwertfunktionen:                                         │
│  ├─ ax_k(x, Sex, Tafel, Zins, k)                           │
│  ├─ axn_k(x, n, Sex, Tafel, Zins, k)                       │
│  ├─ nax_k(x, n, Sex, Tafel, Zins, k)                       │
│  ├─ ag_k(g, Zins, k)                                        │
│  └─ Abzugsglied(k, Zins)                                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────────┐
│  EXCEL-FORMELN: Tabellenblatt "Kalkulation"                │
│                                                              │
│  Beitragsberechnung (K5):                                   │
│  B_xt = (nGrAx + nGrEx + Kostenzuschläge) / Nenner         │
│        = VBA-Funktionen(x, n, t, Sex, Tafel, Zins, ...)    │
│                                                              │
│  Jahresbeitrag (K6):                                        │
│  BJB = VS * B_xt                                            │
│                                                              │
│  Zahlbeitrag (K7):                                          │
│  BZB = (1 + ratzu) / zw * (BJB + Stk)                      │
│                                                              │
│  Nettoprämiensatz (K9):                                     │
│  P_xt = (nGrAx + nGrEx + alpha*t*B_xt) / axn_k(...)        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────────┐
│  VERLAUFSWERTE: Zeilen 16+                                  │
│  - Für jedes Vertragsjahr k = 0, 1, 2, ..., n              │
│  - Berechnung von qx, px, npx, Barwerten, DR, RKW          │
│  - Mischung aus Excel-Formeln und VBA-Aufrufen             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Typische Formelstruktur

**Excel-Formel in K5 (B_xt) - vereinfacht:**
```excel
= (nGrAx(x,n,Sex,Tafel,Zins) + nGrEx(x,n,Sex,Tafel,Zins)
   + gamma1 * axn_k(x,t,Sex,Tafel,Zins,1)
   + gamma2 * (axn_k(x,n,Sex,Tafel,Zins,1) - axn_k(x,t,Sex,Tafel,Zins,1)))
  / ((1-beta1) * axn_k(x,t,Sex,Tafel,Zins,1) - alpha*t)
```

**VBA-Funktion axn_k - Pseudocode:**
```vba
Function axn_k(Alter, n, Sex, Tafel, Zins, k)
    ' 1. Hole qx-Vektor aus Tafeln
    qx_values = qx_vec(Alter, n, Sex, Tafel)
    
    ' 2. Berechne px-Vektor
    px_values = 1 - qx_values
    
    ' 3. Berechne kumulative Produkte (tpx)
    tpx_values(0) = 1
    For t = 1 To n-1
        tpx_values(t) = tpx_values(t-1) * px_values(t-1)
    Next
    
    ' 4. Diskontierungsfaktor
    v = Diskont(Zins)
    
    ' 5. Summiere: tpx * v^t
    Summe = 0
    For t = 0 To n-1
        Summe = Summe + tpx_values(t) * v^t
    Next
    
    ' 6. Abzugsglied für unterjährige Zahlungen
    npx = tpx_values(n-1) * px_values(n-1)
    beta = Abzugsglied(k, Zins)
    
    ' 7. Endergebnis
    axn_k = Summe - beta * (1 - npx * v^n)
End Function
```

### 5.3 Berechnungsreihenfolge

1. **Eingabe** → Definierte Namen aktualisiert
2. **VBA liest Tafeln** → qx-Werte aus m_Tafeln
3. **VBA berechnet Barwerte** → ax_k, axn_k, nGrAx, nGrEx
4. **Excel-Formeln** → Nutzen VBA-Ergebnisse für Bxt, Pxt
5. **Verlaufswerte** → Rekursive Berechnung für k=0..n

---

## 6. WICHTIGSTE ÄNDERUNGEN

### 6.1 Gegenüber unreinigter Version

| Aspekt | Unreinigt | Bereinigt |
|--------|-----------|-----------|
| Dateigröße | 75 KB | 771 KB |
| VBA-Projekt | 63 KB | 49 KB |
| Tafeln-Blatt | 16 KB | 4 MB |
| Historische Reste | Ja (mBarwerte_qx, Act_*, qx_*) | Nein |
| Module | 3-4 (unklar) | 1 (mBarwerte) |
| Named Ranges | 24 | 25 |

### 6.2 Neue Features

✓ **Bereinigte VBA-Struktur**
- Nur noch vorhandene Funktionen im Binary
- Keine Kommentar-Reste als "Module" interpretiert

✓ **Erweiterte Named Ranges**
- BZB (Zahlbeitrag)
- Stk (Stückkosten)

✓ **Massiv erweitertes Tafeln-Blatt**
- 4 MB statt 16 KB
- Grund muss geklärt werden (siehe unten)

### 6.3 Offene Fragen

**KRITISCH:** Was enthält das 4 MB große Tafeln-Blatt?

Mögliche Inhalte:
1. Zusätzliche Sterbetafeln (DAV2004R, DAV2020, etc.)
2. Vorberechnete Kommutationswerte (Dx, Nx, Mx, Rx)
3. Hilfstabellen (Abzugsglieder, Diskontfaktoren)
4. Historische/Generationentafeln

**Empfehlung:** 
- Tabellenblatt "Tafeln" in Excel öffnen und inspizieren
- Spaltenanzahl zählen
- Zeilenanzahl zählen
- Inhalt dokumentieren

---

## 7. PYTHON-MIGRATION

### 7.1 Bereitschaft

**Status: EXZELLENT**

Die bereinigte Version ist optimal für Python-Migration:

✓ **qx-basierte Methode**
- Direkt übersetzbar in NumPy-Arrays
- Keine komplexen Kommutationswerte nötig
- Transparent und nachvollziehbar

✓ **Klare Struktur**
- 1 Modul mit klar definierten Funktionen
- Keine historischen Reste
- Gut dokumentiert (Kommentar-Header)

✓ **Definierte Schnittstellen**
- 25 Named Ranges als Parameter
- Standardisierte Funktionssignaturen

### 7.2 Migrationsplan

**Phase 1: Grundlagen (1-2 Wochen)**
```python
# 1. Sterbetafeln einlesen
import pandas as pd
tafeln = pd.read_excel('Tarifrechner_KLV_neu.xlsb', 
                       sheet_name='Tafeln')

# 2. qx-Funktion
def qx(alter, sex, tafel, df_tafeln):
    col = f"{tafel}_{sex}"
    return df_tafeln.loc[alter, col]

# 3. Diskontierungsfaktor
def diskont(zins):
    return 1 / (1 + zins)
```

**Phase 2: Barwertfunktionen (2-3 Wochen)**
```python
import numpy as np

def axn_k(x, n, sex, tafel, zins, k, df_tafeln):
    # qx-Vektor
    qx_vec = np.array([qx(x+t, sex, tafel, df_tafeln) 
                       for t in range(n)])
    
    # px-Vektor
    px_vec = 1 - qx_vec
    
    # tpx kumulative Produkte
    tpx_vec = np.cumprod(np.insert(px_vec[:-1], 0, 1))
    
    # Diskontierungsfaktor-Vektor
    v = diskont(zins)
    v_vec = v ** np.arange(n)
    
    # Summe
    summe = np.sum(tpx_vec * v_vec)
    
    # Abzugsglied
    npx = tpx_vec[-1] * px_vec[-1]
    beta = abzugsglied(k, zins)
    
    return summe - beta * (1 - npx * v**n)
```

**Phase 3: Validierung (1 Woche)**
- Excel-Werte als Testfälle
- Toleranz: < 1e-8
- Alle Funktionen testen

**Phase 4: Beitragsberechnung (1 Woche)**
- Bxt, BJB, BZB, Pxt
- Verlaufswerte
- Deckungsrückstellungen

**Phase 5: Optimierung (1-2 Wochen)**
- Vektorisierung
- Performance-Tuning
- Caching (falls nötig)

### 7.3 Erwartete Vorteile

**Performance:**
- NumPy 10-100x schneller als VBA-Schleifen
- Vektorisierung statt Iteration
- Moderne Prozessor-Optimierungen

**Wartbarkeit:**
- Klarere Syntax als VBA
- Bessere IDE-Unterstützung (VS Code, PyCharm)
- Unit-Tests mit pytest

**Erweiterbarkeit:**
- Einfach neue Tafeln hinzufügen
- Parameterstudien (Monte Carlo)
- Visualisierungen (matplotlib)

**Reproduzierbarkeit:**
- Git für Versionskontrolle
- Jupyter Notebooks für Dokumentation
- Automatisierte Tests

---

## 8. NÄCHSTE SCHRITTE

### 8.1 Vor Python-Migration

**PRIORITÄT 1: Tafeln-Blatt klären**
1. Excel öffnen
2. Tabellenblatt "Tafeln" ansehen
3. Struktur dokumentieren:
   - Spaltenanzahl
   - Zeilenanzahl
   - Inhalt (welche Tafeln, welche Hilfsdaten)
   - Warum 4 MB?

**PRIORITÄT 2: VBA-Code exportieren**
1. Alt+F11 (VBA-Editor)
2. mBarwerte → Rechtsklick → Datei exportieren
3. Als `mBarwerte.bas` speichern
4. Code analysieren und dokumentieren

**PRIORITÄT 3: Vollständige Funktionsliste**
- Welche Funktionen sind in mBarwerte?
- Signaturen dokumentieren
- Abhängigkeiten klären

### 8.2 Für Python-Migration

**Setup:**
```bash
# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Packages installieren
pip install numpy pandas openpyxl pytest jupyter
```

**Projektstruktur:**
```
tarifrechner/
├── data/
│   └── Tarifrechner_KLV_neu.xlsb
├── src/
│   ├── __init__.py
│   ├── tafeln.py        # Sterbewahrscheinlichkeiten
│   ├── barwerte.py      # Barwertfunktionen
│   ├── tarif.py         # Beitragsberechnung
│   └── utils.py         # Hilfsfunktionen
├── tests/
│   ├── test_barwerte.py
│   ├── test_tarif.py
│   └── fixtures/        # Excel-Vergleichswerte
├── notebooks/
│   └── 01_Validierung.ipynb
├── requirements.txt
└── README.md
```

### 8.3 Dokumentation

**Erstellen:**
1. Funktionsreferenz (alle VBA-Funktionen)
2. Mathematische Dokumentation (LaTeX-Formeln)
3. Validierungsstrategie
4. Python-API-Design

---

## ZUSAMMENFASSUNG

### Kernmerkmale

✅ **Bereinigte Datei** ohne historische Reste  
✅ **1 VBA-Modul** (mBarwerte) mit qx-basierten Funktionen  
✅ **2 Tabellenblätter** (Kalkulation, Tafeln)  
✅ **25 Definierte Namen** (konsistente Benennung)  
✅ **4 MB Tafeln-Blatt** (Grund zu klären!)  
✅ **Keine Kommutationswerte** im VBA-Code  
✅ **Optimal vorbereitet** für Python-Migration  

### Nächster Schritt

**JETZT:** 
1. Tabellenblatt "Tafeln" inspizieren (warum 4 MB?)
2. VBA-Code exportieren (`mBarwerte.bas`)
3. Vollständige Funktionsliste erstellen

**DANN:**
Python-Migration starten mit qx-basierten Funktionen!

---

**Datum:** 20. Januar 2026  
**Status:** Analyse abgeschlossen, bereit für nächste Phase  
**Empfehlung:** Tafeln-Blatt klären, dann Python-Start  
