"""
Test-Script fuer barwerte package
Testet die versicherungsmathematischen Funktionen mit Beispielwerten
"""

from pathlib import Path
import sys
from dataclasses import dataclass

# Import des barwerte-Packages
from barwerte import (
    Sterbetafel, diskont, npx, nqx, abzugsglied,
    ax, ax_k, axn, axn_k, nax_k,
    nAx, nEx, ag_k,
    MAX_ALTER
)


# =============================================================================
# ZENTRALE TESTKONFIGURATION
# =============================================================================

@dataclass
class TestConfig:
    """
    Zentrale Konfiguration fuer alle Tests.
    
    Alle Testfunktionen verwenden diese Parameter, um konsistente
    und vergleichbare Ergebnisse zu erzielen.
    """
    # Versichertendaten
    alter: int = 40
    sex: str = 'M'
    
    # Sterbetafel
    tafel: str = 'DAV1994T'
    
    # Finanzmathematische Parameter
    zins: float = 0.0175  # 1,75%
    
    # Vertragsdaten
    n: int = 30            # Versicherungsdauer in Jahren
    t: int = 20            # Beitragszahldauer in Jahren (t <= n)
    aufschub: int = 25     # Aufschubzeit fuer aufgeschobene Renten
    
    # Zahlungsweise
    zw: int = 12  # monatlich (1=jaehrlich, 2=halb, 4=viertel, 12=monatlich)
    
    # Versicherungssumme
    vs: float = 100000.00  # EUR
    
    # Pfad zum Sterbetafel-Verzeichnis
    data_dir: str = "C:/Users/chares/Documents/Notebooks/xlsmToPython/data"
    
    def __post_init__(self):
        """Validiert die Parameter nach der Initialisierung."""
        if self.t > self.n:
            raise ValueError(f"Beitragszahldauer t={self.t} darf nicht groesser sein als Versicherungsdauer n={self.n}")
        if self.t <= 0:
            raise ValueError(f"Beitragszahldauer t={self.t} muss positiv sein")
        if self.n <= 0:
            raise ValueError(f"Versicherungsdauer n={self.n} muss positiv sein")
    
    def __str__(self) -> str:
        """Formatierte Ausgabe der Konfiguration."""
        return f"""
Testkonfiguration:
  Alter:                {self.alter}
  Geschlecht:           {self.sex}
  Sterbetafel:          {self.tafel}
  Zinssatz:             {self.zins:.4%}
  Versicherungsdauer:   {self.n} Jahre (n)
  Beitragszahldauer:    {self.t} Jahre (t)
  Aufschubzeit:         {self.aufschub} Jahre
  Zahlungsweise:        {self.zw}x pro Jahr
  Versicherungssumme:   {self.vs:,.2f} EUR
  Data-Verzeichnis:     {self.data_dir}
"""


# Globale Instanz der Testkonfiguration
CONFIG = TestConfig()

# Alternative Szenarien (optional verwendbar)
CONFIG_JUNG = TestConfig(alter=25, n=40, t=40)
CONFIG_ALT = TestConfig(alter=60, n=15, t=10)
CONFIG_WEIBLICH = TestConfig(sex='F')
CONFIG_ABGEKUERZT = TestConfig(n=30, t=10)  # Abgekuerzte Beitragszahlung


def test_grundfunktionen():
    """Testet grundlegende Funktionen (Diskont, Abzugsglied)."""
    print("=" * 70)
    print("TEST 1: Grundfunktionen")
    print("=" * 70)
    
    # Test Diskontierungsfaktor
    v = diskont(CONFIG.zins)
    print(f"\nDiskontierungsfaktor v bei i={CONFIG.zins:.4%}: {v:.8f}")
    print(f"Kontrolle: 1/(1+i) = {1/(1+CONFIG.zins):.8f}")
    
    # Test Abzugsglied
    print("\nAbzugsglied beta(k,i) fuer verschiedene Zahlungsweisen:")
    for zw in [1, 2, 4, 12]:
        beta = abzugsglied(zw, CONFIG.zins)
        print(f"  k={zw:2d} (Zahlungen/Jahr): beta = {beta:.6f}")
    
    print("\n" + "=" * 70)


