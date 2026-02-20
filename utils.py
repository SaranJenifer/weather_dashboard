import requests
import streamlit as st
from requests.exceptions import RequestException

OPENWEATHER_API_KEY = "59976539a18e7355a1d67b6960c33cab"
VISUALCROSSING_API_KEY = "95MDU6RHNQK67R7W4HUA5ECUQ"


# ================= GEOCODING =================
def get_coordinates(place):
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": place,
        "limit": 1,
        "appid": OPENWEATHER_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if not data:
            return None

        return data[0]["lat"], data[0]["lon"]

    except RequestException:
        return None


# ================= CURRENT WEATHER =================
@st.cache_data(ttl=600)
def get_current_weather(place):
    coords = get_coordinates(place)

    if coords is None:
        return None

    lat, lon = coords

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            return None

        return response.json()

    except RequestException:
        return None


#============ADDITIONAL WEATHER DATA (UV + Hourly)=============

def get_additional_weather_data(lat, lon):

    url = "https://api.openweathermap.org/data/3.0/onecall"

    params = {
        "lat": lat,
        "lon": lon,
        "exclude": "minutely,daily,alerts",
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200:
            return {}

        return {
            "uvi": data["current"].get("uvi"),
            "hourly": data.get("hourly", [])
        }

    except requests.exceptions.RequestException:
        return {}


# ================= AIR QUALITY =================
@st.cache_data(ttl=1800)
def get_air_quality(lat, lon):
    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except RequestException:
        return None
    
# ================= ADDITIONAL WEATHER DATA (UV + Hourly) =================
@st.cache_data(ttl=1800)
def get_additional_weather_data(lat, lon):

    url = "https://api.openweathermap.org/data/3.0/onecall"

    params = {
        "lat": lat,
        "lon": lon,
        "exclude": "minutely,daily,alerts",
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return {}

        data = response.json()

        return {
            "uvi": data["current"].get("uvi"),
            "hourly": data.get("hourly", [])
        }

    except RequestException:
        return {}
   



# ================= HISTORICAL WEATHER =================
@st.cache_data(ttl=3600)
def get_historical_weather(place, start_date, end_date):
    url = (
        "https://weather.visualcrossing.com/VisualCrossingWebServices/"
        f"rest/services/timeline/{place}/{start_date}/{end_date}"
    )

    params = {
        "unitGroup": "metric",
        "key": VISUALCROSSING_API_KEY,
        "contentType": "json"
    }

    try:
        response = requests.get(url, params=params,timeout=10)

        if response.status_code == 429:
            return {"error": "API rate limit exceeded. Please try again later."}

        if response.status_code != 200:
            return {"error": "Failed to fetch historical weather data."}

        return response.json()

    except RequestException:
        return {"error": "Network error. Please check your connection."}
   

# ================= 5-DAY / 7-DAY FORECAST =================
@st.cache_data(ttl=1800)
def get_forecast_weather(place):
    coords = get_coordinates(place)

    if coords is None:
        return None

    lat, lon = coords

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            return None

        return response.json()

    except RequestException:
        return None