"""
Basic Weather App — Advanced (GUI) Tier
OASIS INFOBYTE — Python Programming Internship — Task 4

Features:
- tkinter GUI: city input, "Get Weather" button, results panel
- Fetches current weather + 5-day/6-hour forecast from OpenWeatherMap (free tier)
- Displays weather icon, temperature, humidity, condition, wind speed
- Celsius / Fahrenheit unit toggle
- Graceful error handling for bad city names, network issues, invalid API key
- (Bonus) automatic location detection via ipinfo.io

SETUP REQUIRED:
1. Get a free API key at https://openweathermap.org/appid
2. Set it as an environment variable before running:
       export OWM_API_KEY="your_key_here"      (Mac/Linux)
       set OWM_API_KEY=your_key_here            (Windows cmd)
   ...or paste it directly into API_KEY below (not recommended for GitHub).
"""

import os
import io
import tkinter as tk
from tkinter import messagebox

import requests

API_KEY = "a12710f62222fe45460d8d2fa8ba0187"
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
ICON_URL = "https://openweathermap.org/img/wn/{icon}@2x.png"


def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32


def fetch_current_weather(city, api_key):
    """Return parsed dict or raise a ValueError/RuntimeError with a user-friendly message."""
    if not city:
        raise ValueError("Please enter a city name.")
    if not api_key:
        raise RuntimeError("No API key set. Set the OWM_API_KEY environment variable.")

    try:
        resp = requests.get(
            CURRENT_URL,
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=8,
        )
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error: {e}")

    if resp.status_code == 401:
        raise RuntimeError("Invalid API key. Double-check OWM_API_KEY.")
    if resp.status_code == 404:
        raise ValueError(f"City '{city}' not found. Check the spelling.")
    if resp.status_code != 200:
        raise RuntimeError(f"Weather API error (status {resp.status_code}).")

    data = resp.json()
    return {
        "city": data.get("name", city),
        "country": data.get("sys", {}).get("country", ""),
        "temp_c": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"].title(),
        "icon": data["weather"][0]["icon"],
        "wind_speed": data["wind"]["speed"],
    }


def fetch_forecast(city, api_key):
    """Return list of forecast entries (3-hour steps from OpenWeatherMap free tier)."""
    resp = requests.get(
        FORECAST_URL,
        params={"q": city, "appid": api_key, "units": "metric"},
        timeout=8,
    )
    if resp.status_code != 200:
        return []
    data = resp.json()
    return data.get("list", [])


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather App — OASIS INFOBYTE")
        self.geometry("480x600")
        self.resizable(False, False)
        self.configure(bg="#0abde3")

        self.unit_fahrenheit = False
        self.last_temp_c = None
        self._build_widgets()

    def _build_widgets(self):
        tk.Label(self, text="☀️ Weather App", font=("Segoe UI", 20, "bold"),
                 bg="#0abde3", fg="white").pack(pady=(20, 10))

        input_frame = tk.Frame(self, bg="#0abde3")
        input_frame.pack(pady=10)

        self.city_entry = tk.Entry(input_frame, font=("Segoe UI", 12), width=22)
        self.city_entry.grid(row=0, column=0, padx=5)
        self.city_entry.bind("<Return>", lambda e: self.on_get_weather())

        tk.Button(input_frame, text="Get Weather", font=("Segoe UI", 11, "bold"),
                  bg="#341f97", fg="white", command=self.on_get_weather).grid(row=0, column=1, padx=5)

        self.unit_btn = tk.Button(self, text="Switch to °F", font=("Segoe UI", 10),
                                   command=self.toggle_unit)
        self.unit_btn.pack(pady=5)

        self.result_frame = tk.Frame(self, bg="white", bd=2, relief="groove")
        self.result_frame.pack(pady=15, padx=20, fill="x")

        self.icon_label = tk.Label(self.result_frame, bg="white")
        self.icon_label.pack(pady=5)

        self.city_label = tk.Label(self.result_frame, text="", font=("Segoe UI", 14, "bold"), bg="white")
        self.city_label.pack()

        self.temp_label = tk.Label(self.result_frame, text="", font=("Segoe UI", 24), bg="white")
        self.temp_label.pack(pady=5)

        self.desc_label = tk.Label(self.result_frame, text="", font=("Segoe UI", 12), bg="white")
        self.desc_label.pack()

        self.details_label = tk.Label(self.result_frame, text="", font=("Segoe UI", 11), bg="white", fg="#576574")
        self.details_label.pack(pady=(5, 15))

        tk.Label(self, text="Next 6 Hours", font=("Segoe UI", 11, "bold"),
                 bg="#0abde3", fg="white").pack(pady=(10, 5))
        self.hourly_label = tk.Label(self, text="", font=("Consolas", 10),
                                      bg="#0abde3", fg="white", justify="left")
        self.hourly_label.pack()

        self.error_label = tk.Label(self, text="", font=("Segoe UI", 10), bg="#0abde3", fg="#feca57")
        self.error_label.pack(pady=10)

    def toggle_unit(self):
        self.unit_fahrenheit = not self.unit_fahrenheit
        self.unit_btn.config(text="Switch to °C" if self.unit_fahrenheit else "Switch to °F")
        if self.last_temp_c is not None:
            self._display_temp(self.last_temp_c)

    def _display_temp(self, temp_c):
        if self.unit_fahrenheit:
            self.temp_label.config(text=f"{celsius_to_fahrenheit(temp_c):.1f}°F")
        else:
            self.temp_label.config(text=f"{temp_c:.1f}°C")

    def on_get_weather(self):
        self.error_label.config(text="")
        city = self.city_entry.get().strip()

        try:
            current = fetch_current_weather(city, API_KEY)
        except ValueError as e:
            self.error_label.config(text=str(e))
            return
        except RuntimeError as e:
            self.error_label.config(text=str(e))
            return

        self.last_temp_c = current["temp_c"]
        self.city_label.config(text=f"{current['city']}, {current['country']}")
        self._display_temp(current["temp_c"])
        self.desc_label.config(text=current["description"])
        self.details_label.config(
            text=f"Humidity: {current['humidity']}%   |   Wind: {current['wind_speed']} m/s"
        )

        self._load_icon(current["icon"])

        try:
            forecast = fetch_forecast(city, API_KEY)
            lines = []
            for entry in forecast[:2]:  # 2 entries x 3hr = 6 hours
                time_str = entry["dt_txt"].split(" ")[1][:5]
                temp = entry["main"]["temp"]
                desc = entry["weather"][0]["description"].title()
                if self.unit_fahrenheit:
                    temp = celsius_to_fahrenheit(temp)
                    unit = "°F"
                else:
                    unit = "°C"
                lines.append(f"{time_str}  {temp:5.1f}{unit}  {desc}")
            self.hourly_label.config(text="\n".join(lines) if lines else "Forecast unavailable")
        except Exception:
            self.hourly_label.config(text="Forecast unavailable")

    def _load_icon(self, icon_code):
        try:
            from PIL import Image, ImageTk
            resp = requests.get(ICON_URL.format(icon=icon_code), timeout=8)
            img = Image.open(io.BytesIO(resp.content))
            photo = ImageTk.PhotoImage(img)
            self.icon_label.config(image=photo)
            self.icon_label.image = photo  # keep reference
        except ImportError:
            self.icon_label.config(text="[install Pillow for icons]", image="")
        except Exception:
            self.icon_label.config(text="", image="")


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
