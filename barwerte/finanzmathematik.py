# =============================================================================
# Rein finanzmathematische Funktionen (ohne Sterblichkeit)
# =============================================================================

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union, Optional

from .basisfunktionen import diskont, abzugsglied

def ag_k(g: int, zins: float, k: int) -> float:
    """
    Berechnet Barwert endliche vorschuessige Rente (ohne Todesfallrisiko).
    Rein finanzmathematische Berechnung fuer g Zahlungen mit k Zahlungen pro Jahr.
    
    Formel: ag^(k) = (1 - v^g) / (1 - v) - abzug(k,i) * (1 - v^g)
    
    Args:
        g: Anzahl Jahre
        zins: Jaehrlicher Zinssatz
        k: Zahlungsweise (1, 2, 4, oder 12)
    
    Returns:
        Barwert der endlichen vorschuessigen Rente
    """
    if k <= 0 or g <= 0:
        return 0.0
    
    if zins == 0:
        return float(g)
    
    v = diskont(zins)
    abzug = abzugsglied(k, zins)
    
    barwert = (1.0 - v ** g) / (1.0 - v) - abzug * (1.0 - v ** g)
    
    return barwert
