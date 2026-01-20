Attribute VB_Name = "mBarwerte"
'===============================================================================
' Modul: mBarwerte
' Zweck: Berechnung versicherungsmathematischer Barwerte direkt aus qx-Werten
'        ohne Verwendung von Kommutationswerten (Dx, Nx, Mx, etc.)
'
' Vorbereitung fuer Python-Migration: Diese Implementation ist transparenter
' und einfacher in Python zu portieren als die Kommutationswerte-Methode.
'===============================================================================

'Option Explicit

Public Const MAX_ALTER As Integer = 123

' Hilfsfunktionen
Private Function Diskont(Zins As Double) As Double
    ' Diskontierungsfaktor v = 1/(1+i)
    If Zins > 0 Then
        Diskont = 1# / (1# + Zins)
    Else
        Diskont = 1#
    End If
End Function

Public Function qx(Alter As Integer, Sex As String, Tafel As String) As Double
    Dim ws As Worksheet, RGL As Variant, col As Integer, idx As Long
    
    Set ws = ThisWorkbook.Worksheets("Tafeln")
    RGL = Range(ws.Range("v_Tafeln"), ws.Range("m_Tafeln"))
    
    Sex = UCase(Sex)
    If Sex <> "M" Then Sex = "F"
    
    Tafel = UCase(Tafel)
    
    Select Case Tafel    ' Prüfen, ob Tafelstring überhaupt implementiert ist
         ' hier muss die komplette Liste aller implementierten Tafeln angegeben werden
        Case "DAV1994_T"
            If Sex = "M" Then col = 1 Else col = 2
            'qx = WorksheetFunction.Index(ws.Range("m_Tafeln"), Alter + 1, WorksheetFunction.Match(UCase(Tafel) & "_" & Sex, ws.Range("v_Tafeln"), 0))
        Case "DAV2008_T"
            If Sex = "M" Then col = 3 Else col = 4
        Case Else
            col = 2
    End Select
    
    qx = RGL(Alter + 2, col)
End Function

Private Function qx_vec(Alter As Integer, n As Integer, Sex As String, Tafel As String) As Variant
    ' Erzeugt Vektor der Sterbewahrscheinlichkeiten qx fuer n Jahre
    ' Rueckgabe: Array(0 to n-1) mit qx-Werten
    
    Dim vek() As Double
    Dim idx As Integer
    
    If n <= 0 Or Alter + n >= MAX_ALTER Then Exit Function
    ReDim vek(0 To n - 1)
    
    For idx = 0 To n - 1
        vek(idx) = qx(Alter + idx, Sex, Tafel)
    Next idx
    
    qx_vec = vek
End Function

Private Function px_vec(Alter As Integer, n As Integer, Sex As String, Tafel As String) As Variant
    ' Erzeugt Vektor der Ueberlebenswahrscheinlichkeiten px fuer n Jahre
    ' px = 1 - qx
    ' Rueckgabe: Array(0 to n-1) mit px-Werten
    
    Dim vek() As Double
    Dim idx As Integer
    
    If n <= 0 Or Alter + n >= MAX_ALTER Then Exit Function
    ReDim vek(0 To n - 1)
    
    For idx = 0 To n - 1
        vek(idx) = 1 - qx(Alter + idx, Sex, Tafel)
    Next idx
    
    px_vec = vek
End Function

Public Function npx(Alter As Integer, n As Integer, Sex As String, Tafel As String) As Double
    ' Berechnet n-jahrige Ueberlebenswahrscheinlichkeit: tpx
    ' tpx = px * px+1 * ... * px+t-1
    
    Dim idx As Integer, p_x As Variant
    
    npx = 1 ' 0px = 1
    If n <= 0 Or Alter + n >= MAX_ALTER Then Exit Function
    
    p_x = px_vec(Alter, n, Sex, Tafel)
    
    For idx = 0 To n - 1
        npx = npx * p_x(idx) ' (1 - qx(Alter + idx, Sex, Tafel))
    Next idx
End Function

Private Function nqx(Alter As Integer, n As Integer, Sex As String, Tafel As String) As Double
    ' Berechnet n-jahrige Sterbewahrscheinlichkeit: tqx
    ' tqx = t-1px * qx+t-1
    Dim q_x As Variant
    
    nqx = 0
    If n <= 0 Or Alter + n >= MAX_ALTER Then Exit Function
    
    If n = 1 Then
        nqx = qx(Alter, Sex, Tafel)
    Else
        nqx = npx(Alter, n - 1, Sex, Tafel) * qx(Alter + n - 1, Sex, Tafel)
    End If
End Function


'===============================================================================
' Abzugsglied fuer unterjahrige Zahlungen (Woolhouse-Naeherung 1. Ordnung)
'===============================================================================

