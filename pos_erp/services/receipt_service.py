class ReceiptService:
    """
    خدمة تنسيق فواتير المبيعات لطباعتها عبر طابعات الإيصالات الحرارية (Thermal Receipt Formatting).
    """
    @staticmethod
    def generate_receipt_text(sale, items, company_name="شركة الأفق الذكي"):
        width = 40
        lines = []
        lines.append("=" * width)
        lines.append(company_name.center(width))
        lines.append("نظام المبيعات المتكامل (POS & ERP)".center(width))
        lines.append("-" * width)
        lines.append(f"رقم الفاتورة: {sale.invoice_number}")
        lines.append(f"التاريخ: {sale.created_at}")
        lines.append(f"طريقة الدفع: {sale.payment_method}")
        lines.append("-" * width)
        lines.append(f"{'المنتج':<20}{'الكمية':<5}{'السعر':<10}")
        lines.append("-" * width)
        
        for item in items:
            p_name = item.product.name[:18] if item.product else "منتج"
            lines.append(f"{p_name:<20}{item.quantity:<5}{item.total:<10,.2f}")
            
        lines.append("-" * width)
        lines.append(f"المجموع الفرعي: {sale.subtotal:,.2f} ج.س")
        lines.append(f"الضريبة (15%): {sale.tax_amount:,.2f} ج.س")
        lines.append(f"الإجمالي النهائي: {sale.total:,.2f} ج.س")
        lines.append(f"المبلغ المدفوع: {sale.paid_amount:,.2f} ج.س")
        lines.append("=" * width)
        lines.append("شكراً لتعاملكم معنا - نسعد خدمتكم دائماً".center(width))
        lines.append("=" * width)
        return "\n".join(lines)
