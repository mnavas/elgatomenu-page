#!/usr/bin/env python3
"""
ElGatoMenu — Ejemplo: Chifa El Dragón de Oro
Carga una carta típica de chifa ecuatoriano.

Uso:
    python load_chifa.py

Variables de entorno opcionales:
    ELGATOMENU_HOST   — IP y puerto de ElGatoMenu (default: http://localhost:3000)
    ELGATOMENU_EMAIL  — correo del administrador
    ELGATOMENU_PASS   — contraseña del administrador
"""

import os
import sys
import json
import getpass
import urllib.request
import urllib.parse
import urllib.error

# ── Configuración ────────────────────────────────────────────────────────────

BASE = os.environ.get("ELGATOMENU_HOST", "http://localhost:3000").rstrip("/")
EMAIL = os.environ.get("ELGATOMENU_EMAIL", "")
PASS  = os.environ.get("ELGATOMENU_PASS", "")

# ── Carta del restaurante ────────────────────────────────────────────────────

RESTAURANT_NAME = "Chifa El Dragón de Oro"

MENU = [
    {
        "category": "🍜 Sopas y entradas",
        "items": [
            ("Wantán frito",          3.50, "8 piezas de wantán crujiente con salsa agridulce", "🥟"),
            ("Sopa wantán",           4.00, "Caldo con wantanes rellenos de cerdo y camarón",   "🍜"),
            ("Rollos primavera",      3.00, "2 rollos de verduras con salsa de soya",           "🌯"),
            ("Sopa de pollo con maíz", 3.50, "Crema de pollo con choclo y huevo",              "🌽"),
        ]
    },
    {
        "category": "🍚 Arroces y chaulafanes",
        "items": [
            ("Chaulafán de pollo",    7.50, "Arroz frito con pollo, huevo, cebolla y soya",     "🍗"),
            ("Chaulafán mixto",       9.00, "Arroz frito con pollo, camarón y cerdo",           "🍚"),
            ("Chaulafán de camarón",  9.50, "Arroz frito con camarones salteados",              "🦐"),
            ("Chaulafán de chancho",  8.00, "Arroz frito con cerdo asado y vegetales",          "🐷"),
            ("Arroz blanco",          1.50, "Porción de arroz blanco al vapor",                 "🍙"),
        ]
    },
    {
        "category": "🥘 Platos fuertes",
        "items": [
            ("Tallarin saltado de pollo",   8.00, "Fideos con pollo, pimientos y salsa de ostión", "🍝"),
            ("Tallarin saltado mixto",       9.50, "Fideos con pollo, camarón y cerdo",            "🍝"),
            ("Lomo saltado",                 9.00, "Lomo de res salteado con tomate y papa",       "🥩"),
            ("Chancho al vapor",             8.50, "Cerdo al vapor con salsa de ciruela",          "🐖"),
            ("Pollo al limón",               8.00, "Pechuga apanada con salsa de limón",           "🍋"),
            ("Cerdo agridulce",              8.50, "Trozos de cerdo en salsa agridulce con piña",  "🍍"),
            ("Camarones con brócoli",        9.50, "Camarones salteados con brócoli y salsa",      "🥦"),
        ]
    },
    {
        "category": "🥢 Acompañantes",
        "items": [
            ("Wantán sopa adicional",  1.50, "Porción adicional de wantanes",    "🥟"),
            ("Verduras salteadas",     3.00, "Mix de verduras con salsa de soya", "🥬"),
        ]
    },
    {
        "category": "🥤 Bebidas",
        "items": [
            ("Té chino caliente",  1.50, "Té verde o negro servido en tetera",           "🍵"),
            ("Jugo de mora",       2.00, "Jugo natural de mora con o sin azúcar",        "🫐"),
            ("Jugo de naranjilla", 2.00, "Jugo natural de naranjilla fresca",            "🍊"),
            ("Gaseosa",            1.50, "Coca-Cola, Sprite o Fanta 350 ml",             "🥤"),
            ("Agua mineral",       1.00, "Agua con o sin gas 500 ml",                    "💧"),
        ]
    },
]

# ── Helpers HTTP ─────────────────────────────────────────────────────────────

session_token = None

def _request(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Cookie"] = token
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            # capture Set-Cookie on login
            cookie = r.getheader("Set-Cookie")
            return json.loads(raw) if raw else {}, cookie
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        print(f"  ✗ HTTP {e.code} {method} {path}: {body_text[:200]}")
        sys.exit(1)

def login(email, password):
    resp, cookie = _request("POST", "/api/auth/login",
                             {"email": email, "password": password})
    if not cookie:
        print("  ✗ Login fallido — verifica tus credenciales")
        sys.exit(1)
    # Keep only the session part (first directive)
    return cookie.split(";")[0]

def create_category(name, token):
    resp, _ = _request("POST", "/api/menu/categories", {"name": name}, token)
    return resp.get("id") or resp.get("data", {}).get("id")

def create_item(category_id, name, price, description, emoji, token):
    _request("POST", "/api/menu/items", {
        "category_id": category_id,
        "name": name,
        "price": price,
        "description": description,
        "emoji": emoji,
    }, token)

# ── Punto de entrada ─────────────────────────────────────────────────────────

def main():
    global EMAIL, PASS

    print(f"\n🍜  ElGatoMenu — Cargando carta: {RESTAURANT_NAME}")
    print(f"    Servidor: {BASE}\n")

    if not EMAIL:
        EMAIL = input("  Correo del administrador: ").strip()
    if not PASS:
        PASS = getpass.getpass("  Contraseña: ")

    print("\n  Iniciando sesión...")
    token = login(EMAIL, PASS)
    print("  ✓ Sesión iniciada\n")

    for section in MENU:
        cat_name = section["category"]
        print(f"  Categoría: {cat_name}")
        cat_id = create_category(cat_name, token)
        if not cat_id:
            print(f"    ✗ No se pudo crear la categoría. Verifica que tienes acceso de admin.")
            sys.exit(1)
        for name, price, desc, emoji in section["items"]:
            create_item(cat_id, name, price, desc, emoji, token)
            print(f"    ✓ {emoji} {name}  —  ${price:.2f}")
        print()

    print(f"  ✅ Carta '{RESTAURANT_NAME}' cargada correctamente.")
    print(f"     Abre {BASE} para verla.\n")

if __name__ == "__main__":
    main()
