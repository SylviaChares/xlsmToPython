# Strukturanalyse: Tarifrechner_KLV.xlsm

## Uebersicht

**Datei:** Tarifrechner_KLV.xlsm  
**Typ:** Excel Macro-Enabled Workbook  
**Zweck:** Aktuarieller Tarifrechner fuer Kapitallebensversicherung (KLV)  
**Berechnungsbasis:** DAV-Sterbetafeln (Deutsche Aktuarvereinigung)

---

## 1. TABELLENBLATT-STRUKTUR

### 1.1 Tabellenblatt "Kalkulation"

**Dimensionen:** A1:L66  
**Max. Zeile:** 66  
**Max. Spalte:** 12 (A-L)  
**Anzahl Formeln:** 309  
**Typ:** Berechnungsblatt mit Eingaben und Ergebnissen

#### Aufbau und Bereiche:

**A. EINGABEBEREICH (Zeilen 1-13)**

**A.1 Vertragsdaten (Spalten A-B, Zeilen 4-9):**
- x (Alter bei Vertragsbeginn): 40 Jahre
- Sex (Geschlecht): M (Maennlich)
- n (Versicherungsdauer): 30 Jahre
- t (Beitragszahlungsdauer): 20 Jahre
- VS (Versicherungssumme): 100.000 EUR
- zw (Zahlungsweise): 12 (monatlich)

**A.2 Tarifdaten (Spalten D-E, Zeilen 4-12):**
- Zins (Rechnungszins): 1,75%
- Tafel (Sterbetafel): DAV1994_T
- alpha (Abschlusskostensatz): 2,50%
- beta1 (Inkassokostensatz): 2,50%
- gamma1 (Verwaltungskostensatz Tod): 0,08%
- gamma2 (Verwaltungskostensatz Erlebensfall): 0,125%
- gamma3 (Verwaltungskostensatz Deckungsrueckstellung): 0,25%
- k (Zahlungen pro Jahr): 24
- ratzu (Ratenzuschlag): 5% (Formel abhaengig von zw)

**A.3 Grenzen (Spalten G-H, Zeilen 4-5):**
- MinAlterFlex (Mindestalter fuer flexible Phase): 60 Jahre
- MinRLZFlex (Mindestrestlaufzeit fuer flexible Phase): 5 Jahre

**A.4 Beitragsberechnungen (Spalten J-K, Zeilen 5-9):**
- Bxt (K5): Array-Formel zur Berechnung Bruttobeitrag Tod
- BJB (K6): Jahresbeitrag = VS * Bxt
- BZB (K7): Zahlbeitrag = (1+ratzu)/zw * (BJB+k)
- Pxt (K9): Array-Formel zur Praemienberechnung

**Kritische Array-Formeln in K5 und K9:**

```excel
K5 (Bxt): 
=( act_nGrAx(x,n,Sex,Tafel,Zins)+Act_Dx(x+n,Sex,Tafel,Zins)/Act_Dx(x,Sex,Tafel,Zins)
  +gamma1*Act_axn_k(x,t,Sex,Tafel,Zins,1)
  +gamma2*(Act_axn_k(x,n,Sex,Tafel,Zins,1)-Act_axn_k(x,t,Sex,Tafel,Zins,1)))
 /((1-beta1)*Act_axn_k(x,t,Sex,Tafel,Zins,1)-alpha*t)

K9 (Pxt):
=(act_nGrAx(x,n,Sex,Tafel,Zins)+Act_Dx(x+n,Sex,Tafel,Zins)/Act_Dx(x,Sex,Tafel,Zins)
 +t*alpha*B_xt)
 /Act_axn_k(x,t,Sex,Tafel,Zins,1)
```

**B. VERLAUFSWERTE (Zeilen 14-66)**

**B.1 Spaltenkoepfe (Zeile 15):**
- Spalte A: k (Vertragsjahr)
- Spalte B: Axn (Todesfallbarwert)
- Spalte C: axn (Rentenbarwert gesamt)
- Spalte D: axt (Rentenbarwert Beitragszahlung)
- Spalte E: kVx_bpfl (Deckungsrueckstellung beitragspflichtig)
- Spalte F: kDRx_bpfl (Deckungsrueckstellung beitragspflichtig in EUR)
- Spalte G: kVx_bfr (Deckungsrueckstellung beitragsfrei)
- Spalte H: kVx_MRV (Deckungsrueckstellung mit Rueckkaufswert)
- Spalte I: flex. Phase (Flexible Phase Kennzeichen)
- Spalte J: StoAb (Stornoabzug)
- Spalte K: RKW (Rueckkaufswert)
- Spalte L: VS_bfr (Versicherungssumme beitragsfrei)