Public Function Abzugsglied(zw As Integer, Zins As Double) As Double
    ' Abzugsglied fuer unterjahrige Zahlungen
    ' Formel (Woolhouse-Naeherung 1. Ordnung): Abzugsglied = \frac{1+i}{k} \sum_{w=0}^{k-1} \frac{w/k}{1 + (w/k) \cdot i}
    ' Vereinfachte Naeherung: $$\beta(k,i) rund \frac{k-1}{2k}$$
    ' Spezialfaelle
    '   k=1 (jaehrlich): = 0
    '   k=2 (halbjaehrlich): rund 0,25
    '   k=4 (vierteljaehrlich): rund 0,375
    '   k=12 (monatlich): rund 0,4583
    
    Dim idx As Integer
    
    Abzugsglied = 0
    
    If zw <= 0 Then Exit Function
    If zw = 1 Then Exit Function  ' Bei jaehrlicher Zahlung ist Abzugsglied = 0
    
    Select Case zw
        Case 1, 2, 4, 12
            For idx = 0 To zw - 1
                Abzugsglied = Abzugsglied + idx / CDbl(zw) / (1 + CDbl(idx) / CDbl(zw) * Zins)
            Next idx
        Case Else
            Abzugsglied = 0
    End Select
    
    Abzugsglied = Abzugsglied * (1 + Zins) / CDbl(zw)
End Function

Function Min(ByVal x1 As Double, ByVal x2 As Double) As Double
    If x1 <= x2 Then Min = x1 Else Min = x2
End Function

Function Max(ByVal x1 As Double, ByVal x2 As Double) As Double
    If x1 >= x2 Then Max = x1 Else Max = x2
End Function

' Barwert: Lebenslange vorschuessige Leibrente
Public Function ax(Alter As Integer, Sex As String, Tafel As String, Zins As Double) As Double
    ' Berechnet Barwert lebenslange vorschuessige Leibrente
    ' mit k Zahlungen pro Jahr
    '
    ' Formel: ax = Summe_{t=0}^{omega-x} [ tpx * v^t ]
    '
    ' wobei omega = MAX_ALTER (123 Jahre)
    
    Dim idx As Integer
    Dim v As Double
    Dim tpx As Double
    
    ax = 0
    If Alter <= 0 Or Alter >= MAX_ALTER Then Exit Function
    
    n = MAX_ALTER - Alter
    v = Diskont(Zins)
    
    ' Berechne Summe: Summe_{t=0}^{n-1} [ tpx * v^t ]
    tpx = 1        ' 0px = 1
    For idx = 0 To n - 1
        ax = ax + tpx * v ^ idx
        
        ' Update fuer naechste Iteration
        If idx < n - 1 Then
            tpx = tpx * (1 - qx(Alter + idx, Sex, Tafel))
        End If
    Next idx
End Function

' Barwert: Lebenslange vorschuessige Leibrente mit k Zahlungen pro Jahr
Public Function ax_k(Alter As Integer, Sex As String, Tafel As String, Zins As Double, zw As Integer) As Double
    ' Berechnet Barwert temporaere vorschuessige Leibrente
    ' Dauer n Jahre, mit k Zahlungen pro Jahr
    '
    ' Formel: ax^(k) = Summe_{t=0}^{n-1} [ tpx * v^t ] - beta(k,i) * [1 - n_px*v^n]
    
    ax_k = 0
    If zw <= 0 Then Exit Function
        
    ' Abzugsglied mit Korrektur fuer temporaere Rente mit n_px * v^n
    ax_k = ax(Alter, Sex, Tafel, Zins) - Abzugsglied(zw, Zins)
End Function

' Barwert: Temporaere vorschuessige Leibrente über n Jahre
Public Function axn(Alter As Integer, n As Integer, Sex As String, Tafel As String, Zins As Double) As Double
    ' Berechnet Barwert temporaere vorschuessige Leibrente
    ' Dauer n Jahre, mit k Zahlungen pro Jahr
    '
    ' Formel: ax:n^(1) = Summe_{t=0}^{n-1} [ tpx * v^t ]
    
    Dim t As Integer
    Dim v As Double
    Dim tpx As Double
    
    axn = 0
    If n <= 0 Or Alter + n > MAX_ALTER Then Exit Function
    
    n = Min(MAX_ALTER - Alter, n)
    v = Diskont(Zins)
    
    ' Berechne Summe: Summe_{t=0}^{n-1} [ tpx * v^t ]
    axn = 0
    tpx = 1        ' 0px = 1
    For idx = 0 To n - 1
        axn = axn + tpx * v ^ idx
        
        ' Update fuer naechste Iteration
        If idx < n - 1 Then
            tpx = tpx * (1 - qx(Alter + idx, Sex, Tafel))
        End If
    Next idx
End Function

