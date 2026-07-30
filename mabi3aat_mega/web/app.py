# -*- coding: utf-8 -*-
"""
=============================================================================
Module: mabi3aat_mega/web/app.py
Description: FastAPI Backend Server replicating and upgrading Mabi3aat.com
             Using 100% robust HTMLResponse for bulletproof operation.
=============================================================================
"""

import uuid
import bcrypt
from datetime import datetime
from typing import List
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel

from mabi3aat_mega.core.database import (
    init_mabi3aat_db, SessionLocal, User, Product, Category, ShippingZone, OnlineOrder, Sale, Expense, Customer
)

app = FastAPI(title="مبيعات دوت كوم - النظام الإمبراطوري المتكامل", version="6.0.0")

@app.on_event("startup")
def startup():
    init_mabi3aat_db()

sessions = {}

def get_logged_user(request: Request):
    token = request.cookies.get("mabi3aat_token")
    if not token or token not in sessions:
        return None
    uid = sessions[token]
    session = SessionLocal()
    try:
        return session.get(User, uid)
    finally:
        session.close()

@app.get("/", response_class=HTMLResponse)
def index(request: Request, error: str = None):
    user = get_logged_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    
    err_div = f'<div class="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded-xl mb-6 text-sm text-center">{error}</div>' if error else ''
    
    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>تسجيل الدخول - مبيعات دوت كوم</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Cairo', sans-serif; }}</style>
    </head>
    <body class="bg-gradient-to-tr from-slate-900 via-indigo-950 to-blue-950 min-h-screen flex items-center justify-center p-6">
        <div class="bg-white/10 backdrop-blur-2xl border border-white/20 p-10 rounded-3xl shadow-2xl w-full max-w-md text-white">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-black bg-gradient-to-r from-sky-400 to-indigo-400 bg-clip-text text-transparent">مبيعات دوت كوم</h1>
                <p class="text-slate-300 text-sm mt-2">نظام إدارة المبيعات، الكاشير، والمتجر الإلكتروني</p>
            </div>
            {err_div}
            <form action="/login" method="POST" class="space-y-5">
                <div>
                    <label class="block text-sm font-bold text-slate-200 mb-2">اسم المستخدم</label>
                    <input type="text" name="username" required value="admin" class="w-full bg-slate-900/60 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-sky-500">
                </div>
                <div>
                    <label class="block text-sm font-bold text-slate-200 mb-2">كلمة المرور</label>
                    <input type="password" name="password" required value="admin123" class="w-full bg-slate-900/60 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-sky-500">
                </div>
                <button type="submit" class="w-full bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-600 hover:to-blue-700 text-white font-black py-4 rounded-xl shadow-lg transition duration-200">
                    تسجيل الدخول
                </button>
            </form>
            <div class="mt-8 text-center text-xs text-slate-400 border-t border-white/10 pt-4">
                الحساب الافتراضي: <span class="text-sky-400 font-bold">admin</span> / <span class="text-sky-400 font-bold">admin123</span>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return index(request, error="اسم المستخدم أو كلمة المرور غير صحيحة")
        
        token = str(uuid.uuid4())
        sessions[token] = user.id
        resp = RedirectResponse(url="/dashboard", status_code=303)
        resp.set_cookie(key="mabi3aat_token", value=token)
        return resp
    finally:
        session.close()

