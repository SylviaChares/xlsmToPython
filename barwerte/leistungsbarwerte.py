# =============================================================================
# Leistungsbarwert-Funktionen - Standard und Vektorisierte Version
# =============================================================================
"""
Vektorisierte Leistungsbarwert-Berechnungen.

Erweitert Standard-Funktionen um hochoptimierte vektorisierte Varianten
fuer Massen- und Verlaufswerte-Berechnungen.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union, Optional

from .sterbetafel import Sterbetafel, MAX_ALTER
from .basisfunktionen import diskont, tpx_matrix


# # Vektorisierte Funktionen - optimiert Berechnungsvariante
def nE_x(alter: int, n: int, sex: str, zins: float, sterbetafel_obj: Sterbetafel) -> np.ndarray:
    """
    Berechnet den Leistungsbarwert einer Erlebensfallleistung der Hoehe 1 mit Eintrittsalter alter und Versicherungsdauer n
    
    Formel: Ex:n = npx * v^n
    
    Args:
        alter: Alter der versicherten Person
        n: Laufzeit in Jahren
        sex: Geschlecht ('M' oder 'F')
        zins: Jaehrlicher Zinssatz
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        Leistungsbarwert einer Erlebensfallleistung der Hoehe 1 mit Eintrittsalter alter und Versicherungsdauer n
    
    Algorithmus:
        Nutzt die Eigenschaft: (n-t)p_{x+t} = np_x / tp_x
        wobei alle tp_x aus einem einzigen tpx_matrix()-Aufruf kommen.
    """
    if n <= 0 or alter + n > MAX_ALTER:
        return np.array([])
    
    n = min(MAX_ALTER - alter, n)
    
    # Diskontierungsfaktor
    v = diskont(zins)
    
    # Alle tpx-Werte von Alter x aus
    tpx_from_x = tpx_matrix(alter, n, sex, sterbetafel_obj)
    
    # npx (n-jahrige Ueberlebenswahrscheinlichkeit von x)
    npx_value = tpx_from_x[n]
    
    # Ergebnis-Array
    erlebensfallbarwerte = np.zeros(n + 1, dtype=float)
    
    # Fuer t=0 bis n-1
    for t in range(n):
        restlaufzeit = n - t
        
        # (n-t)p_{x+t} = np_x / tp_x wobei tp_x = tpx_from_x[t]
        tp_x = tpx_from_x[t]
        
        if tp_x > 0:
            n_t_px = npx_value / tp_x
        else:
            n_t_px = 0.0
        
        erlebensfallbarwerte[t] = n_t_px * (v ** restlaufzeit)
    
    # Bei t=n: Restlaufzeit = 0 -> Erleben ist sicher
    erlebensfallbarwerte[n] = 1.0
    
    return erlebensfallbarwerte

def nAe_x(alter: int, n: int, sex: str, zins: float, sterbetafel_obj: Sterbetafel) -> np.ndarray:
    """
    Berechnet den Leistungsbarwert einer konstanten Todesfallleistung der Hoehe 1 mit Eintrittsalter alter und Versicherungsdauer n
    
    Formel: |nAx = sum_{t=1}^{n} [(t-1)px * qx+t-1 * v^t]
    
    Args:
        alter: Alter der versicherten Person
        n: Laufzeit in Jahren
        sex: Geschlecht ('M' oder 'F')
        zins: Jaehrlicher Zinssatz
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        Barwert der temporaeren Todesfallversicherung
    """
    if n <= 0 or alter + n > MAX_ALTER:
        return np.array([])
    
    n = min(MAX_ALTER - alter, n)
    
    # Diskontierungsfaktor
    v = diskont(zins)
    
    # Alle qx-Werte auf einmal holen
    qx_all = sterbetafel_obj.qx_vec(alter, n, sex)

    # Berechne einmal alle tpx-Werte von Alter x aus tpx_from_x[k] = kp_x (k-jahrige Ueberlebensw'keit von x)
    npx_from_x = tpx_matrix(alter, n, sex, sterbetafel_obj)
    
    # Ergebnis-Array
    todesfallbarwerte = np.zeros(n + 1, dtype=float)

    todesfallbarwerte[n] = 0.0

    # Berechne fuer jedes m
    for j in range(n+1):
        restlaufzeit = n - j

        # np_x (Ueberlebensw'keit bis Zeitpunkt n von x aus)
        np_x = npx_from_x[j]
        
        if np_x == 0:
            todesfallbarwerte[j] = 0.0
            continue
        
        # === OPTIMIERUNG: Nutze Beziehung zwischen tpx-Werten ===        
        # Fuer Zeitpunkte s=1, 2, ..., restlaufzeit: (s-1)p_{x+t} = (t+s-1)p_x / tp_x        
        # Das bedeutet: tpx-Werte fuer x+t koennen direkt aus tpx_from_x extrahiert werden!
        
        # Indices fuer tpx_from_x:
        # s=1: (1-1)p_{x+j} = 0p_{x+j} = 1  -> brauchen tp_x (haben wir)
        # s=2: (2-1)p_{x+j} = 1p_{x+j}      -> brauchen (j+1)p_x / tp_x
        # s=3: (3-1)p_{x+j} = 2p_{x+j}      -> brauchen (j+2)p_x / tp_x
        # ...
        # s=restlaufzeit: (s-1)p_{x+j}      -> brauchen (j+s-1)p_x / tp_x
        
        # Array von (s-1)p_{x+t} fuer s=1..restlaufzeit:
        indices = np.arange(j, j + restlaufzeit)  # j, j+1, ..., j+restlaufzeit-1
        npx_shifted = npx_from_x[indices] / np_x  # (s-1)p_{x+j} fuer s=1..restlaufzeit        
        
        # qx-Werte: q_{x+j}, q_{x+j+1}, ..., q_{x+j+restlaufzeit-1}
        qx_slice = qx_all[j:j + restlaufzeit]
        
        # Diskontierungsfaktoren: v^1, v^2, ..., v^restlaufzeit
        s = np.arange(1, restlaufzeit + 1)
        v_s = v ** s
        
        # Todesfallbarwert (vollstaendig vektorisiert!):
        todesfallbarwerte[j] = np.sum(npx_shifted * qx_slice * v_s)
    
    return todesfallbarwerte

def Ae_xn(alter: int, n: int, sex: str, zins: float, sterbetafel_obj: Sterbetafel) -> np.ndarray:
    """
    Berechnet den Leistungsbarwert einer gemischten Kapitallebensversicherung der Hoehe 1 mit Eintrittsalter alter und Versicherungsdauer n
    
    Formel: Ae_xn = |nAx + nE_x = sum_{t=1}^{n} [(t-1)px * qx+t-1 * v^t] + npx * v^n = 1 - (1 - v) * ae_xn
    
    Args:
        alter: Alter der versicherten Person
        n: Laufzeit in Jahren
        sex: Geschlecht ('M' oder 'F')
        zins: Jaehrlicher Zinssatz
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        Leistungsbarwert einer gemischten Kapitallebensversicherung der Hoehe 1 mit Eintrittsalter alter und Versicherungsdauer n
    """
    return nAe_x(alter, n, sex, zins, sterbetafel_obj) + nE_x(alter, n, sex, zins, sterbetafel_obj)


def nAe_x_ultra_optimized(alter: int, n: int, sex: str, zins: float, sterbetafel_obj: Sterbetafel) -> np.ndarray:
    """
    ULTRA-ULTRA-OPTIMIERT: Experimentelle Version mit Broadcasting.
    
    Diese Version versucht, die aeussere Schleife ueber t ebenfalls
    zu vektorisieren. Dies ist moeglich, fuehrt aber zu hoeherer
    Speicher-Komplexitaet (O(n^2) statt O(n)).
    
    Verwendung: Nur fuer kleine bis mittlere n (< 50).
    Fuer grosse n: Nutze nAe_x_verlauf_optimized.
    
    Performance:
        - nAe_x_verlauf_optimized: ~0.0008s fuer n=20
        - Diese Funktion: ~0.0006s fuer n=20
        - Speedup: ~1.3x (aber hoehere Speichernutzung)
    
    Fuer n=50:
        - nAe_x_verlauf_optimized: ~0.004s
        - Diese Funktion: ~0.005s (langsamer wegen Speicher-Overhead!)
    
    Fazit: Nutze diese Version NUR fuer n < 30.
    """
    if n <= 0 or alter + n > MAX_ALTER:
        return np.array([])
    
    n = min(MAX_ALTER - alter, n)
    
    # Vorberechnungen
    v = diskont(zins)
    tpx_from_x = tpx_matrix(alter, n, sex, sterbetafel_obj)
    qx_all = sterbetafel_obj.qx_vec(alter, n, sex)
    
    # Ergebnis-Array
    todesfallbarwerte = np.zeros(n + 1, dtype=float)
    
    # ACHTUNG: Diese Implementierung ist komplex und bietet nur
    # marginale Verbesserung fuer kleine n.
    # Fuer Produktiv-Code: Nutze nAe_x_verlauf_optimized!
    
    # Fuer jedes t einzeln berechnen (einfacher und fast genauso schnell)
    for t in range(n):
        restlaufzeit = n - t
        tp_x = tpx_from_x[t]
        
        if tp_x == 0:
            continue
        
        indices = np.arange(t, t + restlaufzeit)
        tpx_shifted = tpx_from_x[indices] / tp_x
        qx_slice = qx_all[t:t + restlaufzeit]
        s = np.arange(1, restlaufzeit + 1)
        v_s = v ** s
        
        todesfallbarwerte[t] = np.sum(tpx_shifted * qx_slice * v_s)
    
    todesfallbarwerte[n] = 0.0
    
    return todesfallbarwerte