def test_sterbetafel():
    """Testet Sterbetafel-Funktionalitaet."""
    print("\nTEST 2: Sterbetafel")
    print("=" * 70)
    
    try:
        st = Sterbetafel(CONFIG.tafel, data_dir=CONFIG.data_dir)
        print(f"\nSterbetafel erfolgreich geladen!")
        print(st.info())
        
        # Test qx-Vektor
        n = 5
        qx_vec = st.qx_vec(CONFIG.alter, n, CONFIG.sex)
        print(f"qx-Vektor fuer {n} Jahre ab Alter {CONFIG.alter}:")
        for i, qx in enumerate(qx_vec):
            print(f"  Alter {CONFIG.alter+i}: qx = {qx:.8f}")
        
        return st
        
    except FileNotFoundError as e:
        print(f"\nFEHLER: {e}")
        print("Bitte Pfad in CONFIG.data_dir anpassen!")
        return None
    
    print("\n" + "=" * 70)


def test_ueberlebenswahrscheinlichkeiten(st: Sterbetafel):
    """Testet n-jahrige Ueberlebens- und Sterbewahrscheinlichkeiten."""
    if st is None:
        print("\nTEST 3 uebersprungen (keine Sterbetafel)")
        return
    
    print("\nTEST 3: Ueberlebenswahrscheinlichkeiten")
    print("=" * 70)
    
    print(f"\nParameter: Alter={CONFIG.alter}, Sex={CONFIG.sex}, Tafel={CONFIG.tafel}")
    
    # Test npx fuer verschiedene Laufzeiten
    print("\nn-jahrige Ueberlebenswahrscheinlichkeit npx:")
    for n_jahre in [1, 5, 10, 20, 30]:
        n_px = npx(CONFIG.alter, n_jahre, CONFIG.sex, st)
        print(f"  {n_jahre:2d}px({CONFIG.alter}) = {n_px:.8f} ({n_px*100:.5f}%)")
    
    # Test nqx fuer verschiedene Laufzeiten
    print("\nn-jahrige Sterbewahrscheinlichkeit nqx:")
    for n_jahre in [1, 5, 10, 20, 30]:
        n_qx = nqx(CONFIG.alter, n_jahre, CONFIG.sex, st)
        print(f"  {n_jahre:2d}qx({CONFIG.alter}) = {n_qx:.8f} ({n_qx*100:.5f}%)")
    
    print("\n" + "=" * 70)


def test_leibrenten(st: Sterbetafel):
    """Testet Leibrenten-Barwerte."""
    if st is None:
        print("\nTEST 4 uebersprungen (keine Sterbetafel)")
        return
    
    print("\nTEST 4: Leibrenten-Barwerte")
    print("=" * 70)
    
    print(f"\nParameter: Alter={CONFIG.alter}, Sex={CONFIG.sex}, Tafel={CONFIG.tafel}, Zins={CONFIG.zins:.4%}")
    
    # Test lebenslange Rente
    print("\nLebenslange vorschuessige Leibrente:")
    ax_wert = ax(CONFIG.alter, CONFIG.sex, st, CONFIG.zins)
    print(f"  ax({CONFIG.alter}) = {ax_wert:.6f}")
    
    # Test lebenslange Rente mit unterjahrigen Zahlungen
    print("\nLebenslange Leibrente mit unterjahrigen Zahlungen:")
    for zw in [1, 2, 4, 12]:
        ax_k_wert = ax_k(CONFIG.alter, CONFIG.sex, st, CONFIG.zins, zw)
        print(f"  ax^({zw:2d})({CONFIG.alter}) = {ax_k_wert:.6f}")
    
    # Test temporaere Rente (hier: Beitragszahldauer t)
    print(f"\nTemporaere vorschuessige Leibrente (t={CONFIG.t} Jahre - Beitragszahldauer):")
    axn_wert = axn(CONFIG.alter, CONFIG.t, CONFIG.sex, st, CONFIG.zins)
    print(f"  ax:{CONFIG.t}({CONFIG.alter}) = {axn_wert:.6f}")
    
    # Test temporaere Rente mit unterjahrigen Zahlungen
    print(f"\nTemporaere Leibrente mit unterjahrigen Zahlungen (t={CONFIG.t} Jahre):")
    for zw in [1, 2, 4, 12]:
        axn_k_wert = axn_k(CONFIG.alter, CONFIG.t, CONFIG.sex, st, CONFIG.zins, zw)
        print(f"  ax:{CONFIG.t}^({zw:2d})({CONFIG.alter}) = {axn_k_wert:.6f}")
    
    # Test aufgeschobene Rente
    print(f"\nAufgeschobene Leibrente (Aufschub={CONFIG.aufschub} Jahre, monatlich):")
    nax_k_wert = nax_k(CONFIG.alter, CONFIG.aufschub, CONFIG.sex, st, CONFIG.zins, 12)
    print(f"  {CONFIG.aufschub}|ax^(12)({CONFIG.alter}) = {nax_k_wert:.6f}")
    
    print("\n" + "=" * 70)


