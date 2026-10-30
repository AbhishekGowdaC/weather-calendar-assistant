import httpx

from datetime import date, time

GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

FORECAST_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Severe thunderstorm with hail",
}


async def get_event_weather(
    location: str,
    event_date: date,
    start_time: time,
    end_time: time,
) -> dict:

    location = location.strip()

    if not location:
        raise ValueError("Location cannot be empty.")

    if end_time <= start_time:
        raise ValueError("End time must be later than start time.")

    async with httpx.AsyncClient(timeout=20.0) as client:

        # 1. Geocode the location

        geo_response = await client.get(
            GEOCODING_URL,
            params={
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json",
            },
        )

        geo_response.raise_for_status()

        results = geo_response.json().get("results", [])

        if not results:
            raise ValueError(
                f"Location not found: {location}"
            )

        place = results[0]

        latitude = place["latitude"]
        longitude = place["longitude"]

        # 2. Fetch forecast for requested date

        forecast_response = await client.get(
            FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "hourly": (
                    "temperature_2m,"
                    "precipitation_probability,"
                    "precipitation,"
                    "weather_code"
                ),
                "start_date": event_date.isoformat(),
                "end_date": event_date.isoformat(),
                "timezone": "auto",
            },
        )

        forecast_response.raise_for_status()

        forecast = forecast_response.json()

        hourly = forecast.get("hourly", {})

        if not hourly.get("time"):
            raise ValueError(
                "No forecast available for the requested date."
            )

        # 3. Filter forecast by event time

        event_hours = []

        for index, timestamp in enumerate(hourly["time"]):

            forecast_time = time.fromisoformat(
                timestamp.split("T")[1]
            )

            if start_time <= forecast_time < end_time:

                event_hours.append({
                    "time": timestamp,
                    "temperature": hourly[
                        "temperature_2m"
                    ][index],
                    "rain_probability": hourly[
                        "precipitation_probability"
                    ][index],
                    "precipitation_mm": hourly[
                        "precipitation"
                    ][index],
                    "weather_code": hourly[
                        "weather_code"
                    ][index],
                })

        if not event_hours:
            raise ValueError(
                "No hourly forecast matches the event time."
            )

        # 4. Calculate weather statistics

        temperatures = [
            item["temperature"]
            for item in event_hours
            if item["temperature"] is not None
        ]

        rain_probabilities = [
            item["rain_probability"]
            for item in event_hours
            if item["rain_probability"] is not None
        ]

        precipitation_values = [
            item["precipitation_mm"]
            for item in event_hours
            if item["precipitation_mm"] is not None
        ]

        if not temperatures:
            raise ValueError("Temperature data unavailable.")

        if not rain_probabilities:
            raise ValueError("Rain probability unavailable.")

        max_rain_probability = max(rain_probabilities)

        total_precipitation = sum(precipitation_values)

        min_temperature = min(temperatures)
        max_temperature = max(temperatures)

        # 5. Generate a basic weather recommendation

        if max_rain_probability >= 60:
            recommendation = "High rain risk"
        elif max_rain_probability >= 30:
            recommendation = "Moderate rain risk"
        else:
            recommendation = "Low rain risk"

        return {
            "location": place["name"],
            "country": place.get("country"),
            "latitude": latitude,
            "longitude": longitude,
            "timezone": forecast.get("timezone"),

            "event_date": event_date.isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),

            "temperature": {
                "minimum": min_temperature,
                "maximum": max_temperature,
            },

            "rain": {
                "maximum_probability": max_rain_probability,
                "total_precipitation_mm": round(
                    total_precipitation, 2
                ),
            },

            "recommendation": recommendation,

            "hourly_forecast": event_hours,
        }