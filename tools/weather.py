import requests
from langchain_core.tools import tool


GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def _geocode(city: str) -> tuple[float, float, str]:
    resp = requests.get(GEOCODE_URL, params={"name": city, "count": 1, "language": "uk"})
    resp.raise_for_status()
    results = resp.json().get("results")
    if not results:
        raise ValueError(f"Місто '{city}' не знайдено.")
    r = results[0]
    return r["latitude"], r["longitude"], r.get("name", city)


@tool
def get_weather(city: str) -> str:
    """Отримати поточну погоду у місті. Параметр city — назва міста (наприклад, 'Київ')."""
    try:
        lat, lon, name = _geocode(city)
    except ValueError as e:
        return str(e)

    resp = requests.get(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
                       "precipitation,wind_speed_10m,weather_code",
            "wind_speed_unit": "ms",
            "timezone": "auto",
        },
    )
    resp.raise_for_status()
    cur = resp.json()["current"]

    wmo = {
        0: "ясно ☀️", 1: "переважно ясно 🌤", 2: "хмарно з проясненнями ⛅",
        3: "похмуро ☁️", 45: "туман 🌫", 48: "іній 🌫",
        51: "мряка 🌦", 53: "мряка 🌦", 55: "сильна мряка 🌧",
        61: "невеликий дощ 🌧", 63: "дощ 🌧", 65: "сильний дощ 🌧",
        71: "невеликий сніг 🌨", 73: "сніг 🌨", 75: "сильний сніг ❄️",
        80: "зливи 🌧", 81: "зливи 🌧", 82: "сильні зливи ⛈",
        95: "гроза ⛈", 96: "гроза з градом ⛈", 99: "гроза з градом ⛈",
    }
    desc = wmo.get(cur["weather_code"], f"код {cur['weather_code']}")

    return (
        f"📍 {name}\n"
        f"🌡 Температура: {cur['temperature_2m']}°C (відчувається як {cur['apparent_temperature']}°C)\n"
        f"💧 Вологість: {cur['relative_humidity_2m']}%\n"
        f"🌬 Вітер: {cur['wind_speed_10m']} м/с\n"
        f"🌧 Опади: {cur['precipitation']} мм\n"
        f"🌤 {desc}"
    )


@tool
def get_forecast(city: str, days: int = 3) -> str:
    """Отримати прогноз погоди на кілька днів. city — місто, days — кількість днів (1-7, за замовчуванням 3)."""
    try:
        lat, lon, name = _geocode(city)
    except ValueError as e:
        return str(e)

    days = max(1, min(days, 7))
    resp = requests.get(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
            "wind_speed_unit": "ms",
            "timezone": "auto",
            "forecast_days": days,
        },
    )
    resp.raise_for_status()
    daily = resp.json()["daily"]

    wmo_short = {
        0: "☀️", 1: "🌤", 2: "⛅", 3: "☁️", 45: "🌫", 48: "🌫",
        51: "🌦", 53: "🌦", 55: "🌧", 61: "🌧", 63: "🌧", 65: "🌧",
        71: "🌨", 73: "🌨", 75: "❄️", 80: "🌧", 81: "🌧", 82: "⛈",
        95: "⛈", 96: "⛈", 99: "⛈",
    }

    lines = [f"📍 Прогноз для {name} на {days} дн.:"]
    for i in range(len(daily["time"])):
        icon = wmo_short.get(daily["weather_code"][i], "?")
        lines.append(
            f"  {daily['time'][i]}: {icon} "
            f"{daily['temperature_2m_min'][i]}..{daily['temperature_2m_max'][i]}°C, "
            f"опади {daily['precipitation_sum'][i]} мм"
        )
    return "\n".join(lines)
