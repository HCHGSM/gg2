class BarcodeService:
    """
    خدمة توليد وطباعة باركود المنتجات وملصقات الأسعار والباركود التجاري.
    """
    @staticmethod
    def generate_code128(text):
        # Placeholder logic for barcode encoding generation or verification
        return f"* {text} *"

    @staticmethod
    def validate_barcode(barcode):
        if not barcode:
            return False, "الباركود فارغ"
        if len(barcode) < 3:
            return False, "رمز الباركود قصير جداً"
        return True, "باركود صالح"
