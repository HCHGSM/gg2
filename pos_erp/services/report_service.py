import openpyxl
from sqlalchemy import func
from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Sale, SaleItem, Purchase, Expense, Revenue, Product, Customer, Supplier, Account, JournalEntry, JournalEntryLine

class ReportService:
    @staticmethod
    def get_dashboard_stats():
        session = SessionLocal()
        try:
            # Sales Total (Invoice total, includes tax)
            total_sales = session.query(func.coalesce(func.sum(Sale.total), 0.0)).filter_by(status='COMPLETED').scalar()
            
            # Net Sales = Subtotal - Discount (excl. tax)
            net_sales = session.query(func.coalesce(func.sum(Sale.subtotal - Sale.discount), 0.0)).filter_by(status='COMPLETED').scalar()
            
            # Cost of Goods Sold (COGS)
            cogs = session.query(func.coalesce(func.sum(SaleItem.quantity * SaleItem.unit_cost), 0.0)) \
                .join(Sale) \
                .filter(Sale.status == 'COMPLETED') \
                .scalar()
                
            total_purchases = session.query(func.coalesce(func.sum(Purchase.total), 0.0)).filter_by(status='COMPLETED').scalar()
            total_expenses = session.query(func.coalesce(func.sum(Expense.amount), 0.0)).scalar()
            total_revenues = session.query(func.coalesce(func.sum(Revenue.amount), 0.0)).scalar()

            customers_count = session.query(Customer).count()
            suppliers_count = session.query(Supplier).count()
            products_count = session.query(Product).count()
            
            low_stock_count = session.query(Product).filter(Product.quantity <= Product.min_stock).count()
            
            # Proper Accounting Net Profit
            gross_profit = net_sales - cogs
            net_profit = gross_profit - total_expenses + total_revenues
            
            return {
                'total_sales': total_sales,
                'total_purchases': total_purchases,
                'total_expenses': total_expenses,
                'total_revenues': total_revenues,
                'customers_count': customers_count,
                'suppliers_count': suppliers_count,
                'products_count': products_count,
                'low_stock_count': low_stock_count,
                'net_profit': net_profit
            }
        finally:
            session.close()

    @staticmethod
    def get_trial_balance():
        session = SessionLocal()
        try:
            accounts = session.query(Account).order_by(Account.code).all()
            total_assets = sum(a.balance for a in accounts if a.account_type == 'ASSET')
            total_liabilities = sum(a.balance for a in accounts if a.account_type == 'LIABILITY')
            total_equity = sum(a.balance for a in accounts if a.account_type == 'EQUITY')
            total_revenue = sum(a.balance for a in accounts if a.account_type == 'REVENUE')
            total_expense = sum(a.balance for a in accounts if a.account_type == 'EXPENSE')
            
            return {
                'accounts': [{'code': a.code, 'name': a.name, 'balance': a.balance, 'type': a.account_type} for a in accounts],
                'total_assets': total_assets,
                'total_liabilities': total_liabilities,
                'total_equity': total_equity,
                'total_revenue': total_revenue,
                'total_expense': total_expense,
                'is_balanced': round(total_assets + total_expense, 2) == round(total_liabilities + total_equity + total_revenue, 2)
            }
        finally:
            session.close()

    @staticmethod
    def get_cash_flow(start_date=None, end_date=None):
        session = SessionLocal()
        try:
            query = session.query(JournalEntryLine).join(JournalEntry).join(Account).filter(Account.code.in_(['1001', '1002']))
            if start_date:
                query = query.filter(JournalEntry.date >= start_date)
            if end_date:
                query = query.filter(JournalEntry.date <= end_date)
                
            lines = query.all()
            
            inflows = sum(l.debit for l in lines)
            outflows = sum(l.credit for l in lines)
            net_cash_flow = inflows - outflows
            
            return {
                'inflows': inflows,
                'outflows': outflows,
                'net_cash_flow': net_cash_flow
            }
        finally:
            session.close()

    @staticmethod
    def export_sales_excel(file_path):
        session = SessionLocal()
        try:
            sales = session.query(Sale).yield_per(1000)
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Sales Report"
            
            headers = ["Invoice No", "Customer ID", "Subtotal", "Discount", "Tax", "Total", "Paid", "Status", "Date"]
            ws.append(headers)
            
            for s in sales:
                ws.append([
                    s.invoice_number,
                    s.customer_id or "Walk-in",
                    s.subtotal,
                    s.discount,
                    s.tax_amount,
                    s.total,
                    s.paid_amount,
                    s.status,
                    str(s.created_at)
                ])
            wb.save(file_path)
            return True, "تم تصدير تقرير المبيعات إلى Excel بنجاح"
        except Exception as e:
            return False, str(e)
        finally:
            session.close()