def test_versicherungsleistungen(st: Sterbetafel):
    """Testet Barwerte von Versicherungsleistungen."""
    if st is None:
        print("\nTEST 5 uebersprungen (keine Sterbetafel)")
        return
    
    print("\nTEST 5: Versicherungsleistungen")
    print("=" * 70)
    
    print(f"\nParameter: Alter={CONFIG.alter}, Sex={CONFIG.sex}, Tafel={CONFIG.tafel}, Zins={CONFIG.zins:.4%}")
    
    # Test Todesfallversicherung (verwendet Versicherungsdauer n)
    print(f"\nTemporaere Todesfallversicherung (n={CONFIG.n} Jahre - Versicherungsdauer):")
    nAx_wert = nAx(CONFIG.alter, CONFIG.n, CONFIG.sex, st, CONFIG.zins)
    print(f"  Ax:{CONFIG.n}({CONFIG.alter}) = {nAx_wert:.8f}")
    
    # Test Erlebensfallversicherung (verwendet Versicherungsdauer n)
    print(f"\nErlebensfallversicherung (n={CONFIG.n} Jahre - Versicherungsdauer):")
    nEx_wert = nEx(CONFIG.alter, CONFIG.n, CONFIG.sex, st, CONFIG.zins)
    print(f"  Ex:{CONFIG.n}({CONFIG.alter}) = {nEx_wert:.8f}")
    
    # Kontrolle: Ax:n + Ex:n sollte ungefaehr dem Barwert einer gemischten Versicherung entsprechen
    print(f"\nKontrolle (Ax + Ex - gemischte Versicherung):")
    summe = nAx_wert + nEx_wert
    print(f"  Ax:{CONFIG.n} + Ex:{CONFIG.n} = {summe:.8f}")
    
    print("\n" + "=" * 70)


def test_finanzmathematik():
    """Testet rein finanzmathematische Funktionen."""
    print("\nTEST 6: Finanzmathematik (ohne Sterblichkeit)")
    print("=" * 70)
    
    print(f"\nParameter: Laufzeit g={CONFIG.t} Jahre (Beitragszahldauer), Zins={CONFIG.zins:.4%}")
    
    print("\nBarwert endliche vorschuessige Rente:")
    for k in [1, 2, 4, 12]:
        ag_k_wert = ag_k(CONFIG.t, CONFIG.zins, k)
        print(f"  ag^({k:2d}) = {ag_k_wert:.6f}")
    
    print("\n" + "=" * 70)


