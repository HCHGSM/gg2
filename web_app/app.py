# -*- coding: utf-8 -*-
"""
=============================================================================
Project: Ultra-Advanced Enterprise POS & ERP Web Application
File: web_app/app.py
Description: FastAPI backend server serving modern responsive web interface
             and API endpoints for POS, Sales, Products, Inventory, and Dashboard.
=============================================================================
"""

import os
import time
import uuid
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional

from pos_erp.database.db import init_db, SessionLocal
from pos_erp.database.models import User, Product, Sale
from pos_erp.services.auth_service import AuthService
from pos_erp.services.product_service import ProductService
from pos_erp.services.sales_service import SalesService
from pos_erp.services.report_service import ReportService
from pos_erp.services.finance_service import FinanceService

app = FastAPI(title="Smart POS & ERP Web App", version="2.0.0")

# Initialize DB on startup
@app.on_event("startup")
def startup_event():
    init_db()

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    return response

templates = Jinja2Templates(directory="web_app/templates")

# --- Session handling -------------------------------------------------------
# In-memory store: fine for a single-process deployment (matches how this app
# is actually run today). If this is ever scaled to multiple worker processes,
# swap this for a shared store (e.g. Redis) since sessions won't be visible
# across processes otherwise — noted in deployment guide.
SESSION_TTL_SECONDS = int(os.environ.get('POS_ERP_SESSION_TTL', 8 * 3600))  # 8 hours
IS_PRODUCTION = os.environ.get('POS_ERP_ENV', 'development').lower() == 'production'

active_sessions = {}  # token -> {"user_id": int, "expires_at": float}

def _cleanup_expired_sessions():
    now = time.time()
    expired = [t for t, s in active_sessions.items() if s["expires_at"] < now]
    for t in expired:
        del active_sessions[t]

def create_session(user_id: int) -> str:
    _cleanup_expired_sessions()
    token = str(uuid.uuid4())
    active_sessions[token] = {"user_id": user_id, "expires_at": time.time() + SESSION_TTL_SECONDS}
    return token

def set_session_cookie(response, token: str):
    response.set_cookie(
        key="session_token",
        value=token,
        max_age=SESSION_TTL_SECONDS,
        httponly=True,          # not readable from JS -> mitigates XSS token theft
        samesite="lax",         # mitigates basic CSRF via cross-site navigation
        secure=IS_PRODUCTION,   # only sent over HTTPS once deployed behind TLS
    )

# --- Basic login rate limiting -----------------------------------------------
# Blunts brute-force password guessing. Keyed by client IP; resets on success.
LOGIN_ATTEMPT_LIMIT = 5
LOGIN_ATTEMPT_WINDOW_SECONDS = 15 * 60
_login_attempts = {}  # ip -> [timestamps]

def _too_many_login_attempts(ip: str) -> bool:
    now = time.time()
    attempts = [t for t in _login_attempts.get(ip, []) if now - t < LOGIN_ATTEMPT_WINDOW_SECONDS]
    _login_attempts[ip] = attempts
    return len(attempts) >= LOGIN_ATTEMPT_LIMIT

def _record_login_attempt(ip: str):
    _login_attempts.setdefault(ip, []).append(time.time())

def _reset_login_attempts(ip: str):
    _login_attempts.pop(ip, None)

def get_current_user(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token or session_token not in active_sessions:
        return None
    entry = active_sessions[session_token]
    if entry["expires_at"] < time.time():
        del active_sessions[session_token]
        return None
    session = SessionLocal()
    try:
        return session.query(User).get(entry["user_id"])
    finally:
        session.close()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    client_ip = request.client.host if request.client else "unknown"

    if _too_many_login_attempts(client_ip):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "محاولات كثيرة جداً، حاول مرة أخرى لاحقاً"},
            status_code=429,
        )

    user, msg = AuthService.authenticate(username, password)
    if not user:
        _record_login_attempt(client_ip)
        return templates.TemplateResponse("login.html", {"request": request, "error": msg})

    _reset_login_attempts(client_ip)
    token = create_session(user.id)

    response = RedirectResponse(url="/dashboard", status_code=303)
    set_session_cookie(response, token)
    return response

@app.get("/logout")
def logout(request: Request):
    token = request.cookies.get("session_token")
    if token in active_sessions:
        del active_sessions[token]
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_token")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    stats = ReportService.get_dashboard_stats()
    recent_sales = SalesService.get_all_sales()[:15]
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "stats": stats,
        "recent_sales": recent_sales
    })

@app.get("/pos", response_class=HTMLResponse)
def pos_terminal(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    products = ProductService.get_all_products()
    return templates.TemplateResponse("pos.html", {
        "request": request,
        "user": user,
        "products": products
    })

class SaleItemSchema(BaseModel):
    product_id: int
    quantity: float
    unit_price: float
    discount: float = 0.0
    tax: float = 0.0

class SaleSchema(BaseModel):
    sale_data: dict
    items_data: List[SaleItemSchema]

@app.post("/api/sales")
def api_create_sale(payload: SaleSchema, request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    items_dicts = [item.dict() for item in payload.items_data]
    success, invoice_no, msg = SalesService.create_sale(payload.sale_data, items_dicts, user.id)
    if success:
        return {"success": True, "invoice_number": invoice_no, "message": msg}
    else:
        return {"success": False, "message": msg}

@app.get("/products", response_class=HTMLResponse)
def products_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)
    products = ProductService.get_all_products()
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "stats": ReportService.get_dashboard_stats(), "recent_sales": []})

@app.get("/inventory", response_class=HTMLResponse)
def inventory_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/customers", response_class=HTMLResponse)
def customers_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/suppliers", response_class=HTMLResponse)
def suppliers_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/expenses", response_class=HTMLResponse)
def expenses_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/dashboard", status_code=303)
