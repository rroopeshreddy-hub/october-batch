
from flask import Flask, request
import urllib.request
import urllib.parse
import json
import html

app = Flask(__name__)

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy",
    3: "Overcast", 45: "Fog", 48: "Fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Moderate showers",
    82: "Heavy showers", 95: "Thunderstorm",
    96: "Thunderstorm with hail", 99: "Thunderstorm with hail"
}

def get_json(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "WeatherApp/1.0"}
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))

def get_weather(city):
    params = urllib.parse.urlencode({
        "name": city, "count": 1, "language": "en", "format": "json"
    })
    places = get_json(
        "https://geocoding-api.open-meteo.com/v1/search?" + params
    ).get("results", [])

    if not places:
        raise ValueError("City not found. Try another city name.")

    place = places[0]
    params = urllib.parse.urlencode({
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "apparent_temperature,precipitation,"
            "weather_code,wind_speed_10m"
        ),
        "daily": (
            "temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max,sunrise,sunset"
        ),
        "timezone": "auto",
        "forecast_days": 1
    })
    data = get_json(
        "https://api.open-meteo.com/v1/forecast?" + params
    )

    current = data["current"]
    daily = data["daily"]

    return {
        "city": ", ".join(
            x for x in [
                place.get("name"),
                place.get("admin1"),
                place.get("country")
            ] if x
        ),
        "condition": WEATHER_CODES.get(
            current["weather_code"], "Unknown"
        ),
        "temperature": current["temperature_2m"],
        "feels": current["apparent_temperature"],
        "humidity": current["relative_humidity_2m"],
        "wind": current["wind_speed_10m"],
        "rain": current["precipitation"],
        "high": daily["temperature_2m_max"][0],
        "low": daily["temperature_2m_min"][0],
        "rain_chance": daily["precipitation_probability_max"][0],
        "sunrise": daily["sunrise"][0],
        "sunset": daily["sunset"][0],
        "updated": current["time"]
    }

@app.route("/", methods=["GET", "POST"])
def home():
    city = request.form.get("city", "").strip()
    weather = None
    error = None

    if request.method == "POST":
        if not city:
            error = "Please enter a city name."
        else:
            try:
                weather = get_weather(city)
            except ValueError as e:
                error = str(e)
            except Exception:
                error = "Could not fetch weather. Check your internet connection."

    city_safe = html.escape(city, quote=True)
    error_html = (
        f'<div class="error">{html.escape(error)}</div>'
        if error else ""
    )

    weather_html = ""
    if weather:
        def val(key):
            return html.escape(str(weather[key]))

        weather_html = f"""
        <section class="report">
          <div class="location">{val('city')}</div>
          <div class="condition">{val('condition')}</div>
          <div class="temperature">{val('temperature')}<span>°C</span></div>
          <p class="muted">Feels like {val('feels')}°C</p>

          <div class="grid">
            <div class="metric"><span>Humidity</span><strong>{val('humidity')}%</strong></div>
            <div class="metric"><span>Wind speed</span><strong>{val('wind')} km/h</strong></div>
            <div class="metric"><span>Precipitation</span><strong>{val('rain')} mm</strong></div>
            <div class="metric"><span>Chance of rain</span><strong>{val('rain_chance')}%</strong></div>
            <div class="metric"><span>Today's high</span><strong>{val('high')}°C</strong></div>
            <div class="metric"><span>Today's low</span><strong>{val('low')}°C</strong></div>
            <div class="metric"><span>Sunrise</span><strong>{val('sunrise')}</strong></div>
            <div class="metric"><span>Sunset</span><strong>{val('sunset')}</strong></div>
          </div>
          <p class="muted updated">Updated: {val('updated')}</p>
        </section>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weather Now</title>
<style>
* {{ box-sizing: border-box; }}
body {{
    margin: 0; min-height: 100vh; padding: 40px 16px;
    font-family: Arial, sans-serif; color: #f8fafc;
    background: linear-gradient(135deg, #0f172a, #1d4ed8);
}}
.container {{ max-width: 680px; margin: auto; }}
header {{ text-align: center; margin-bottom: 28px; }}
header h1 {{ font-size: 36px; margin: 0 0 10px; }}
header p {{ color: #cbd5e1; margin: 0; }}
.search {{
    display: flex; gap: 10px; padding: 10px;
    background: white; border-radius: 14px; margin-bottom: 20px;
}}
input {{
    flex: 1; min-width: 0; border: 0; outline: none;
    padding: 12px; font-size: 16px; color: #0f172a;
}}
button {{
    border: 0; border-radius: 10px; padding: 12px 20px;
    background: #2563eb; color: white; font-size: 15px;
    font-weight: bold; cursor: pointer;
}}
button:hover {{ background: #1d4ed8; }}
.report {{
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.2);
    border-radius: 20px; padding: 26px;
    backdrop-filter: blur(10px);
}}
.location {{ font-size: 23px; font-weight: bold; }}
.condition {{ margin-top: 8px; color: #dbeafe; }}
.temperature {{ font-size: 76px; font-weight: bold; margin-top: 12px; }}
.temperature span {{ font-size: 34px; vertical-align: top; }}
.muted {{ color: #cbd5e1; }}
.grid {{
    display: grid; grid-template-columns: repeat(2, 1fr);
    gap: 12px; margin-top: 24px;
}}
.metric {{
    background: rgba(15,23,42,.35);
    padding: 16px; border-radius: 12px;
}}
.metric span {{ display: block; font-size: 13px; color: #cbd5e1; }}
.metric strong {{ display: block; margin-top: 9px; font-size: 19px; }}
.updated {{ font-size: 12px; margin: 20px 0 0; }}
.error {{
    background: #fee2e2; color: #991b1b; padding: 14px;
    border-radius: 10px; margin-bottom: 16px;
}}
footer {{ text-align: center; color: #cbd5e1; font-size: 12px; margin-top: 22px; }}
@media (max-width: 440px) {{
    header h1 {{ font-size: 29px; }}
    .temperature {{ font-size: 62px; }}
    .report {{ padding: 18px; }}
    .metric {{ padding: 12px; }}
    .metric strong {{ font-size: 16px; }}
    button {{ padding: 12px; }}
}}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>☀ Weather Now</h1>
    <p>Discover current weather in any city</p>
  </header>

  <form class="search" method="POST">
    <input name="city" placeholder="Enter city (e.g. Bengaluru)"
           value="{city_safe}" required>
    <button type="submit">Search</button>
  </form>

  {error_html}
  {weather_html}

  <footer>Weather data provided by Open-Meteo · Free API · No API key needed</footer>
</div>
</body>
</html>"""

if __name__ == "__main__":
    app.run(debug=True)
