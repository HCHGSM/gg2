# Phase 1 — Full Audit Report
**Project:** POS & ERP System | **Date:** 2026-07-30 | **Auditor:** Lead Engineer

## Executive Summary

The repository does not contain one application — it contains **five separate, competing
implementations** of the same POS/ERP idea, plus six different entry-point scripts and three
PyInstaller `.spec` files. This is the single most important finding of the audit and it blocks
safe, automated repair. Everything else below is secondary until this is resolved.

| # | Directory | Lines (py) | Stack | Entry point(s) | Status |
|---|-----------|-----------|-------|-----------------|--------|
| 1 | `pos_erp/` | 2,588 | PySide6 (desktop) + FastAPI (`web_app/`) sharing one SQLAlchemy model layer | `main.py`, `run_web.py` | **Most complete.** Proper layering: `database/`, `services/`, `ui/views/`, `utils/`. Has real unit tests (`tests/`) that import it directly. Matches what `README.md` documents as "how to run" the app. |
| 2 | `enterprise_pos_erp/` | 984 | PySide6, monolithic `gui.py` + `database.py` | `main_enterprise_app.py` | Parallel rewrite, no tests, no service layering. |
| 3 | `hardcore_erp/` | 744 | PySide6, `core/` + `ui/` | `run_hardcore.py` | Parallel rewrite, no tests. |
| 4 | `mabi3aat_mega/` | 636 | FastAPI, HTML built inline as Python strings | `run_mabi3aat.py` | Parallel rewrite, no tests, no template files (HTML embedded in `.py`). |
| 5 | `enterprise_erp/` | 467 | FastAPI, HTML built inline as Python strings | `desktop_app.py` (opens a browser window) | Smallest / least developed, no tests. |

Additional loose files with no clear owner: `desktop_app_gui.py` (a **sixth**, Tkinter-based
implementation with raw SQL), `SmartPOS.spec` / `EnterprisePOS.spec` / `EnterpriseApp.spec`
(three different, inconsistent PyInstaller specs — `build.py` even points at `SmartPOS.spec`,
which references `desktop_app_gui.py`, none of which match the README's documented app).

**Working hypothesis:** each of the last four implementations was generated in a separate
session that started over from scratch instead of extending `pos_erp/`. `pos_erp/` +
`web_app/` is the only pair that (a) share one data model, (b) match the README, and (c) have
tests. I treat it as canonical for the rest of this report, but **this needs your confirmation
before Phase 2 touches anything** — see "Decision Required" at the end.

---

## Critical Issues

1. **Five parallel codebases / six entry points / three build specs** targeting the same
   product. Massive duplication, no clear source of truth, high risk of someone editing the
   wrong copy. (See table above.)
2. **No dependency manifest.** There is no `requirements.txt`, `pyproject.toml`, or `Pipfile`
   anywhere in the repo, despite depending on PySide6, FastAPI, SQLAlchemy, Uvicorn, bcrypt,
   Jinja2, python-multipart, PyInstaller, and Tkinter is also used by one variant.
3. **No version control.** No `.git` directory — there is no history, no diffing capability,
   no safe rollback if something goes wrong during repair.
4. **Hardcoded default admin credentials in source (`admin` / `admin123`)**, duplicated in at
   least 9 files across every implementation, several of which also pre-fill the password in
   the login form UI. This is a real security exposure if ever deployed as-is, and it's the
   kind of duplication that will keep going stale as the app evolves.
5. **Web session management is insecure and non-persistent** (`web_app/app.py`):
   - Sessions live in a plain Python dict (`active_sessions = {}`) — lost on every server
     restart, unbounded growth, no expiry, not usable with more than one worker process.
   - `response.set_cookie(key="session_token", value=token)` sets no `httponly`, `secure`, or
     `samesite` flags — the cookie is readable by JavaScript and sent over plain HTTP, and
     there is no CSRF protection on the login form.
6. **Database files, logs, and backups are committed inside the repo** (`pos_erp.db`,
   `enterprise_erp.db`, `mabi3aat_mega.db`, `server.log`, `mabi3aat.log`,
   `pos_backups/*.db` — 568 KB of binary backups). These should never be in source control;
   right now there's no `.gitignore` to prevent it going forward either.
7. **The canonical DB path is outside the repo:** `pos_erp/database/db.py` writes to
   `~/pos_erp.db` (the user's home directory), while a *different* `pos_erp.db` sits committed
   at the repo root — meaning the committed file isn't even the one the app actually uses.
   This will confuse anyone trying to inspect "the" database.

## High Priority Issues

1. No `.gitignore` — logs, `.db` files, `__pycache__`, and a stray uploaded screenshot
   (`uploads/image.png`) are all sitting in the repo root.
2. No environment-based configuration (`.env` / settings module) anywhere — DB paths, ports,
   and the secret admin seed are all hardcoded in source.
3. No password complexity/rotation policy, no account lockout after failed login attempts in
   `AuthService` (needs re-verification once canonical codebase is confirmed).
4. No CI, no linting config (`ruff`/`flake8`/`black`), no pre-commit hooks.
5. Three inconsistent PyInstaller specs referencing different, sometimes non-canonical entry
   scripts — packaging is not currently reproducible.
6. Test suite is small (152 lines across 3 files) relative to the size of the canonical app
   (2,588 lines) and has not been run/verified in this audit yet (deferred to Phase 2 so it
   isn't run against the wrong codebase).

## Medium Priority Issues

1. Arabic-language docstrings/UI strings mixed with English identifiers throughout — fine for
   an RTL-first product, but no `docs/` guidance yet on the localization approach for future
   contributors.
2. `docs/architecture.md`, `docs/user_guide.md`, `docs/api.md` exist but haven't been checked
   yet for whether they describe `pos_erp/` or one of the abandoned variants (likely stale;
   revisit in Phase 10).
3. No indication yet (pending Phase 3) of migration tooling (Alembic) — schema changes today
   would have to be applied by hand.

## Low Priority Issues

1. Mixed logging approaches (`print()` statements in entry scripts vs. a dedicated
   `pos_erp/utils/logger.py`).
2. Emoji/box-drawing banners printed to console on startup (cosmetic, harmless, but not
   "enterprise" styling).

---

## Decision Required Before Phase 2

I will not delete or merge code without your sign-off, since four of the five implementations
represent real (if abandoned) work and destroying them is irreversible without version
control. Please confirm:

**Is `pos_erp/` (desktop, PySide6) + `web_app/` (FastAPI) the application you want turned into
the production system?**

If yes, my Phase 2 plan is:
- Archive `enterprise_pos_erp/`, `hardcore_erp/`, `mabi3aat_mega/`, `enterprise_erp/`,
  `desktop_app_gui.py`, and their entry scripts/specs into a `_archive/` folder (not delete)
  so nothing is lost, and remove them from the active build.
- Initialize git so all further changes are tracked and reversible.
- Add `requirements.txt`, `.gitignore`, and stop committing `.db`/`.log`/backup files.
- Fix the web session/cookie security issues under Phase 2 (they're "broken/insecure startup
  behavior," not a new feature) and move the hardcoded admin seed behind an env var.
- Reconcile the `~/pos_erp.db` vs repo-root `pos_erp.db` path inconsistency.

If instead one of the other four is actually the intended direction (or you want them merged
feature-by-feature into one), tell me which and I'll re-scope Phase 2 around that instead.
