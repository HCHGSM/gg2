# Database Schema Documentation

The system uses SQLAlchemy ORM over a SQLite database. For production performance, WAL mode and foreign key constraints are enabled.

## Core Entities
1. **User / Role / Permission**
   - Handles authentication and RBAC.
   - Users are linked to roles, roles linked to multiple permissions.

2. **Product / Category / Warehouse**
   - Core inventory items.
   - Products have `purchase_price` (Cost/Average Cost) and `selling_price`.
   - `quantity` tracks current total stock.

3. **Sale / SaleItem**
   - Invoice headers and lines for customer sales.
   - `SaleItem.unit_cost` securely tracks the COGS at the time of sale.

4. **Purchase / PurchaseItem**
   - Supplier purchases. Automatically updates Product `quantity` and moving average `purchase_price`.

5. **InventoryMovement**
   - An immutable audit log of every change in stock quantity (IN, OUT).

6. **Account / Transaction**
   - Financial ledger. Tracks balances in CASH and BANK accounts. Every Sale/Purchase automatically deposits/withdraws from these accounts.

7. **Expense / Revenue**
   - Operating expenses and non-operating revenues affecting Net Profit.

## Accounting Integrity
- Net Profit = (Net Sales - COGS) - Expenses + Revenues
- COGS = sum(SaleItem.quantity * SaleItem.unit_cost)
- Stock is never deleted, only adjusted via standard IN/OUT movements.