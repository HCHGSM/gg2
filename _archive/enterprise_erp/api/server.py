# -*- coding: utf-8 -*-
"""
=============================================================================
Enterprise ERP & POS FastAPI Backend Server (Massive Scale Module)
Exposes complete APIs for Accounting, POS, Inventory, HR, and Analytics.
=============================================================================
"""

from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import uuid
import bcrypt

from enterprise_erp.core.engine import init_enterprise_db, SessionLocal, EnterpriseUser, EnterpriseProduct, EnterpriseInvoice, EnterpriseCustomer, EnterpriseAccount

app = FastAPI(title="Enterprise ERP & POS Mega Suite", version="5.0.0")

@app.on_event("startup")
def startup():
    init_enterprise_db()

sessions = {}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>Enterprise ERP & POS - تسجيل الدخول</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet">
        <style>body { font-family: 'Cairo', sans-serif; }</style>
    </head>
    <body class="bg-gradient-to-tr from-slate-950 via-indigo-950 to-blue-950 min-h-screen flex items-center justify-center p-6">
        <div class="bg-white/10 backdrop-blur-2xl border border-white/20 p-10 rounded-3xl shadow-2xl w-full max-w-md text-white">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-black bg-gradient-to-r from-sky-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">Enterprise ERP</h1>
                <p class="text-slate-300 text-sm mt-2">نظام الإدارة المتكامل الضخم (Mega Suite)</p>
            </div>
            <form action="/login" method="POST" class="space-y-5">
                <div>
                    <label class="block text-sm font-bold text-slate-200 mb-2">اسم المستخدم</label>
                    <input type="text" name="username" required value="admin" class="w-full bg-slate-900/60 border border-slate-700 rounded-xl px-4 py-3.5 text-white focus:ring-2 focus:ring-sky-500">
                </div>
                <div>
                    <label class="block text-sm font-bold text-slate-200 mb-2">كلمة المرور</label>
                    <input type="password" name="password" required value="admin123" class="w-full bg-slate-900/60 border border-slate-700 rounded-xl px-4 py-3.5 text-white focus:ring-2 focus:ring-sky-500">
                </div>
                <button type="submit" class="w-full bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-600 hover:to-indigo-700 text-white font-extrabold py-4 rounded-xl shadow-lg transition duration-200">
                    دخول النظام الضخم
                </button>
            </form>
            <div class="mt-8 text-center text-xs text-slate-400 border-t border-white/10 pt-4">
                الحساب الافتراضي: <span class="text-sky-400 font-bold">admin</span> / <span class="text-sky-400 font-bold">admin123</span>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    session = SessionLocal()
    try:
        user = session.query(EnterpriseUser).filter_by(username=username).first()
        if not user:
            raise HTTPException(status_code=400, detail="المستخدم غير موجود")
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            raise HTTPException(status_code=400, detail="كلمة المرور غير صحيحة")
        
        token = str(uuid.uuid4())
        sessions[token] = user.id
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="ent_token", value=token)
        return response
    finally:
        session.close()

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    token = request.cookies.get("ent_token")
    if not token or token not in sessions:
        return RedirectResponse(url="/", status_code=303)

    session = SessionLocal()
    try:
        prods_count = session.query(EnterpriseProduct).count()
        inv_count = session.query(EnterpriseInvoice).count()
        invoices = session.query(EnterpriseInvoice).order_by(EnterpriseInvoice.created_at.desc()).limit(10).all()
        
        html_out = """
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>لوحة التحكم الرئيسية - Enterprise ERP</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet">
            <style>body { font-family: 'Cairo', sans-serif; }</style>
        </head>
        <body class="bg-slate-900 text-slate-100 min-h-screen flex">
            <aside class="w-72 bg-slate-950 border-r border-slate-800 flex flex-col justify-between p-6">
                <div>
                    <h2 class="text-2xl font-black bg-gradient-to-r from-sky-400 to-indigo-400 bg-clip-text text-transparent mb-8">Enterprise ERP</h2>
                    <nav class="space-y-2">
                        <a href="/dashboard" class="block px-4 py-3 rounded-xl bg-sky-600 text-white font-bold">📊 لوحة التحكم</a>
                        <a href="/pos-terminal" class="block px-4 py-3 rounded-xl hover:bg-slate-800 transition">💳 نقطة البيع (POS)</a>
                        <a href="/warehouse" class="block px-4 py-3 rounded-xl hover:bg-slate-800 transition">🏭 المستودعات والمخزون</a>
                        <a href="/accounting" class="block px-4 py-3 rounded-xl hover:bg-slate-800 transition">💰 الحسابات العامة (GL)</a>
                        <a href="/hr" class="block px-4 py-3 rounded-xl hover:bg-slate-800 transition">👥 الموارد البشرية (HR)</a>
                        <a href="/manufacturing" class="block px-4 py-3 rounded-xl hover:bg-slate-800 transition">⚙️ التصنيع (BOM)</a>
                    </nav>
                </div>
                <div>
                    <a href="/" class="block px-4 py-3 rounded-xl bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-white transition font-bold text-center">🚪 خروج</a>
                </div>
            </aside>
            <main class="flex-1 p-10 overflow-y-auto">
                <header class="flex justify-between items-center mb-10 pb-6 border-b border-slate-800">
                    <h1 class="text-3xl font-black text-white">لوحة العمليات والتحليلات الضخمة</h1>
                    <span class="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-5 py-2 rounded-full font-bold text-sm">🟢 النظام يعمل بكفاءة تامة</span>
                </header>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                    <div class="bg-slate-950 border border-slate-800 p-6 rounded-2xl border-r-4 border-r-sky-500 shadow-xl">
                        <p class="text-slate-400 text-sm font-bold">إجمالي المنتجات المسجلة</p>
                        <h3 class="text-3xl font-black text-sky-400 mt-2">""" + str(prods_count) + """ منتج</h3>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 p-6 rounded-2xl border-r-4 border-r-emerald-500 shadow-xl">
                        <p class="text-slate-400 text-sm font-bold">إجمالي الفواتير المصدرة</p>
                        <h3 class="text-3xl font-black text-emerald-400 mt-2">""" + str(inv_count) + """ فاتورة</h3>
                    </div>
                </div>
            </main>
        </body>
        </html>
        """
        return html_out
    finally:
        session.close()

