import requests
import os

# API_KEY = os.getenv('API')
API_KEY = "AQasPW6U65ELqkEkfYGmNjzAspc6qyIR"

def get_location_key(location):
    url = f'http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={location}&language=ru-ru'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if not data:
            return None
        return data[0]['Key']
    except requests.RequestException as e:
        print(f"Ошибка при получении ключа локации для '{location}': {e}")
        return None

def get_weather_data(location_key):
    url = f'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}?apikey={API_KEY}&language=ru-ru&details=true&metric=true'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Ошибка при получении данных о погоде для ключа '{location_key}': {e}")
        return None

def get_weather_info(weather_data):
    daily_forecasts = weather_data['DailyForecasts']
    weather_info = []
    for forecast in daily_forecasts:
        date = forecast['Date']
        temperature_min = forecast['Temperature']['Minimum']['Value']
        temperature_max = forecast['Temperature']['Maximum']['Value']
        wind_speed = forecast['Day']['Wind']['Speed']['Value']
        precipitation_probability = forecast['Day']['PrecipitationProbability']
        weather_info.append({
            'date': date,
            'temperature_min': temperature_min,
            'temperature_max': temperature_max,
            'wind_speed': wind_speed,
            'precipitation_probability': precipitation_probability
        })
    return weather_info

def get_coordinates(location):
    location_key = get_location_key(location)
    if location_key is None:
        return None
    url = f'http://dataservice.accuweather.com/locations/v1/{location_key}?apikey={API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return (data['GeoPosition']['Latitude'], data['GeoPosition']['Longitude'])
    except requests.RequestException as e:
        print(f"Ошибка при получении координат для '{location}': {e}")
        return None