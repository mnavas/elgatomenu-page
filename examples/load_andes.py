#!/usr/bin/env python3
"""
MishiMenu — Ejemplo: Picantería La Sierra Encantada
Carga una carta típica de comida serrana andina ecuatoriana.

Uso:
    python load_andes.py

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

RESTAURANT_NAME = "Picantería La Sierra Encantada"

MENU = [
    {
        "category": "🥣 Sopas y caldos",
        "items": [
            ("Caldo de patas",      4.50, "Caldo de pata de res con maní, maíz y hierbas serranas",    "🦴"),
            ("Yaguarlocro",         5.00, "Locro de papas con sangre cocinada, aguacate y tostado",    "🥔"),
            ("Locro de papa",       4.00, "Sopa cremosa de papa con queso, aguacate y tostado",        "🧀"),
            ("Caldo de 31",         4.50, "Caldo de panza de res con hierbas y papas",                 "🍲"),
            ("Sopa de quinua",      3.50, "Sopa andina de quinua con papas y verduras de temporada",   "🌾"),
        ]
    },
    {
        "category": "🍽️ Platos fuertes",
        "items": [
            ("Seco de pollo",               7.00, "Pollo en salsa criolla con arroz, fréjol y aguacate",    "🍗"),
            ("Fritada completa",            8.50, "Cerdo fritado con mote, tostado, choclo y plátano",      "🐷"),
            ("Llapingachos con hornado",    8.00, "Tortillas de papa con carne de hornado y ensalada",      "🥔"),
            ("Cuy asado",                  12.00, "Cuy entero asado a la brasa con papas y ají de pepa",    "🐾"),
            ("Churrasco serrano",           9.00, "Bistec a la plancha con huevo, papas y ensalada",        "🥩"),
            ("Trucha frita",                8.00, "Trucha de río frita entera con papas y ensalada",        "🐟"),
            ("Hornado de chancho",          9.00, "Cerdo al horno con mote, tortillas y llapingachos",      "🍖"),
        ]
    },
    {
        "category": "🌽 Entradas y snacks",
        "items": [
            ("Mote con chicharrón",  4.00, "Mote cocinado con chicharrón de cerdo crujiente", "🌽"),
            ("Tostado con queso",    3.00, "Maíz tostado con queso fresco de hacienda",       "🧀"),
            ("Empanadas de viento",  2.50, "3 empanadas fritas de harina con queso y azúcar", "🫓"),
            ("Humitas",              2.00, "2 humitas de choclo tierno al vapor",              "🌽"),
        ]
    },
    {
        "category": "🍮 Postres",
        "items": [
            ("Colada morada",       2.50, "Bebida morada de granos y frutas, servida caliente",          "🍷"),
            ("Guaguas de pan",      1.50, "Pan dulce con forma tradicional, 2 unidades",                "🍞"),
            ("Buñuelos con miel",   3.00, "Buñuelos fritos bañados en miel de panela",                  "🍯"),
            ("Pristiños",           2.50, "Fritura dulce con miel de panela, 3 unidades",               "🍪"),
            ("Helado de paila",     2.50, "Helado artesanal batido en paila de cobre, sabores mixtos",  "🍨"),
        ]
    },
    {
        "category": "🥤 Bebidas",
        "items": [
            ("Chicha de jora",          2.00, "Chicha artesanal fermentada de maíz, servida fría", "🍺"),
            ("Colada de avena",         1.50, "Bebida caliente de avena con canela y panela",      "☕"),
            ("Jugo de tomate de árbol", 2.00, "Jugo natural de tomate de árbol con o sin azúcar", "🍅"),
            ("Jugo de taxo",            2.00, "Jugo natural de taxo fresco de la sierra",         "🍋"),
            ("Jugo de mora",            2.00, "Jugo de mora negra con o sin azúcar",              "🫐"),
            ("Agua aromática",          1.00, "Infusión de cedrón, hierba luisa o manzanilla",    "🍵"),
            ("Gaseosa",                 1.50, "Coca-Cola, Sprite o Fanta 350 ml",                 "🥤"),
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

    print(f"\n🏔️  MishiMenu — Cargando carta: {RESTAURANT_NAME}")
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
