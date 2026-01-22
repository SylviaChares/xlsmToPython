"""
Modul: sterbetafel.py
Zweck: Verwaltung und Zugriff auf Sterbetafeln (mortality tables)

Sterbetafeln werden aus CSV-Dateien geladen mit der Struktur:
    Alter;qx;qy
    
wobei:
    - Alter: Alter in Jahren (0 bis MAX_ALTER)
    - qx: Sterbewahrscheinlichkeit maennlich
    - qy: Sterbewahrscheinlichkeit weiblich
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union, Optional


# Konstanten
MAX_ALTER = 121  # Maximales Alter fuer Berechnungen


class Sterbetafel:
    """
    Klasse zum Laden und Verwalten von Sterbetafeln (z.B. DAV-Tafeln).
    
    Die Sterbetafel wird beim Initialisieren aus einer CSV-Datei geladen
    und im Speicher gehalten fuer effizienten Zugriff.
    
    CSV-Format:
        Alter;qx;qy
        0;0,002345;0,001876
        1;0,000123;0,000098
        ...
    
    Attribute:
        name (str): Name der Sterbetafel (z.B. 'DAV1994T')
        data (pd.DataFrame): DataFrame mit Spalten 'Alter', 'qx', 'qy'
        min_alter (int): Minimales Alter in der Tafel
        max_alter (int): Maximales Alter in der Tafel
    
    Beispiel:
        >>> st = Sterbetafel("DAV1994T", data_dir="data")
        >>> qx_40 = st.qx(40, 'M')
        >>> print(f"qx(40) = {qx_40:.8f}")
    """
    
    def __init__(self, tafel_name: str, data_dir: Union[str, Path] = "data"):
        """
        Initialisiert Sterbetafel-Objekt durch Laden der CSV-Datei.
        
        Args:
            tafel_name: Name der Sterbetafel (z.B. 'DAV1994T')
                       Dateiname wird automatisch konstruiert: {tafel_name}.csv
            data_dir: Verzeichnis, in dem die CSV-Dateien liegen
        
        Raises:
            FileNotFoundError: Wenn die CSV-Datei nicht gefunden wird
            ValueError: Wenn die CSV-Struktur nicht korrekt ist
        """
        self.name = tafel_name
        self.data_dir = Path(data_dir)
        
        # Konstruiere Dateipfad
        csv_file = self.data_dir / f"{tafel_name}.csv"
        
        if not csv_file.exists():
            raise FileNotFoundError(
                f"Sterbetafel '{tafel_name}' nicht gefunden.\n"
                f"Erwarteter Pfad: {csv_file}\n"
                f"Bitte CSV-Datei mit Format 'Alter;qx;qy' bereitstellen."
            )
        
        # Lade CSV-Datei
        # Beachte: Deutsche CSV-Dateien verwenden oft Komma als Dezimaltrennzeichen
        try:
            data_raw = pd.read_csv(
                csv_file, 
                sep=';',
                decimal=','  # Deutsches Format: Komma als Dezimaltrennzeichen
            )
        except Exception as e:
            raise ValueError(f"Fehler beim Laden von {csv_file}: {e}")
        
        # Validiere Struktur
        expected_columns = ['Alter', 'qx', 'qy']
        if not all(col in data_raw.columns for col in expected_columns):
            raise ValueError(
                f"CSV-Datei {csv_file} hat nicht die erwartete Struktur.\n"
                f"Erwartet: {expected_columns}\n"
                f"Gefunden: {list(data_raw.columns)}"
            )
        
        # WICHTIG: Filtere nur Alter 0 bis MAX_ALTER (121)
        self.data = data_raw[data_raw['Alter'] <= MAX_ALTER].copy()
        
        # Speichere Altersgrenzen
        self.min_alter = int(self.data['Alter'].min())
        self.max_alter = int(self.data['Alter'].max())
        
        # Setze Index auf Alter fuer schnellen Zugriff
        self.data = self.data.set_index('Alter')
        
        # Info-Meldung wenn Daten gefiltert wurden
        anzahl_gesamt = len(data_raw)
        anzahl_geladen = len(self.data)
        if anzahl_gesamt > anzahl_geladen:
            print(f"Info: Von {anzahl_gesamt} Zeilen wurden {anzahl_geladen} geladen "
                  f"(Alter 0-{MAX_ALTER})")
    
    def qx(self, alter: int, sex: str) -> float:
        """
        Gibt Sterbewahrscheinlichkeit qx fuer gegebenes Alter zurueck.
        
        Args:
            alter: Alter der versicherten Person (0 bis MAX_ALTER)
            sex: Geschlecht ('M' = maennlich, 'F' = weiblich)
        
        Returns:
            Sterbewahrscheinlichkeit qx als float
        
        Raises:
            ValueError: Wenn Alter ausserhalb des gueltigen Bereichs
        
        Beispiel:
            >>> st = Sterbetafel("DAV1994T")
            >>> qx_40_m = st.qx(40, 'M')
        """
        # Validiere Alter
        if alter < self.min_alter or alter > self.max_alter:
            raise ValueError(
                f"Alter {alter} ausserhalb des gueltigen Bereichs "
                f"[{self.min_alter}, {self.max_alter}] fuer Tafel '{self.name}'"
            )
        
        # Geschlecht normalisieren
        sex = sex.upper()
        if sex not in ['M', 'F']:
            sex = 'F'  # Default: weiblich
        
        # Waehle richtige Spalte
        spalte = 'qx' if sex == 'M' else 'qy'
        
        # Gebe qx-Wert zurueck
        return float(self.data.loc[alter, spalte])
    
    def qx_vec(self, alter: int, n: int, sex: str) -> np.ndarray:
        """
        Erzeugt Vektor der Sterbewahrscheinlichkeiten qx fuer n Jahre.
        
        Args:
            alter: Startalter
            n: Anzahl Jahre
            sex: Geschlecht ('M' oder 'F')
        
        Returns:
            NumPy-Array mit qx-Werten fuer Alter x bis x+n-1
        
        Beispiel:
            >>> st = Sterbetafel("DAV1994T")
            >>> qx_vec = st.qx_vec(40, 5, 'M')  # qx fuer Alter 40-44
        """
        if n <= 0 or alter + n > self.max_alter:
            return np.array([])
        
        return np.array([self.qx(alter + i, sex) for i in range(n)])
    
    def px_vec(self, alter: int, n: int, sex: str) -> np.ndarray:
        """
        Erzeugt Vektor der Ueberlebenswahrscheinlichkeiten px fuer n Jahre.
        px = 1 - qx
        
        Args:
            alter: Startalter
            n: Anzahl Jahre
            sex: Geschlecht ('M' oder 'F')
        
        Returns:
            NumPy-Array mit px-Werten fuer Alter x bis x+n-1
        
        Beispiel:
            >>> st = Sterbetafel("DAV1994T")
            >>> px_vec = st.px_vec(40, 5, 'M')  # px fuer Alter 40-44
        """
        qx_werte = self.qx_vec(alter, n, sex)
        return 1.0 - qx_werte
    
    def __repr__(self) -> str:
        """String-Repraesentation der Sterbetafel."""
        return (
            f"Sterbetafel('{self.name}', "
            f"Alter: {self.min_alter}-{self.max_alter}, "
            f"Zeilen: {len(self.data)})"
        )
    
    def info(self) -> str:
        """
        Gibt detaillierte Informationen zur Sterbetafel aus.
        
        Returns:
            Formatierter String mit Tafel-Informationen
        """
        info_str = f"""
