# Anleitung: Projekt **xlsmToPython** mit Git und GitHub versionieren (für Anfänger)

Diese Anleitung zeigt dir **Schritt für Schritt**, wie du dein zweites VS‑Code‑Projekt

- `C:\Users\chares\Documents\Notebooks\xlsmToPython`

in Git versionierst und auf GitHub sicherst – inklusive eines **sauberen Tagesablaufs** („morgens starten“, „abends sichern“).

> Du nutzt dafür bevorzugt das **Terminal in VS Code** oder **PowerShell**. Git Bash ist ebenfalls möglich, aber nicht nötig.

---

## 0) Grundidee (kurz, damit du das Warum verstehst)

- **Git** speichert Versionen deines Projekts lokal (auf deinem Rechner) als **Commits**.
- **GitHub** ist der entfernte Speicherort (**Remote**), auf den du deine Commits per **push** hochlädst.
- Du arbeitest normalerweise so:
  1. Ordner öffnen  
  2. Änderungen machen  
  3. Änderungen **committen** (lokal sichern)  
  4. **push** (auf GitHub sichern)

---

## 1) Wichtig: Soll es ein eigenes GitHub-Repository werden oder in ein bestehendes?

Du hast bereits ein Repo auf GitHub:  
`mein-erstes-projekt` (Remote: `https://github.com/SylviaChares/mein-erstes-projekt.git`).

Für ein **zweites, separates Projekt** empfehle ich als Anfänger fast immer:

### Empfehlung: **Eigenes Repository pro Projekt**
- Vorteil: sauber getrennt, übersichtlicher, weniger Verwechslungsgefahr.
- Ergebnis: z. B. `https://github.com/SylviaChares/xlsmToPython`

### Alternative: Beide Projekte in *einem* Repository (Monorepo)
- Nur sinnvoll, wenn beide Projekte eng zusammengehören.
- Dann wäre `xlsmToPython` ein Unterordner in `mein-erstes-projekt`.

> In der Anleitung unten mache ich **die empfohlene Variante: eigenes Repository**.  
> Am Ende findest du auch kurz die **Alternative (Monorepo)**.

---

## 2) Einmalig: Projekt lokal als Git-Repository initialisieren

### 2.1 VS Code öffnen
1. Öffne VS Code
2. **Datei → Ordner öffnen…**
3. Wähle: `C:\Users\chares\Documents\Notebooks\xlsmToPython`

### 2.2 Terminal öffnen
In VS Code:
- **Terminal → Neues Terminal**

### 2.3 Prüfen, dass du im richtigen Ordner bist
Im Terminal:

```powershell
pwd
```

Die Ausgabe soll auf den Projektordner zeigen, z. B.:

`C:\Users\chares\Documents\Notebooks\xlsmToPython`

Wenn nicht, wechsle dorthin:

```powershell
cd C:\Users\chares\Documents\Notebooks\xlsmToPython
```

---

## 3) Einmalig: Git initialisieren und ersten Commit machen

### 3.1 Git initialisieren
```powershell
git init
```

Erklärung:
- Dadurch entsteht ein versteckter Ordner `.git`. Dort speichert Git alle Versionen.

### 3.2 Prüfen, ob alles ok ist
```powershell
git status
```

Du wirst vermutlich viele „untracked files“ sehen (das ist normal – Git kennt die Dateien noch nicht).

### 3.3 Eine `.gitignore` anlegen (sehr wichtig)
Eine `.gitignore` sagt Git, welche Dateien **nicht** versioniert werden sollen (z. B. temporäre Dateien, virtuelle Umgebungen, große Artefakte).

Erstelle im Projektordner eine Datei namens `.gitignore`.

In PowerShell:

```powershell
notepad .gitignore
```

Füge z. B. folgenden Inhalt ein (Startpunkt für Python + VS Code + typische Artefakte):

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.venv/
venv/
ENV/
*.egg-info/

# Jupyter
.ipynb_checkpoints/

# VS Code
.vscode/

# OS
.DS_Store
Thumbs.db

# Logs / temp
*.log
*.tmp