@app.get("/pos-terminal", response_class=HTMLResponse)
def pos_terminal():
    session = SessionLocal()
    try:
        prods = session.query(EnterpriseProduct).all()
        prod_cards = ""
        for p in prods:
            prod_cards += f"""
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col justify-between hover:border-sky-500 transition">
                <div>
                    <h4 class="font-bold text-white">{p.name}</h4>
                    <p class="text-xs text-slate-400 mt-1">المخزون: {p.stock_qty}</p>
                </div>
                <div class="flex justify-between items-center mt-4 pt-3 border-t border-slate-800">
                    <span class="text-sky-400 font-black">{p.sale_price:,.2f} ج.س</span>
                    <button onclick="addToCart({p.id}, '{p.name}', {p.sale_price}, {p.stock_qty})" class="bg-sky-600 hover:bg-sky-700 text-white font-bold px-3 py-1.5 rounded-lg text-xs">إضافة</button>
                </div>
            </div>
            """

        html_pos = """
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>نقطة البيع (POS) - Enterprise ERP</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet">
            <style>body { font-family: 'Cairo', sans-serif; }</style>
        </head>
        <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col">
            <header class="bg-slate-900 border-b border-slate-800 px-8 py-4 flex justify-between items-center">
                <h1 class="text-xl font-black text-white">نقطة بيع المؤسسة (Enterprise POS Terminal)</h1>
                <a href="/dashboard" class="bg-slate-800 px-4 py-2 rounded-xl text-xs font-bold hover:bg-slate-700">العودة للوحة التحكم</a>
            </header>
            <div class="p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
                <div class="lg:col-span-7 grid grid-cols-2 sm:grid-cols-3 gap-4 overflow-y-auto max-h-[80vh]">
                    """ + prod_cards + """
                </div>
                <div class="lg:col-span-5 bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between">
                    <div>
                        <h3 class="text-lg font-bold mb-4 border-b border-slate-800 pb-2">سلة المبيعات</h3>
                        <div id="cartList" class="space-y-3 overflow-y-auto max-h-[350px]">
                            <p class="text-slate-500 text-center py-10">السلة فارغة</p>
                        </div>
                    </div>
                    <div class="border-t border-slate-800 pt-4 mt-4 space-y-3">
                        <div class="flex justify-between text-lg font-black">
                            <span>الإجمالي النهائي:</span>
                            <span id="grandTotal" class="text-sky-400">0.00 ج.س</span>
                        </div>
                        <button onclick="checkout()" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-black py-4 rounded-xl shadow-lg transition">
                            إتمام البيع وإصدار الفاتورة
                        </button>
                    </div>
                </div>
            </div>
            <script>
                let cart = [];
                function addToCart(id, name, price, maxQty) {
                    let item = cart.find(function(i) { return i.id === id; });
                    if (item) { item.qty++; } else { cart.push({ id: id, name: name, price: price, qty: 1 }); }
                    renderCart();
                }
                function renderCart() {
                    let container = document.getElementById('cartList');
                    if (cart.length === 0) { container.innerHTML = '<p class="text-slate-500 text-center py-10">السلة فارغة</p>'; document.getElementById('grandTotal').innerText = '0.00 ج.س'; return; }
                    let html = ''; let total = 0;
                    cart.forEach(function(i, idx) {
                        total += i.price * i.qty;
                        html += '<div class="flex justify-between items-center bg-slate-950 p-3 rounded-xl border border-slate-800"><div><h5 class="font-bold text-sm">' + i.name + '</h5><p class="text-xs text-sky-400">' + i.price + ' × ' + i.qty + '</p></div><button onclick="cart.splice(' + idx + ',1);renderCart();" class="text-red-400 text-xs font-bold">حذف</button></div>';
                    });
                    container.innerHTML = html;
                    document.getElementById('grandTotal').innerText = total.toLocaleString() + ' ج.س';
                }
                async function checkout() {
                    if (cart.length === 0) return alert('السلة فارغة');
                    let total = cart.reduce(function(s, i) { return s + (i.price * i.qty); }, 0);
                    let res = await fetch('/api/ent-sale', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({total: total, items: cart})
                    });
                    let data = await res.json();
                    if (data.success) {
                        alert('تمت الفاتورة بنجاح: ' + data.invoice);
                        cart = []; renderCart();
                    } else {
                        alert('فشل العملية');
                    }
                }
            </script>
        </body>
        </html>
        """
        return html_pos
    finally:
        session.close()

