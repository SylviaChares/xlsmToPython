# Mathematische Dokumentation: qx-basierte Barwertfunktionen

## Uebersicht

Diese Dokumentation beschreibt die mathematischen Formeln fuer die direkten
Barwertberechnungen aus Sterbewahrscheinlichkeiten (qx-Werten) ohne Verwendung
von Kommutationswerten.

## Notation

### Grundgroessen

- $x$ = Alter zu Vertragsbeginn
- $q_x$ = Einjahres-Sterbewahrscheinlichkeit im Alter $x$
- $p_x = 1 - q_x$ = Einjahres-Ueberlebenswahrscheinlichkeit im Alter $x$
- $i$ = Rechnungszins (als Dezimalzahl, z.B. 0,0175 fuer 1,75%)
- $v = \frac{1}{1+i}$ = Diskontierungsfaktor
- $k$ = Anzahl Zahlungen pro Jahr (1, 2, 4, 12)
- $n$ = Versicherungsdauer in Jahren
- $t$ = Beitragszahlungsdauer in Jahren
- $\omega$ = Hoechstalter (123 Jahre)

### Mehrjahrige Wahrscheinlichkeiten

**t-jahrige Ueberlebenswahrscheinlichkeit:**
$$_tp_x = p_x \cdot p_{x+1} \cdot p_{x+2} \cdots p_{x+t-1} = \prod_{j=0}^{t-1} p_{x+j}$$

**t-jahrige Sterbewahrscheinlichkeit:**
$$_tq_x = {}_{t-1}p_x \cdot q_{x+t-1}$$

Bedeutung: Wahrscheinlichkeit, dass Person im Alter $x$ innerhalb von $t$ Jahren
(aber nicht frueher) stirbt.

## 1. Lebenslange vorschuessige Leibrente

### Formel

$$\ddot{a}_x^{(k)} = \sum_{t=0}^{\omega-x} {}_tp_x \cdot v^t - \beta(k,i)$$

### Bedeutung

Barwert einer lebenslangen Leibrente mit Zahlungen zu Periodenbeginn (vorschuessig),
$k$ Zahlungen pro Jahr.

### VBA-Funktion

```vba
qx_ax_k(Alter, Sex, Tafel, Zins, k)
```

### Berechnung

1. Initialisierung: $_0p_x = 1$, $v^0 = 1$
2. Fuer $t = 0, 1, 2, \ldots, \omega-x$:
   - Addiere $_tp_x \cdot v^t$ zur Summe
   - Update: $_{t+1}p_x = {}_tp_x \cdot p_{x+t}$
   - Update: $v^{t+1} = v^t \cdot v$
3. Subtrahiere Abzugsglied $\beta(k,i)$

### Spezialfall jaehrliche Zahlung ($k=1$)

$$\ddot{a}_x = \sum_{t=0}^{\omega-x} {}_tp_x \cdot v^t$$

(Abzugsglied $\beta(1,i) = 0$)

## 2. Temporaere vorschuessige Leibrente

### Formel

$$\ddot{a}_{x:\overline{n}\,}^{(k)} = \sum_{t=0}^{n-1} {}_tp_x \cdot v^t - \beta(k,i) \cdot \left(1 - {}_np_x \cdot v^n\right)$$

### Bedeutung

Barwert einer Leibrente mit maximaler Laufzeit $n$ Jahre, Zahlungen vorschuessig,
$k$ Zahlungen pro Jahr.

### VBA-Funktion

```vba
qx_axn_k(Alter, n, Sex, Tafel, Zins, k)
```

### Berechnung

1. Initialisierung: $_0p_x = 1$, $v^0 = 1$
2. Fuer $t = 0, 1, 2, \ldots, n-1$:
   - Addiere $_tp_x \cdot v^t$ zur Summe
   - Update: $_{t+1}p_x = {}_tp_x \cdot p_{x+t}$
   - Update: $v^{t+1} = v^t \cdot v$
3. Berechne $_np_x \cdot v^n$
4. Subtrahiere Abzugsglied mit Korrektur: $\beta(k,i) \cdot (1 - {}_np_x \cdot v^n)$

### Zusammenhang mit lebenslanger Rente

$$\ddot{a}_{x:\overline{n}\,}^{(k)} = \ddot{a}_x^{(k)} - {}_np_x \cdot v^n \cdot \ddot{a}_{x+n}^{(k)}$$

## 3. Aufgeschobene vorschuessige Leibrente

### Formel

