# =============================================================================
# Basisfunktionen - Standard und Vektorisiert
# =============================================================================
"""
Standard und vektorisierte Basis-Funktionen fuer versicherungsmathematische Berechnungen.

Diese Version erweitert die Standard-Basisfunktionen um vollstaendig
vektorisierte Varianten, die NumPy-Arrays verarbeiten koennen.

Performance-Gewinn:
- Einzelne Berechnungen: Keine Aenderung
- Massenberechnungen: 10-100x schneller (abhaengig von Array-Groesse)
- Monte-Carlo-Simulationen: Deutliche Beschleunigung
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union, Optional

from .sterbetafel import Sterbetafel, MAX_ALTER



def diskont(zins: float) -> float:
    """
    Berechnet Diskontierungsfaktor v = 1/(1+i).
    
    Args:
        zins: Jaehrlicher Zinssatz (z.B. 0.0175 fuer 1,75%)
    
    Returns:
        Diskontierungsfaktor v
    """
    if zins > 0:
        return 1.0 / (1.0 + zins)
    else:
        return 1.0

def diskont_vec(zins: float, t: int) -> np.ndarray:
    """
    Berechnet v^t fuer Array von t-Werten.
    
    Args:
        zins: Zinssatz (skalar)
        n: Laufzeit
    
    Returns:
        NumPy-Array mit v^t-Werten
    """
    return diskont(zins) ** np.arange(t)

def abzugsglied(k: int, zins: float) -> float:
    """
    Berechnet Abzugsglied fuer unterjahrige Zahlungen (Woolhouse-Naeherung 1. Ordnung).    
    Formel: abzug(k,i) = (1+i)/k * sum_{w=0}^{k-1} [(w/k) / (1 + (w/k)*i)]    
    Vereinfachte Naeherung: abzug(k,i) ≈ (k-1)/(2*k)
    
    Spezialfaelle:
        k=1 (jaehrlich): abzug = 0
        k=2 (halbjaehrlich): abzug ≈ 0,25
        k=4 (vierteljaehrlich): abzug ≈ 0,375
        k=12 (monatlich): abzug ≈ 0,4583
    
    Args:
        k: Zahlungsweise (1=jaehrlich, 2=halbjaehrlich, 4=vierteljaehrlich, 12=monatlich)
        zins: Jaehrlicher Zinssatz
    
    Returns:
        Abzugsglied
    """

    if k <= 0 or k == 1:
        return 0.0
    
    if k not in [1, 2, 4, 12]:
        return 0.0
    
    abzug = 0.0
    for w in range(k):
        abzug += (w / k) / (1.0 + (w / k) * zins)
    
    abzug *= (1.0 + zins) / k
    
    return abzug

def npx(alter: int, n: int, sex: str, sterbetafel_obj: Sterbetafel) -> np.ndarray:
    """
    Berechnet n-jahrige Ueberlebenswahrscheinlichkeit: npx
    
    Formel: npx = px * px+1 * ... * px+n-1 = npx = (1-qx) * (1-qx+1) * ... * (1-qx+n-1)
    """
    if n <= 0 or alter + n > MAX_ALTER:
        return np.array([])
    
    n = min(MAX_ALTER - alter, n)
    
    # Alle qx-Werte auf einmal holen
    qx_all = sterbetafel_obj.qx_vec(alter, n, sex)
    px_all = 1.0 - qx_all

    # Ergebnis-Array
    n_j_px = np.zeros(n+1, dtype=float)
    
    # Berechne fuer jedes m
    for j in range(n+1):
        # px-Werte 
        px_slice = np.append([1.0], px_all[0:j][:j])

        # tpx via kumulative Produkte
        jpx_values = np.ones(j+2)
        jpx_values[1:] = np.cumprod(px_slice)
        n_j_px[j] = jpx_values[j+1]

    return n_j_px

def nqx(alter: int, n: int, sex: str, sterbetafel_obj: Sterbetafel) -> np.ndarray:
    """
    Berechnet n-jahrige Sterbewahrscheinlichkeit: nqx
    
    Formel: nqx = (n-1)px * qx+n-1
    """
    if n <= 0 or alter + n > MAX_ALTER:
        return np.array([])
    
    n = min(MAX_ALTER - alter, n)
    
    # Alle qx-Werte auf einmal holen
    qx_all = sterbetafel_obj.qx_vec(alter-1, n+1, sex)
    npx_all = npx(alter, n, sex, sterbetafel_obj)

    # Ergebnis-Array
    n_j_qx = np.zeros(n+1, dtype=float)
    
    # Berechne fuer jedes m
    for j in range(n+1):
        # qx-Werte 
        if j == 0:
             n_j_qx[j] = qx_all[j]
        else:
            n_j_qx[j] = qx_all[j] * npx_all[j-1]

    return n_j_qx

def tpx_matrix(alter: int, max_t: int, sex: str, sterbetafel_obj: Sterbetafel) -> np.ndarray:
    """
    VEKTORISIERT: Berechnet Matrix aller tpx-Werte fuer t = 0, 1, ..., max_t.
    
    Diese Funktion ist hochoptimiert fuer die Verlaufswerte-Berechnung.
    Sie berechnet einmal alle benoetigten Ueberlebenswahrscheinlichkeiten
    und speichert sie in einer Matrix.
    
    Formel:
        tpx = px[0] * px[1] * ... * px[t-1]  fuer t > 0
        0px = 1
    
    Args:
        alter: Startalter
        max_t: Maximale Laufzeit
        sex: Geschlecht ('M' oder 'F')
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        NumPy-Array der Laenge (max_t + 1) mit tpx-Werten
        Index t enthaelt tpx (Ueberlebenswahrscheinlichkeit bis Zeit t)
    
    Beispiel:
        >>> # Berechne alle tpx fuer Alter 40, t = 0..20
        >>> tpx_values = tpx_matrix(40, 20, 'M', st)
        >>> print(tpx_values[0])   # 0px = 1.0
        >>> print(tpx_values[10])  # 10px
    
    Performance:
        - Einzelner Aufruf: Minimal langsamer als npx()
        - Mehrere t-Werte: 100x+ schneller als mehrere npx()-Aufrufe
    
    Technische Details:
        Nutzt np.cumprod() fuer kumulative Produkte - sehr effizient!
    """
    if max_t <= 0 or alter >= MAX_ALTER:
        return np.array([1.0])
    
    # Begrenze auf verfuegbare Alter
    max_t = min(max_t, MAX_ALTER - alter)
    
    # Hole alle px-Werte auf einmal
    px_werte = sterbetafel_obj.px_vec(alter, max_t, sex)
    
    # Berechne kumulative Produkte
    # tpx[0] = 1 (0px = 1)
    # tpx[1] = px[0]
    # tpx[2] = px[0] * px[1]
    # ...
    # tpx[t] = px[0] * px[1] * ... * px[t-1]
    tpx_values = np.ones(max_t + 1, dtype=float)
    tpx_values[1:] = np.cumprod(px_werte)
    
    return tpx_values



# =======================================================================================================================
# Backup Funktionen
# =======================================================================================================================

# Skalare Funktionen
def npx_val(alter: int, n: int, sex: str, sterbetafel_obj: Sterbetafel) -> float:
    """
    Berechnet n-jahrige Ueberlebenswahrscheinlichkeit: npx    
    Formel: npx = px * px+1 * ... * px+n-1 = npx = (1-qx) * (1-qx+1) * ... * (1-qx+n-1)
    
    Args:
        alter: Startalter
        n: Anzahl Jahre
        sex: Geschlecht ('M' oder 'F')
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        n-jahrige Ueberlebenswahrscheinlichkeit
    """
    if n <= 0 or alter + n >= MAX_ALTER:
        return 1.0
    
    px_werte = sterbetafel_obj.px_vec(alter, n, sex)
    return np.prod(px_werte)

def nqx_val(alter: int, n: int, sex: str, sterbetafel_obj: Sterbetafel) -> float:
    """
    Berechnet n-jahrige Sterbewahrscheinlichkeit: nqx
    
    Formel: nqx = (n-1)px * qx+n-1
    
    Args:
        alter: Startalter
        n: Anzahl Jahre
        sex: Geschlecht ('M' oder 'F')
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        n-jahrige Sterbewahrscheinlichkeit
    """
    if n <= 0 or alter + n >= MAX_ALTER:
        return 0.0
    
    if n == 1:
        return sterbetafel_obj.qx(alter, sex)
    else:
        n_minus_1_px = npx_val(alter, n - 1, sex, sterbetafel_obj)
        qx_wert = sterbetafel_obj.qx(alter + n - 1, sex)
        return n_minus_1_px * qx_wert




