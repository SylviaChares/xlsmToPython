"""
barwerte - Versicherungsmathematische Barwertberechnungen

Dieses Package enthaelt Funktionen zur Berechnung von:
- Sterbetafeln und Ueberlebenswahrscheinlichkeiten
- Rentenbarwerten
- Leistungsbarwerten
- Finanzmathematischen Grundfunktionen

Verwendung:
    from barwerte import Sterbetafel, ae_x, ae_xn_k, nAe_x, nE_x
    
    st = Sterbetafel("DAV1994T", data_dir="data")
    ae_x_wert = ae_x(40, 'M', 0.0175, st)
"""

# Version
__version__ = "0.1.0"

# Konstanten
from .basisfunktionen import MAX_ALTER

# Sterbetafel
from .sterbetafel import Sterbetafel

# Grundfunktionen
from .basisfunktionen import (
    diskont,
    npx,
    nqx,
    abzugsglied
)

# Rentenbarwerte 
from .rentenbarwerte import (
    ae_x,           # Lebenslanger Rentenbarwert
    ae_x_k,         # Lebenslanger Rentenbarwert mit k Zahlungen pro Jahr
    ae_xn_old,      # Rentenbarwert mit Dauer n
    ae_xn_k_old,    # Rentenbarwert mit Dauer n mit k Zahlungen pro Jahr
    n_ae_x_k,       # Um n Jahre aufgeschobener Rentenbarwert mit k Zahlungen pro Jahr
    m_ae_xn_k       # Um m Jahre aufgeschobener Rentenbarwert mit Dauer n mit k Zahlungen pro Jahr
)

# Leistungsbarwerte 
from .leistungsbarwerte import (
    nAe_x,          # Leistungsbarwert Todesfallleistung
    nE_x,           # Leistungsbarwert Erlebensfallleistung
    Ae_xn           # Leistungsbarwert gemischte Versicherung
)

# Finanzmathematik
from .finanzmathematik import (
    ag_k
)

# Public API
__all__ = [
    # Konstanten
    'MAX_ALTER',
    
    # Klassen
    'Sterbetafel',
    
    # Grundfunktionen
    'diskont',
    'npx',
    'nqx',
    'abzugsglied',
    
    # Rentenbarwerte
    'ae_x',
    'ae_x_k',
    'ae_xn_old',
    'ae_xn_k_old',
    'n_ae_x_k',
    'm_ae_xn_k',
    
    # Leistungsbarwerte
    'nAe_x',
    'nE_x',
    'Ae_xn',
    
    # Finanzmathematik
    'ag_k',
]
