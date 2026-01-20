#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Workspace Diagnostics
Zeigt Informationen über den aktuellen Workspace, Python-Interpreter und installierte Packages
"""

import sys
import os
from pathlib import Path
import subprocess
import platform

# Konfiguriere stdout für UTF-8 (wichtig für Windows)
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def print_section(title):
    """Hilfsfunktion zum Drucken von Sektions-Überschriften"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def get_workspace_info():
    """Ermittelt Workspace-Informationen"""
    print_section("WORKSPACE INFORMATION")
    
    # Aktuelles Arbeitsverzeichnis
    current_dir = Path.cwd()
    print(f"Aktuelles Verzeichnis: {current_dir}")
    
    # Prüfe auf virtuelle Umgebung
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print(f"Virtuelle Umgebung:    {venv_path}")
        venv_name = Path(venv_path).name
        print(f"venv Name:             {venv_name}")
    else:
        print("Virtuelle Umgebung:    Keine aktiv")
    
    # Workspace Root (suche nach .venv im Pfad)
    if venv_path:
        workspace_root = Path(venv_path).parent
        print(f"Workspace Root:        {workspace_root}")

def get_python_info():
    """Zeigt Python-Interpreter Informationen"""
    print_section("PYTHON INTERPRETER")
    
    print(f"Python Version:        {sys.version}")
    print(f"Python Executable:     {sys.executable}")
    print(f"Python Prefix:         {sys.prefix}")
    print(f"Platform:              {platform.platform()}")
    print(f"Architecture:          {platform.machine()}")

def get_installed_packages():
    """Liste alle installierten Packages auf"""
    print_section("INSTALLIERTE PACKAGES")
    
    try:
        # Verwende pip list für eine übersichtliche Darstellung
        # WICHTIG: encoding='utf-8' und errors='replace' für Windows
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        print(result.stdout)
        
        # Zähle Packages
        lines = result.stdout.strip().split('\n')
        # Überspringe Header (erste 2 Zeilen)
        package_count = len(lines) - 2 if len(lines) > 2 else 0
        print(f"\nAnzahl installierter Packages: {package_count}")
        
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Abrufen der Package-Liste: {e}")
    except Exception as e:
        print(f"Unerwarteter Fehler: {type(e).__name__}: {e}")

def check_important_packages():
    """Prüfe auf wichtige Data Science / ML Packages"""
    print_section("WICHTIGE PACKAGES")
    
    important_packages = [
        'numpy',
        'pandas',
        'matplotlib',
        'scipy',
        'scikit-learn',
        'tensorflow',
        'torch',
        'jupyter',
        'notebook',
        'ipykernel'
    ]
    
    print("Status wichtiger Data Science Packages:\n")
    
    for package in important_packages:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package],
                capture_output=True,
                text=True,
                encoding='utf-8',      # Explizites UTF-8 Encoding
                errors='replace',      # Ersetze ungültige Zeichen statt Fehler
                check=True
            )
            
            # WICHTIG: Prüfe ob stdout nicht None ist
            if result.stdout:
                # Extrahiere Version aus der Ausgabe
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':', 1)[1].strip()
                        # Verwende ASCII-Zeichen statt Unicode-Symbole
                        print(f"[OK] {package:20s} Version: {version}")
                        break
            else:
                print(f"[??] {package:20s} [Informationen nicht verfuegbar]")
                
        except subprocess.CalledProcessError:
            # Package ist nicht installiert
            print(f"[--] {package:20s} [nicht installiert]")
        except UnicodeDecodeError as e:
            # Encoding-Fehler abfangen
            print(f"[??] {package:20s} [Encoding-Fehler]")
        except Exception as e:
            # Fange alle anderen Fehler ab
            print(f"[??] {package:20s} [Fehler: {type(e).__name__}]")

def get_vscode_info():
    """Zeigt VSCode-spezifische Informationen"""
    print_section("VSCODE INFORMATIONEN")
    
    # Jupyter Kernel Information
    jupyter_kernel = os.environ.get('JPY_PARENT_PID')
    if jupyter_kernel:
        print(f"Jupyter Kernel aktiv:  Ja (PID: {jupyter_kernel})")
    else:
        print("Jupyter Kernel aktiv:  Nein (oder nicht als Notebook ausgefuehrt)")
    
    # Python Extension Path
    python_path = os.environ.get('PYTHONPATH')
    if python_path:
        print(f"PYTHONPATH:            {python_path}")
    else:
        print("PYTHONPATH:            Nicht gesetzt")

def main():
    """Hauptfunktion"""
    print("\n" + "="*60)
    print("  PYTHON WORKSPACE DIAGNOSTICS v2.0")
    print("="*60)
    
    try:
        import datetime
        print(f"\nDatum/Zeit: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except:
        pass
    
    try:
        get_workspace_info()
    except Exception as e:
        print(f"\n[!!] Fehler bei Workspace-Info: {e}")
    
    try:
        get_python_info()
    except Exception as e:
        print(f"\n[!!] Fehler bei Python-Info: {e}")
    
    try:
        get_vscode_info()
    except Exception as e:
        print(f"\n[!!] Fehler bei VSCode-Info: {e}")
    
    try:
        get_installed_packages()
    except Exception as e:
        print(f"\n[!!] Fehler bei Package-Liste: {e}")
    
    try:
        check_important_packages()
    except Exception as e:
        print(f"\n[!!] Fehler bei Package-Check: {e}")
    
    print("\n" + "="*60)
    print("  DIAGNOSE ABGESCHLOSSEN")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!!] Abgebrochen durch Benutzer")
    except Exception as e:
        print(f"\n[!!] Kritischer Fehler: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
