# Git & GitHub Cheat-Sheet (Einsteiger)  
**Projekt: xlsmToPython**

Dieses Cheat-Sheet ist eine **kurze, praxisorientierte Gedächtnisstütze** für den Alltag.
Keine Theorie, nur: *Was mache ich wann und warum?*

---

## 1. Grundbegriffe (ultrakurz)

- **Repository (Repo)**: Versionsspeicher für ein Projekt  
- **lokales Repo**: liegt auf deinem Rechner  
- **Remote**: das entfernte Repo (meist GitHub), i. d. R. `origin`  
- **Commit**: Versions-Schnappschuss  
- **Push**: Commits zu GitHub hochladen  
- **Pull**: Änderungen von GitHub holen  
- **Branch**: Entwicklungszweig (Standard: `main`)

---

## 2. Wo muss ich stehen?

👉 **Immer im Projektordner**, der den `.git`-Ordner enthält.

Beispiel:
```powershell
C:\Users\chares\Documents\Notebooks\xlsmToPython
```

Prüfen:
```powershell
pwd
dir .git
```

---

## 3. Einmalige Initialisierung (neues Projekt)

```powershell
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/SylviaChares/xlsmToPython.git
git branch -M main
git push -u origin main
```

---

## 4. Täglicher Ablauf

### Morgens
```powershell
git status
git pull
```

### Abends
```powershell
git status
git add .
git commit -m "Kurzbeschreibung"
git push
```

---

## 5. Wichtige Bedeutungen

### `git remote -v`
➡ zeigt nur die **gespeicherte Zieladresse**, nicht ob das Repo existiert.

### `Repository not found`
➡ Repo existiert nicht, falscher Account oder falscher Name.

### Erfolgreicher Push
➡ Repo existiert und Verbindung stimmt.

---

## 6. Repo im Browser finden

```powershell
git remote get-url origin
```

`.git` entfernen und URL im Browser öffnen.

---

## 7. Typische Anfängerfehler

- Repo im Browser nicht sichtbar → falscher Account
- Untracked files → `git add`
- Binärdateien (Excel) → ggf. `.gitignore`

---

## 8. Mini-Diagnose

```powershell
git status
git remote -v
git branch
```

---

## Merksätze

> `git remote -v` ≠ Repo existiert  
> Erfolgreicher `git push` = alles korrekt
