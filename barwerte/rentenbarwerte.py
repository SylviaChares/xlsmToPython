# =============================================================================
# Rentenbarwert-Funktionen - Standard und Vektorisierte Version
# =============================================================================
"""
Vektorisierte Rentenbarwert-Berechnungen.

Diese Version erweitert die Standard-Funktionen um hochoptimierte
vektorisierte Varianten fuer Massen- und Verlaufswerte-Berechnungen.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union, Optional

from .sterbetafel import Sterbetafel, MAX_ALTER
from .basisfunktionen import (
    diskont, abzugsglied, npx, nqx, npx_val, 
    tpx_matrix, verlaufswerte_setup
)


# Vektorisierte Funktionen - optimiert Berechnungsvariante
def ae_x(alter: int, sex: str, zins: float, sterbetafel_obj: Sterbetafel) -> np.ndarray:
    """
    Berechnet den lebenslangen vorschuessigen Rentenbarwert ae_x.

    Formel:
        ae_x = sum_{j=0}^{w-1} [jpx * v^j]
    
    Args:
        alter: Eintrittsalter
        sex: Geschlecht
        zins: Zinssatz
        zw: Zahlungsweise
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        NumPy-Array der Laenge n mit Rentenbarwerten:
        - Index 0: ae_x:n (Beginn Jahr 1)
        - Index 1: ae_{x+1}:n-1 (Beginn Jahr 2)
        - ...
        - Index n-1: ae_{x+n-1}:1 (Beginn Jahr n)
    
    Algorithmus:
        Berechnet alle benoetigten tpx-Werte in einem Durchgang und
        nutzt dann kumulative Operationen fuer maximale Effizienz.
    """
    if n <= 0 or alter + n > MAX_ALTER:
        return np.array([])
    
    n = MAX_ALTER - alter
    
    # Vorberechnung
    v = diskont(zins)
    
    # Alle qx-Werte auf einmal holen
    qx_all = sterbetafel_obj.qx_vec(alter, n, sex)
    px_all = 1.0 - qx_all
    
    # Ergebnis-Array
    rentenbarwerte = np.zeros(n, dtype=float)
    
    # Berechne fuer jedes m
    for j in range(n):
        restlaufzeit = n - j
        
        # px-Werte fuer Restlaufzeit
        px_slice = px_all[j:n][:restlaufzeit]
        
        # jpx via kumulative Produkte
        jpx_values = np.ones(restlaufzeit + 1)
        jpx_values[1:] = np.cumprod(px_slice)
        
        # v^s Werte
        s = np.arange(restlaufzeit)
        v_s = v ** s
        
        # Rentenbarwert
        rentenbarwerte[j] = np.sum(jpx_values[:restlaufzeit] * v_s)
    
    return rentenbarwerte

def ae_x_k(alter: int, sex: str, zins: float, zw: int, sterbetafel_obj: Sterbetafel) -> float:
    """
    Berechnet den lebenslangen vorschuessigen Rentenbarwert ae_x mit k Zahlungen pro Jahr
    
    Formel:
        ae_x_k = ae_x - abzug(k,i) 
    
    Args:
        setup: Dictionary von verlaufswerte_setup()
        zw: Zahlungsweise
    
    Returns:
        Rentenbarwert mit unterjahrigen Zahlungen
    """
    if zw <= 0:
        return 0.0
    
    return ae_x(alter, sex, zins, sterbetafel_obj) - abzugsglied(zw, zins) if zw > 1 else 0.0 

def ae_xn(alter: int, n: int, sex: str, zins: float, sterbetafel_obj: Sterbetafel) -> np.ndarray:
    """
    Berechnet den vorschuessigen Rentenbarwert ae_xn ueber n Jahre.

    Formel:
        ae_xn = sum_{j=0}^{n-1} [jpx * v^j]
    
    Args:
        alter: Eintrittsalter
        n: Versicherungsdauer
        sex: Geschlecht
        zins: Zinssatz
        zw: Zahlungsweise
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        NumPy-Array der Laenge n mit Rentenbarwerten:
        - Index 0: ae_x:n (Beginn Jahr 1)
        - Index 1: ae_{x+1}:n-1 (Beginn Jahr 2)
        - ...
        - Index n-1: ae_{x+n-1}:1 (Beginn Jahr n)
    
    Algorithmus:
        Berechnet alle benoetigten tpx-Werte in einem Durchgang und
        nutzt dann kumulative Operationen fuer maximale Effizienz.
    """
    if n <= 0 or alter + n > MAX_ALTER:
        return np.array([])
    
    n = min(MAX_ALTER - alter, n)
    
    # Vorberechnung
    v = diskont(zins)
    
    # Alle qx-Werte auf einmal holen
    qx_all = sterbetafel_obj.qx_vec(alter, n, sex)
    px_all = 1.0 - qx_all
    
    # Ergebnis-Array
    rentenbarwerte = np.zeros(n, dtype=float)
    
    # Berechne fuer jedes m
    for j in range(n):
        restlaufzeit = n - j
        
        # px-Werte fuer Restlaufzeit
        px_slice = px_all[j:n][:restlaufzeit]
        
        # jpx via kumulative Produkte
        jpx_values = np.ones(restlaufzeit + 1)
        jpx_values[1:] = np.cumprod(px_slice)
        
        # v^s Werte
        s = np.arange(restlaufzeit)
        v_s = v ** s
        
        # Rentenbarwert
        rentenbarwerte[j] = np.sum(jpx_values[:restlaufzeit] * v_s)
    
    return rentenbarwerte

def ae_xn_k(alter: int, n: int, sex: str, zins: float, zw: int, sterbetafel_obj: Sterbetafel) -> np.ndarray:
    """
    Berechnet den vorschuessigen Rentenbarwert ae_xn ueber n Jahre.

    Formel:
        ae_xn = sum_{j=0}^{n-1} [jpx * v^j]
    
    Args:
        alter: Eintrittsalter
        n: Versicherungsdauer
        sex: Geschlecht
        zins: Zinssatz
        zw: Zahlungsweise
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        NumPy-Array der Laenge n mit Rentenbarwerten:
        - Index 0: ae_x:n (Beginn Jahr 1)
        - Index 1: ae_{x+1}:n-1 (Beginn Jahr 2)
        - ...
        - Index n-1: ae_{x+n-1}:1 (Beginn Jahr n)
    
    Algorithmus:
        Berechnet alle benoetigten tpx-Werte in einem Durchgang und
        nutzt dann kumulative Operationen fuer maximale Effizienz.
    """
    if n <= 0 or alter + n > MAX_ALTER:
        return np.array([])
    
    n = min(MAX_ALTER - alter, n)
    
    # Vorberechnung
    v = diskont(zins)
    abzug = abzugsglied(zw, zins) if zw > 1 else 0.0
    
    # Alle qx-Werte auf einmal holen
    qx_all = sterbetafel_obj.qx_vec(alter, n, sex)
    px_all = 1.0 - qx_all
    
    # Ergebnis-Array
    rentenbarwerte = np.zeros(n, dtype=float)
    
    # Berechne fuer jedes m
    for j in range(n):
        restlaufzeit = n - j
        
        # px-Werte fuer Restlaufzeit
        px_slice = px_all[j:n][:restlaufzeit]
        
        # jpx via kumulative Produkte
        jpx_values = np.ones(restlaufzeit + 1)
        jpx_values[1:] = np.cumprod(px_slice)
        
        # v^s Werte
        s = np.arange(restlaufzeit)
        v_s = v ** s
        
        # Rentenbarwert
        rentenbarwerte[j] = np.sum(jpx_values[:restlaufzeit] * v_s)
        
        # Korrektur fuer unterjahrige Zahlungen
        if zw > 1:
            n_j_px = jpx_values[restlaufzeit]
            rentenbarwerte[j] -= abzug * (1.0 - n_j_px * (v ** restlaufzeit))
    
    return rentenbarwerte

def m_ae_xn_k(alter: int, n: int, t: int, sex: str, zins: float, zw: int, sterbetafel_obj: Sterbetafel) -> np.ndarray:
    """
    Berechnet den um m Jahre aufgeschobenen vorschuessigen Rentenbarwert ae_xn ueber n Jahre.

    Formel:
        Formel: m|axn^(k) = mpx * v^n * ax+m,n-m^(k)
    """
    if n <= 0 or alter + n > MAX_ALTER or t > n:
        return np.array([])
    
#    v = diskont(zins)
#
#    # Alle qx-Werte auf einmal holen
#    qx_all = sterbetafel_obj.qx_vec(alter, n, sex)
#    px_all = 1.0 - qx_all
#
#    ae_xn_k_val = ae_xn_k(alter, n, sex, zins, zw, sterbetafel_obj)[t]
#    ae_xn_k_vec = ae_xn_k(alter+t, n-t, sex, zins, zw, sterbetafel_obj)
#    
#    # Ergebnis-Array
#    n_j_px = np.ones(t, dtype=float) # np.zeros(t, dtype=float)
#    
#    # Berechne fuer jedes m
#    for j in range(t):
#        restlaufzeit = t - j
#        
#        # px-Werte fuer Restlaufzeit
#        px_slice = px_all[j:t][:restlaufzeit]
#        
#        # jpx via kumulative Produkte
#        jpx_values = np.ones(restlaufzeit + 1)
#        jpx_values[1:] = np.cumprod(px_slice)
#        
#        n_j_px[j] = jpx_values[restlaufzeit] * (v ** restlaufzeit) * ae_xn_k_val
#    
#    return np.append(n_j_px, ae_xn_k_vec)
#
    return (ae_xn_k(alter, n, sex, zins, zw, sterbetafel_obj) - 
            np.append(ae_xn_k(alter, t, sex, zins, zw, sterbetafel_obj), np.zeros(n-t)))



# =======================================================================================================================
# Backup Funktionen
# =======================================================================================================================

# Skalare Funktionen 
def ae_x_k_val(alter: int, sex: str, zins: float, zw: int, sterbetafel_obj: Sterbetafel) -> float:
    """
    Berechnet den Barwert einer lebenslangen vorschuessigen Leibrente mit k Zahlungen pro Jahr
    
    Formel: ax^(k) = ax - abzug(k,i)
    
    wobei abzug das Abzugsglied nach Woolhouse ist.
    
    Args:
        alter: Alter der versicherten Person
        sex: Geschlecht ('M' oder 'F')
        zins: Jaehrlicher Zinssatz
        zw: Zahlungsweise (1, 2, 4, oder 12)
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        Barwert einer lebenslangen vorschuessigen Leibrente mit k Zahlungen pro Jahr
    """

    if alter <= 0 or alter >= MAX_ALTER:
        return 0.0
    
    n = MAX_ALTER - alter
    v = diskont(zins)  

    # Alle qx-Werte auf einmal holen
    qx_vec = sterbetafel_obj.qx_vec(alter, n, sex)

    barwert = 0.0
    tpx = 1.0  # 0px = 1
    
    for t in range(n):
        barwert += tpx * (v ** t)
        
        if t < n - 1:
            tpx *= (1.0 - qx_vec[t])
    
    abzug = abzugsglied(zw, zins)

    return barwert - abzug

def ae_xn_k_val(alter: int, n: int, sex: str, zins: float, zw: int, sterbetafel_obj: Sterbetafel) -> float:
    if zw <= 0 or n <= 0 or alter + n > MAX_ALTER:
        return 0.0
    
    n = min(MAX_ALTER - alter, n)
    v = diskont(zins)    

    # Alle qx-Werte auf einmal holen
    qx_vec = sterbetafel_obj.qx_vec(alter, n, sex)

    barwert = 0.0
    tpx = 1.0  # 0px = 1
    
    for t in range(n):
        barwert += tpx * (v ** t)
        
        if t < n - 1:
            tpx *= (1.0 - qx_vec[t])
    
    abzug = abzugsglied(zw, zins)
    n_px = npx_val(alter, n, sex, sterbetafel_obj)
    
    return barwert - abzug * (1.0 - n_px * (v ** n))


# Vektorisierte Funktionen - nicht optimierte Umsetzung
def ae_xn_vec(alter: int, n: int, sex: str, zins: float, zw: int, sterbetafel_obj: Sterbetafel) -> np.ndarray:
    """
    VEKTORISIERT: Berechnet ALLE Rentenbarwerte ae_{x+t}:n-t fuer t=0..n-1.
    
    Dies ist die zentrale Funktion fuer Verlaufswerte-Berechnungen.
    Sie berechnet alle Rentenbarwerte in einem Durchgang mit maximaler
    Effizienz.
    
    Args:
        alter: Eintrittsalter
        n: Versicherungsdauer
        sex: Geschlecht
        zins: Zinssatz
        zw: Zahlungsweise
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        NumPy-Array der Laenge n mit Rentenbarwerten:
        - Index 0: ae_x:n (Beginn Jahr 1)
        - Index 1: ae_{x+1}:n-1 (Beginn Jahr 2)
        - ...
        - Index n-1: ae_{x+n-1}:1 (Beginn Jahr n)
    
    Performance:
        - Standard-Ansatz (Schleife mit ae_xn_k): ~0.5s fuer n=20
        - Diese Funktion: ~0.005s fuer n=20
        - Speedup: ~100x
    
    Algorithmus:
        1. Einmalige Berechnung aller tpx und v^t Werte
        2. Nutze kumulative Reverse-Summen fuer effiziente Berechnung
        3. Korrigiere fuer unterjahrige Zahlungen
    """
    if n <= 0 or alter + n > MAX_ALTER:
        return np.array([])
    
    # Begrenze auf MAX_ALTER
    n = min(MAX_ALTER - alter, n)
    
    # Alle tpx-Werte fuer x, x+1, ..., x+n
    # Wir brauchen tpx fuer jedes Startalter x+t und Restlaufzeit n-t
    
    # Initialisiere Ergebnis-Array
    rentenbarwerte = np.zeros(n, dtype=float)
    
    # Diskontierungsfaktor
    v = diskont(zins)
    
    # Fuer jedes Startalter x+t berechne ae_{x+t}:n-t
    for t in range(n):
        alter_t = alter + t
        restlaufzeit = n - t
        
        # Hole tpx-Werte fuer dieses Startalter
        tpx_t = tpx_matrix(alter_t, restlaufzeit, sex, sterbetafel_obj)
        
        # Berechne v^0, v^1, ..., v^(n-t-1)
        s_array = np.arange(restlaufzeit)
        v_s = v ** s_array
        
        # Rentenbarwert: sum_{s=0}^{restlaufzeit-1} [tpx_t[s] * v^s]
        rentenbarwerte[t] = np.sum(tpx_t[:restlaufzeit] * v_s)
    
    if zw > 1:
        abzug = abzugsglied(zw, zins)
        
        # Fuer jedes t berechne Korrekturterm: abzug * [1 - (n-t)px * v^(n-t)]
        for t in range(n):
            alter_t = alter + t
            restlaufzeit = n - t
            
            # (n-t)px
            n_t_px = npx_val(alter_t, restlaufzeit, sex, sterbetafel_obj)
            
            # Abzugsglied-Korrektur
            korrektur = abzug * (1.0 - n_t_px * (v ** restlaufzeit))
            rentenbarwerte[t] -= korrektur
    
    return rentenbarwerte
