
import urllib.request
import urllib.parse
import json

# Free Open-Meteo API
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Heavy drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Heavy rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}


def get_json(url):
    """Fetch JSON data from an API."""
    request = urllib.request.Request(
        url, headers={"User-Agent": "PythonWeatherApp/1.0"}
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def get_city(city):
    """Find a city's latitude and longitude."""
    params = urllib.parse.urlencode({
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    })

    data = get_json(f"{GEOCODING_URL}?{params}")
    results = data.get("results", [])

    if not results:
        raise ValueError("City not found. Please check the spelling.")

    return results[0]


def show_weather(city):
    place = get_city(city)
    latitude = place["latitude"]
    longitude = place["longitude"]

    params = urllib.parse.urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "apparent_temperature,is_day,precipitation,"
            "weather_code,wind_speed_10m,wind_direction_10m"
        ),
        "daily": (
            "weather_code,temperature_2m_max,"
            "temperature_2m_min,precipitation_probability_max,"
            "sunrise,sunset"
        ),
        "timezone": "auto",
        "forecast_days": 1
    })

    data = get_json(f"{WEATHER_URL}?{params}")
    current = data["current"]
    daily = data["daily"]

    condition = WEATHER_CODES.get(
        current["weather_code"], "Unknown conditions"
    )

    location = ", ".join(
        x for x in [
            place.get("name"),
            place.get("admin1"),
            place.get("country")
        ] if x
    )

    print("\n" + "=" * 40)
    print(f" WEATHER REPORT: {location}")
    print("=" * 40)
    print(f"Updated at:       {current['time']}")
    print(f"Conditions:       {condition}")
    print(f"Temperature:      {current['temperature_2m']} °C")
    print(f"Feels like:       {current['apparent_temperature']} °C")
    print(f"Humidity:         {current['relative_humidity_2m']}%")
    print(f"Wind speed:       {current['wind_speed_10m']} km/h")
    print(f"Wind direction:   {current['wind_direction_10m']}°")
    print(f"Precipitation:    {current['precipitation']} mm")

    print("\nTODAY'S FORECAST")
    print(f"Maximum temp:     {daily['temperature_2m_max'][0]} °C")
    print(f"Minimum temp:     {daily['temperature_2m_min'][0]} °C")
    print(
        "Rain probability:",
        f"{daily['precipitation_probability_max'][0]}%"
    )
    print(f"Sunrise:          {daily['sunrise'][0]}")
    print(f"Sunset:           {daily['sunset'][0]}")
    print("=" * 40)


def main():
    print("Welcome to the Python Weather App!")
    print("Enter a city name or type 'q' to quit.")

    while True:
        city = input("\nEnter city: ").strip()

        if city.lower() in ("q", "quit", "exit"):
            print("Goodbye!")
            break

        if not city:
            print("Please enter a city name.")
            continue

        try:
            show_weather(city)
        except ValueError as error:
            print(error)
        except Exception as error:
            print("Could not fetch weather:", error)


if __name__ == "__main__":
    main()