def test_beispielrechnung(st: Sterbetafel):
    """
    Beispielrechnung: Kapitallebensversicherung wie im Excel-Tarifrechner.
    
    Wichtig: 
    - Versicherungsleistungen (Todesfall, Erlebensfall) verwenden n (Versicherungsdauer)
    - Beitragsbarwert verwendet t (Beitragszahldauer)
    - Bei laufender Beitragszahlung: t = n
    - Bei abgekuerzter Beitragszahlung: t < n
    """
    if st is None:
        print("\nBEISPIELRECHNUNG uebersprungen (keine Sterbetafel)")
        return
    
    print("\nBEISPIELRECHNUNG: Kapitallebensversicherung")
    print("=" * 70)
    
    print(f"\nVertragsdaten:")
    print(f"  Alter:                {CONFIG.alter}")
    print(f"  Geschlecht:           {CONFIG.sex}")
    print(f"  Versicherungsdauer:   {CONFIG.n} Jahre (n)")
    print(f"  Beitragszahldauer:    {CONFIG.t} Jahre (t)")
    print(f"  Versicherungssumme:   {CONFIG.vs:,.2f} EUR")
    print(f"  Zinssatz:             {CONFIG.zins:.4%}")
    print(f"  Tafel:                {CONFIG.tafel}")
    print(f"  Zahlungsweise:        {CONFIG.zw}x pro Jahr (monatlich)")
    
    if CONFIG.t < CONFIG.n:
        print(f"\n  >>> Abgekuerzte Beitragszahlung: Beitraege nur bis Jahr {CONFIG.t}")
    
    # Berechnung Barwerte (pro 1 EUR Versicherungssumme)
    print(f"\nBarwerte (pro 1 EUR Versicherungssumme):")
    print("-" * 70)
    
    # Todesfallleistung (verwendet n - Versicherungsdauer)
    Bxt = nAx(CONFIG.alter, CONFIG.n, CONFIG.sex, st, CONFIG.zins)
    print(f"  Todesfall (Bxt):      {Bxt:.8f}  [ueber n={CONFIG.n} Jahre]")
    
    # Erlebensfallleistung (verwendet n - Versicherungsdauer)
    Bxe = nEx(CONFIG.alter, CONFIG.n, CONFIG.sex, st, CONFIG.zins)
    print(f"  Erlebensfall (Bxe):   {Bxe:.8f}  [nach n={CONFIG.n} Jahren]")
    
    # Beitragsbarwert (verwendet t - Beitragszahldauer)
    Pxt = axn_k(CONFIG.alter, CONFIG.t, CONFIG.sex, st, CONFIG.zins, CONFIG.zw)
    print(f"  Beitrag (Pxt):        {Pxt:.8f}  [ueber t={CONFIG.t} Jahre]")
    
    # Gesamte Leistung
    BzB = Bxt + Bxe
    total_leistung = BzB * CONFIG.vs
    print(f"\nGesamtleistung (BzB = Bxt + Bxe):")
    print(f"  Pro 1 EUR VS:         {BzB:.8f}")
    print(f"  Bei VS={CONFIG.vs:,.0f}:        {total_leistung:,.2f} EUR")
    
    # Aequivalenzprinzip: Beitrag = Leistung / Rentenbarwert
    # Bei reiner Nettoberechnung (ohne Kosten)
    print("\n" + "-" * 70)
    print("Netto-Praemie (Aequivalenzprinzip: Leistung / Beitragsbarwert):")
    print("-" * 70)
    
    # Pro 1 EUR Versicherungssumme
    praemie_pro_euro = BzB / Pxt
    print(f"\nPraemie pro 1 EUR VS:")
    print(f"  {praemie_pro_euro:.10f} EUR/Jahr")
    
    # Bei gegebener Versicherungssumme
    jahrespram = praemie_pro_euro * CONFIG.vs
    print(f"\nJahrespramie bei VS = {CONFIG.vs:,.2f} EUR:")
    print(f"  {jahrespram:,.2f} EUR/Jahr")
    print(f"  gezahlt ueber {CONFIG.t} Jahre")
    
    # Monatsprämie
    monatspraem = jahrespram / 12
    print(f"\nMonatspraemie:")
    print(f"  {monatspraem:,.2f} EUR/Monat")
    print(f"  gezahlt ueber {CONFIG.t * 12} Monate")
    
    # Gesamtbeitrag
    gesamtbeitrag = jahrespram * CONFIG.t
    print(f"\nGesamtbeitrag:")
    print(f"  {gesamtbeitrag:,.2f} EUR (ueber {CONFIG.t} Jahre)")
    
    # Kontrolle: Verhaeltnis Leistung/Beitrag
    verhaeltnis = total_leistung / gesamtbeitrag
    print(f"\nVerhaeltnis Leistung/Gesamtbeitrag:")
    print(f"  {verhaeltnis:.4f} (= Aufzinsung + Sterblichkeitsgewinn)")
    
    print("\n" + "=" * 70)


def main():
    """Hauptfunktion: Fuehrt alle Tests aus."""
    print("\n" + "=" * 70)
    print(" " * 15 + "BARWERTE PACKAGE - TEST-SUITE")
    print("=" * 70)
    
    # Zeige verwendete Testkonfiguration
    print(CONFIG)
    
    # Test 1: Grundfunktionen
    test_grundfunktionen()
    
    # Test 2: Sterbetafel laden
    st = test_sterbetafel()
    
    # Test 3: Ueberlebenswahrscheinlichkeiten
    test_ueberlebenswahrscheinlichkeiten(st)
    
    # Test 4: Leibrenten
    test_leibrenten(st)
    
    # Test 5: Versicherungsleistungen
    test_versicherungsleistungen(st)
    
    # Test 6: Finanzmathematik
    test_finanzmathematik()
    
    # Beispielrechnung
    test_beispielrechnung(st)
    
    print("\n" + "=" * 70)
    print(" " * 20 + "TESTS ABGESCHLOSSEN")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
