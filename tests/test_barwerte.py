"""
Test-Script fuer barwerte package
Testet die versicherungsmathematischen Funktionen mit Beispielwerten
"""

from pathlib import Path
import sys

print("=" * 60)
print("DEBUG: Import-Diagnose")
print("=" * 60)

script_dir = Path(__file__).parent
parent_dir = script_dir.parent

print(f"Script liegt in: {script_dir}")
print(f"Parent-Dir ist:  {parent_dir}")
print(f"barwerte/ sollte sein in: {parent_dir / 'barwerte'}")
print(f"Existiert? {(parent_dir / 'barwerte').exists()}")
print()

# WICHTIG: Füge Parent-Verzeichnis zum Python-Pfad hinzu
# Damit Python das barwerte-Package finden kann
sys.path.insert(0, str(parent_dir))
print(f"sys.path[0] ist jetzt: {sys.path[0]}")
print()

# Test: Kann barwerte importiert werden?
try:
    import barwerte
    print(f"✓ 'import barwerte' funktioniert!")
    print(f"  Geladen von: {barwerte.__file__}")
    print(f"  Enthält: {[x for x in dir(barwerte) if not x.startswith('_')][:5]}...")
except Exception as e:
    print(f"✗ 'import barwerte' fehlgeschlagen: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 60)
print()


from dataclasses import dataclass

# Import des barwerte-Packages
#import barwerte as bw
import barwerte.sterbetafel as rgl
import barwerte.basisfunktionen as bf
import barwerte.leistungsbarwerte as lbw
import barwerte.rentenbarwerte as rbw
import barwerte.finanzmathematik as fin


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
    v = bf.diskont(CONFIG.zins)
    print(f"\nDiskontierungsfaktor v bei i={CONFIG.zins:.4%}: {v:.8f}")
    print(f"Kontrolle: 1/(1+i) = {1/(1+CONFIG.zins):.12f}")
    
    # Test Abzugsglied
    print("\nAbzugsglied beta(k,i) fuer verschiedene Zahlungsweisen:")
    for zw in [1, 2, 4, 12]:
        abzug = bf.abzugsglied(zw, CONFIG.zins)
        print(f"  k={zw:2d} (Zahlungen/Jahr): abzug = {abzug:.6f}")
    
    print("\n" + "=" * 70)


def test_sterbetafel():
    """Testet Sterbetafel-Funktionalitaet."""
    print("\nTEST 2: Sterbetafel")
    print("=" * 70)
    
    try:
        st = rgl.Sterbetafel(CONFIG.tafel, data_dir=CONFIG.data_dir)
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


def test_ueberlebenswahrscheinlichkeiten(st: rgl.Sterbetafel):
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
        n_px = bf.npx(CONFIG.alter, n_jahre, CONFIG.sex, st)
        print(f"  {n_jahre:2d}px({CONFIG.alter}) = {n_px:.8f}")
    
    # Test nqx fuer verschiedene Laufzeiten
    print("\nn-jahrige Sterbewahrscheinlichkeit nqx:")
    for n_jahre in [1, 5, 10, 20, 30]:
        n_qx = bf.nqx(CONFIG.alter, n_jahre, CONFIG.sex, st)
        print(f"  {n_jahre:2d}qx({CONFIG.alter}) = {n_qx:.8f}")
    
    print("\n" + "=" * 70)


def test_rentenbarwerte(st: rgl.Sterbetafel):
    """Testet Rentenbarwerte"""
    if st is None:
        print("\nTEST 4 uebersprungen (keine Sterbetafel)")
        return
    
    print("\nTEST 4: Rentenbarwerte")
    print("=" * 70)
    
    print(f"\nParameter: Alter={CONFIG.alter}, Sex={CONFIG.sex}, Tafel={CONFIG.tafel}, Zins={CONFIG.zins:.4%}")
    
    # Test lebenslanger Rentenbarwerte
    print(f"\nLebenslanger vorschuessige Rentenbarwerte zu Alter {CONFIG.alter}:")
    ax_wert = rbw.ae_x(CONFIG.alter, CONFIG.sex, CONFIG.zins, st)
    print(f"  ae_{CONFIG.alter} = {ax_wert:.12f}")
    
    # Test lebenslange Rente mit unterjahrigen Zahlungen
    print(f"\nLebenslanger vorschuessige Rentenbarwerte zu Alter {CONFIG.alter} mit unterjahrigen Zahlungen:")
    for zw in [1, 2, 4, 12]:
        ax_k_wert = rbw.ae_x_k(CONFIG.alter, CONFIG.sex, CONFIG.zins, zw, st)
        print(f"  ae^({zw:2d})_{CONFIG.alter} = {ax_k_wert:.12f}")
    
    # Test temporaere Rente (hier: Beitragszahldauer t)
    print(f"\n1. Temporaerer vorschuessiger Rentenbarwerte ueber t={CONFIG.t} Jahre:")
    axn_wert = rbw.ae_xn_old(CONFIG.alter, CONFIG.t, CONFIG.sex, CONFIG.zins, st)
    print(f"  ae_{CONFIG.alter},{CONFIG.t} = {axn_wert:.12f}")

    # Test temporaere Rente (hier: Beitragszahldauer t) 2
    setup = bf.verlaufswerte_setup(40, 20, 'M', 0.0175, st)
    print(f"\n2. Temporaerer vorschuessiger Rentenbarwerte ueber t={CONFIG.t} Jahre:")
    axn_wert = rbw.ae_xn_vec(setup)
    print(f"  ae_{CONFIG.alter},{CONFIG.t} = {axn_wert:.12f}")
    
    # Test temporaere Rente mit unterjahrigen Zahlungen
    print(f"\nTemporaerer vorschuessiger Rentenbarwerte ueber t={CONFIG.t} Jahre mit unterjahrigen Zahlungen:")
    for zw in [1, 2, 4, 12]:
        axn_k_wert = rbw.ae_xn_k_old(CONFIG.alter, CONFIG.t, CONFIG.sex, CONFIG.zins, zw, st)
        print(f"  ae^({zw:2d}_{CONFIG.alter},{CONFIG.t} = {axn_k_wert:.12f}")
    
    # Barwert einer temporaeren um m Jahre aufgeschobenen lebenslangen vorschuessigen Leibrente
    print(f"\nBarwert einer temporaeren um {CONFIG.aufschub} Jahre aufgeschobenen lebenslangen vorschuessigen Leibrente:")
    nax_k_wert = rbw.n_ae_x_k(CONFIG.alter, CONFIG.aufschub, CONFIG.sex, CONFIG.zins, 1, st)
    print(f"  {CONFIG.aufschub}|ae^(1)_{CONFIG.alter} = {nax_k_wert:.12f}")
    
    # Test Barwert einer temporaeren um m Jahre aufgeschobenen vorschuessigen Leibrente ueber n Jahre
    print(f"\nBarwert einer temporaeren um {CONFIG.aufschub} Jahre aufgeschobenen vorschuessigen Leibrente ueber {CONFIG.aufschub} Jahre:")
    nax_k_wert = rbw.m_ae_xn_k(CONFIG.alter, CONFIG.n, CONFIG.aufschub, CONFIG.sex, CONFIG.zins, 1, st)
    print(f"  {CONFIG.aufschub}|ae^(1)_{CONFIG.alter},{CONFIG.n} = {nax_k_wert:.12f}")
    
    print("\n" + "=" * 70)


def test_leistungsbarwerte(st: rgl.Sterbetafel):
    """Testet Leistungsbarwerte"""
    if st is None:
        print("\nTEST 5 uebersprungen (keine Sterbetafel)")
        return
    
    print("\nTEST 5: Leistungsbarwerte")
    print("=" * 70)
    
    print(f"\nParameter: Alter={CONFIG.alter}, Sex={CONFIG.sex}, Tafel={CONFIG.tafel}, Zins={CONFIG.zins:.4%}")
    
    # Test Leistungsbarwert einer konstanten Todesfallleistung der Hoehe 1 mit Eintrittsalter x und Versicherungsdauer n
    print(f"\nLeistungsbarwert einer konstanten Todesfallleistung der Hoehe 1 mit Eintrittsalter {CONFIG.alter} und Versicherungsdauer {CONFIG.n}:")
    nAx_wert = lbw.nAe_x(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.zins, st)
    print(f"  {CONFIG.n}Ae_{CONFIG.alter} = {nAx_wert:.12f}")
    
    # Test Leistungsbarwert einer Erlebensfallleistung der Hoehe 1 mit Eintrittsalter alter und Versicherungsdauer n
    print(f"\nLeistungsbarwert einer Erlebensfallleistung der Hoehe 1 mit Eintrittsalter {CONFIG.alter} und Versicherungsdauer {CONFIG.n}")
    nEx_wert = lbw.nE_x(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.zins, st)
    print(f"  {CONFIG.n}E_{CONFIG.alter} = {nEx_wert:.12f}")

    # Test Leistungsbarwert einer gemischten Kapitallebensversicherung der Hoehe 1 mit Eintrittsalter alter und Versicherungsdauer n
    print(f"\nLeistungsbarwert einer gemischten Kapitallebensversicherung der Hoehe 1 mit Eintrittsalter {CONFIG.alter} und Versicherungsdauer {CONFIG.n}")
    Axn_wert = lbw.Ae_xn(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.zins, st)
    print(f"  Ae_{CONFIG.alter},{CONFIG.n} = {Axn_wert:.12f}")
    
    # Kontrolle: Ax:n + Ex:n sollte ungefaehr dem Barwert einer gemischten Versicherung entsprechen
    print(f"\nKontrolle (Ax + Ex - gemischte Versicherung):")
    summe = nAx_wert + nEx_wert
    print(f"  {CONFIG.n}Ae_{CONFIG.alter} + {CONFIG.n}E_{CONFIG.alter} = {summe:.12f}")
    
    print("\n" + "=" * 70)


def test_finanzmathematik():
    """Testet rein finanzmathematische Funktionen."""
    print("\nTEST 6: Finanzmathematik (ohne Sterblichkeit)")
    print("=" * 70)
    
    print(f"\nParameter: Laufzeit g={CONFIG.t} Jahre (Beitragszahldauer), Zins={CONFIG.zins:.4%}")
    
    print("\nBarwert endliche vorschuessige Rente:")
    for k in [1, 2, 4, 12]:
        ag_k_wert = fin.ag_k(CONFIG.t, CONFIG.zins, k)
        print(f"  ag^({k:2d}) = {ag_k_wert:.12f}")
    
    print("\n" + "=" * 70)


def test_beispielrechnung(st: rgl.Sterbetafel):
    """
    Beispielrechnung: Kapitallebensversicherung wie im Excel-Tarifrechner.
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
    nAe_x_wert = lbw.nAe_x(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.zins, st)
    print(f"  nAe_x:  {nAe_x_wert:.12f}  [ueber n={CONFIG.n} Jahre]")
    
    # Erlebensfallleistung (verwendet n - Versicherungsdauer)
    nE_x_wert = lbw.nE_x(CONFIG.alter, CONFIG.n, CONFIG.sex, CONFIG.zins, st)
    print(f"  nE_x:   {nE_x_wert:.12f}  [nach n={CONFIG.n} Jahren]")
    
    # Beitragsbarwert (verwendet t - Beitragszahldauer)
    bbw = rbw.ae_xn_k(CONFIG.alter, CONFIG.t, CONFIG.sex, CONFIG.zins, 1, st)
    print(f"  Bbw:    {bbw:.12f}  [ueber t={CONFIG.t} Jahre]")
    
    # Gesamte Leistung
    Axn_wert = nAe_x_wert + nE_x_wert
    total_leistung = Axn_wert * CONFIG.vs
    print(f"\nGesamtleistung (Ae_xn = nAe_x + nE_x):")
    print(f"  Pro 1 EUR VS:         {Axn_wert:.12f}")
    print(f"  Bei VS={CONFIG.vs:,.0f}:        {total_leistung:,.2f} EUR")
    
    # Aequivalenzprinzip: Beitrag = Leistung / Rentenbarwert
    # Bei reiner Nettoberechnung (ohne Kosten)
    print("\n" + "-" * 70)
    print("Netto-Praemie (Aequivalenzprinzip: Leistung / Beitragsbarwert):")
    print("-" * 70)
    
    # Pro 1 EUR Versicherungssumme
    praemie_pro_euro = Axn_wert / bbw
    print(f"\nPraemie pro 1 EUR VS:")
    print(f"  {praemie_pro_euro:.12f} EUR/Jahr")
    
    # Bei gegebener Versicherungssumme
    jahrespram = praemie_pro_euro * CONFIG.vs
    print(f"\nJahrespramie bei VS = {CONFIG.vs:,.2f} EUR:")
    print(f"  {jahrespram:,.2f} EUR/Jahr gezahlt ueber {CONFIG.t} Jahre")
    
    # Monatsprämie
    monatspraem = jahrespram / 12 * (1+0.05)
    print(f"\nMonatspraemie:")
    print(f"  {monatspraem:,.2f} EUR/Monat gezahlt ueber {CONFIG.t * 12} Monate mit ratzu = 5%")
    
    # Gesamtbeitrag
    gesamtbeitrag = jahrespram * CONFIG.t
    print(f"\nGesamtbeitrag:")
    print(f"  {gesamtbeitrag:,.2f} EUR (ueber {CONFIG.t} Jahre)")
    
    # Kontrolle: Verhaeltnis Leistung/Beitrag
    verhaeltnis = total_leistung / gesamtbeitrag
    print(f"\nVerhaeltnis Leistung/Gesamtbeitrag:")
    print(f"  {verhaeltnis:.4f} (= Aufzinsung + Sterblichkeitsgewinn)")
    
    print("\n" + "=" * 70)


def test_verlaufswerte(st: rgl.Sterbetafel):
    """
    Beispielrechnung: Verlaufswerte wie im Excel-Tarifrechner.
    """
    if st is None:
        print("\nBEISPIELRECHNUNG uebersprungen (keine Sterbetafel)")
        return
    
    print("\nBEISPIELRECHNUNG: KapitalleVerlaufswertebensversicherung")
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

    print("-" * 70)
    
    # Barwerte
    print("\nBBW:")
    for i in range(CONFIG.t):
        bbw = rbw.ae_xn_k(CONFIG.alter+i, CONFIG.t-i, CONFIG.sex, CONFIG.zins, 1, st)
        print(f"  ae_{CONFIG.alter+i},{CONFIG.t-i}:  {bbw:.12f}")
    
    print("\nnAe_x:")
    for i in range(CONFIG.n):
        nAe_x_wert = lbw.nAe_x(CONFIG.alter+i, CONFIG.n-i, CONFIG.sex, CONFIG.zins, st)
        print(f"  {CONFIG.n-i}Ae_{CONFIG.alter+i}:  {nAe_x_wert:.12f}")

    print("\nnE_x:")
    for i in range(CONFIG.n+1):
        nE_x_wert = lbw.nE_x(CONFIG.alter+i, CONFIG.n-i, CONFIG.sex, CONFIG.zins, st)
        print(f"  {CONFIG.n-i}E_{CONFIG.alter+i}:  {nE_x_wert:.12f}")

    print("\n" + "=" * 70)


def main():
    """Hauptfunktion: Fuehrt alle Tests aus."""
    print("\n" + "=" * 70)
    print(" " * 15 + "BARWERTE PACKAGE - TEST-SUITE")
    print("=" * 70)
    
    # Zeige verwendete Testkonfiguration
    print(CONFIG)
    
    # Test 1: Grundfunktionen
#    test_grundfunktionen()
    
    # Test 2: Sterbetafel laden
    st = test_sterbetafel()
    
    # Test 3: Ueberlebenswahrscheinlichkeiten
#    test_ueberlebenswahrscheinlichkeiten(st)
    
    # Test 4: Leibrenten
    test_rentenbarwerte(st)
    
    # Test 5: Versicherungsleistungen
#    test_leistungsbarwerte(st)
    
    # Test 6: Finanzmathematik
#    test_finanzmathematik()
    
    # Beispielrechnung
#    test_beispielrechnung(st)

    # Verlaufswerte
#    test_verlaufswerte(st)
    
    print("\n" + "=" * 70)
    print(" " * 20 + "TESTS ABGESCHLOSSEN")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