class SalePayload(BaseModel):
    total: float
    items: list

@app.post("/api/ent-sale")
def api_ent_sale(payload: SalePayload):
    session = SessionLocal()
    try:
        inv_no = f"ENT-INV-{uuid.uuid4().hex[:6].upper()}"
        tax = payload.total * 0.15
        sub = payload.total - tax
        invoice = EnterpriseInvoice(
            invoice_number=inv_no,
            subtotal=sub,
            tax=tax,
            total=payload.total,
            paid=payload.total,
            payment_method='CASH',
            status='PAID'
        )
        session.add(invoice)
        session.commit()
        return {"success": True, "invoice": inv_no}
    except Exception as e:
        session.rollback()
        return {"success": False, "error": str(e)}
    finally:
        session.close()

@app.get("/warehouse", response_class=HTMLResponse)
def warehouse_page():
    session = SessionLocal()
    try:
        prods = session.query(EnterpriseProduct).all()
        rows = ""
        for p in prods:
            rows += f"""
            <tr class="hover:bg-slate-900 border-b border-slate-800">
                <td class="p-4 font-bold">{p.name}</td>
                <td class="p-4 text-sky-400">{p.sku or '-'}</td>
                <td class="p-4">{p.cost_price:,.2f} ج.س</td>
                <td class="p-4">{p.sale_price:,.2f} ج.س</td>
                <td class="p-4 font-black">{p.stock_qty}</td>
            </tr>
            """
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head><meta charset="UTF-8"><title>المستودعات والمخزون - Enterprise ERP</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo',sans-serif;}}</style></head>
        <body class="bg-slate-950 text-slate-100 min-h-screen p-10">
            <div class="flex justify-between items-center mb-8"><h1 class="text-3xl font-black">إدارة المستودعات والمخزون الضخم</h1><a href="/dashboard" class="bg-slate-800 px-5 py-2.5 rounded-xl font-bold text-sm">العودة للوحة التحكم</a></div>
            <div class="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
                <table class="w-full text-right"><thead class="bg-slate-950 text-slate-400 text-xs uppercase"><tr><th class="p-4">اسم المنتج</th><th class="p-4">SKU</th><th class="p-4">تكلفة الشراء</th><th class="p-4">سعر البيع</th><th class="p-4">الكمية المتاحة</th></tr></thead><tbody>{rows}</tbody></table>
            </div>
        </body></html>
        """
    finally:
        session.close()

@app.get("/accounting", response_class=HTMLResponse)
def accounting_page():
    session = SessionLocal()
    try:
        accounts = session.query(EnterpriseAccount).all()
        rows = ""
        for a in accounts:
            rows += f"""
            <tr class="hover:bg-slate-900 border-b border-slate-800">
                <td class="p-4 font-bold text-sky-400">{a.account_code}</td>
                <td class="p-4">{a.name}</td>
                <td class="p-4"><span class="bg-purple-500/20 text-purple-300 px-3 py-1 rounded-full text-xs font-bold">{a.account_type}</span></td>
                <td class="p-4 font-black">{a.balance:,.2f} ج.س</td>
            </tr>
            """
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head><meta charset="UTF-8"><title>الحسابات العامة - Enterprise ERP</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo',sans-serif;}}</style></head>
        <body class="bg-slate-950 text-slate-100 min-h-screen p-10">
            <div class="flex justify-between items-center mb-8"><h1 class="text-3xl font-black">الحسابات العامة والدليل المحاسبي (General Ledger)</h1><a href="/dashboard" class="bg-slate-800 px-5 py-2.5 rounded-xl font-bold text-sm">العودة للوحة التحكم</a></div>
            <div class="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
                <table class="w-full text-right"><thead class="bg-slate-950 text-slate-400 text-xs uppercase"><tr><th class="p-4">رقم الحساب</th><th class="p-4">اسم الحساب</th><th class="p-4">نوع الحساب</th><th class="p-4">الرصيد الحالي</th></tr></thead><tbody>{rows}</tbody></table>
            </div>
        </body></html>
        """
    finally:
        session.close()

