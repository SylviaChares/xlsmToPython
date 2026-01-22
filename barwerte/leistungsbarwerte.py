# =============================================================================
# Leistungsbarwert-Funktionen
# =============================================================================

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union, Optional

from .sterbetafel import Sterbetafel, MAX_ALTER
from .basisfunktionen import diskont, abzugsglied, npx, nqx

def nAe_x(alter: int, n: int, sex: str, tafel: str, zins: float, sterbetafel_obj: Sterbetafel) -> float:
    """
    Berechnet den Leistungsbarwert einer konstanten Todesfallleistung der Hoehe 1 mit Eintrittsalter alter und Versicherungsdauer n
    
    Formel: |nAx = sum_{t=1}^{n} [(t-1)px * qx+t-1 * v^t]
    
    Args:
        alter: Alter der versicherten Person
        n: Laufzeit in Jahren
        sex: Geschlecht ('M' oder 'F')
        tafel: Name der Sterbetafel
        zins: Jaehrlicher Zinssatz
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        Barwert der temporaeren Todesfallversicherung
    """
    if n <= 0 or alter + n > MAX_ALTER:
        return 0.0
    
    n = min(MAX_ALTER - alter, n)
    v = diskont(zins)
    
    barwert = 0.0
    tpx = 1.0  # 0px = 1
    
    for t in range(1, n + 1):
        qx_wert = sterbetafel_obj.qx(alter + t - 1, sex, tafel)
        barwert += tpx * qx_wert * (v ** t)
        
        # Update fuer naechste Iteration
        if t < n:
            tpx *= (1.0 - qx_wert)
    
    return barwert


def nE_x(alter: int, n: int, sex: str, tafel: str, zins: float, sterbetafel_obj: Sterbetafel) -> float:
    """
    Berechnet den Leistungsbarwert einer Erlebensfallleistung der Hoehe 1 mit Eintrittsalter x und Versicherungsdauer n
    
    Formel: Ex:n = npx * v^n
    
    Args:
        alter: Alter der versicherten Person
        n: Laufzeit in Jahren
        sex: Geschlecht ('M' oder 'F')
        tafel: Name der Sterbetafel
        zins: Jaehrlicher Zinssatz
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        Leistungsbarwert einer Erlebensfallleistung der Hoehe 1 mit Eintrittsalter x und Versicherungsdauer n
    """
    if n <= 0 or alter + n > MAX_ALTER:
        return 1.0
    
    v = diskont(zins)
    n_px = npx(alter, n, sex, tafel, sterbetafel_obj)
    
    return n_px * (v ** n)


def Ae_xn(alter: int, n: int, sex: str, tafel: str, zins: float, sterbetafel_obj: Sterbetafel) -> float:
    """
    Berechnet den Leistungsbarwert einer gemischten Kapitallebensversicherung der Hoehe 1 mit Eintrittsalter x und Versicherungsdauer n
    
    Formel: Ae_xn = |nAx + nE_x = sum_{t=1}^{n} [(t-1)px * qx+t-1 * v^t] + npx * v^n = 1 - (1 - v) * ae_xn
    
    Args:
        alter: Alter der versicherten Person
        n: Laufzeit in Jahren
        sex: Geschlecht ('M' oder 'F')
        tafel: Name der Sterbetafel
        zins: Jaehrlicher Zinssatz
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        Leistungsbarwert einer gemischten Kapitallebensversicherung der Hoehe 1 mit Eintrittsalter x und Versicherungsdauer n
    """
    return nAe_x(alter, n, sex, tafel, zins, sterbetafel_obj) + nE_x(alter, n, sex, tafel, zins, sterbetafel_obj)