**B.2 Datenbereich (Zeilen 16-29):**
Array-Formeln fuer jedes Vertragsjahr (k=0 bis k=13 sichtbar)

Typische Array-Formeln in den Spalten B-E:
```excel
B16: =IF(A16<=n,act_nGrAx(x+$A16,MAX(0,n-$A16),Sex,Tafel,Zins)
         +Act_Dx(x+n,Sex,Tafel,Zins)/Act_Dx(x+$A16,Sex,Tafel,Zins),0)

C16: =Act_axn_k(x+$A16,MAX(0,n-$A16),Sex,Tafel,Zins,1)

D16: =Act_axn_k(x+$A16,MAX(0,t-$A16),Sex,Tafel,Zins,1)

E16: =B16-P_xt*D16+gamma2*(C16-Act_axn_k(x,n,Sex,Tafel,Zins,1)
     /Act_axn_k(x,t,Sex,Tafel,Zins,1)*D16)
```

Einfache Formeln in F-L:
```excel
F16: =VS*E16
G16: =B16+gamma3*C16
```

### 1.2 Tabellenblatt "Tafeln"

**Dimensionen:** A3:E127  
**Max. Zeile:** 127  
**Max. Spalte:** 5 (A-E)  
**Anzahl Formeln:** 0  
**Typ:** Reines Datenblatt (Sterbewahrscheinlichkeiten)

#### Struktur:

**Header (Zeile 3):**
- Spalte A: x/y (Alter)
- Spalte B: DAV1994_T_M (DAV 1994 Tafel, Maennlich)
- Spalte C: DAV1994_T_F (DAV 1994 Tafel, Weiblich)
- Spalte D: DAV2008_T_M (DAV 2008 Tafel, Maennlich)
- Spalte E: DAV2008_T_F (DAV 2008 Tafel, Weiblich)

**Daten (Zeilen 4-127):**
- Alter: 0 bis 123 Jahre
- Sterbewahrscheinlichkeiten qx fuer jede Tafel
- Letztes Alter (123): qx = 1.0 (sicherer Tod)

**Beispiel-Daten:**
```
x   DAV1994_T_M  DAV1994_T_F  DAV2008_T_M  DAV2008_T_F
0   0.011687     0.009003     0.006113     0.005088
40  0.002378     0.001233     0.001618     0.000680
60  0.007891     0.003932     0.005913     0.002861
123 1.000000     1.000000     1.000000     1.000000
```

---

## 2. VBA-MODUL-STRUKTUR

### 2.1 Modul "mConstants"

**Zweck:** Definiert globale Konstanten fuer Rundung und Altersgrenzen

**Konstanten:**
```vba
Public Const rund_lx As Integer = 16    ' Rundung fuer Lebende
Public Const rund_tx As Integer = 16    ' Rundung fuer Tote
Public Const rund_Dx As Integer = 16    ' Rundung fuer Dx-Werte
Public Const rund_Cx As Integer = 16    ' Rundung fuer Cx-Werte
Public Const rund_Nx As Integer = 16    ' Rundung fuer Nx-Werte
Public Const rund_Mx As Integer = 16    ' Rundung fuer Mx-Werte
Public Const rund_Rx As Integer = 16    ' Rundung fuer Rx-Werte
Public Const max_Alter As Integer = 123 ' Maximales Alter
```

**Erlaeuterung:**
- Alle Rundungen auf 16 Dezimalstellen
- Hoechstalter 123 Jahre (entspricht Tafel-Maximum)

### 2.2 Modul "mGWerte"

**Zweck:** Berechnung aktuarieller Grundwerte (Commutation Functions)

**Hauptfunktionen:**

#### 2.2.1 Sterbewahrscheinlichkeiten