Sterbetafel: {self.name}
{'=' * 50}
Altersbereich:     {self.min_alter} - {self.max_alter} Jahre
Anzahl Zeilen:     {len(self.data)}
Verzeichnis:       {self.data_dir}

Beispielwerte (Alter 40):
  qx (maennlich):  {self.qx(40, 'M'):.8f}
  qy (weiblich):   {self.qx(40, 'F'):.8f}
"""
        return info_str


def lade_sterbetafel(tafel_name: str, data_dir: Union[str, Path] = "data") -> Sterbetafel:
    """
    Hilfsfunktion zum Laden einer Sterbetafel.
    
    Args:
        tafel_name: Name der Sterbetafel (z.B. 'DAV1994T')
        data_dir: Verzeichnis mit CSV-Dateien
    
    Returns:
        Sterbetafel-Objekt
    
    Beispiel:
        >>> st = lade_sterbetafel("DAV1994T", "data")
    """
    return Sterbetafel(tafel_name, data_dir)


if __name__ == "__main__":
    # Beispiel-Nutzung
    print("Sterbetafel-Modul")
    print("=" * 50)
    
    # Test mit DAV1994T (wenn verfuegbar)
    try:
        st = Sterbetafel("DAV1994T", data_dir="data")
        print(st.info())
        
        # Test qx-Vektor
        print("\nqx-Vektor fuer Alter 40-44 (maennlich):")
        qx_vec = st.qx_vec(40, 5, 'M')
        for i, qx in enumerate(qx_vec):
            print(f"  qx({40+i}) = {qx:.8f}")
            
    except FileNotFoundError as e:
        print(f"Hinweis: {e}")