@app.get("/logout")
def logout(request: Request):
    token = request.cookies.get("mabi3aat_token")
    if token in sessions:
        del sessions[token]
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie("mabi3aat_token")
    return resp

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = get_logged_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    session = SessionLocal()
    try:
        sales = session.query(Sale).all()
        total_sales = sum(s.total for s in sales)
        total_profit = sum(s.total * 0.35 for s in sales)
        products_count = session.query(Product).count()
        orders_count = session.query(OnlineOrder).count()
        recent_sales = session.query(Sale).order_by(Sale.created_at.desc()).limit(10).all()

        rows_html = ""
        for s in recent_sales:
            rows_html += f"""
            <tr class="hover:bg-slate-50 border-b border-slate-100">
                <td class="p-3 font-bold text-sky-600">{s.invoice_number}</td>
                <td class="p-3">{s.total:,.2f} ج.س</td>
                <td class="p-3">{s.paid_amount:,.2f} ج.س</td>
                <td class="p-3"><span class="bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full text-xs font-bold">{s.payment_method}</span></td>
                <td class="p-3 text-slate-400 text-xs">{s.created_at}</td>
            </tr>
            """

        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>لوحة التحكم - مبيعات دوت كوم</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet">
            <style>body {{ font-family: 'Cairo', sans-serif; }}</style>
        </head>
        <body class="bg-slate-50 text-slate-800 min-h-screen flex">
            <aside class="w-72 bg-slate-900 text-slate-300 flex flex-col justify-between border-l border-slate-800">
                <div>
                    <div class="p-6 text-xl font-black text-white border-b border-slate-800 bg-gradient-to-r from-sky-500 to-indigo-600 bg-clip-text text-transparent">
                        مبيعات دوت كوم
                    </div>
                    <nav class="p-4 space-y-2">
                        <a href="/dashboard" class="flex items-center gap-3 px-4 py-3 rounded-xl bg-sky-600 text-white font-bold shadow-lg">📊 لوحة التحكم</a>
                        <a href="/pos" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800 hover:text-white transition">💳 شاشة البيع (الكاشير)</a>
                        <a href="/products" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800 hover:text-white transition">📦 المنتجات والمخزون</a>
                    </nav>
                </div>
                <div class="p-4 border-t border-slate-800">
                    <a href="/logout" class="block py-3 rounded-xl bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-white transition font-bold text-center text-sm">🚪 تسجيل الخروج</a>
                </div>
            </aside>

            <main class="flex-1 flex flex-col min-w-0">
                <header class="bg-white border-b border-slate-200 px-8 py-4 flex justify-between items-center shadow-xs">
                    <h1 class="text-2xl font-black text-slate-800">لوحة التحكم والتحليلات الزمنية</h1>
                    <span class="bg-sky-100 text-sky-700 px-4 py-1 rounded-full text-sm font-bold">👤 {user.full_name}</span>
                </header>

                <div class="p-8 space-y-8">
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm border-r-4 border-r-blue-500">
                            <p class="text-xs font-bold text-slate-400 uppercase">إجمالي المبيعات</p>
                            <h3 class="text-2xl font-black text-blue-600 mt-2">{total_sales:,.2f} ج.س</h3>
                        </div>
                        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm border-r-4 border-r-emerald-500">
                            <p class="text-xs font-bold text-slate-400 uppercase">صافي الأرباح التقديرية</p>
                            <h3 class="text-2xl font-black text-emerald-600 mt-2">{total_profit:,.2f} ج.س</h3>
                        </div>
                        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm border-r-4 border-r-indigo-500">
                            <p class="text-xs font-bold text-slate-400 uppercase">إجمالي المنتجات</p>
                            <h3 class="text-2xl font-black text-indigo-600 mt-2">{products_count} منتج</h3>
                        </div>
                        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm border-r-4 border-r-amber-500">
                            <p class="text-xs font-bold text-slate-400 uppercase">الطلبات أونلاين</p>
                            <h3 class="text-2xl font-black text-amber-600 mt-2">{orders_count} طلب</h3>
                        </div>
                    </div>

                    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden p-6">
                        <h3 class="text-lg font-extrabold text-slate-800 mb-4">أحدث الفواتير المسجلة</h3>
                        <table class="w-full text-right">
                            <thead>
                                <tr class="text-slate-400 border-b border-slate-100 text-xs font-bold uppercase">
                                    <th class="p-3">رقم الفاتورة</th>
                                    <th class="p-3">الإجمالي النهائي</th>
                                    <th class="p-3">المبلغ المدفوع</th>
                                    <th class="p-3">طريقة الدفع</th>
                                    <th class="p-3">التاريخ</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100 text-sm font-semibold">
                                {rows_html if rows_html else '<tr><td colspan="5" class="p-6 text-center text-slate-400">لا توجد مبيعات بعد</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>
        </body>
        </html>
        """
    finally:
        session.close()

@app.get("/pos", response_class=HTMLResponse)
def pos_screen(request: Request):
    user = get_logged_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    session = SessionLocal()
    try:
        products = session.query(Product).all()
        pinned_cards = ""
        all_cards = ""
        for p in products:
            card_html = f"""
            <div onclick="addProd({p.id}, '{p.name}', {p.selling_price}, {p.quantity})" class="bg-white p-4 rounded-xl border border-slate-200 shadow-xs hover:border-sky-500 cursor-pointer transition flex flex-col justify-between">
                <div>
                    <h5 class="font-bold text-slate-800 text-sm">{p.name}</h5>
                    <p class="text-xs text-slate-400 mt-1">المخزون: <span class="font-bold text-slate-600">{p.quantity}</span></p>
                </div>
                <div class="mt-4 pt-2 border-t border-slate-100 flex justify-between items-center">
                    <span class="text-sky-600 font-black">{p.selling_price:,.2f} ج.س</span>
                    <span class="bg-sky-50 text-sky-600 font-bold text-xs px-2.5 py-1 rounded-lg">إضافة</span>
                </div>
            </div>
            """
            all_cards += card_html
            if p.is_pinned:
                pinned_cards += card_html

        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>شاشة البيع والكاشير - مبيعات دوت كوم</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet">
            <style>body {{ font-family: 'Cairo', sans-serif; }}</style>
        </head>
        <body class="bg-slate-50 text-slate-800 min-h-screen flex">
            <aside class="w-64 bg-slate-900 text-slate-300 flex flex-col justify-between border-l border-slate-800">
                <div>
                    <div class="p-6 text-xl font-black text-white border-b border-slate-800">مبيعات دوت كوم</div>
                    <nav class="p-4 space-y-2">
                        <a href="/dashboard" class="block px-4 py-3 rounded-xl hover:bg-slate-800 transition">📊 لوحة التحكم</a>
                        <a href="/pos" class="block px-4 py-3 rounded-xl bg-sky-600 text-white font-bold shadow-lg">💳 شاشة البيع (الكاشير)</a>
                        <a href="/products" class="block px-4 py-3 rounded-xl hover:bg-slate-800 transition">📦 المنتجات والمخزون</a>
                    </nav>
                </div>
                <div class="p-4 border-t border-slate-800">
                    <a href="/logout" class="block py-3 rounded-xl bg-red-500/10 text-red-400 text-center font-bold text-sm">🚪 تسجيل الخروج</a>
                </div>
            </aside>

            <main class="flex-1 flex flex-col min-w-0">
                <header class="bg-white border-b border-slate-200 px-8 py-4 flex justify-between items-center shadow-xs">
                    <h1 class="text-xl font-black text-slate-800">شاشة البيع السريع (POS Cashier)</h1>
                    <span class="bg-sky-100 text-sky-700 px-4 py-1 rounded-full text-sm font-bold">👤 {user.full_name}</span>
                </header>

                <div class="p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
                    <div class="lg:col-span-7 flex flex-col space-y-4">
                        <input type="text" id="searchInput" placeholder="🔍 مسح الباركود أو البحث باسم الصنف..." class="w-full bg-white border border-slate-300 rounded-xl px-4 py-3 shadow-xs focus:ring-2 focus:ring-sky-500">
                        
                        <div>
                            <h4 class="text-xs font-bold text-slate-400 uppercase mb-2">المنتجات المثبتة للوصول السريع</h4>
                            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                                {pinned_cards}
                            </div>
                        </div>

                        <div class="mt-4">
                            <h4 class="text-xs font-bold text-slate-400 uppercase mb-2">جميع المنتجات</h4>
                            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 overflow-y-auto max-h-[350px]">
                                {all_cards}
                            </div>
                        </div>
                    </div>

                    <div class="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                        <div>
                            <h3 class="text-lg font-extrabold text-slate-800 mb-4 pb-2 border-b border-slate-100">سلة الطلب الحالية</h3>
                            <div id="cartItems" class="space-y-3 overflow-y-auto max-h-[320px]">
                                <p class="text-slate-400 text-center py-10 text-sm">السلة فارغة</p>
                            </div>
                        </div>

                        <div class="border-t border-slate-200 pt-4 mt-4 space-y-2">
                            <div class="flex justify-between text-sm font-semibold text-slate-600">
                                <span>المجموع الفرعي:</span>
                                <span id="subtotalText">0.00 ج.س</span>
                            </div>
                            <div class="flex justify-between text-sm font-semibold text-slate-600">
                                <span>الضريبة (15%):</span>
                                <span id="taxText">0.00 ج.س</span>
                            </div>
                            <div class="flex justify-between text-lg font-black text-slate-900 border-t border-slate-100 pt-2">
                                <span>الإجمالي النهائي:</span>
                                <span id="totalText" class="text-sky-600">0.00 ج.س</span>
                            </div>

                            <button onclick="submitCheckout()" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-black py-4 rounded-xl shadow-lg shadow-emerald-600/20 transition mt-2">
                                ✅ إتمام البيع وطبع الفاتورة
                            </button>
                        </div>
                    </div>
                </div>
            </main>

            <script>
                const cart = [];
                function addProd(id, name, price, maxQty) {
                    let existing = cart.find(i => i.id === id);
                    if (existing) {
                        if (existing.qty + 1 > maxQty) { alert('الكمية تتجاوز المخزون!'); return; }
                        existing.qty++;
                    } else {
                        cart.push({ id, name, price, qty: 1, maxQty });
                    }
                    updateCartUI();
                }
                function removeProd(idx) {
                    cart.splice(idx, 1);
                    updateCartUI();
                }
                function updateCartUI() {
                    let container = document.getElementById('cartItems');
                    if (cart.length === 0) {
                        container.innerHTML = '<p class="text-slate-400 text-center py-10 text-sm">السلة فارغة</p>';
                        document.getElementById('subtotalText').innerText = '0.00 ج.س';
                        document.getElementById('taxText').innerText = '0.00 ج.س';
                        document.getElementById('totalText').innerText = '0.00 ج.س';
                        return;
                    }
                    let html = '';
                    let subtotal = 0;
                    cart.forEach((item, idx) => {
                        let tot = item.price * item.qty;
                        subtotal += tot;
                        html += '<div class="flex justify-between items-center bg-slate-50 p-3 rounded-xl border border-slate-200"><div><h5 class="font-bold text-slate-800 text-sm">' + item.name + '</h5><p class="text-xs text-sky-600 font-bold">' + item.price.toLocaleString() + ' × ' + item.qty + '</p></div><button onclick="removeProd(' + idx + ')" class="text-red-500 font-bold text-xs">🗑️ حذف</button></div>';
                    });
                    let tax = subtotal * 0.15;
                    let total = subtotal + tax;
                    container.innerHTML = html;
                    document.getElementById('subtotalText').innerText = subtotal.toLocaleString() + ' ج.س';
                    document.getElementById('taxText').innerText = tax.toLocaleString() + ' ج.س';
                    document.getElementById('totalText').innerText = total.toLocaleString() + ' ج.س';
                }
                async function submitCheckout() {
                    if (cart.length === 0) { alert('السلة فارغة!'); return; }
                    let subtotal = cart.reduce((s, i) => s + (i.price * i.qty), 0);
                    let tax = subtotal * 0.15;
                    let total = subtotal + tax;
                    let itemsData = cart.map(i => ({ product_id: i.id, quantity: i.qty, unit_price: i.price, tax: (i.price * i.qty) * 0.15 }));
                    let payload = { sale_data: { subtotal, tax_amount: tax, total, paid_amount: total, payment_method: 'CASH' }, items_data: itemsData };
                    let res = await fetch('/api/sale', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
                    let data = await res.json();
                    if (data.success) {
                        alert('تمت الفاتورة بنجاح! رقم الفاتورة: ' + data.invoice);
                        cart.length = 0;
                        updateCartUI();
                        location.reload();
                    } else {
                        alert('فشل إتمام البيع: ' + data.msg);
                    }
                }
            </script>
        </body>
        </html>
        """
    finally:
        session.close()

class ItemSchema(BaseModel):
    product_id: int
    quantity: float
    unit_price: float
    tax: float = 0.0

class SaleSchema(BaseModel):
    sale_data: dict
    items_data: List[ItemSchema]

@app.post("/api/sale")
def api_sale(payload: SaleSchema, request: Request):
    user = get_logged_user(request)
    if not user:
        raise HTTPException(status_code=401)

    session = SessionLocal()
    try:
        count = session.query(Sale).count() + 1
        inv_no = f"MAB-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
        
        sd = payload.sale_data
        sale = Sale(
            invoice_number=inv_no,
            subtotal=sd['subtotal'],
            tax_amount=sd['tax_amount'],
            total=sd['total'],
            paid_amount=sd['paid_amount'],
            payment_method=sd['payment_method']
        )
        session.add(sale)
        session.flush()

        for item in payload.items_data:
            p = session.get(Product, item.product_id)
            if not p or p.quantity < item.quantity:
                raise ValueError(f"الكمية غير متوفرة للمنتج: {p.name if p else 'مجهول'}")
            p.quantity -= item.quantity

        session.commit()
        return {"success": True, "invoice": inv_no}
    except Exception as e:
        session.rollback()
        return {"success": False, "msg": str(e)}
    finally:
        session.close()

@app.get("/products", response_class=HTMLResponse)
def products_page(request: Request):
    user = get_logged_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    session = SessionLocal()
    try:
        products = session.query(Product).all()
        rows = ""
        for p in products:
            rows += f"""
            <tr class="hover:bg-slate-50 border-b border-slate-100">
                <td class="p-3 font-bold">{p.name}</td>
                <td class="p-3 text-sky-600">{p.sku or '-'}</td>
                <td class="p-3">{p.selling_price:,.2f} ج.س</td>
                <td class="p-3 font-black">{p.quantity}</td>
            </tr>
            """
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>المنتجات والمخزون - مبيعات دوت كوم</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet">
            <style>body {{ font-family: 'Cairo', sans-serif; }}</style>
        </head>
        <body class="bg-slate-50 text-slate-800 min-h-screen p-10 space-y-6">
            <div class="flex justify-between items-center bg-white p-6 rounded-2xl border border-slate-200">
                <h1 class="text-2xl font-black">إدارة المنتجات وتتبع المخزون</h1>
                <a href="/dashboard" class="bg-slate-800 text-white px-4 py-2 rounded-xl text-xs font-bold">العودة للوحة التحكم</a>
            </div>
            <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                <table class="w-full text-right">
                    <thead>
                        <tr class="text-slate-400 text-xs uppercase border-b">
                            <th class="p-3">اسم المنتج</th>
                            <th class="p-3">SKU</th>
                            <th class="p-3">سعر البيع</th>
                            <th class="p-3">الكمية المتاحة</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y">{rows}</tbody>
                </table>
            </div>
        </body>
        </html>
        """
    finally:
        session.close()