**Act_qx(Alter, Sex, Tafel, [GebJahr], [Rentenbeginnalter], [Schicht])**
- Liest Sterbewahrscheinlichkeit aus Tabellenblatt "Tafeln"
- Unterstuetzte Tafeln: DAV1994_T, DAV2008_T
- Geschlecht: M (Maennlich), F (Weiblich)
- Gibt qx-Wert zurueck

#### 2.2.2 Anzahl Lebende (lx-Werte)

**v_lx(Endalter, Sex, Tafel, ...)**
- Private Funktion, erzeugt Vektor der lx-Werte
- Startkohorte: 1.000.000 (lx=0 = 1000000)
- Rekursion: lx+1 = lx * (1 - qx)
- Rundung nach rund_lx

**Act_lx(Alter, Sex, Tafel, ...)**
- Public Funktion, gibt Einzelwert lx zurueck

#### 2.2.3 Anzahl Tote (tx-Werte)

**v_tx(Endalter, Sex, Tafel, ...)**
- Private Funktion, erzeugt Vektor der tx-Werte
- Berechnung: tx = lx - lx+1
- Rundung nach rund_tx

**Act_tx(Alter, Sex, Tafel, ...)**
- Public Funktion, gibt Einzelwert tx zurueck

#### 2.2.4 Kommutationswerte Dx

**v_Dx(Endalter, Sex, Tafel, Zins, ...)**
- Private Funktion, erzeugt Vektor der Dx-Werte
- Berechnung: Dx = lx * v^x (diskontierte Lebende)
- v = 1/(1+Zins) (Diskontierungsfaktor)
- Rundung nach rund_Dx

**Act_Dx(Alter, Sex, Tafel, Zins, ...)**
- Public Funktion mit Cache
- Prueft Dictionary-Cache vor Berechnung
- Speichert Ergebnis im Cache
- Cache-Key: "Dx_Alter_Sex_Tafel_Zins_..."

#### 2.2.5 Kommutationswerte Cx

**v_Cx(Endalter, Sex, Tafel, Zins, ...)**
- Private Funktion, erzeugt Vektor der Cx-Werte
- Berechnung: Cx = tx * v^(x+1) (diskontierte Tote)
- Rundung nach rund_Cx

**Act_Cx(Alter, Sex, Tafel, Zins, ...)**
- Public Funktion mit Cache
- Analog zu Act_Dx

#### 2.2.6 Kommutationswerte Nx

**v_Nx(Sex, Tafel, Zins, ...)**
- Private Funktion, erzeugt Vektor der Nx-Werte
- Berechnung: Nx = Summe(Di) fuer i>=x (rueckwaerts)
- Nx(max_Alter) = Dx(max_Alter)
- Nx(x) = Nx(x+1) + Dx(x)
- Rundung nach rund_Nx

**Act_Nx(Alter, Sex, Tafel, Zins, ...)**
- Public Funktion mit Cache
- Analog zu Act_Dx

#### 2.2.7 Kommutationswerte Mx

**v_Mx(Sex, Tafel, Zins, ...)**
- Private Funktion, erzeugt Vektor der Mx-Werte
- Berechnung: Mx = Summe(Ci) fuer i>=x (rueckwaerts)
- Analog zu Nx mit Cx-Werten
- Rundung nach rund_Mx

**Act_Mx(Alter, Sex, Tafel, Zins, ...)**
- Public Funktion mit Cache

#### 2.2.8 Kommutationswerte Rx

**v_Rx(Sex, Tafel, Zins, ...)**
- Private Funktion, erzeugt Vektor der Rx-Werte
- Berechnung: Rx = Summe(Mi) fuer i>=x (rueckwaerts)
- Analog zu Nx mit Mx-Werten
- Rundung nach rund_Rx

**Act_Rx(Alter, Sex, Tafel, Zins, ...)**
- Public Funktion mit Cache

#### 2.2.9 Altersberechnung

**Act_Altersberechnung(GebDat, BerDat, Methode)**
- Methode "K": Kalenderjahresmethode (nur Jahresdifferenz)
- Methode "H": Halbjahresmethode (mit Monatsberuecksichtigung)
- Standard: Halbjahresmethode

#### 2.2.10 Cache-Management

**InitializeCache()**
- Initialisiert Scripting.Dictionary
- Wird automatisch beim ersten Zugriff aufgerufen

