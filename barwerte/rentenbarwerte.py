# =============================================================================
# Rentenbarwert-Funktionen
# =============================================================================

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union, Optional

from .sterbetafel import Sterbetafel, MAX_ALTER
from .basisfunktionen import diskont, abzugsglied, npx, nqx

def ae_x(alter: int, sex: str, tafel: str, zins: float, sterbetafel_obj: Sterbetafel) -> float:
    """
    Berechnet den Barwert einer lebenslangen vorschuessigen Leibrente
    
    Formel: ax = sum_{t=0}^{omega-x} [tpx * v^t]
    
    wobei omega = MAX_ALTER (121 Jahre)
    
    Args:
        alter: Alter der versicherten Person
        sex: Geschlecht ('M' oder 'F')
        tafel: Name der Sterbetafel
        zins: Jaehrlicher Zinssatz
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        Barwert einer lebenslangen vorschuessigen Leibrente
    """
    if alter <= 0 or alter >= MAX_ALTER:
        return 0.0
    
    n = MAX_ALTER - alter
    v = diskont(zins)
    
    barwert = 0.0
    tpx = 1.0  # 0px = 1
    
    for t in range(n):
        barwert += tpx * (v ** t)
        
        # Update fuer naechste Iteration
        if t < n - 1:
            tpx *= (1.0 - sterbetafel_obj.qx(alter + t, sex, tafel))
    
    return barwert


def ae_x_k(alter: int, sex: str, tafel: str, zins: float, zw: int, sterbetafel_obj: Sterbetafel) -> float:
    """
    Berechnet den Barwert einer lebenslangen vorschuessigen Leibrente mit k Zahlungen pro Jahr
    
    Formel: ax^(k) = ax - abzug(k,i)
    
    wobei abzug das Abzugsglied nach Woolhouse ist.
    
    Args:
        alter: Alter der versicherten Person
        sex: Geschlecht ('M' oder 'F')
        tafel: Name der Sterbetafel
        zins: Jaehrlicher Zinssatz
        zw: Zahlungsweise (1, 2, 4, oder 12)
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        Barwert einer lebenslangen vorschuessigen Leibrente mit k Zahlungen pro Jahr
    """
    if zw <= 0:
        return 0.0
    
    ax_wert = ae_x(alter, sex, tafel, zins, sterbetafel_obj)
    abzug = abzugsglied(zw, zins)
    
    return ax_wert - abzug


def ae_xn(alter: int, n: int, sex: str, tafel: str, zins: float, sterbetafel_obj: Sterbetafel) -> float:
    """
    Berechnet den Barwert einer temporaeren vorschuessigen Leibrente ueber n Jahre
    
    Formel: ax:n = sum_{t=0}^{n-1} [tpx * v^t]
    
    Args:
        alter: Alter der versicherten Person
        n: Laufzeit in Jahren
        sex: Geschlecht ('M' oder 'F')
        tafel: Name der Sterbetafel
        zins: Jaehrlicher Zinssatz
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        Barwert einer temporaeren vorschuessigen Leibrente ueber n Jahre 
    """
    if n <= 0 or alter + n > MAX_ALTER:
        return 0.0
    
    n = min(MAX_ALTER - alter, n)
    v = diskont(zins)
    
    barwert = 0.0
    tpx = 1.0  # 0px = 1
    
    for t in range(n):
        barwert += tpx * (v ** t)
        
        # Update fuer naechste Iteration
        if t < n - 1:
            tpx *= (1.0 - sterbetafel_obj.qx(alter + t, sex, tafel))
    
    return barwert


def ae_xn_k(alter: int, n: int, sex: str, tafel: str, zins: float, zw: int, sterbetafel_obj: Sterbetafel) -> float:
    """
    Berechnet den Barwert einer temporaeren vorschuessigen Leibrente ueber n Jahre  mit k Zahlungen pro Jahr
    
    Formel: ax:n^(k) = ax:n - abzug(k,i) * [1 - npx*v^n]
    
    Args:
        alter: Alter der versicherten Person
        n: Laufzeit in Jahren
        sex: Geschlecht ('M' oder 'F')
        tafel: Name der Sterbetafel
        zins: Jaehrlicher Zinssatz
        zw: Zahlungsweise (1, 2, 4, oder 12)
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        Barwert einer temporaeren vorschuessigen Leibrente ueber n Jahre  mit k Zahlungen pro Jahr
    """
    if zw <= 0 or n <= 0 or alter + n > MAX_ALTER:
        return 0.0
    
    n = min(MAX_ALTER - alter, n)
    v = diskont(zins)
    
    axn_wert = ae_xn(alter, n, sex, tafel, zins, sterbetafel_obj)
    abzug = abzugsglied(zw, zins)
    n_px = npx(alter, n, sex, tafel, sterbetafel_obj)
    
    return axn_wert - abzug * (1.0 - n_px * (v ** n))


def n_ae_x_k(alter: int, n: int, sex: str, tafel: str, zins: float, k: int,
          sterbetafel_obj: Sterbetafel) -> float:
    """
    Berechnet den Barwert einer um n Jahre aufgeschobenen vorschuessigen Leibrente mit k Zahlungen pro Jahr
    
    Formel: n|ax^(k) = npx * v^n * ax+n^(k)
    
    Args:
        alter: Alter der versicherten Person
        n: Aufschubzeit in Jahren
        sex: Geschlecht ('M' oder 'F')
        tafel: Name der Sterbetafel
        zins: Jaehrlicher Zinssatz
        k: Zahlungsweise (1, 2, 4, oder 12)
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        Barwert einer um n Jahre aufgeschobenen vorschuessigen Leibrente mit k Zahlungen pro Jahr
    """
    if k <= 0 or n <= 0 or alter + n > MAX_ALTER:
        return 0.0
    
    v = diskont(zins)
    n_px = npx(alter, n, sex, tafel, sterbetafel_obj)
    ax_k_wert = ae_x_k(alter + n, sex, tafel, zins, k, sterbetafel_obj)
    
    return n_px * (v ** n) * ax_k_wert

def m_ae_xn_k(alter: int, n: int, m: int, sex: str, tafel: str, zins: float, k: int,
          sterbetafel_obj: Sterbetafel) -> float:
    """
    Berechnet den Barwert einer temporaeren um m Jahre aufgeschobenen vorschuessigen Leibrente ueber n Jahre mit k Zahlungen pro Jahr
    Beginn nach m Jahren Aufschub, Dauer n.
    
    Formel: m|axn^(k) = mpx * v^n * ax+m,n-m^(k)
    
    Args:
        alter: Alter der versicherten Person
        n: Laufzeit in Jahren
        m: Aufschubzeit in Jahren
        sex: Geschlecht ('M' oder 'F')
        tafel: Name der Sterbetafel
        zins: Jaehrlicher Zinssatz
        k: Zahlungsweise (1, 2, 4, oder 12)
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        Barwert einer temporaeren um m Jahre aufgeschobenen vorschuessigen Leibrente ueber n Jahre mit k Zahlungen pro Jahr
    """
    if k <= 0 or n <= 0 or alter + n > MAX_ALTER:
        return 0.0
    
    v = diskont(zins)
    m_px = npx(alter, m, sex, tafel, sterbetafel_obj)
    axn_k_wert = ae_xn_k(alter + m, n-m, sex, tafel, zins, k, sterbetafel_obj)
    
    return m_px * (v ** m) * axn_k_wert