' Barwert: Temporaere vorschuessige Leibrente über n Jahre mit k Zahlungen pro Jahr
Public Function axn_k(Alter As Integer, n As Integer, Sex As String, Tafel As String, Zins As Double, zw As Integer) As Double
    ' Berechnet Barwert temporaere vorschuessige Leibrente
    ' Dauer n Jahre, mit k Zahlungen pro Jahr
    '
    ' Formel: ax:n^(k) = Summe_{t=0}^{n-1} [ tpx * v^t ] - Abzugsglied(k,i) * [1 - n_px*v^n]
    
    Dim v As Double
    
    axn_k = 0
    If zw <= 0 Or n <= 0 Or Alter + n > MAX_ALTER Then Exit Function
    
    n = Min(MAX_ALTER - Alter, n)
    v = Diskont(Zins)
    
    ' Abzugsglied mit Korrektur fuer temporaere Rente mit n_px * v^n
    axn_k = axn(Alter, n, Sex, Tafel, Zins) - Abzugsglied(zw, Zins) * (1# - npx(Alter, n, Sex, Tafel) * v ^ n)
End Function

' Barwert: Aufgeschobene vorschuessige Leibrente mit k Zahlungen pro Jahr
Public Function nax_k(Alter As Integer, n As Integer, Sex As String, Tafel As String, Zins As Double, k As Integer) As Double
    ' Berechnet Barwert aufgeschobene vorschuessige Leibrente
    ' Beginn nach n Jahren, mit k Zahlungen pro Jahr
    '
    ' Formel: n|ax^(k) = npx * v^n * ax+n^(k)
    
    Dim v As Double
    
    nax_k = 0
    If k <= 0 Or n <= 0 Or Alter + n > MAX_ALTER Then Exit Function
    
    v = Diskont(Zins)
    
    nax_k = npx(Alter, n, Sex, Tafel) * v ^ n * ax_k(Alter + n, Sex, Tafel, Zins, k)
End Function

' Barwert: Temporaere Todesfallversicherung (Leistung am Jahresende)
Public Function nAx(Alter As Integer, n As Integer, Sex As String, Tafel As String, Zins As Double) As Double
    ' Berechnet Barwert temporaere Todesfallversicherung
    ' Leistung 1 EUR am Ende des Todesjahres
    '
    ' Formel: A_x:n = Summe_{t=1}^{n} [ t-1|qx * v^t ] = Summe_{t=1}^{n} [ t-1px * qx+t-1 * v^t ]
    
    Dim idx As Integer
    Dim v As Double
    Dim tpx As Double  ' Hier: t-1px
    
    nAx = 0
    If n <= 0 Or Alter + n > MAX_ALTER Then Exit Function
    
    n = Min(MAX_ALTER - Alter, n)
    v = Diskont(Zins)
    
    ' Berechne Summe: Summe_{t=1}^{n} [ t-1px * qx+t-1 * v^t ]
    nAx = 0
    tpx = 1        ' 0px = 1
    
    For idx = 1 To n
        nAx = nAx + tpx * qx(Alter + idx - 1, Sex, Tafel) * v ^ idx
        
        ' Update fuer naechste Iteration
        If idx < n Then
            tpx = tpx * (1 - qx(Alter + idx - 1, Sex, Tafel))
        End If
    Next idx
End Function

' Barwert: Reine Erlebensfallversicherung
Public Function nEx(Alter As Integer, n As Integer, Sex As String, Tafel As String, Zins As Double) As Double
    ' Berechnet Barwert reine Erlebensfallversicherung
    ' Leistung 1 EUR nach n Jahren bei Erleben
    '
    ' Formel: E_x:n = npx * v^n
    
    Dim v As Double
    
    nEx = 1
    If n <= 0 Or Alter + n > MAX_ALTER Then Exit Function
    
    v = Diskont(Zins)
    nEx = npx(Alter, n, Sex, Tafel) * (v ^ n)
End Function

' Barwert: Endliche vorschuessige Rente (ohne Todesfall-Risiko)
Public Function ag_k(g As Integer, Zins As Double, k As Integer) As Double
    ' Berechnet Barwert endliche vorschuessige Rente
    ' g Zahlungen, k Zahlungen pro Jahr
    ' Kein Todesfallrisiko (rein finanzmathematisch)
    '
    ' Formel: a_g^(k) = (1 - v^g) / (1 - v) - beta(k,i) * (1 - v^g)
    
    Dim v As Double
    
    ag_k = 0
    If k <= 0 Or g <= 0 Then Exit Function
    
    If Zins = 0 Then
        ag_k = CDbl(g)
        Exit Function
    End If
    
    v = Diskont(Zins)
    
    ag_k = (1# - v ^ g) / (1# - v) - Abzugsglied(k, Zins) * (1# - v ^ g)
End Function