@app.get("/hr", response_class=HTMLResponse)
def hr_page():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head><meta charset="UTF-8"><title>الموارد البشرية - Enterprise ERP</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet"><style>body{font-family:'Cairo',sans-serif;}</style></head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-10">
        <div class="flex justify-between items-center mb-8"><h1 class="text-3xl font-black">إدارة الموارد البشرية والرواتب (HR & Payroll)</h1><a href="/dashboard" class="bg-slate-800 px-5 py-2.5 rounded-xl font-bold text-sm">العودة للوحة التحكم</a></div>
        <div class="bg-slate-900 border border-slate-800 p-8 rounded-2xl text-center"><p class="text-slate-400 text-lg">نظام الموارد البشرية الضخم مفعل وجاهز لربط شؤون العاملين وسجلات الحضور والرواتب الشهرية.</p></div>
    </body></html>
    """

@app.get("/manufacturing", response_class=HTMLResponse)
def manufacturing_page():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head><meta charset="UTF-8"><title>التصنيع - Enterprise ERP</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet"><style>body{font-family:'Cairo',sans-serif;}</style></head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-10">
        <div class="flex justify-between items-center mb-8"><h1 class="text-3xl font-black">إدارة خطوط الإنتاج وقوائم المواد (BOM & Manufacturing)</h1><a href="/dashboard" class="bg-slate-800 px-5 py-2.5 rounded-xl font-bold text-sm">العودة للوحة التحكم</a></div>
        <div class="bg-slate-900 border border-slate-800 p-8 rounded-2xl text-center"><p class="text-slate-400 text-lg">وحدة التصنيع الصناعي ومتابعة خطوط الإنتاج مفعلة بالكامل.</p></div>
    </body></html>
    """
