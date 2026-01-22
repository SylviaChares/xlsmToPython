#!/usr/bin/env python3
"""
VBA-Projekt Binäranalyse für Excel-Dateien (.xlsm, .xlsb)

WARNUNG: Diese Analyse ist UNZUVERLÄSSIG für das Zählen von Modulen!
Sie zeigt nur Textvorkommen im Binärformat.

Verwendung:
    python vba_binary_analysis.py Tarifrechner_KLV_neu.xlsb
"""

import sys
import zipfile
import os
from pathlib import Path


def analyze_xlsb_structure(filepath):
    """Analysiert die Struktur einer .xlsb Datei"""
    print("="*80)
    print(f"ANALYSE: {os.path.basename(filepath)}")
    print("="*80)
    print()
    
    # Prüfe ob Datei existiert
    if not os.path.exists(filepath):
        print(f"FEHLER: Datei nicht gefunden: {filepath}")
        return
    
    # Zeige Dateigröße
    size = os.path.getsize(filepath)
    print(f"Dateigröße: {size:,} Bytes ({size/1024:.1f} KB)")
    print()
    
    # Öffne als ZIP
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            print("INHALT DER XLSB-DATEI:")
            print("-" * 80)
            
            # Liste alle Dateien
            for info in zf.infolist():
                if 'vbaProject' in info.filename:
                    print(f">>> {info.filename:50s} {info.file_size:>10,} Bytes  *** VBA ***")
                elif info.filename.startswith('xl/worksheets/'):
                    print(f"    {info.filename:50s} {info.file_size:>10,} Bytes")
                elif info.filename.endswith('.xml'):
                    print(f"    {info.filename:50s} {info.file_size:>10,} Bytes")
            
            print()
            
            # Extrahiere vbaProject.bin
            if 'xl/vbaProject.bin' in zf.namelist():
                print("VBA-PROJEKT GEFUNDEN!")
                print("-" * 80)
                
                vba_data = zf.read('xl/vbaProject.bin')
                print(f"VBA-Projekt Größe: {len(vba_data):,} Bytes")
                print()
                
                # Header prüfen
                header = vba_data[:8]
                print(f"Header: {header.hex()}")
                if header.hex().startswith('d0cf11e0'):
                    print("Format: OLE2 (Compound File Binary Format)")
                print()
                
                # Suche nach Text-Strings
                analyze_vba_strings(vba_data)
            else:
                print("KEIN VBA-Projekt gefunden (keine Makros)")
                
    except zipfile.BadZipFile:
        print("FEHLER: Keine gültige ZIP-Datei (xlsb ist beschädigt)")
    except Exception as e:
        print(f"FEHLER: {e}")


def analyze_vba_strings(vba_data):
    """Analysiert Text-Strings im VBA-Projekt"""
    print("TEXT-STRING ANALYSE (UNZUVERLÄSSIG!):")
    print("-" * 80)
    print("WARNUNG: Diese Methode findet:")
    print("  - Modulnamen")
    print("  - Kommentare")
    print("  - String-Literale")
    print("  - Historische/gelöschte Reste")
    print()
    
    # Konvertiere zu String (mit Fehlerbehandlung)
    try:
        text = vba_data.decode('latin-1', errors='ignore')
    except:
        text = str(vba_data)
    
    # Suche nach potentiellen Modulnamen
    print("Gefundene Strings mit 'm' am Anfang (mögliche Module):")
    lines = text.split('\n')
    module_candidates = set()
    
    for line in lines:
        words = line.split()
        for word in words:
            # Suche Wörter die mit 'm' beginnen und plausibel sind
            if word.startswith('m') and len(word) > 3 and word[1].isupper():
                clean = ''.join(c for c in word if c.isalnum() or c == '_')
                if len(clean) > 3:
                    module_candidates.add(clean)
    
    for candidate in sorted(module_candidates):
        count = text.count(candidate)
        print(f"  {candidate:30s} {count:3d}x gefunden")
    
    print()
    
    # Suche nach Funktionspräfixen
    print("Funktionspräfixe:")
    prefixes = ['Act_', 'qx_', 'Public Function', 'Private Function']
    for prefix in prefixes:
        count = vba_data.count(prefix.encode('latin-1'))
        print(f"  {prefix:20s} {count:3d}x")
    
    print()
    
    # Zeige Kontext um wichtige Begriffe
    print("KONTEXT-ANALYSE für 'mBarwerte_qx':")
    print("-" * 80)
    
    search_term = 'mBarwerte_qx'
    if search_term in text:
        idx = text.find(search_term)
        # Zeige 200 Zeichen vor und nach
        start = max(0, idx - 200)
        end = min(len(text), idx + 200)
        context = text[start:end]
        
        # Bereinige Ausgabe
        context = context.replace('\x00', ' ')
        context = ''.join(c if c.isprintable() or c == '\n' else '·' for c in context)
        
        print("Kontext (200 Zeichen vor/nach):")
        print(context)
        print()
        
        # Prüfe ob es ein Kommentar ist
        if "' Modul:" in context or "Modul:" in context:
            print(">>> INTERPRETATION: Dies sieht aus wie ein KOMMENTAR-Header!")
            print(">>> mBarwerte_qx ist wahrscheinlich KEIN separates Modul,")
            print(">>> sondern nur eine Dokumentation im Code.")
    else:
        print(f"'{search_term}' nicht gefunden")
    
    print()


def main():
    print(sys.argv)
    if len(sys.argv) < 2:
        print("Verwendung: python vba_binary_analysis.py <Excel-Datei.xlsb>")
        print()
        print("Beispiel:")
        print("  python vba_binary_analysis.py Tarifrechner_KLV_neu.xlsb")
        sys.exit(1)
    
    filepath = sys.argv[1]
    analyze_xlsb_structure(filepath)
    
    print()
    print("="*80)
    print("FAZIT:")
    print("="*80)
    print("Diese Binäranalyse kann NICHT zuverlässig zählen, wie viele Module")
    print("tatsächlich existieren!")
    print()
    print("Um die echte Modulanzahl zu ermitteln:")
    print("  1. Excel öffnen")
    print("  2. Alt+F11 drücken (VBA-Editor)")
    print("  3. Im Projekt-Explorer die Module zählen")
    print()
    print("Alternative: VBA-Code in .bas-Dateien exportieren")
    print("  - Im VBA-Editor: Rechtsklick auf Modul -> Datei exportieren")
    print("  - Dann .bas-Dateien direkt analysieren")
    print()


if __name__ == '__main__':
    main()
