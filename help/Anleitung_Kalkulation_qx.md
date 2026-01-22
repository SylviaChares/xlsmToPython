# Anleitung: Erstellung Tabellenblatt "Kalkulation_qx"

## Uebersicht

Diese Anleitung beschreibt, wie Sie ein neues Tabellenblatt mit qx-basierten 
Berechnungen (statt Kommutationswerten) erstellen.

## Schritt 1: VBA-Modul importieren

1. Oeffnen Sie `Tarifrechner_KLV.xlsm` in Excel
2. Druecken Sie Alt+F11 fuer VBA-Editor
3. Menue: Datei -> Datei importieren
4. Waehlen Sie die Datei `mBarwerte_qx.bas`
5. Das Modul "mBarwerte_qx" erscheint im Projekt-Explorer

## Schritt 2: Funktionen testen

Im VBA-Editor:
1. Druecken Sie Strg+G fuer Direktbereich
2. Fuehren Sie aus: `Test_qx_vs_Kommutation`
3. Pruefen Sie die Ausgabe - die Werte sollten identisch sein

Erwartete Ausgabe (gerundet):
```
ax^(1) - Lebenslange Leibrente:
  qx-Methode:        23.5742396825
  Kommutationswerte: 23.5742396825

ax:n^(1) - Temporaere Leibrente (n=30):
  qx-Methode:        21.4202775476
  Kommutationswerte: 21.4202775476

A_x:n - Temporaere Todesfallversicherung (n=30):
  qx-Methode:        0.6315922781
  Kommutationswerte: 0.6315922781

E_x:n - Erlebensfallversicherung (n=30):
  qx-Methode:        0.5843538895
  Kommutationswerte: 0.5843538895
```

## Schritt 3: Neues Tabellenblatt erstellen

1. Rechtsklick auf Tab "Kalkulation"
2. "Verschieben oder kopieren..."
3. "Kopie erstellen" ankreuzen
4. Neues Blatt umbenennen in: "Kalkulation_qx"

## Schritt 4: Formeln im neuen Blatt anpassen

### A. Beitragsberechnung (Zelle K5)

**Alte Formel (mit Kommutationswerten):**
```
=( Act_nGrAx(x,n,Sex,Tafel,Zins)+Act_Dx(x+n,Sex,Tafel,Zins)/Act_Dx(x,Sex,Tafel,Zins)
  +gamma1*Act_axn_k(x,t,Sex,Tafel,Zins,1)
  +gamma2*(Act_axn_k(x,n,Sex,Tafel,Zins,1)-Act_axn_k(x,t,Sex,Tafel,Zins,1)))
 /((1-beta1)*Act_axn_k(x,t,Sex,Tafel,Zins,1)-alpha*t)
```

**Neue Formel (mit qx-Werten):**
```
=( qx_nGrAx(x,n,Sex,Tafel,Zins)+qx_nGrEx(x,n,Sex,Tafel,Zins)
  +gamma1*qx_axn_k(x,t,Sex,Tafel,Zins,1)
  +gamma2*(qx_axn_k(x,n,Sex,Tafel,Zins,1)-qx_axn_k(x,t,Sex,Tafel,Zins,1)))
 /((1-beta1)*qx_axn_k(x,t,Sex,Tafel,Zins,1)-alpha*t)
```

**Aenderungen:**
- `Act_nGrAx` -> `qx_nGrAx`
- `Act_Dx(x+n,...)/Act_Dx(x,...)` -> `qx_nGrEx(x,n,...)`
- `Act_axn_k` -> `qx_axn_k`

### B. Nettopraemiensatz (Zelle K9)

**Alte Formel:**
```
=(Act_nGrAx(x,n,Sex,Tafel,Zins)+Act_Dx(x+n,Sex,Tafel,Zins)/Act_Dx(x,Sex,Tafel,Zins)
 +t*alpha*B_xt)
 /Act_axn_k(x,t,Sex,Tafel,Zins,1)
```

**Neue Formel:**
```
=(qx_nGrAx(x,n,Sex,Tafel,Zins)+qx_nGrEx(x,n,Sex,Tafel,Zins)
 +t*alpha*B_xt)
 /qx_axn_k(x,t,Sex,Tafel,Zins,1)
```

### C. Verlaufswerte (Spalte B, ab Zeile 16)

**Alte Formel (B16):**
```
=IF(A16<=n,
   Act_nGrAx(x+$A16,MAX(0,n-$A16),Sex,Tafel,Zins)
   +Act_Dx(x+n,Sex,Tafel,Zins)/Act_Dx(x+$A16,Sex,Tafel,Zins),
   0)
```

**Neue Formel:**
```
=IF(A16<=n,
   qx_nGrAx(x+$A16,MAX(0,n-$A16),Sex,Tafel,Zins)
   +qx_nGrEx(x+$A16,MAX(0,n-$A16),Sex,Tafel,Zins),
   0)
```

