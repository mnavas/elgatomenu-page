#!/usr/bin/env python3
"""
MishiMenu — Ejemplo: Marisquería La Concha de Plata
Carga una carta típica de marisquería ecuatoriana de costa.

Uso:
    python load_marisqueria.py

Variables de entorno opcionales:
    MISHIMENU_HOST   — IP y puerto de MishiMenu (default: http://localhost:3000)
    MISHIMENU_EMAIL  — correo del administrador
    MISHIMENU_PASS   — contraseña del administrador
"""

import os
import sys
import json
import getpass
import urllib.request
import urllib.error

# ── Configuración ────────────────────────────────────────────────────────────

BASE  = os.environ.get("MISHIMENU_HOST", "http://localhost:3000").rstrip("/")
EMAIL = os.environ.get("MISHIMENU_EMAIL", "")
PASS  = os.environ.get("MISHIMENU_PASS", "")

# ── Carta del restaurante ────────────────────────────────────────────────────

RESTAURANT_NAME = "Marisquería La Concha de Plata"

MENU = [
    {
        "category": "🦞 Ceviches",
        "items": [
            ("Ceviche de camarón",       8.50, "Camarón mediano en limón, tomate y cebolla morada",        "🦐"),
            ("Ceviche mixto",            9.50, "Camarón, calamar, concha y pulpo en ceviche",              "🦑"),
            ("Ceviche de concha prieta", 8.00, "Conchas negras frescas con limón y tomate",               "🐚"),
            ("Ceviche de pescado",       7.50, "Corvina fresca en ceviche con chifles y cangil",          "🐟"),
            ("Ceviche de langostino",   12.00, "Langostinos enteros en ceviche clásico",                  "🦞"),
        ]
    },
    {
        "category": "🍲 Sopas y caldos",
        "items": [
            ("Encebollado",              4.50, "Caldo de albacora con yuca, cebolla y cilantro",           "🧅"),
            ("Sopa marinera",            8.00, "Caldo con camarón, concha, pescado y mejillones",         "🍲"),
            ("Caldo de bola de verde",   5.00, "Bola de verde rellena en caldo con chicharrón",           "🍵"),
            ("Sancocho de pescado",      6.50, "Caldo espeso con corvina, yuca y patacones",              "🐠"),
        ]
    },
    {
        "category": "🍤 Platos fuertes",
        "items": [
            ("Seco de camarón",          9.00, "Camarones en salsa criolla con arroz y patacones",        "🦐"),
            ("Jaiba al ajillo",         10.00, "Jaiba entera salteada con ajo, mantequilla y limón",      "🦀"),
            ("Pescado apanado",          8.00, "Filete de corvina apanado con ensalada y arroz",          "🐟"),
            ("Langostinos al vapor",    14.00, "Langostinos enteros al vapor con salsa de ajo",           "🦞"),
            ("Camarones apanados",       9.50, "Camarones jumbo apanados con papas y ensalada",           "🍤"),
            ("Arroz marinero",           9.00, "Arroz con mariscos mixtos en salsa de tomate",            "🍚"),
            ("Pescado a la plancha",     8.50, "Filete a la plancha con arroz, ensalada y patacón",       "🐠"),
            ("Mariscos al ajillo",      12.00, "Mezcla de mariscos salteados en salsa de ajo y limón",    "🧄"),
        ]
    },
    {
        "category": "🍟 Acompañantes",
        "items": [
            ("Patacones",        2.50, "Plátano verde frito, 4 unidades con ají",  "🍌"),
            ("Chifles",          2.00, "Plátano verde en chips con sal",           "🍟"),
            ("Arroz blanco",     1.50, "Porción de arroz blanco",                  "🍙"),
            ("Menestra de fréjol", 2.50, "Fréjol cocinado en salsa con culantro", "🫘"),
        ]
    },
    {
        "category": "🥤 Bebidas",
        "items": [
            ("Jugo de maracuyá", 2.00, "Jugo natural de maracuyá fresco con o sin azúcar", "🍹"),
            ("Jugo de sandía",   2.00, "Jugo natural de sandía fresca",                    "🍉"),
            ("Jugo de coco",     2.50, "Agua de coco natural",                             "🥥"),
            ("Cerveza nacional", 2.50, "Cerveza Pilsener o Club 600 ml bien fría",         "🍺"),
            ("Gaseosa",          1.50, "Coca-Cola, Sprite o Fanta 350 ml",                 "🥤"),
            ("Agua mineral",     1.00, "Agua con o sin gas 500 ml",                        "💧"),
        ]
    },
]

# ── Helpers HTTP ─────────────────────────────────────────────────────────────

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

    print(f"\n🦞  MishiMenu — Cargando carta: {RESTAURANT_NAME}")
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
            print(f"    ✗ No se pudo crear la categoría.")
            sys.exit(1)
        for name, price, desc, emoji in section["items"]:
            create_item(cat_id, name, price, desc, emoji, token)
            print(f"    ✓ {emoji} {name}  —  ${price:.2f}")
        print()

    print(f"  ✅ Carta '{RESTAURANT_NAME}' cargada correctamente.")
    print(f"     Abre {BASE} para verla.\n")

if __name__ == "__main__":
    main()
