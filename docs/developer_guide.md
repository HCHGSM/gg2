# Developer Guide

## Environment Setup
1. Install Python 3.11+
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment.
4. Install dependencies: `pip install -r requirements.txt`

## Running Locally
- Desktop PySide6 App: `python main.py`
- Web FastAPI App: `python run_web.py`

## Running Tests
Run the comprehensive automated testing suite:
`python test_accounting.py`
`python test_system.py`

## Adding a New Service
1. Create `pos_erp/services/my_service.py`
2. Follow the existing pattern using `@staticmethod`
3. Always manage transactions properly with `session.rollback()` in `except` blocks.

## Adding a New View
1. Create `pos_erp/ui/views/my_view.py`
2. Inherit from `QWidget`
3. Implement `init_ui()` and `load_data()`
4. Important: clear table rows with `self.table.setRowCount(0)` before repopulating.
5. Register in `MainWindow`'s `QStackedWidget` and sidebar.