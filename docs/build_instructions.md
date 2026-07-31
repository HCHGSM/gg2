# Windows Build Instructions (.exe + Installer)

**These steps must be run on an actual Windows machine.** PyInstaller does not
cross-compile — a Windows `.exe` cannot be produced from Linux or macOS. If
you don't have a Windows machine handy, a Windows GitHub Actions runner works
fine for this (see the CI note at the bottom).

## 1. Prerequisites (on Windows)

- Python 3.11 or 3.12 (64-bit) installed and on `PATH`
- [Inno Setup 6.x](https://jrsoftware.org/isinfo.php) installed, for the installer step

## 2. Set up the environment

```powershell
git clone <this-repo>
cd <this-repo>
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Sanity-check the app runs from source first

```powershell
python main.py
```
Log in with `admin` / `admin123` (or whatever `POS_ERP_ADMIN_PASSWORD` you set)
and click through the main modules (POS, Inventory, Reports) before building —
it's much faster to catch a bug here than after packaging.

## 4. Build the one-file executable

```powershell
python build.py
```

This runs `pyinstaller SmartPOS.spec --clean` under the hood. On success:
- Output: `dist\SmartPOS_ERP.exe`
- Windowed (no console window), single file, custom icon, version info embedded
  (right-click → Properties → Details in Explorer to confirm)

**Before running it standalone**, test it on a clean(-ish) machine or VM
without your dev Python environment active, to confirm it truly doesn't
depend on your local Python install.

## 5. Build the installer

```powershell
cd installer
iscc SmartPOS_ERP.iss
```

Output: `dist_installer\SmartPOS_ERP_Setup_1.0.0.exe`

Before shipping, edit `installer/SmartPOS_ERP.iss` and set:
- `MyAppPublisher` — your real company/publisher name
- `MyAppURL` — your real support/website URL
- `MyAppVersion` — bump this (and `version_info.txt`, and `CHANGELOG.md`) on every release

## 6. What the installer does

- Installs to `Program Files\Smart POS & ERP\` by default (configurable at install time)
- Creates a Start Menu entry and an optional Desktop shortcut
- Registers a standard Windows uninstaller
- The app itself stores its database and logs in
  `%LOCALAPPDATA%\SmartPOS_ERP\data\` (writable without admin rights, and
  preserved across reinstalls/updates) — **not** inside the Program Files
  install folder, which standard users can't write to.

## 7. Code signing (optional but recommended for production)

This build produces an **unsigned** executable. Windows SmartScreen will show
an "unknown publisher" warning on first run until either (a) enough users run
it to build reputation, or (b) you sign it with a code-signing certificate
(`signtool sign /f cert.pfx /p <password> dist\SmartPOS_ERP.exe`). Obtaining a
certificate is a purchase decision only you can make (from a CA like
DigiCert, Sectigo, etc.) — not something I can provision.

## Building via CI instead of a physical Windows machine

If you don't have Windows available, a free GitHub Actions `windows-latest`
runner can execute steps 2–5 above in a workflow (`runs-on: windows-latest`),
uploading `dist\SmartPOS_ERP.exe` and the installer as build artifacts. I can
write that workflow file on request — it wasn't included here since it needs
your repository's actual remote/CI setup to be wired up correctly.
