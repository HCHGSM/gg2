import csv
from datetime import datetime
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Sale, Purchase, Expense, Revenue, Product, Customer, Supplier

class ReportService:
    @staticmethod
    def get_dashboard_stats():
        session = SessionLocal()
        try:
            total_sales = sum(s.total for s in session.query(Sale).filter_by(status='COMPLETED').all())
            total_purchases = sum(p.total for p in session.query(Purchase).filter_by(status='COMPLETED').all())
            total_expenses = sum(e.amount for e in session.query(Expense).all())
            total_revenues = sum(r.amount for r in session.query(Revenue).all())
            
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