### D. Verlaufswerte (Spalte C, ab Zeile 16)

**Alte Formel (C16):**
```
=Act_axn_k(x+$A16,MAX(0,n-$A16),Sex,Tafel,Zins,1)
```

**Neue Formel:**
```
=qx_axn_k(x+$A16,MAX(0,n-$A16),Sex,Tafel,Zins,1)
```

### E. Verlaufswerte (Spalte D, ab Zeile 16)

**Alte Formel (D16):**
```
=Act_axn_k(x+$A16,MAX(0,t-$A16),Sex,Tafel,Zins,1)
```

**Neue Formel:**
```
=qx_axn_k(x+$A16,MAX(0,t-$A16),Sex,Tafel,Zins,1)
```

### F. Verlaufswerte (Spalte E, ab Zeile 16)

**Alte Formel (E16):**
```
=B16-P_xt*D16+gamma2*(C16-Act_axn_k(x,n,Sex,Tafel,Zins,1)/Act_axn_k(x,t,Sex,Tafel,Zins,1)*D16)
```

**Neue Formel:**
```
=B16-P_xt*D16+gamma2*(C16-qx_axn_k(x,n,Sex,Tafel,Zins,1)/qx_axn_k(x,t,Sex,Tafel,Zins,1)*D16)
```

## Schritt 5: Formeln kopieren

Die Formeln in den Spalten F-L bleiben unveraendert, da sie auf Spalten B-E 
referenzieren. Diese koennen einfach aus dem Original-Blatt kopiert werden.

**Wichtig:** Die Formeln in Zeile 16 muessen als Array-Formeln nach unten kopiert 
werden fuer alle Vertragsjahre (k = 0, 1, 2, ..., n).

## Schritt 6: Definierte Namen anpassen (Optional)

Falls Sie die definierten Namen auch fuer das neue Blatt verwenden moechten:

1. Formeln -> Namens-Manager
2. Erstellen Sie neue Namen mit Suffix "_qx":
   - `B_xt_qx` -> Kalkulation_qx!$K$5
   - `P_xt_qx` -> Kalkulation_qx!$K$9

Oder passen Sie die Formeln an, um direkt auf die Zellen zu referenzieren.

## Schritt 7: Validierung

Vergleichen Sie die Ergebnisse zwischen beiden Blaettern:

| Zelle | Original (Kommutation) | Neu (qx-Methode) | Differenz |
|-------|------------------------|------------------|-----------|
| K5    | 0,04226001            | sollte ~gleich   | < 1e-9    |
| K6    | 4.226,00 EUR          | sollte gleich    | 0         |
| K9    | 0,04001217            | sollte ~gleich   | < 1e-9    |

**Hinweis:** Minimale Abweichungen (< 10^-9) koennen durch Rundungsdifferenzen 
in der Berechnungsreihenfolge entstehen. Dies ist normal und akzeptabel.

## Schritt 8: Performance-Vergleich

Die qx-basierte Methode ist:
- **Langsamer** als Kommutationswerte (keine Vorberechnung/Cache)
- **Transparenter** und leichter zu verstehen
- **Besser geeignet** fuer Python-Migration

Fuer groeßere Verlaufstabellen (z.B. k = 0 bis 50) kann die Berechnung 
merklich laenger dauern. Dies ist der Preis fuer die direkte Methode.

## Vorteile der qx-Methode

1. **Keine Vorab-Berechnung:** Kommutationswerte muessen nicht erst 
   erstellt werden
2. **Flexibler:** Leicht erweiterbar fuer andere Produkte
3. **Verstaendlicher:** Formeln sind naeher an der mathematischen Definition
4. **Python-freundlich:** Direkte Umsetzung in NumPy-Arrays moeglich

## Naechste Schritte fuer Python

Nach erfolgreicher Validierung in Excel:

1. Port der qx-Funktionen nach Python mit NumPy
2. Validierung gegen Excel-Werte
3. Performance-Optimierung durch Vektorisierung
4. Erweiterung um zusaetzliche Funktionen

## Troubleshooting

**Problem:** #NAME? Fehler in Formeln
**Loesung:** VBA-Modul wurde nicht korrekt importiert. Pruefen Sie im 
            VBA-Editor, ob "mBarwerte_qx" vorhanden ist.

**Problem:** Werte weichen stark ab (> 0,001)
**Loesung:** Pruefen Sie, ob die Parameter (x, Sex, Tafel, Zins) korrekt 
            uebergeben werden. Fuehren Sie Test_qx_vs_Kommutation aus.

**Problem:** Excel wird langsam
**Loesung:** Reduzieren Sie die Anzahl der Verlaufszeilen temporaer oder 
            deaktivieren Sie die automatische Berechnung (Formeln -> 
            Berechnungsoptionen -> Manuell).