# Optional: große Daten/Exportdateien (nur falls du sie NICHT versionieren willst)
# *.xlsx
# *.xlsm
# *.csv
```

Wichtig zu Excel-Dateien:
- **Exceldateien kannst du grundsätzlich versionieren**, aber sie sind binär (Git kann Unterschiede nicht gut anzeigen).
- Wenn sie **groß** sind oder sich oft ändern, ist das unpraktisch.
- Wenn du sie brauchst (z. B. als Testdaten), kannst du sie trotzdem committen – oder später Git LFS nutzen.

> Empfehlung als Anfänger:  
> - Kleine Excel-Testdateien: ok zu committen  
> - Große/oft wechselnde Excel-Dateien: eher ignorieren oder mit LFS

### 3.4 Dateien zum Commit vormerken („stagen“)
```powershell
git add .
```

Erklärung:
- Damit sagst du: „Diese aktuellen Dateistände sollen in den nächsten Commit.“

### 3.5 Ersten Commit erstellen
```powershell
git commit -m "Initial commit"
```

Erklärung:
- Ein **Commit** ist ein sauberer Versions-Schnappschuss.

---

## 4) Einmalig: Neues Repository auf GitHub erstellen und verbinden

### 4.1 Repository auf GitHub erstellen
Auf GitHub (im Browser):
1. „New repository“ erstellen
2. Name: **xlsmToPython**
3. **Public/Private** nach Wunsch
4. Wichtig: **NICHT** zusätzlich README/.gitignore/Licence automatisch erstellen (weil du schon lokal committet hast)

### 4.2 Remote „origin“ setzen
Zurück im Terminal im Projektordner:

```powershell
git remote add origin https://github.com/SylviaChares/xlsmToPython.git
```

Wenn du dir beim Link unsicher bist: er steht auf GitHub im neuen Repo (Code → HTTPS).

### 4.3 Standard-Branch auf `main` setzen (falls nötig)
Manchmal heißt der lokale Branch nach `git init` noch `master`. Prüfe:

```powershell
git branch
```

Wenn du `master` siehst und `main` möchtest:

```powershell
git branch -M main
```

### 4.4 Erstes Push zu GitHub
```powershell
git push -u origin main
```

Erklärung:
- `push` lädt deine Commits auf GitHub.
- `-u` merkt sich, dass `main` künftig standardmäßig nach `origin/main` gepusht wird.

---

## 5) Täglicher Arbeitsablauf (morgens starten)

Wenn du am nächsten Tag weiterarbeiten willst, machst du in der Regel:

### 5.1 Projekt öffnen
- VS Code öffnen → Ordner `xlsmToPython` öffnen

### 5.2 Prüfen, ob du auf dem aktuellen Stand bist
Im Terminal:

```powershell
git status
```

Wenn alles sauber ist, steht da sinngemäß „working tree clean“.

### 5.3 Änderungen vom Remote holen (falls du auf mehreren Geräten arbeitest)
Wenn du **nur** auf diesem Rechner arbeitest, ist das oft unnötig.  
Wenn du sicher sein willst:

```powershell
git pull
```

Erklärung:
- Holt Änderungen von GitHub, falls dort neuere Commits liegen.

---

## 6) Täglicher Arbeitsablauf (abends sichern)

Das ist der wichtigste Teil: **Sauber committen und pushen**, bevor du Schluss machst.

### 6.1 Prüfen, was sich geändert hat
```powershell
git status
```

Du siehst z. B.:
- „modified“ (geändert)
- „new file“ (neu)
- „untracked“ (neu, noch nicht hinzugefügt)

Optional hilfreich:

```powershell
git diff
```

Erklärung:
- Zeigt Text-Änderungen im Detail (bei Binärdateien wie Excel geht das nicht).

### 6.2 Änderungen stagen
Wenn du alles sichern willst:

```powershell
git add .
```

Wenn du nur bestimmte Dateien sichern willst:

```powershell
git add pfad\zur\datei.py
```

### 6.3 Commit machen (mit sinnvoller Nachricht)
```powershell
git commit -m "Beschreibung deiner Änderung"
```

Beispiele:
- `git commit -m "Add initial converter script"`
- `git commit -m "Refactor parsing and add tests"`
- `git commit -m "Update README and usage instructions"`

### 6.4 Auf GitHub pushen
```powershell
git push
```

Damit ist dein Tagesstand **zusätzlich** in GitHub gesichert.

---

## 7) Häufige Anfängerfragen und typische Stolperfallen

### 7.1 „Ich sehe untracked files – was heißt das?“
Das sind neue Dateien, die Git noch nicht versioniert.  
Wenn du sie sichern willst: `git add <datei>`

### 7.2 „Ich habe etwas aus Versehen committed“
- Wenn es noch **nicht gepusht** ist: man kann es rückgängig machen (sag Bescheid, dann gebe ich dir die passende Variante).
- Wenn es **schon gepusht** ist: besser mit einem neuen Commit korrigieren (sauberer Workflow).

### 7.3 Excel-Dateien im Repo
- Kleine Excel-Dateien als Beispiel/Testdaten: ok
- Große oder häufig wechselnde Dateien: besser ignorieren oder LFS verwenden

Wenn du später feststellst „Die Exceldateien sind groß und nerven“:
- Dann kann man Git LFS einrichten oder die Dateien aus der Historie entfernen.

### 7.4 Zugang/Anmeldung bei GitHub
Du nutzt HTTPS. Wenn `git push` nach Login fragt:
- Das ist normal, wenn keine Credentials gespeichert sind.
- Git Credential Manager übernimmt das meistens.

---

## 8) Kontroll-Checkliste (damit du sicher bist, dass alles stimmt)

Im Projektordner `xlsmToPython`:

### Repository erkannt?
```powershell
git status
```

### Remote korrekt?
```powershell
git remote -v
```

Sollte zeigen:
`origin https://github.com/SylviaChares/xlsmToPython.git (fetch/push)`

### Branch korrekt?
```powershell
git branch
```

Sollte `main` mit `*` markieren.

---

## 9) Alternative: xlsmToPython in dein bestehendes Repo „mein-erstes-projekt“ legen (Monorepo)

Nur falls du das wirklich willst.

### Vorgehen (Kurzform)
1. Entscheide einen gemeinsamen Ordner, z. B.:
   `C:\Users\chares\Documents\Notebooks\mein-erstes-projekt`
2. Lege darin einen Unterordner `xlsmToPython` an
3. Kopiere dein Projekt hinein
4. Dann im **Hauptrepo**:
   ```powershell
   git add .
   git commit -m "Add xlsmToPython project"
   git push
   ```

Nachteil: Die beiden Projekte hängen in einem Repo zusammen; als Anfänger wird das schnell unübersichtlich.

---

## 10) Empfohlenes Minimal‑Ritual (merken!)

**Morgens (Start):**
```powershell
git status
git pull
```

**Abends (Sichern):**
```powershell
git status
git add .
git commit -m "Kurzbeschreibung"
git push
```

Wenn `git commit` sagt „nothing to commit“: alles ist bereits gesichert.