**CreateCacheKey(Art, Alter, Sex, Tafel, Zins, GebJahr, Rentenbeginnalter, Schicht)**
- Private Funktion
- Erzeugt eindeutigen String-Key fuer Cache
- Format: "Art_Alter_Sex_Tafel_Zins_GebJahr_Rentenbeginnalter_Schicht"

**Cache-Strategie:**
- Vermeidet Mehrfachberechnung identischer Werte
- Wichtig bei Array-Formeln mit vielen Funktionsaufrufen
- Cache existiert nur waehrend Excel-Sitzung

### 2.3 Modul "mBarwerte"

**Zweck:** Berechnung versicherungsmathematischer Barwerte

**Hauptfunktionen:**

#### 2.3.1 Lebenslange Leibrente

**Act_ax_k(Alter, Sex, Tafel, Zins, k, [GebJahr], [Rentenbeginnalter], [Schicht])**
- Berechnet Barwert lebenslange vorschuessige Leibrente
- k: Zahlungen pro Jahr (12=monatlich, 1=jaehrlich)
- Formel: ax^(k) = Nx/Dx - Abzugsglied(k, Zins)
- Abzugsglied korrigiert fuer unterjahrige Zahlung

#### 2.3.2 Temporaere Leibrente

**Act_axn_k(Alter, n, Sex, Tafel, Zins, k, [GebJahr], [Rentenbeginnalter], [Schicht])**
- Berechnet Barwert temporaere vorschuessige Leibrente (n Jahre)
- Formel: ax:n^(k) = (Nx - Nx+n)/Dx - Abzugsglied(k, Zins) * (1 - Dx+n/Dx)

#### 2.3.3 Aufgeschobene Leibrente

**Act_nax_k(Alter, n, Sex, Tafel, Zins, k, [GebJahr], [Rentenbeginnalter], [Schicht])**
- Berechnet Barwert aufgeschobene vorschuessige Leibrente (Beginn nach n Jahren)
- Formel: n|ax^(k) = (Dx+n/Dx) * ax+n^(k)

#### 2.3.4 Todesfallbarwert (Temporaer)

**Act_nGrAx(Alter, n, Sex, Tafel, Zins, [GebJahr], [Rentenbeginnalter], [Schicht])**
- Berechnet Barwert temporaere Todesfallversicherung
- "GrA" = Grosse A (Todesfallleistung am Jahresende)
- Formel: A_x:n = (Mx - Mx+n)/Dx

#### 2.3.5 Erlebensfallbarwert

**Act_nGrEx(Alter, n, Sex, Tafel, Zins, [GebJahr], [Rentenbeginnalter], [Schicht])**
- Berechnet Barwert reine Erlebensfallversicherung
- "GrE" = Grosse E (Erlebensfallleistung nach n Jahren)
- Formel: A_x:n^1 = Dx+n/Dx

#### 2.3.6 Endliche Rente

**Act_ag_k(g, Zins, k)**
- Berechnet Barwert endliche vorschuessige Rente (g Zahlungen)
- Kein Todesfallrisiko (rein finanzmathematisch)
- Formel: a_g^(k) = (1-v^g)/(1-v) - Abzugsglied(k, Zins) * (1-v^g)
- Spezialfall Zins=0: a_g^(k) = g

#### 2.3.7 Abzugsglied fuer unterjahrige Zahlungen

**Act_Abzugsglied(k, Zins)**
- Korrektur fuer unterjahrige Rentenzahlungen
- k: Zahlungen pro Jahr
- Formel (Woolhouse-Naeherung):
  Summe_{l=0}^{k-1} [ (l/k) / (1 + l/k * Zins) ] * (1+Zins)/k
- Bei k=1 (jaehrlich): Abzugsglied = 0

---

## 3. DEFINIERTE NAMEN (Named Ranges)

**Eingabeparameter:**
- x: Kalkulation!$B$4 (Eintrittsalter)
- Sex: Kalkulation!$B$5 (Geschlecht)
- n: Kalkulation!$B$6 (Versicherungsdauer)
- t: Kalkulation!$B$7 (Beitragszahlungsdauer)
- VS: Kalkulation!$B$8 (Versicherungssumme)
- zw: Kalkulation!$B$9 (Zahlungsweise)