$${}_n\ddot{a}_x^{(k)} = {}_np_x \cdot v^n \cdot \ddot{a}_{x+n}^{(k)}$$

### Bedeutung

Barwert einer lebenslangen Leibrente, die erst nach $n$ Jahren beginnt,
$k$ Zahlungen pro Jahr.

### VBA-Funktion

```vba
qx_nax_k(Alter, n, Sex, Tafel, Zins, k)
```

### Berechnung

1. Berechne $_np_x$ (mehrjahrige Ueberlebenswahrscheinlichkeit)
2. Berechne $v^n$ (Diskontierungsfaktor)
3. Berechne $\ddot{a}_{x+n}^{(k)}$ (lebenslange Rente ab Alter $x+n$)
4. Multipliziere alle drei Faktoren

## 4. Temporaere Todesfallversicherung

### Formel

$$A_{x:\overline{n}\,} = \sum_{t=1}^{n} {}_{t-1}|q_x \cdot v^t = \sum_{t=1}^{n} {}_{t-1}p_x \cdot q_{x+t-1} \cdot v^t$$

### Bedeutung

Barwert einer Todesfallversicherung mit Laufzeit $n$ Jahre, Leistung 1 EUR
am Ende des Todesjahres.

### VBA-Funktion

```vba
qx_nGrAx(Alter, n, Sex, Tafel, Zins)
```

### Berechnung

1. Initialisierung: $_0p_x = 1$, $v^1 = v$
2. Fuer $t = 1, 2, 3, \ldots, n$:
   - Addiere $_{t-1}p_x \cdot q_{x+t-1} \cdot v^t$ zur Summe
   - Update: $_tp_x = {}_{t-1}p_x \cdot p_{x+t-1} = {}_{t-1}p_x \cdot (1 - q_{x+t-1})$
   - Update: $v^{t+1} = v^t \cdot v$

### Hinweis zu Indexierung

Die Summe beginnt bei $t=1$ (nicht $t=0$), da die Todesfallleistung am Ende
des ersten Jahres fruestens faellig wird.

## 5. Reine Erlebensfallversicherung

### Formel

$$E_{x:\overline{n}\,} = {}_np_x \cdot v^n$$

### Bedeutung

Barwert einer Versicherung, die 1 EUR zahlt, wenn die Person das Alter $x+n$
erlebt.

### VBA-Funktion

```vba
qx_nGrEx(Alter, n, Sex, Tafel, Zins)
```

### Berechnung

1. Berechne $_np_x = p_x \cdot p_{x+1} \cdot \ldots \cdot p_{x+n-1}$
2. Berechne $v^n = v \cdot v \cdot \ldots \cdot v$ ($n$-mal)
3. Multipliziere: $E_{x:\overline{n}\,} = {}_np_x \cdot v^n$

## 6. Endliche vorschuessige Rente (ohne Todesfall-Risiko)

### Formel

Fuer $i > 0$:
$$\ddot{a}_{\overline{g}\,}^{(k)} = \frac{1 - v^g}{1 - v} - \beta(k,i) \cdot (1 - v^g)$$

Fuer $i = 0$:
$$\ddot{a}_{\overline{g}\,}^{(k)} = g$$

### Bedeutung

Rein finanzmathematischer Barwert einer endlichen Rente mit $g$ Zahlungen,
$k$ Zahlungen pro Jahr, ohne Beruecksichtigung eines Todesfall-Risikos.

### VBA-Funktion

```vba
qx_ag_k(g, Zins, k)
```

### Verwendung

Diese Funktion wird typischerweise nicht direkt fuer Versicherungsberechnungen
verwendet, sondern fuer interne Zwecke oder Plausibilitätspruefungen.

## 7. Abzugsglied fuer unterjahrige Zahlungen

### Formel (Woolhouse-Naeherung 1. Ordnung)

$$\beta(k,i) = \frac{1+i}{k} \sum_{\ell=0}^{k-1} \frac{\ell/k}{1 + (\ell/k) \cdot i}$$

### Vereinfachte Naeherung

$$\beta(k,i) \approx \frac{k-1}{2k}$$

Diese Naeherung ist fuer kleine Zinssaetze ausreichend genau.

### Spezialfaelle

- $k=1$ (jaehrlich): $\beta(1,i) = 0$
- $k=2$ (halbjaehrlich): $\beta(2,i) \approx 0,25$
- $k=4$ (vierteljaehrlich): $\beta(4,i) \approx 0,375$
- $k=12$ (monatlich): $\beta(12,i) \approx 0,4583$

