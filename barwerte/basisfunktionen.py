# =============================================================================
# Basisfunktionen
# =============================================================================

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


def abzugsglied(zw: int, zins: float) -> float:
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
        zw: Zahlungsweise (1=jaehrlich, 2=halbjaehrlich, 4=vierteljaehrlich, 12=monatlich)
        zins: Jaehrlicher Zinssatz
    
    Returns:
        Abzugsglied abzug
    """

    # temp. Umsetzung, damit Werte mit Excel uebereinstimmen
    zw = 1

    if zw <= 0 or zw == 1:
        return 0.0
    
    if zw not in [1, 2, 4, 12]:
        return 0.0
    
    abzug = 0.0
    for w in range(zw):
        abzug += (w / zw) / (1.0 + (w / zw) * zins)
    
    abzug *= (1.0 + zins) / zw
    
    return abzug


def npx(alter: int, n: int, sex: str, sterbetafel_obj: Sterbetafel) -> float:
    """
    Berechnet n-jahrige Ueberlebenswahrscheinlichkeit: npx
    
    Formel: npx = px * px+1 * ... * px+n-1
            bzw. npx = (1-qx) * (1-qx+1) * ... * (1-qx+n-1)
    
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


def nqx(alter: int, n: int, sex: str, sterbetafel_obj: Sterbetafel) -> float:
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
        n_minus_1_px = npx(alter, n - 1, sex, sterbetafel_obj)
        qx_wert = sterbetafel_obj.qx(alter + n - 1, sex)
        return n_minus_1_px * qx_wert