**Tarifdaten:**
- Zins: Kalkulation!$E$4 (Rechnungszins)
- Tafel: Kalkulation!$E$5 (Sterbetafel)
- alpha: Kalkulation!$E$6 (Abschlusskostensatz)
- beta1: Kalkulation!$E$7 (Inkassokostensatz)
- gamma1: Kalkulation!$E$8 (Verwaltungskostensatz Tod)
- gamma2: Kalkulation!$E$9 (Verwaltungskostensatz Erlebensfall)
- gamma3: Kalkulation!$E$10 (Verwaltungskostensatz DR)
- k: Kalkulation!$E$11 (Zahlungen pro Jahr)
- ratzu: Kalkulation!$E$12 (Ratenzuschlag)

**Grenzen:**
- MinAlterFlex: Kalkulation!$H$4 (Mindestalter flexible Phase)
- MinRLZFlex: Kalkulation!$H$5 (Mindestrestlaufzeit flexible Phase)

**Berechnete Werte:**
- B_xt: Kalkulation!$K$5 (Bruttobeitrag Tod)
- BJB: Kalkulation!$K$6 (Jahresbeitrag)
- P_xt: Kalkulation!$K$9 (Nettopraemie Tod)

**Tafel-Bereiche:**
- v_Tafeln: Tafeln!$B$3:$E$3 (Tafelbezeichnungen)
- m_Tafeln: Tafeln!$B$4:$E$127 (qx-Werte)
- v_x: Tafeln!$A$4:$A$127 (Alter 0-123)

---

## 4. BERECHNUNGSLOGIK UND ABHÄNGIGKEITEN

### 4.1 Berechnungskette

```
1. Eingabe: Vertragsdaten (x, Sex, n, t, VS, zw) + Tarifdaten (Zins, Tafel, Kosten)
   |
   v
2. VBA: Grundwerte (qx -> lx -> Dx, Cx, Nx, Mx, Rx)
   |
   v  
3. VBA: Barwerte (ax_k, axn_k, nGrAx, nGrEx)
   |
   v
4. Excel-Formel K5: Beitrag Bxt
   - Zaehler: Todesfallbarwert + Erlebensfallbarwert + Kostenzuschlaege
   - Nenner: Beitragszahlungsbarwert abzueglich Abschlusskosten
   |
   v
5. Excel-Formeln K6-K7: BJB, BZB (mit Ratenzuschlag)
   |
   v
6. Excel-Formel K9: Nettopraemie Pxt
   |
   v
7. Excel-Formeln Zeilen 16+: Verlaufswerte pro Vertragsjahr
   - Barwerte (Axn, axn, axt)
   - Deckungsrueckstellungen (kVx_bpfl, kVx_bfr)
   - Rueckkaufswerte (RKW)
```

### 4.2 Kritische Berechnungsbestandteile

**Cache-Optimierung:**
- Dx, Cx, Nx, Mx, Rx werden gecacht
- Vermeidet Mehrfachberechnung bei Array-Formeln
- Cache-Invalidierung: Nur bei Excel-Neustart

**Array-Formeln:**
- K5, K9: Berechnungsintensive Hauptformeln
- Spalten B-E (Zeilen 16+): Array-Formeln fuer Verlaufswerte
- Vorteil: Kompakte Darstellung, automatische Aktualisierung
- Nachteil: Langsam bei vielen Zeilen, schwer zu debuggen

**Rundungsgenauigkeit:**
- Alle VBA-Berechnungen: 16 Dezimalstellen
- Excel-Anzeige: Oft weniger Stellen (Formatierung)
- Kritisch: Kleine Abweichungen koennen sich akkumulieren

---

## 5. DATENFLUSS-ÜBERSICHT

