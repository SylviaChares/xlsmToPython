# =============================================================================
# Verlaufswerte-Funktionen
# =============================================================================
"""
Modul zur Berechnung versicherungsmathematischer Verlaufswerte.

Verlaufswerte sind zeitabhaengige Barwerte, die fuer jedes Versicherungsjahr
(oder jeden Zeitpunkt) die verbleibenden Verpflichtungen bzw. Ansprueche
darstellen.

Die Implementierung nutzt NumPy-Vektorisierung fuer effiziente Berechnung
aller Verlaufswerte in einem Durchgang.

Abhaengigkeiten:
    - barwerte.sterbetafel: Sterbetafel-Verwaltung
    - barwerte.rentenbarwerte: Rentenbarwert-Berechnungen
    - barwerte.leistungsbarwerte: Leistungsbarwert-Berechnungen
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Any
from dataclasses import dataclass

# Importiere aus dem barwerte-Package
from barwerte.sterbetafel import Sterbetafel, MAX_ALTER
from barwerte import rentenbarwerte as rbw
from barwerte import leistungsbarwerte as lbw


@dataclass
class VerlaufswerteConfig:
    """
    Konfiguration fuer Verlaufswerte-Berechnung.
    
    Attributes:
        alter: Eintrittsalter der versicherten Person
        n: Versicherungsdauer in Jahren
        sex: Geschlecht ('M' oder 'F')
        zins: Jaehrlicher Technischer Zinssatz
        zw: Zahlungsweise (1, 2, 4, 12)
        sterbetafel: Name der Sterbetafel
    """
    alter: int
    n: int
    sex: str
    zins: float
    zw: int
    sterbetafel: str


class Verlaufswerte:
    """
    Klasse zur Berechnung und Verwaltung von Verlaufswerten.
    
    Diese Klasse berechnet die zeitliche Entwicklung verschiedener
    versicherungsmathematischer Barwerte ueber die Vertragslaufzeit.
    
    Berechnete Verlaufswerte:
    - Rentenbarwerte (ae_xn_k): Barwert temporaerer vorschuessiger Leibrente
    - Todesfallbarwerte (nAe_x): Barwert Todesfallleistung
    - Erlebensfallbarwerte (nE_x): Barwert Erlebensfallleistung
    - Weitere nach Bedarf
    
    Die Berechnung erfolgt vektorisiert fuer alle Zeitpunkte gleichzeitig,
    was deutlich effizienter ist als sequentielle for-Schleifen.
    """
    
    def __init__(self, config: VerlaufswerteConfig, sterbetafel_obj: Sterbetafel):
        """
        Initialisiert Verlaufswerte-Objekt.
        
        Args:
            config: Konfigurationsobjekt mit Vertragsparametern
            sterbetafel_obj: Sterbetafel-Objekt fuer Berechnungen
        """
        self.config = config
        self.st = sterbetafel_obj
        
        # Validierung
        if config.alter + config.n > MAX_ALTER:
            raise ValueError(
                f"Alter + Laufzeit ({config.alter} + {config.n}) "
                f"ueberschreitet MAX_ALTER ({MAX_ALTER})"
            )
        
        # Ergebnisse werden hier gespeichert
        self._verlaufswerte: Optional[Dict[str, np.ndarray]] = None
    
    def berechne_rentenbarwerte(self) -> np.ndarray:
        """
        Berechnet Verlauf der Rentenbarwerte ae_x+t,n-t fuer t = 0, 1, ..., n-1.
        
        Dies ist der Barwert einer temporaeren vorschuessigen Leibrente
        zu jedem Zeitpunkt t waehrend der Vertragslaufzeit.
        
        Formel: ae_{x+t}:n-t fuer t = 0, ..., n-1
        
        Returns:
            NumPy-Array mit Rentenbarwerten fuer jedes Versicherungsjahr
            Array-Laenge = n (Index 0 = Beginn Jahr 1, Index n-1 = Beginn Jahr n)
        
        Technische Details:
        - Vektorisierte Berechnung: Alle Alter und Laufzeiten werden
          als Arrays uebergeben, Berechnung erfolgt in einem Durchgang
        - Memory-efficient: Nur ein Array-Durchlauf, keine expliziten Schleifen
        """
        n = self.config.n
        alter_start = self.config.alter
        
        # Erzeuge Arrays fuer Alter und verbleibende Laufzeit
        # t = 0, 1, 2, ..., n-1 (Beginn jedes Versicherungsjahres)
        t_array = np.arange(n)
        alter_array = alter_start + t_array  # Alter zu Beginn Jahr t+1
        restlaufzeit_array = n - t_array     # Verbleibende Laufzeit
        
        # Vektorisierte Berechnung aller Rentenbarwerte
        # HINWEIS: Da ae_xn_k noch nicht vektorisiert ist, nutzen wir
        # hier zunaechst eine List Comprehension. Dies ist deutlich
        # schneller als eine for-Schleife mit print-Ausgaben.
        rentenbarwerte = np.array([
            rbw.ae_xn_k(
                alter=int(alter_array[i]),
                n=int(restlaufzeit_array[i]),
                sex=self.config.sex,
                zins=self.config.zins,
                zw=self.config.zw,
                sterbetafel_obj=self.st
            )
            for i in range(n)
        ])
        
        return rentenbarwerte
    
    def berechne_todesfallbarwerte(self) -> np.ndarray:
        """
        Berechnet Verlauf der Todesfallbarwerte nAe_x+t fuer t = 0, 1, ..., n.
        
        Dies ist der Barwert einer temporaeren Todesfallleistung
        zu jedem Zeitpunkt t waehrend der Vertragslaufzeit.
        
        Formel: (n-t)Ae_{x+t} fuer t = 0, ..., n
        
        Returns:
            NumPy-Array mit Todesfallbarwerten
            Array-Laenge = n+1 (Index 0 = Beginn, Index n = Ende Laufzeit)
        
        Hinweis:
        - Array hat Laenge n+1, da auch der Endzeitpunkt (t=n) relevant ist
        - Bei t=n ist die Restlaufzeit 0, daher nAe_x = 0
        """
        n = self.config.n
        alter_start = self.config.alter
        
        # t = 0, 1, 2, ..., n
        t_array = np.arange(n + 1)
        alter_array = alter_start + t_array
        restlaufzeit_array = n - t_array
        
        # Vektorisierte Berechnung
        todesfallbarwerte = np.array([
            lbw.nAe_x(
                alter=int(alter_array[i]),
                n=int(restlaufzeit_array[i]),
                sex=self.config.sex,
                zins=self.config.zins,
                sterbetafel_obj=self.st
            ) if restlaufzeit_array[i] > 0 else 0.0
            for i in range(n + 1)
        ])
        
        return todesfallbarwerte
    
    def berechne_erlebensfallbarwerte(self) -> np.ndarray:
        """
        Berechnet Verlauf der Erlebensfallbarwerte nE_x+t fuer t = 0, 1, ..., n.
        
        Dies ist der Barwert einer Erlebensfallleistung zu jedem Zeitpunkt t.
        
        Formel: (n-t)E_{x+t} fuer t = 0, ..., n
        
        Returns:
            NumPy-Array mit Erlebensfallbarwerten
            Array-Laenge = n+1
        
        Hinweis:
        - Bei t=n ist die Restlaufzeit 0, daher nE_x = 1.0 (Erleben ist sicher)
        """
        n = self.config.n
        alter_start = self.config.alter
        
        # t = 0, 1, 2, ..., n
        t_array = np.arange(n + 1)
        alter_array = alter_start + t_array
        restlaufzeit_array = n - t_array
        
        # Vektorisierte Berechnung
        erlebensfallbarwerte = np.array([
            lbw.nE_x(
                alter=int(alter_array[i]),
                n=int(restlaufzeit_array[i]),
                sex=self.config.sex,
                zins=self.config.zins,
                sterbetafel_obj=self.st
            ) if restlaufzeit_array[i] > 0 else 1.0
            for i in range(n + 1)
        ])
        
        return erlebensfallbarwerte
    
    def berechne_alle(self) -> Dict[str, np.ndarray]:
        """
        Berechnet alle Verlaufswerte in einem Durchgang.
        
        Dies ist die zentrale Methode, die alle relevanten Verlaufswerte
        berechnet und als Dictionary zurueckgibt.
        
        Returns:
            Dictionary mit folgenden Keys:
            - 'rentenbarwerte': Array der Laenge n
            - 'todesfallbarwerte': Array der Laenge n+1
            - 'erlebensfallbarwerte': Array der Laenge n+1
            - 'zeitpunkte_rente': Array der Zeitpunkte (0, 1, ..., n-1)
            - 'zeitpunkte_leistung': Array der Zeitpunkte (0, 1, ..., n)
        
        Verwendung:
            >>> vw = Verlaufswerte(config, sterbetafel_obj)
            >>> ergebnisse = vw.berechne_alle()
            >>> rentenbarwerte = ergebnisse['rentenbarwerte']
        """
        # Berechne alle Verlaufswerte
        rentenbarwerte = self.berechne_rentenbarwerte()
        todesfallbarwerte = self.berechne_todesfallbarwerte()
        erlebensfallbarwerte = self.berechne_erlebensfallbarwerte()
        
        # Zeitpunkte fuer Indizierung
        zeitpunkte_rente = np.arange(self.config.n)
        zeitpunkte_leistung = np.arange(self.config.n + 1)
        
        # Speichere Ergebnisse
        self._verlaufswerte = {
            'rentenbarwerte': rentenbarwerte,
            'todesfallbarwerte': todesfallbarwerte,
            'erlebensfallbarwerte': erlebensfallbarwerte,
            'zeitpunkte_rente': zeitpunkte_rente,
            'zeitpunkte_leistung': zeitpunkte_leistung
        }
        
        return self._verlaufswerte
    
    def als_dataframe(self) -> pd.DataFrame:
        """
        Gibt Verlaufswerte als pandas DataFrame zurueck.
        
        Dies ist nuetzlich fuer:
        - Uebersichtliche Darstellung
        - Export nach Excel/CSV
        - Weitere Analysen mit pandas
        
        Returns:
            DataFrame mit Spalten:
            - 't': Zeitpunkt (Versicherungsjahr)
            - 'Alter': Alter zu Beginn des Jahres
            - 'Restlaufzeit': Verbleibende Laufzeit
            - 'ae_xn_k': Rentenbarwert
            - 'nAe_x': Todesfallbarwert
            - 'nE_x': Erlebensfallbarwert
        
        Verwendung:
            >>> vw = Verlaufswerte(config, sterbetafel_obj)
            >>> df = vw.als_dataframe()
            >>> df.to_excel("verlaufswerte.xlsx")
        """
        if self._verlaufswerte is None:
            self.berechne_alle()
        
        n = self.config.n
        alter_start = self.config.alter
        
        # Zeitpunkte und zugehoerige Werte
        t_values = np.arange(n + 1)
        alter_values = alter_start + t_values
        restlaufzeit_values = n - t_values
        
        # DataFrame erstellen
        # HINWEIS: Rentenbarwerte haben Laenge n, Leistungsbarwerte Laenge n+1
        # Daher fuellen wir Rentenbarwerte mit NaN am Ende auf
        rentenbarwerte_padded = np.append(
            self._verlaufswerte['rentenbarwerte'],
            np.nan
        )
        
        df = pd.DataFrame({
            't': t_values,
            'Alter': alter_values,
            'Restlaufzeit': restlaufzeit_values,
            'ae_xn_k': rentenbarwerte_padded,
            'nAe_x': self._verlaufswerte['todesfallbarwerte'],
            'nE_x': self._verlaufswerte['erlebensfallbarwerte']
        })
        
        return df
    
    def drucke_verlaufswerte(self, precision: int = 8):
        """
        Gibt Verlaufswerte formatiert auf der Konsole aus.
        
        Args:
            precision: Anzahl Dezimalstellen (default: 8)
        
        Verwendung:
            >>> vw = Verlaufswerte(config, sterbetafel_obj)
            >>> vw.drucke_verlaufswerte(precision=10)
        """
        if self._verlaufswerte is None:
            self.berechne_alle()
        
        print("\n" + "=" * 80)
        print(f"VERLAUFSWERTE - Vertrag: Alter {self.config.alter}, "
              f"Laufzeit {self.config.n} Jahre, {self.config.sex}")
        print("=" * 80)
        
        # Rentenbarwerte
        print(f"\nRentenbarwerte ae_{{x+t}}:{self.config.n}-t "
              f"(Zahlungsweise: {self.config.zw}x jaehrlich):")
        print("-" * 60)
        for t, wert in enumerate(self._verlaufswerte['rentenbarwerte']):
            alter = self.config.alter + t
            restlaufzeit = self.config.n - t
            print(f"  t={t:2d} | Alter {alter:2d} | "
                  f"ae_{{{alter}}}:{restlaufzeit:2d} = {wert:.{precision}f}")
        
        # Todesfallbarwerte
        print(f"\nTodesfallbarwerte (n-t)Ae_{{x+t}}:")
        print("-" * 60)
        for t, wert in enumerate(self._verlaufswerte['todesfallbarwerte']):
            alter = self.config.alter + t
            restlaufzeit = self.config.n - t
            print(f"  t={t:2d} | Alter {alter:2d} | "
                  f"{restlaufzeit:2d}Ae_{{{alter}}} = {wert:.{precision}f}")
        
        # Erlebensfallbarwerte
        print(f"\nErlebensfallbarwerte (n-t)E_{{x+t}}:")
        print("-" * 60)
        for t, wert in enumerate(self._verlaufswerte['erlebensfallbarwerte']):
            alter = self.config.alter + t
            restlaufzeit = self.config.n - t
            print(f"  t={t:2d} | Alter {alter:2d} | "
                  f"{restlaufzeit:2d}E_{{{alter}}} = {wert:.{precision}f}")
        
        print("\n" + "=" * 80)


def berechne_verlaufswerte(
    alter: int,
    n: int,
    sex: str,
    zins: float,
    zw: int,
    sterbetafel_obj
) -> Dict[str, np.ndarray]:
    """
    Convenience-Funktion zur direkten Berechnung von Verlaufswerten.
    
    Dies ist eine vereinfachte Schnittstelle fuer schnelle Berechnungen
    ohne explizite Erstellung von Config-Objekten.
    
    Args:
        alter: Eintrittsalter
        n: Versicherungsdauer
        sex: Geschlecht ('M' oder 'F')
        zins: Technischer Zinssatz
        zw: Zahlungsweise
        sterbetafel_obj: Sterbetafel-Objekt
    
    Returns:
        Dictionary mit allen Verlaufswerten
    
    Beispiel:
        >>> st = Sterbetafel("DAV1994T", "data")
        >>> vw = berechne_verlaufswerte(40, 20, 'M', 0.0175, 1, st)
        >>> print(vw['rentenbarwerte'])
    """
    config = VerlaufswerteConfig(
        alter=alter,
        n=n,
        sex=sex,
        zins=zins,
        zw=zw,
        sterbetafel=""  # Wird nicht benoetigt, da Objekt uebergeben wird
    )
    
    verlaufswerte = Verlaufswerte(config, sterbetafel_obj)
    return verlaufswerte.berechne_alle()


def berechne_reserve(alter: int, n: int, t: int, sex: str, zins: float, 
                     zw: int, sterbetafel_obj: Sterbetafel) -> dict:
    """
    Berechnet Reserveverlauf fuer Versicherung mit t < n
    
    Args:
        alter: Eintrittsalter
        n: Versicherungsdauer
        t: Beitragszahldauer (t <= n)
        sex: Geschlecht
        zins: Zinssatz
        zw: Zahlungsweise
        sterbetafel_obj: Sterbetafel
    
    Returns:
        Dictionary mit Verlaufsvektoren (alle Laenge n)

    Verwendung:
        Rentenbarwerte auf Laenge n erweitert (ab Jahr t nur Nullen)
        rentenbarwerte = ae_xn_verlauf_vec(alter=40, n=20, sex='M', zins=0.0175, zw=12, sterbetafel_obj=tafel, output_length=30)  
    """
    
    # Berechne Verlaufswerte fuer Versicherungsleistungen (Laenge n)
    todesfallleistung = lbw.nAe_x_verlauf_vec(alter, n, sex, zins, sterbetafel_obj)
    erlebensfallleistung = lbw.nE_x_verlauf_vec(alter, n, sex, zins, sterbetafel_obj)
    
    # Berechne Rentenbarwerte nur fuer Beitragszahldauer t (Laenge t)
    rentenbarwerte_t = rbw.ae_xn_verlauf_vec(alter, t, sex, zins, zw, sterbetafel_obj)
    
    # Erweitere Rentenbarwerte mit Nullen auf Laenge n
    # Jahre 0 bis t-1: Rentenbarwerte
    # Jahre t bis n-1: Nullen (keine Beitragszahlung mehr)
    rentenbarwerte_n = np.zeros(n)
    rentenbarwerte_n[:t] = rentenbarwerte_t
    
    # Berechne Nettoprämie (basierend auf Rentenbarwert zu Beginn)
    nettopraemie = (todesfallleistung[0] + erlebensfallleistung[0]) / rentenbarwerte_n[0]
    
    # Berechne Reserve fuer jedes Jahr
    # Reserve = Leistungsbarwert - Praemienbarwert
    reserve = (todesfallleistung + erlebensfallleistung) - nettopraemie * rentenbarwerte_n
    
    return {
        'reserve': reserve,
        'todesfallleistung': todesfallleistung,
        'erlebensfallleistung': erlebensfallleistung,
        'rentenbarwerte': rentenbarwerte_n,
        'nettopraemie': nettopraemie
    }

# =============================================================================
# OPTIMIERUNG: Vektorisierte Basis-Funktionen (fuer zukuenftige Verwendung)
# =============================================================================
# 
# Die folgenden Funktionen zeigen, wie die Barwert-Funktionen selbst
# vektorisiert werden koennten. Dies wuerde die Performance nochmals
# deutlich steigern, erfordert aber Anpassungen in den Basis-Modulen.
# 
# Beispiel fuer vektorisierte Rentenbarwert-Berechnung:
#
# def ae_xn_k_vec(alter_array, n_array, sex, zins, zw, st):
#     """
#     Vektorisierte Berechnung von ae_xn_k fuer mehrere Alter/Laufzeiten.
#     
#     Args:
#         alter_array: NumPy-Array mit Altern
#         n_array: NumPy-Array mit Laufzeiten
#         ... weitere Parameter ...
#     
#     Returns:
#         NumPy-Array mit Rentenbarwerten
#     """
#     # Implementation wuerde komplette Vektorisierung
#     # der inneren Berechnungen erfordern
#     pass
#
# Dies waere der naechste Optimierungsschritt, wenn die Performance
# kritisch wird (z.B. fuer Monte-Carlo-Simulationen).