# =============================================================================
# Kommutationswerte
# =============================================================================

"""
===============================================================================
Modul: kommutationswerte.py
Zweck: Berechnung versicherungsmathematischer Barwerte mittels Kommutationswerten
       (lx, Dx, Nx, Cx, Mx, Rx)

Diese Implementation nutzt die klassische Kommutationswerte-Methode,
die effizienter ist als die direkte qx-basierte Methode bei vielen Berechnungen.

Migriert von VBA (mKommutationswerte.txt)
===============================================================================
"""

import numpy as np
from typing import Optional, Literal
from barwerte import Sterbetafel

# Konstanten fuer Rundung
RUND_LX = 16
RUND_TX = 16
RUND_DX = 16
RUND_CX = 16
RUND_NX = 16
RUND_MX = 16
RUND_RX = 16
MAX_ALTER = 121  # Abweichend von barwerte.py (dort 123)


class Kommutationswerte:
    """
    Klasse zur Berechnung von Kommutationswerten und darauf basierenden Barwerten.
    
    Die Kommutationswerte-Methode ist die klassische Berechnungsmethode in der
    Versicherungsmathematik. Sie berechnet zunaechst Hilfswerte (lx, Dx, Nx, etc.)
    und ermoeglicht dann sehr effiziente Barwertberechnungen.
    
    Hauptkommutationswerte:
    - lx: Anzahl Lebende im Alter x (bei Radix = 1.000.000)
    - tx: Anzahl Tote zwischen Alter x und x+1
    - Dx: Diskontierte Anzahl Lebende (lx * v^x)
    - Cx: Diskontierte Anzahl Tote (tx * v^(x+1))
    - Nx: Summe aller Dx ab Alter x
    - Mx: Summe aller Cx ab Alter x
    - Rx: Summe aller Mx ab Alter x
    
    Diese Werte werden einmal berechnet und gecacht, wodurch viele
    Barwertberechnungen sehr schnell durchgefuehrt werden koennen.
    """
    
    def __init__(self, sterbetafel: Sterbetafel, zins: float):
        """
        Initialisiert Kommutationswerte-Objekt.
        
        Parameters
        ----------
        sterbetafel : Sterbetafel
            Sterbetafel-Objekt mit qx-Werten
        zins : float
            Rechnungszins (z.B. 0.0175 fuer 1,75%)
        """
        self.sterbetafel = sterbetafel
        self.zins = zins
        self.v = 1.0 / (1.0 + zins) if zins > 0 else 1.0
        
        # Cache fuer berechnete Vektoren (nach Geschlecht)
        self._cache = {}
    
    def _get_cache_key(self, geschlecht: str) -> str:
        """Erzeugt Cache-Schluessel."""
        return f"{geschlecht}_{self.zins}"
    
    def _berechne_lx_vektor(self, geschlecht: str, endalter: Optional[int] = None) -> np.ndarray:
        """
        Berechnet Vektor der lx-Werte (Anzahl Lebende).
        
        Die lx-Werte zeigen, wie viele Personen einer Kohorte von initial
        1.000.000 Personen im jeweiligen Alter noch am Leben sind.
        
        Formel: lx+1 = lx * (1 - qx)
        
        Parameters
        ----------
        geschlecht : str
            'M' oder 'F'
        endalter : int, optional
            Bis zu welchem Alter berechnet werden soll.
            Wenn None, wird bis MAX_ALTER berechnet.
            
        Returns
        -------
        np.ndarray
            Array mit lx-Werten von Alter 0 bis endalter
        """
        grenze = MAX_ALTER if endalter is None else endalter
        
        # Initialisierung: Radix = 1.000.000
        lx = np.zeros(grenze + 1)
        lx[0] = 1_000_000.0
        
        # Iterative Berechnung: lx+1 = lx * (1 - qx)
        for i in range(1, grenze + 1):
            qx_wert = self.sterbetafel.qx(i - 1, geschlecht)
            lx[i] = lx[i - 1] * (1.0 - qx_wert)
            lx[i] = np.round(lx[i], RUND_LX)
        
        return lx
    
    def _berechne_tx_vektor(self, geschlecht: str, endalter: Optional[int] = None) -> np.ndarray:
        """
        Berechnet Vektor der tx-Werte (Anzahl Tote).
        
        tx gibt an, wie viele Personen zwischen Alter x und x+1 sterben.
        
        Formel: tx = lx - lx+1
        
        Parameters
        ----------
        geschlecht : str
            'M' oder 'F'
        endalter : int, optional
            Bis zu welchem Alter berechnet werden soll
            
        Returns
        -------
        np.ndarray
            Array mit tx-Werten von Alter 0 bis endalter-1
        """
        grenze = MAX_ALTER if endalter is None else endalter
        
        # Hole lx-Vektor
        lx = self._berechne_lx_vektor(geschlecht, grenze)
        
        # Berechne tx = lx - lx+1
        tx = np.zeros(grenze)
        for i in range(grenze):
            tx[i] = lx[i] - lx[i + 1]
            tx[i] = np.round(tx[i], RUND_TX)
        
        return tx
    
    def _berechne_Dx_vektor(self, geschlecht: str, endalter: Optional[int] = None) -> np.ndarray:
        """
        Berechnet Vektor der Dx-Werte (diskontierte Anzahl Lebende).
        
        Dx ist die auf den Zeitpunkt 0 diskontierte Anzahl der Lebenden
        im Alter x. Dies ist ein zentraler Wert fuer Leibrentenberechnungen.
        
        Formel: Dx = lx * v^x
        
        Parameters
        ----------
        geschlecht : str
            'M' oder 'F'
        endalter : int, optional
            Bis zu welchem Alter berechnet werden soll
            
        Returns
        -------
        np.ndarray
            Array mit Dx-Werten von Alter 0 bis endalter
        """
        grenze = MAX_ALTER if endalter is None else endalter
        
        # Hole lx-Vektor
        lx = self._berechne_lx_vektor(geschlecht, grenze)
        
        # Berechne Dx = lx * v^x
        Dx = np.zeros(grenze + 1)
        for i in range(grenze + 1):
            Dx[i] = lx[i] * (self.v ** i)
            Dx[i] = np.round(Dx[i], RUND_DX)
        
        return Dx
    
    def _berechne_Cx_vektor(self, geschlecht: str, endalter: Optional[int] = None) -> np.ndarray:
        """
        Berechnet Vektor der Cx-Werte (diskontierte Anzahl Tote).
        
        Cx ist die auf den Zeitpunkt 0 diskontierte Anzahl der zwischen
        Alter x und x+1 Verstorbenen. Dies ist zentral fuer Todesfallversicherungen.
        
        Formel: Cx = tx * v^(x+1)
        
        Parameters
        ----------
        geschlecht : str
            'M' oder 'F'
        endalter : int, optional
            Bis zu welchem Alter berechnet werden soll
            
        Returns
        -------
        np.ndarray
            Array mit Cx-Werten von Alter 0 bis endalter-1
        """
        grenze = MAX_ALTER if endalter is None else endalter
        
        # Hole tx-Vektor
        tx = self._berechne_tx_vektor(geschlecht, grenze)
        
        # Berechne Cx = tx * v^(x+1)
        Cx = np.zeros(grenze)
        for i in range(grenze):
            Cx[i] = tx[i] * (self.v ** (i + 1))
            Cx[i] = np.round(Cx[i], RUND_CX)
        
        return Cx
    
    def _berechne_Nx_vektor(self, geschlecht: str) -> np.ndarray:
        """
        Berechnet Vektor der Nx-Werte (Summe der Dx-Werte).
        
        Nx ist die Summe aller zukuenftigen Dx-Werte ab Alter x.
        Dies ist der zentrale Wert fuer Leibrentenberechnungen.
        
        Formel: Nx = sum(Dx[i] for i >= x)
        Rekursiv: Nx = Dx + Nx+1
        
        Parameters
        ----------
        geschlecht : str
            'M' oder 'F'
            
        Returns
        -------
        np.ndarray
            Array mit Nx-Werten von Alter 0 bis MAX_ALTER
        """
        # Hole Dx-Vektor
        Dx = self._berechne_Dx_vektor(geschlecht, None)
        
        # Berechne Nx rekursiv von hinten
        Nx = np.zeros(MAX_ALTER + 1)
        Nx[MAX_ALTER] = Dx[MAX_ALTER]
        
        for i in range(MAX_ALTER - 1, -1, -1):
            Nx[i] = Nx[i + 1] + Dx[i]
            Nx[i] = np.round(Nx[i], RUND_NX)
        
        return Nx
    
    def _berechne_Mx_vektor(self, geschlecht: str) -> np.ndarray:
        """
        Berechnet Vektor der Mx-Werte (Summe der Cx-Werte).
        
        Mx ist die Summe aller zukuenftigen Cx-Werte ab Alter x.
        Dies ist der zentrale Wert fuer Todesfallversicherungen.
        
        Formel: Mx = sum(Cx[i] for i >= x)
        Rekursiv: Mx = Cx + Mx+1
        
        Parameters
        ----------
        geschlecht : str
            'M' oder 'F'
            
        Returns
        -------
        np.ndarray
            Array mit Mx-Werten von Alter 0 bis MAX_ALTER
        """
        # Hole Cx-Vektor
        Cx = self._berechne_Cx_vektor(geschlecht, None)
        
        # Berechne Mx rekursiv von hinten
        Mx = np.zeros(MAX_ALTER + 1)
        Mx[MAX_ALTER] = Cx[MAX_ALTER - 1] if MAX_ALTER > 0 else 0.0
        
        for i in range(MAX_ALTER - 1, -1, -1):
            Mx[i] = Mx[i + 1] + Cx[i]
            Mx[i] = np.round(Mx[i], RUND_MX)
        
        return Mx
    
    def _berechne_Rx_vektor(self, geschlecht: str) -> np.ndarray:
        """
        Berechnet Vektor der Rx-Werte (Summe der Mx-Werte).
        
        Rx ist die Summe aller zukuenftigen Mx-Werte ab Alter x.
        Wird fuer komplexere Berechnungen verwendet.
        
        Formel: Rx = sum(Mx[i] for i >= x)
        Rekursiv: Rx = Mx + Rx+1
        
        Parameters
        ----------
        geschlecht : str
            'M' oder 'F'
            
        Returns
        -------
        np.ndarray
            Array mit Rx-Werten von Alter 0 bis MAX_ALTER
        """
        # Hole Mx-Vektor
        Mx = self._berechne_Mx_vektor(geschlecht)
        
        # Berechne Rx rekursiv von hinten
        Rx = np.zeros(MAX_ALTER + 1)
        Rx[MAX_ALTER] = Mx[MAX_ALTER]
        
        for i in range(MAX_ALTER - 1, -1, -1):
            Rx[i] = Rx[i + 1] + Mx[i]
            Rx[i] = np.round(Rx[i], RUND_RX)
        
        return Rx
    
    def _get_kommutationswerte(self, geschlecht: str) -> dict:
        """
        Holt alle Kommutationswerte aus dem Cache oder berechnet sie.
        
        Parameters
        ----------
        geschlecht : str
            'M' oder 'F'
            
        Returns
        -------
        dict
            Dictionary mit allen Kommutationswerten (lx, Dx, Nx, Cx, Mx, Rx)
        """
        cache_key = self._get_cache_key(geschlecht)
        
        if cache_key not in self._cache:
            # Berechne alle Werte
            self._cache[cache_key] = {
                'lx': self._berechne_lx_vektor(geschlecht),
                'Dx': self._berechne_Dx_vektor(geschlecht),
                'Nx': self._berechne_Nx_vektor(geschlecht),
                'Cx': self._berechne_Cx_vektor(geschlecht),
                'Mx': self._berechne_Mx_vektor(geschlecht),
                'Rx': self._berechne_Rx_vektor(geschlecht)
            }
        
        return self._cache[cache_key]
    
    # Oeffentliche Methoden fuer einzelne Kommutationswerte
    
    def lx(self, alter: int, geschlecht: str) -> float:
        """
        Gibt lx-Wert fuer gegebenes Alter zurueck.
        
        Parameters
        ----------
        alter : int
            Alter (0 bis MAX_ALTER)
        geschlecht : str
            'M' oder 'F'
            
        Returns
        -------
        float
            lx-Wert (Anzahl Lebende)
        """
        if alter < 0 or alter > MAX_ALTER:
            return 0.0
        
        werte = self._get_kommutationswerte(geschlecht)
        return werte['lx'][alter]
    
    def tx(self, alter: int, geschlecht: str) -> float:
        """
        Gibt tx-Wert fuer gegebenes Alter zurueck.
        
        Parameters
        ----------
        alter : int
            Alter (0 bis MAX_ALTER-1)
        geschlecht : str
            'M' oder 'F'
            
        Returns
        -------
        float
            tx-Wert (Anzahl Tote zwischen Alter x und x+1)
        """
        if alter < 0 or alter >= MAX_ALTER:
            return 0.0
        
        werte = self._get_kommutationswerte(geschlecht)
        return werte['lx'][alter] - werte['lx'][alter + 1]
    
    def Dx(self, alter: int, geschlecht: str) -> float:
        """
        Gibt Dx-Wert fuer gegebenes Alter zurueck.
        
        Parameters
        ----------
        alter : int
            Alter (0 bis MAX_ALTER)
        geschlecht : str
            'M' oder 'F'
            
        Returns
        -------
        float
            Dx-Wert (diskontierte Anzahl Lebende)
        """
        if alter < 0 or alter > MAX_ALTER:
            return 0.0
        
        werte = self._get_kommutationswerte(geschlecht)
        return werte['Dx'][alter]
    
    def Cx(self, alter: int, geschlecht: str) -> float:
        """
        Gibt Cx-Wert fuer gegebenes Alter zurueck.
        
        Parameters
        ----------
        alter : int
            Alter (0 bis MAX_ALTER-1)
        geschlecht : str
            'M' oder 'F'
            
        Returns
        -------
        float
            Cx-Wert (diskontierte Anzahl Tote)
        """
        if alter < 0 or alter >= MAX_ALTER:
            return 0.0
        
        werte = self._get_kommutationswerte(geschlecht)
        return werte['Cx'][alter]
    
    def Nx(self, alter: int, geschlecht: str) -> float:
        """
        Gibt Nx-Wert fuer gegebenes Alter zurueck.
        
        Parameters
        ----------
        alter : int
            Alter (0 bis MAX_ALTER)
        geschlecht : str
            'M' oder 'F'
            
        Returns
        -------
        float
            Nx-Wert (Summe aller Dx ab Alter x)
        """
        if alter < 0 or alter > MAX_ALTER:
            return 0.0
        
        werte = self._get_kommutationswerte(geschlecht)
        return werte['Nx'][alter]
    
    def Mx(self, alter: int, geschlecht: str) -> float:
        """
        Gibt Mx-Wert fuer gegebenes Alter zurueck.
        
        Parameters
        ----------
        alter : int
            Alter (0 bis MAX_ALTER)
        geschlecht : str
            'M' oder 'F'
            
        Returns
        -------
        float
            Mx-Wert (Summe aller Cx ab Alter x)
        """
        if alter < 0 or alter > MAX_ALTER:
            return 0.0
        
        werte = self._get_kommutationswerte(geschlecht)
        return werte['Mx'][alter]
    
    def Rx(self, alter: int, geschlecht: str) -> float:
        """
        Gibt Rx-Wert fuer gegebenes Alter zurueck.
        
        Parameters
        ----------
        alter : int
            Alter (0 bis MAX_ALTER)
        geschlecht : str
            'M' oder 'F'
            
        Returns
        -------
        float
            Rx-Wert (Summe aller Mx ab Alter x)
        """
        if alter < 0 or alter > MAX_ALTER:
            return 0.0
        
        werte = self._get_kommutationswerte(geschlecht)
        return werte['Rx'][alter]
    
    # Barwertberechnungen basierend auf Kommutationswerten
    
    def abzugsglied(self, zw: int) -> float:
        """
        Berechnet Abzugsglied fuer unterjahrige Zahlungen.
        
        Woolhouse-Naeherung 1. Ordnung fuer unterjahrige Zahlungen.
        
        Parameters
        ----------
        zw : int
            Zahlungsweise (1=jaehrlich, 2=halbjaehrlich, 4=vierteljaehrlich, 12=monatlich)
            
        Returns
        -------
        float
            Abzugsglied beta(k, i)
        """
        if zw <= 0 or zw == 1:
            return 0.0
        
        if zw not in [1, 2, 4, 12]:
            return 0.0
        
        beta = 0.0
        for idx in range(zw):
            beta += (idx / zw) / (1.0 + (idx / zw) * self.zins)
        
        beta *= (1.0 + self.zins) / zw
        return beta
    
    def ax_k(self, alter: int, geschlecht: str, zw: int = 1) -> float:
        """
        Barwert lebenslange vorschuessige Leibrente mit k Zahlungen pro Jahr.
        
        Formel mit Kommutationswerten:
        ax^(k) = Nx / Dx - beta(k, i)
        
        Parameters
        ----------
        alter : int
            Eintrittsalter
        geschlecht : str
            'M' oder 'F'
        zw : int
            Zahlungsweise (1, 2, 4, 12)
            
        Returns
        -------
        float
            Barwert der Leibrente
        """
        if zw <= 0:
            return 0.0
        
        Nx_wert = self.Nx(alter, geschlecht)
        Dx_wert = self.Dx(alter, geschlecht)
        
        if Dx_wert == 0:
            return 0.0
        
        return Nx_wert / Dx_wert - self.abzugsglied(zw)
    
    def axn_k(self, alter: int, n: int, geschlecht: str, zw: int = 1) -> float:
        """
        Barwert temporaere vorschuessige Leibrente mit k Zahlungen pro Jahr.
        
        Formel mit Kommutationswerten:
        ax:n^(k) = (Nx - Nx+n) / Dx - beta(k, i) * (1 - Dx+n / Dx)
        
        Parameters
        ----------
        alter : int
            Eintrittsalter
        n : int
            Laufzeit in Jahren
        geschlecht : str
            'M' oder 'F'
        zw : int
            Zahlungsweise (1, 2, 4, 12)
            
        Returns
        -------
        float
            Barwert der temporaeren Leibrente
        """
        if zw <= 0 or n <= 0 or alter + n > MAX_ALTER:
            return 0.0
        
        Nx_wert = self.Nx(alter, geschlecht)
        Nx_n_wert = self.Nx(alter + n, geschlecht)
        Dx_wert = self.Dx(alter, geschlecht)
        Dx_n_wert = self.Dx(alter + n, geschlecht)
        
        if Dx_wert == 0:
            return 0.0
        
        return (Nx_wert - Nx_n_wert) / Dx_wert - \
               self.abzugsglied(zw) * (1.0 - Dx_n_wert / Dx_wert)
    
    def nax_k(self, alter: int, n: int, geschlecht: str, zw: int = 1) -> float:
        """
        Barwert aufgeschobene vorschuessige Leibrente mit k Zahlungen pro Jahr.
        
        Formel mit Kommutationswerten:
        n|ax^(k) = (Dx+n / Dx) * ax+n^(k)
        
        Parameters
        ----------
        alter : int
            Eintrittsalter
        n : int
            Aufschubzeit in Jahren
        geschlecht : str
            'M' oder 'F'
        zw : int
            Zahlungsweise (1, 2, 4, 12)
            
        Returns
        -------
        float
            Barwert der aufgeschobenen Leibrente
        """
        if zw <= 0 or n <= 0 or alter + n > MAX_ALTER:
            return 0.0
        
        Dx_wert = self.Dx(alter, geschlecht)
        Dx_n_wert = self.Dx(alter + n, geschlecht)
        
        if Dx_wert == 0:
            return 0.0
        
        return (Dx_n_wert / Dx_wert) * self.ax_k(alter + n, geschlecht, zw)
    
    def nAx(self, alter: int, n: int, geschlecht: str) -> float:
        """
        Barwert temporaere Todesfallversicherung (Gross-Ax).
        
        Formel mit Kommutationswerten:
        A_x:n = (Mx - Mx+n) / Dx
        
        Parameters
        ----------
        alter : int
            Eintrittsalter
        n : int
            Laufzeit in Jahren
        geschlecht : str
            'M' oder 'F'
            
        Returns
        -------
        float
            Barwert der Todesfallversicherung
        """
        if n <= 0 or alter + n > MAX_ALTER:
            return 0.0
        
        Mx_wert = self.Mx(alter, geschlecht)
        Mx_n_wert = self.Mx(alter + n, geschlecht)
        Dx_wert = self.Dx(alter, geschlecht)
        
        if Dx_wert == 0:
            return 0.0
        
        return (Mx_wert - Mx_n_wert) / Dx_wert
    
    def nEx(self, alter: int, n: int, geschlecht: str) -> float:
        """
        Barwert reine Erlebensfallversicherung (Gross-Ex).
        
        Formel mit Kommutationswerten:
        E_x:n = Dx+n / Dx
        
        Parameters
        ----------
        alter : int
            Eintrittsalter
        n : int
            Laufzeit in Jahren
        geschlecht : str
            'M' oder 'F'
            
        Returns
        -------
        float
            Barwert der Erlebensfallversicherung
        """
        if n <= 0 or alter + n > MAX_ALTER:
            return 1.0 if n <= 0 else 0.0
        
        Dx_wert = self.Dx(alter, geschlecht)
        Dx_n_wert = self.Dx(alter + n, geschlecht)
        
        if Dx_wert == 0:
            return 0.0
        
        return Dx_n_wert / Dx_wert
    
    def ag_k(self, g: int, zw: int = 1) -> float:
        """
        Barwert endliche vorschuessige Rente (ohne Todesfallrisiko).
        
        Rein finanzmathematische Berechnung ohne biometrisches Risiko.
        
        Formel:
        a_g^(k) = (1 - v^g) / (1 - v) - beta(k, i) * (1 - v^g)
        
        Parameters
        ----------
        g : int
            Anzahl Zahlungen
        zw : int
            Zahlungsweise (1, 2, 4, 12)
            
        Returns
        -------
        float
            Barwert der endlichen Rente
        """
        if zw <= 0 or g <= 0:
            return 0.0
        
        if self.zins == 0:
            return float(g)
        
        v_g = self.v ** g
        
        return (1.0 - v_g) / (1.0 - self.v) - self.abzugsglied(zw) * (1.0 - v_g)


