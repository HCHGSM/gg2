# Changelog

## [1.1.0] - Complete Audit and Fixes (Agent Run)

### Accounting Integrity
- Fixed Net Profit Calculation: Net profit now properly uses Cost of Goods Sold (COGS) rather than naive total purchases.
- Added `SaleItem.unit_cost` to reliably lock in the COGS at the time of sale.
- Implemented `PurchaseService` logic for handling purchases, updating inventory, recalculating moving average cost, and debiting Supplier/Cash accounts.
- Implemented `SalesService.return_sale()` logic to correctly handle sales returns by returning inventory, refunding cash, and updating logs.
- Added `get_trial_balance()` and `get_cash_flow()` to `ReportService`.

### Database & Performance
- Enabled `PRAGMA journal_mode=WAL` for robust concurrent reads/writes and `PRAGMA foreign_keys=ON` in SQLite.
- Fixed missing index configuration on all SQLAlchemy `ForeignKey` columns to enhance lookup performance on relations.
- Added `yield_per()` usage in large data exports (e.g. `export_sales_excel`) to prevent out-of-memory errors on massive databases.

### Desktop App
- Fixed memory leaks in PySide6 `QTableWidget`s by using `setRowCount(0)` before repopulating tables.
- Added an auto-refresh hook to `switch_view` to prevent stale data when switching between tabs.
- Added explicit Logout functionality to securely replace the main window session.

### Web App
- Added Role-Based Access Control (RBAC) via the `require_role` dependency for both UI routes and API endpoints.

### Testing & Docs
- Developed `test_accounting.py` and `test_system.py` to continuously verify the financial and system integrity.
- Created `developer_guide.md` and `database_guide.md`.

## [1.0.0] - Production readiness pass

### Fixed (crash / correctness)
- `main.py`: `sys.Qt.RightToLeft` was invalid (`sys` has no `Qt` attribute) and
  crashed the desktop app on every launch. Now imports `Qt` from `PySide6.QtCore`.
- `SalesService.create_sale`: invoice-number generation had a race condition —
  two near-simultaneous sales could compute the same invoice number and the
  second would fail on the unique constraint. Now retries with a fresh number
  on collision instead of failing the sale.
- `Role.users` relationship used `cascade='all, delete-orphan'`, meaning
  deleting a Role would have silently deleted every User assigned to it.
  Removed that cascade.
- Fixed a packaging-time bug that would have silently reset the database on
  every run once built as a PyInstaller onefile `.exe` (path resolution was
  landing inside the ephemeral extraction temp directory). Also fixed the
  install-location issue where a Program-Files install (not writable by
  standard users) would have prevented the database from being created at
  all. Data now lives in `%LOCALAPPDATA%\SmartPOS_ERP\` on frozen Windows builds.

### Security
- Web sessions: replaced an in-memory dict with no expiry and an insecure
  cookie (no `httponly`/`secure`/`samesite`) with a session store that expires
  (8h default, configurable), and cookies set with `httponly`, `samesite=lax`,
  and `secure` (in production mode).
- Added basic login rate-limiting (5 attempts / 15 min per IP) to blunt
  brute-force password guessing on the web login.
- Fixed username enumeration: login now returns the same generic error for
  "no such user" and "wrong password."
- Moved the default admin password out of source code into an environment
  variable (`POS_ERP_ADMIN_PASSWORD`), defaulting to the previous value for
  a frictionless first run.
- Added basic security response headers (`X-Content-Type-Options`,
  `X-Frame-Options`, `Referrer-Policy`) to the web app.
- Removed an unused, misleading `sanitize_input()` helper that neither
  prevented SQL injection (real protection already comes from SQLAlchemy's
  parameterized queries) nor was ever called anywhere in the codebase.

### Performance
- `ReportService.get_dashboard_stats()` was loading every row of the
  sales/purchases/expenses/revenues tables into Python memory just to sum
  them, on every dashboard view. Now aggregated in SQL (`func.sum`).
- Added missing indexes on foreign-key columns across `sale_items`,
  `purchase_items`, `inventory_movements`, and `transactions`.

### Project structure
- Archived four abandoned, duplicate parallel implementations
  (`enterprise_pos_erp/`, `hardcore_erp/`, `mabi3aat_mega/`, `enterprise_erp/`)
  and their entry scripts/spec files into `_archive/`. `pos_erp/` + `web_app/`
  is now the single active codebase.
- Initialized git version control (none existed before).
- Added `requirements.txt` (none existed before).
- Added `.gitignore`; removed committed `.db`/`.log`/backup binaries and a
  stray uploaded screenshot from tracking.
- Fixed the database and log file paths, which previously wrote to the
  user's home directory inconsistently with a *different* `pos_erp.db` that
  was committed at the repo root.
- Added missing `__init__.py` files across the `pos_erp` package tree
  (needed for reliable PyInstaller bundling).

### UX
- Login: pressing Enter in the password field now submits the form; pressing
  Enter in the username field moves focus to the password field.

### Packaging (new)
- Generated an app icon (`assets/icons/app_icon.ico`/`.png`).
- Rewrote `SmartPOS.spec` for a proper one-file, windowed Windows build with
  icon and version info; fixed `build.py` (previously pointed at an archived,
  mismatched entry script).
- Added `version_info.txt` (Windows exe version resource — update the
  placeholder company name before shipping).
- Added `installer/SmartPOS_ERP.iss` (Inno Setup script: desktop/start-menu
  shortcuts, uninstaller — update placeholder publisher name/URL before
  shipping).

### Documentation (new/updated)
- Rewrote `README.md` with accurate run instructions, environment variables,
  and project structure.
- Added `docs/build_instructions.md`, `docs/deployment_guide.md`,
  `docs/testing_checklist.md`, this `CHANGELOG.md`, and `FINAL_AUDIT_REPORT.md`.

### Known gaps (not fixed in this pass — flagged for a decision)
- Web app routes `/products`, `/inventory`, `/customers`, `/suppliers`,
  `/expenses`, `/reports` are stubs that redirect to `/dashboard`; they were
  never built out as full pages. Desktop app has full functionality for all
  of these. Building full parity is a real feature-scope decision, not a bug fix.
- Web session store is in-memory and single-process only; documented in the
  deployment guide as needing a shared store (e.g. Redis) before scaling to
  multiple worker processes.
- No automated migration tool (Alembic) is set up; schema changes today are
  applied via `create_all()` only (fine for new installs, not for altering
  an existing production database's schema later).