```
┌─────────────────────────────────────────────────────────────────┐
│ EINGABE: Vertragsdaten & Tarifdaten (Kalkulation A4:E12)       │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────────────┐
│ STERBETAFELN: qx-Werte (Tafeln B4:E127)                        │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────────────┐
│ VBA mGWerte: Berechnung Grundwerte                             │
│  - lx (Ueberlebende)                                           │
│  - Dx, Cx, Nx, Mx, Rx (Kommutationswerte)                     │
│  - Mit Cache-Mechanismus                                        │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────────────┐
│ VBA mBarwerte: Berechnung Barwerte                             │
│  - ax_k, axn_k (Leibrenten)                                    │
│  - nGrAx (Todesfallbarwert)                                    │
│  - nGrEx (Erlebensfallbarwert)                                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────────────┐
│ EXCEL-FORMELN: Beitragsberechnung                              │
│  K5: Bxt (Bruttobeitrag Tod)                                   │
│  K9: Pxt (Nettopraemie Tod)                                    │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────────────┐
│ EXCEL-FORMELN: Verlaufswerte (Zeilen 16+)                      │
│  - Barwerte pro Vertragsjahr                                   │
│  - Deckungsrueckstellungen                                     │
│  - Rueckkaufswerte                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. ANFORDERUNGEN FÜR PYTHON-MIGRATION

### 6.1 Funktionale Anforderungen

**Pflicht:**
1. Berechnung identischer Ergebnisse wie Excel-Version
2. Unterstuetzung DAV1994_T und DAV2008_T Tafeln
3. Alle Barwert-Funktionen (ax_k, axn_k, nGrAx, nGrEx)
4. Beitragsberechnung Bxt, Pxt
5. Verlaufswerte fuer beliebige Anzahl Vertragsjahre

**Optional:**
1. Caching-Mechanismus (Performance)
2. Validierung Eingabeparameter
3. Export nach Excel/PDF

### 6.2 Technische Anforderungen

**Python-Packages:**
- numpy: Array-Operationen, Vektorisierung
- pandas: Datenmanagement, Tafel-Handling
- openpyxl: Excel-Export (falls gewuenscht)

**Architektur:**
- Modularer Aufbau (analog VBA-Module)
- Klare Trennung: Grundwerte, Barwerte, Tarife
- Testbarkeit: Unit-Tests fuer alle Funktionen

**Validierung:**
- Vergleich Python vs. Excel fuer Testfaelle
- Toleranz fuer Rundungsdifferenzen (z.B. 1e-10)

---

## 7. KRITISCHE PUNKTE FÜR MIGRATION

### 7.1 Genauigkeitsaspekte

**Rundung:**
- Excel: WorksheetFunction.Round verwendet Banker's Rounding
- Python: numpy.round verwendet dieselbe Methode
- Kritisch: Konsistenz pruefen bei Grenzfaellen

**Akkumulation:**
- lx-Werte: Rekursive Berechnung akkumuliert Rundungsfehler
- Nx, Mx, Rx: Summationen vergroessern Abweichungen
- Loesung: Hohe Praezision beibehalten (np.float64)

### 7.2 Performance-Aspekte

**Cache:**
- Excel: Dictionary in VBA, Lebensdauer = Sitzung
- Python: Decorator @lru_cache oder dict-basierter Cache
- Wichtig: Cache-Keys muessen alle Parameter beinhalten

**Vektorisierung:**
- Vermeidung von Schleifen wo moeglich
- numpy.vectorize oder direkte Array-Operationen
- Profiling mit timeit

### 7.3 Usability-Aspekte

**Eingabe:**
- Excel: Direkte Eingabe in Zellen
- Python: Parameteruebergabe oder Config-File (JSON/YAML)

**Ausgabe:**
- Excel: Tabelle mit Verlaufswerten
- Python: DataFrame, Excel-Export oder Grafik

---

## 8. BEISPIELRECHNUNG (Validierung)

**Eingabewerte:**
```
x = 40 (Alter)
Sex = M (Maennlich)
n = 30 (Versicherungsdauer)
t = 20 (Beitragszahlung)
VS = 100.000 EUR
Zins = 1,75%
Tafel = DAV1994_T
```

**Erwartete Ergebnisse (aus Excel):**
```
Bxt (K5) = 0,04226001
BJB (K6) = 4.226,00 EUR
BZB (K7) = 371,88 EUR (monatlich)
Pxt (K9) = 0,04001217

Verlaufswert k=0:
  Axn = 0,6315923
  axn = 21,4202775
  axt = 16,3130941
  kVx_bpfl = -0,0211300
```

**Validierungsstrategie:**
- Berechne mit Python
- Vergleiche mit Excel-Werten
- Akzeptiere Abweichung < 1e-6 (relative Toleranz)

---

## ENDE DER ANALYSE
