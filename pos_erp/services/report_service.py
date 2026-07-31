import csv
from datetime import datetime
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy import func
from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Sale, Purchase, Expense, Revenue, Product, Customer, Supplier

class ReportService:
    @staticmethod
    def get_dashboard_stats():
        session = SessionLocal()
        try:
            # Aggregate with SQL (func.sum) instead of loading every row into
            # Python and summing in memory — this used to load the entire
            # sales/purchases/expenses/revenues tables on every dashboard view.
            total_sales = session.query(func.coalesce(func.sum(Sale.total), 0.0)).filter_by(status='COMPLETED').scalar()
            total_purchases = session.query(func.coalesce(func.sum(Purchase.total), 0.0)).filter_by(status='COMPLETED').scalar()
            total_expenses = session.query(func.coalesce(func.sum(Expense.amount), 0.0)).scalar()
            total_revenues = session.query(func.coalesce(func.sum(Revenue.amount), 0.0)).scalar()

            customers_count = session.query(Customer).count()
            suppliers_count = session.query(Supplier).count()
            products_count = session.query(Product).count()
            
            low_stock_count = session.query(Product).filter(Product.quantity <= Product.min_stock).count()
            
            net_profit = total_sales - total_purchases - total_expenses + total_revenues
            
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
    def export_sales_excel(file_path):
        session = SessionLocal()
        try:
            sales = session.query(Sale).all()
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
