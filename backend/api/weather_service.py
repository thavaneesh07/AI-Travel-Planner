import requests
from datetime import datetime, timedelta
import os

API_KEY = "d31c336374b603dce7c5c7b7543c33d8"  

def get_weather_forecast(city: str):
    """
    Fetch 5-day weather forecast using OpenWeatherMap API.
    Falls back to mock data if API fails.
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url)
        data = res.json()

        if "list" not in data:
            raise ValueError("Invalid API response")

        forecast = {}
        today = datetime.today()

        # Extract next 5 days (averaging every 24 hours)
        for i in range(5):
            date_str = (today + timedelta(days=i)).strftime("%Y-%m-%d")
            entry = data["list"][i * 8]  # every ~8 entries = 24h
            forecast[date_str] = {
                "temp": round(entry["main"]["temp"]),
                "desc": entry["weather"][0]["description"]
            }

        return {"city": city, "forecast": forecast}

    except Exception as e:
        print(f"⚠️ Weather API failed ({e}) — using mock data.")
        mock_forecast = {}
        today = datetime.today()
        for i in range(5):
            date_str = (today + timedelta(days=i)).strftime("%Y-%m-%d")
            mock_forecast[date_str] = {
                "temp": 25 + i % 3,
                "desc": ["sunny", "clear sky", "partly cloudy", "light rain", "clear sky"][i % 5]
            }
        return {"city": city, "forecast": mock_forecast}
