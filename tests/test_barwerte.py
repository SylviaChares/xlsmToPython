"""
Test-Script fuer barwerte.py
Testet die versicherungsmathematischen Funktionen mit Beispielwerten
"""

from pathlib import Path
import sys
from dataclasses import dataclass
from typing import Optional

# Import des barwerte-Moduls
from barwerte import (
    Sterbetafel, diskont, npx, nqx, abzugsglied,
    ax, ax_k, axn, axn_k, nax_k, maxn_k,
    Axn, nEx, nAx, ag_k,
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
    tafel: str = 'DAV1994_T'
    
    # Finanzmathematische Parameter
    zins: float = 0.0175  # 1,75%
    
    # Vertragsdaten
    t: int = 20             # Beitragszahlungsdauer fuer temporaere Produkte
    n: int = 30             # Versicherungsdauer fuer Beispielrechnung
    aufschub: int = 20      # Aufschubzeit fuer aufgeschobene Renten
    
    # Zahlungsweise
    zw: int = 12  # monatlich (1=jaehrlich, 2=halb, 4=viertel, 12=monatlich)
    
    # Versicherungssumme
    vs: float = 100000.00  # EUR
    
    # Pfad zur Sterbetafel
    tafel_pfad: str = "C:/Users/chares/Documents/Notebooks/xlsmToPython/data/Tafeln.xlsx"
    
    def __str__(self) -> str:
        """Formatierte Ausgabe der Konfiguration."""
        return f"""
Testkonfiguration:
  Alter:                {self.alter}
  Geschlecht:           {self.sex}
  Sterbetafel:          {self.tafel}
  Zinssatz:             {self.zins:.4%}
  Versicherungsdauer:   {self.n} Jahre
  Beitragszahldauer:    {self.t} Jahre
  Aufschubzeit:         {self.aufschub} Jahre
  Zahlungsweise:        {self.zw}x pro Jahr
  Versicherungssumme:   {self.vs:,.2f} EUR
  Tafel-Pfad:           {self.tafel_pfad}
"""


# Globale Instanz der Testkonfiguration
CONFIG = TestConfig()

# Alternative Szenarien (optional verwendbar)
CONFIG_JUNG = TestConfig(alter=25, n=40, t=40)
CONFIG_ALT = TestConfig(alter=60, n=10, t=15)
CONFIG_WEIBLICH = TestConfig(sex='F')


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
    
    # Pfad zur Sterbetafel aus CONFIG
    tafel_pfad = Path(CONFIG.tafel_pfad)
    
    try:
        st = Sterbetafel(tafel_pfad)
        print(f"\nSterbetafel erfolgreich geladen aus: {tafel_pfad}")
        print(f"Verfuegbare Tafeln: {st.verfuegbare_tafeln}")
        
        # Test einzelner qx-Wert mit CONFIG-Parametern
        qx_wert = st.qx(CONFIG.alter, CONFIG.sex, CONFIG.tafel)
        print(f"\nSterbewahrscheinlichkeit qx({CONFIG.alter}) fuer {CONFIG.tafel}_{CONFIG.sex}: {qx_wert:.8f}")
        
        # Test qx-Vektor
        # n = 5
        qx_vec = st.qx_vec(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.tafel)
        print(f"\nqx-Vektor fuer {CONFIG.n} Jahre ab Alter {CONFIG.alter}:")
        for i, qx in enumerate(qx_vec):
            print(f"  Alter {CONFIG.alter+i}: qx = {qx:.8f}")
        
        # Test px-Vektor
        px_vec = st.px_vec(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.tafel)
        print(f"\npx-Vektor fuer {CONFIG.n} Jahre ab Alter {CONFIG.alter}:")
        for i, px in enumerate(px_vec):
            print(f"  Alter {CONFIG.alter+i}: px = {px:.8f}")
        
        return st
        
    except FileNotFoundError:
        print(f"\nFEHLER: Sterbetafel nicht gefunden unter {tafel_pfad}")
        print("Bitte Pfad in CONFIG.tafel_pfad anpassen!")
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
    
    # Test npx fuer verschiedene versicherungsdaueren
    print("\nn-jahrige Ueberlebenswahrscheinlichkeit npx:")
    for m in [1, 5, 10, 20, 30]:
        n_px = npx(CONFIG.alter, m, CONFIG.sex, CONFIG.tafel, st)
        print(f"  {m:2d}px({CONFIG.alter}) = {n_px:.8f} ({n_px*100:.5f}%)")
    
    # Test nqx fuer verschiedene versicherungsdaueren
    print("\nn-jahrige Sterbewahrscheinlichkeit nqx:")
    for m in [1, 5, 10, 20, 30]:
        n_qx = nqx(CONFIG.alter, m, CONFIG.sex, CONFIG.tafel, st)
        print(f"  {m:2d}qx({CONFIG.alter}) = {n_qx:.8f} ({n_qx*100:.5f}%)")
    
    print("\n" + "=" * 70)


def test_leibrenten(st: Sterbetafel):
    """Testet Vorschuessiger Rentenbarwerte."""
    if st is None:
        print("\nTEST 4 uebersprungen (keine Sterbetafel)")
        return
    
    print("\nTEST 4: Leibrenten-Barwerte")
    print("=" * 70)
    
    print(f"\nParameter: Alter={CONFIG.alter}, Sex={CONFIG.sex}, Tafel={CONFIG.tafel}, Zins={CONFIG.zins:.4%}")
    
    # Test lebenslange Rente
    print("\nLebenslanger vorschuessiger Rentenbarwert:")
    ax_wert = ax(CONFIG.alter, CONFIG.sex, CONFIG.tafel, CONFIG.zins, st)
    print(f"  ax({CONFIG.alter}) = {ax_wert:.12f}")
    
    # Test lebenslange Rente mit unterjarhrigen Zahlungen
    print("\nLebenslanger vorschuessiger Rentenbarwert mit unterjaehrigen Zahlungen:")
    for zw in [1, 2, 4, 12]:
        ax_k_wert = ax_k(CONFIG.alter, CONFIG.sex, CONFIG.tafel, CONFIG.zins, zw, st)
        print(f"  ax^({zw:2d})({CONFIG.alter}) = {ax_k_wert:.12f}")
    
    # Test temporaere Rente
    print(f"\nTemporaer vorschuessiger Rentenbarwert fuer eine Laufzeit von n={CONFIG.n} Jahren und anschließend n={CONFIG.t} Jahren:")
    axn_wert = axn(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.tafel, CONFIG.zins, st)
    print(f"  ax:{CONFIG.n}({CONFIG.alter}) = {axn_wert:.12f}")
    axn_wert = axn(CONFIG.alter, CONFIG.t, CONFIG.sex, CONFIG.tafel, CONFIG.zins, st)
    print(f"  ax:{CONFIG.t}({CONFIG.alter}) = {axn_wert:.12f}")
    
    # Test temporaere Rente mit unterjaehrigen Zahlungen
    print(f"\nTemporaer vorschuessiger Rentenbarwert fuer eine Laufzeit mit unterjaehrigen Zahlungen (n={CONFIG.n} Jahre):")
    for zw in [1, 2, 4, 12]:
        axn_k_wert = axn_k(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.tafel, CONFIG.zins, zw, st)
        print(f"  ax:{CONFIG.n}^({zw:2d})({CONFIG.alter}) = {axn_k_wert:.12f}")
    
    # Test aufgeschobene Rente
    print(f"\nAufgeschobener Rentenbarwert (Aufschub={CONFIG.aufschub} Jahre, monatlich):")
    nax_k_wert = nax_k(CONFIG.alter, CONFIG.aufschub, CONFIG.sex, CONFIG.tafel, CONFIG.zins, 1, st)
    print(f"  {CONFIG.aufschub}|ax^(1)({CONFIG.alter}) = {nax_k_wert:.12f}")
    
    # Test temporaere aufgeschobene Rente
    print(f"\nTemporaer aufgeschobener Rentenbarwert (Aufschub={CONFIG.aufschub} Jahre, monatlich):")
    maxn_k_wert = maxn_k(CONFIG.alter, CONFIG.n, CONFIG.aufschub, CONFIG.sex, CONFIG.tafel, CONFIG.zins, 1, st)
    print(f"  {CONFIG.aufschub}|ax{CONFIG.n}^(1)({CONFIG.alter}) = {maxn_k_wert:.12f}")
    
    print("\n" + "=" * 70)


def test_versicherungsleistungen(st: Sterbetafel):
    """Testet Barwerte von Versicherungsleistungen."""
    if st is None:
        print("\nTEST 5 uebersprungen (keine Sterbetafel)")
        return
    
    print("\nTEST 5: Versicherungsleistungen")
    print("=" * 70)
    
    print(f"\nParameter: Alter={CONFIG.alter}, Sex={CONFIG.sex}, Tafel={CONFIG.tafel}, Zins={CONFIG.zins:.4%}")
    
    # Test Todesfallversicherung
    print(f"\nTemporaere Todesfallversicherung (n={CONFIG.n} Jahre):")
    Axn_wert = Axn(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.tafel, CONFIG.zins, st)
    print(f"  Ax:{CONFIG.n}({CONFIG.alter}) = {Axn_wert:.12f}")
    
    # Test Erlebensfallversicherung
    print(f"\nErlebensfallversicherung (n={CONFIG.n} Jahre):")
    nEx_wert = nEx(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.tafel, CONFIG.zins, st)
    print(f"  Ex:{CONFIG.n}({CONFIG.alter}) = {nEx_wert:.12f}")
    
    # Kontrolle: Ax:n + Ex:n sollte ungefaehr dem Barwert einer gemischten Versicherung entsprechen
    print(f"\nKontrolle (Ax + Ex):")
    summe = Axn_wert + nEx_wert
    print(f"  Ax:{CONFIG.n} + Ex:{CONFIG.n} = {summe:.12f}")

    # Test gemischten Versicherung
    print(f"\nTemporaere gemischten Versicherung (n={CONFIG.n} Jahre):")
    nAx_wert = nAx(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.tafel, CONFIG.zins, st)
    print(f"  {CONFIG.n}Ax:({CONFIG.alter}) = {nAx_wert:.12f}")
    
    print("\n" + "=" * 70)


def test_finanzmathematik():
    """Testet rein finanzmathematische Funktionen."""
    print("\nTEST 6: Finanzmathematik (ohne Sterblichkeit)")
    print("=" * 70)
    
    print(f"\nParameter: versicherungsdauer g={CONFIG.n} Jahre, Zins={CONFIG.zins:.4%}")
    
    print("\nBarwert endliche vorschuessige Rente:")
    for k in [1, 2, 4, 12]:
        ag_k_wert = ag_k(CONFIG.n, CONFIG.zins, k)
        print(f"  ag^({k:2d}) = {ag_k_wert:.6f}")
    
    print("\n" + "=" * 70)


def test_beispielrechnung(st: Sterbetafel):
    """
    Beispielrechnung: Kapitallebensversicherung wie im Excel-Tarifrechner.
    Verwendet CONFIG.t fuer realistische KLV-versicherungsdauer.
    """
    if st is None:
        print("\nBEISPIELRECHNUNG uebersprungen (keine Sterbetafel)")
        return
    
    print("\nBEISPIELRECHNUNG: Kapitallebensversicherung")
    print("=" * 70)
    
    print(f"\nVertragsdaten:")
    print(f"  Alter:                {CONFIG.alter}")
    print(f"  Geschlecht:           {CONFIG.sex}")
    print(f"  Versicherungsdauer:   {CONFIG.n} Jahre")
    print(f"  Beitragszahldauer:    {CONFIG.t} Jahre")
    print(f"  Versicherungssumme:   {CONFIG.vs:,.2f} EUR")
    print(f"  Zinssatz:             {CONFIG.zins:.4%}")
    print(f"  Tafel:                {CONFIG.tafel}")
    print(f"  Zahlungsweise:        {CONFIG.zw} (monatlich)")
    
    # Berechnung Barwerte (pro 1 EUR Versicherungssumme)
    print(f"\nBarwerte (pro 1 EUR Versicherungssumme):")

    # Todesfallleistung
    Bxt = Axn(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.tafel, CONFIG.zins, st)
    print(f"  Todesfall (Bxt):      {Bxt:.12f}")
    
    # Erlebensfallleistung
    Bxe = nEx(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.tafel, CONFIG.zins, st)
    print(f"  Erlebensfall (Bxe):   {Bxe:.12f}")
    
    # Beitragsbarwert
    Pxt = axn_k(CONFIG.alter, CONFIG.t, CONFIG.sex, CONFIG.tafel, CONFIG.zins, 1, st)
    print(f"  Beitrag (Pxt):        {Pxt:.12f}")
    
    # Gesamte Leistung
    total_leistung = (Bxt + Bxe) * CONFIG.vs
    print(f"\nGesamte Leistung (Bxt + Bxe) * VS:")
    print(f"  {total_leistung:,.2f} EUR")
    
    # Aequivalenzprinzip: Beitrag = Leistung / Rentenbarwert
    # Bei reiner Nettoberechnung (ohne Kosten)
    beitrag_netto = (Bxt + Bxe) / Pxt
    print(f"\nNetto-Jahresbeitrag (ohne Kosten):")
    print(f"  {beitrag_netto:.12f} EUR pro 1 EUR VS")
    print(f"  {beitrag_netto * CONFIG.vs:,.2f} EUR bei VS = {CONFIG.vs:,.2f} EUR")
    
    beitrag_monatlich = beitrag_netto * CONFIG.vs / 12
    print(f"\nNetto-Monatsbeitrag:")
    print(f"  {beitrag_monatlich:,.2f} EUR")
    
    print("\n" + "=" * 70)


def main():
    """Hauptfunktion: Fuehrt alle Tests aus."""
    print("\n" + "=" * 70)
    print(" " * 15 + "BARWERTE.PY - TEST-SUITE")
    print("=" * 70)
    
    # Zeige verwendete Testkonfiguration
    print(CONFIG)
    
    # Test 1: Grundfunktionen
    #test_grundfunktionen()
    
    # Test 2: Sterbetafel laden
    st = test_sterbetafel()
    
    # Test 3: Ueberlebenswahrscheinlichkeiten
    #test_ueberlebenswahrscheinlichkeiten(st)
    
    # Test 4: Leibrenten
    test_leibrenten(st)
    
    # Test 5: Versicherungsleistungen
    test_versicherungsleistungen(st)
    
    # Test 6: Finanzmathematik
    #test_finanzmathematik()
    
    # Beispielrechnung
    test_beispielrechnung(st)
    
    print("\n" + "=" * 70)
    print(" " * 20 + "TESTS ABGESCHLOSSEN")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()