### VBA-Funktion

```vba
qx_Abzugsglied(k, Zins)
```

### Bedeutung

Das Abzugsglied korrigiert den Rentenbarwert fuer unterjahrige Zahlungen.
Es beruecksichtigt, dass bei $k$ Zahlungen pro Jahr die Zahlungen nicht
gleichmaessig ueber das Jahr verteilt sind, sondern zu diskreten Zeitpunkten
erfolgen.

## Vergleich: Kommutationswerte vs. qx-Methode

### Kommutationswerte-Methode

**Vorteile:**
- Sehr schnell (Vorberechnung)
- Kompakte Formeln
- Traditionelle aktuarielle Methode

**Nachteile:**
- Weniger transparent
- Zusaetzlicher Berechnungsaufwand (Dx, Nx, etc.)
- Schwerer in moderne Programmiersprachen zu portieren

### qx-Methode

**Vorteile:**
- Direkt verstaendlich
- Keine Vorberechnungen noetig
- Einfach in Python/NumPy zu implementieren
- Flexibler erweiterbar

**Nachteile:**
- Langsamer (keine Cache-Nutzung)
- Mehr Berechnungen bei jedem Aufruf

## Numerische Stabilitaet

### Potenzielle Probleme

1. **Akkumulation von Rundungsfehlern** bei langen Produkten ($_tp_x$)
2. **Ausloeschung** bei Differenzen nahe Null
3. **Overflow/Underflow** bei sehr hohen Altern oder langen Laufzeiten

### Loesungsansaetze

1. **Double-Precision** verwenden (VBA: Double, Python: np.float64)
2. **Logarithmische Berechnungen** fuer lange Produkte:
   $$\log({}_tp_x) = \sum_{j=0}^{t-1} \log(p_{x+j})$$
   dann: $_tp_x = \exp(\log({}_tp_x))$
3. **Kahan-Summation** fuer bessere Summengenauigkeit

## Testfaelle

### Testfall 1: Standardparameter

```
x = 40
Sex = M
n = 30
t = 20
Zins = 1,75%
Tafel = DAV1994_T
k = 1
```

**Erwartete Werte:**
- $\ddot{a}_{40}^{(1)} \approx 23,574240$
- $\ddot{a}_{40:30}^{(1)} \approx 21,420278$
- $\ddot{a}_{40:20}^{(1)} \approx 16,313094$
- $A_{40:30} \approx 0,631592$
- $E_{40:30} \approx 0,584354$

### Testfall 2: Hoeheres Alter

```
x = 65
n = 20
Zins = 1,75%
Tafel = DAV1994_T
k = 1
```

**Plausibilitaetspruefungen:**
- $\ddot{a}_{65}^{(1)} < \ddot{a}_{40}^{(1)}$ (kuerze Lebenserwartung)
- $A_{65:20} > A_{40:20}$ (hoehere Sterblichkeit)
- $E_{65:20} < E_{40:20}$ (geringere Ueberlebenswahrscheinlichkeit)

### Testfall 3: Unterjahrige Zahlungen

```
x = 40
n = 30
Zins = 1,75%
k = 12 (monatlich)
```

**Plausibilitaetspruefungen:**
- $\ddot{a}_{40:30}^{(12)} > \ddot{a}_{40:30}^{(1)}$ (haeufigere Zahlungen)
- Differenz $\approx \beta(12, 0.0175) \approx 0,458$

## Python-Migration: Vektorisierung

Die qx-Methode ist ideal fuer NumPy-Vektorisierung:

```python
# Beispiel: tpx-Vektor berechnen
px_array = 1 - qx_array  # Element-weise
tpx_array = np.cumprod(px_array)  # Kumulative Produkte

# Beispiel: Rentenbarwert
v_array = v ** np.arange(n)  # v^0, v^1, ..., v^(n-1)
ax_n = np.sum(tpx_array * v_array) - beta(k, i)
```

## Zusammenfassung

Die qx-basierte Methode:
1. Berechnet Barwerte direkt aus Sterbewahrscheinlichkeiten
2. Ist transparenter und verstaendlicher
3. Eignet sich besser fuer Python-Migration
4. Ist langsamer als Kommutationswerte-Methode
5. Liefert identische Ergebnisse (bis auf Rundungsfehler)

Die Implementation sollte vor Python-Migration in Excel validiert werden,
um sicherzustellen, dass die Formeln korrekt sind.
