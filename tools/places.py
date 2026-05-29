import requests
from langchain_core.tools import tool

NOMINATIM_URL = "https://nominatim.openstreetmap.org"
HEADERS = {"User-Agent": "TolikBot/1.0"}


@tool
def find_place(query: str) -> str:
    """Знайти місце за назвою або адресою (геокодинг). Наприклад: 'Київ, Хрещатик 1' або 'Ейфелева вежа'."""
    resp = requests.get(
        f"{NOMINATIM_URL}/search",
        params={"q": query, "format": "json", "limit": 3, "accept-language": "uk"},
        headers=HEADERS,
    )
    resp.raise_for_status()
    results = resp.json()
    if not results:
        return f"Нічого не знайдено за запитом '{query}'."

    lines = []
    for r in results:
        lines.append(
            f"📍 {r['display_name']}\n"
            f"   📌 {r['lat']}, {r['lon']}"
        )
    return "\n".join(lines)


@tool
def find_nearby(category: str) -> str:
    """Знайти найближчі місця за категорією навколо координат.
    lat, lon — координати.
    category — що шукати (наприклад: 'pharmacy', 'shop', 'cafe', 'hospital', 'shelter', 'supermarket', 'atm').
    """
    CATEGORY_MAP = {
        "pharmacy": "[amenity=pharmacy]",
        "shop": "[shop]",
        "cafe": "[amenity=cafe]",
        "restaurant": "[amenity=restaurant]",
        "hospital": "[amenity=hospital]",
        "shelter": "[amenity=shelter]",
        "supermarket": "[shop=supermarket]",
        "atm": "[amenity=atm]",
        "bar": "[amenity=bar]",
        "toilet": "[amenity=toilets]",
        "water": "[amenity=drinking_water]",
        "bank": "[amenity=bank]",
    }

    tag = CATEGORY_MAP.get(category.lower())
    if not tag:
        available = ", ".join(sorted(CATEGORY_MAP))
        return f"Невідома категорія '{category}'. Доступні: {available}"

    radius = 1500
    query = f"""
    [out:json][timeout:10];
    (
      node{tag}(around:{radius},{lat},{lon});
    );
    out body 5;
    """
    resp = requests.post(
        "https://overpass-api.de/api/interpreter",
        data={"data": query},
    )
    resp.raise_for_status()
    elements = resp.json().get("elements", [])

    if not elements:
        return f"Нічого не знайдено в радіусі {radius}м."

    lines = [f"📍 Знайдено {len(elements)} ({category}) в радіусі {radius}м:"]
    for el in elements:
        name = el.get("tags", {}).get("name", "без назви")
        addr = el.get("tags", {}).get("addr:street", "")
        house = el.get("tags", {}).get("addr:housenumber", "")
        addr_str = f", {addr} {house}".strip(", ") if addr else ""
        lines.append(f"  • {name}{addr_str}")
    return "\n".join(lines)