# Hilfsfunktionen fuer Kompatibilitaet mit VBA-Namen

def Act_ax_k(alter: int, geschlecht: str, tafel: str, zins: float, k: int) -> float:
    """Wrapper-Funktion fuer Kompatibilitaet mit VBA-Code."""
    sterbetafel = Sterbetafel(tafel)
    komm = Kommutationswerte(sterbetafel, zins)
    return komm.ax_k(alter, geschlecht, k)


def Act_axn_k(alter: int, n: int, geschlecht: str, tafel: str, zins: float, k: int) -> float:
    """Wrapper-Funktion fuer Kompatibilitaet mit VBA-Code."""
    sterbetafel = Sterbetafel(tafel)
    komm = Kommutationswerte(sterbetafel, zins)
    return komm.axn_k(alter, n, geschlecht, k)


def Act_nax_k(alter: int, n: int, geschlecht: str, tafel: str, zins: float, k: int) -> float:
    """Wrapper-Funktion fuer Kompatibilitaet mit VBA-Code."""
    sterbetafel = Sterbetafel(tafel)
    komm = Kommutationswerte(sterbetafel, zins)
    return komm.nax_k(alter, n, geschlecht, k)


def Act_nGrAx(alter: int, n: int, geschlecht: str, tafel: str, zins: float) -> float:
    """Wrapper-Funktion fuer Kompatibilitaet mit VBA-Code."""
    sterbetafel = Sterbetafel(tafel)
    komm = Kommutationswerte(sterbetafel, zins)
    return komm.nAx(alter, n, geschlecht)


def Act_nGrEx(alter: int, n: int, geschlecht: str, tafel: str, zins: float) -> float:
    """Wrapper-Funktion fuer Kompatibilitaet mit VBA-Code."""
    sterbetafel = Sterbetafel(tafel)
    komm = Kommutationswerte(sterbetafel, zins)
    return komm.nEx(alter, n, geschlecht)


def Act_ag_k(g: int, zins: float, k: int) -> float:
    """Wrapper-Funktion fuer Kompatibilitaet mit VBA-Code."""
    # Dummy-Sterbetafel, da ag_k kein biometrisches Risiko hat
    sterbetafel = Sterbetafel("DAV2008_T")
    komm = Kommutationswerte(sterbetafel, zins)
    return komm.ag_k(g, k)

