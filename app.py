import socket
from flask import Flask, render_template, request
import requests
import json
import re

app = Flask(__name__)

API_KEY = 'NhT3aNM1cRJcnp7epQ7OqAGOhWxSgk4q'


def get_location_key(city):
    location_url = f'http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city}&language=ru'
    try:
        location_response = requests.get(location_url)
        location_response.raise_for_status()
        location_data = location_response.json()
        if location_data:
            return location_data[0]['Key']
    except requests.exceptions.RequestException as e:
        print(f"Ошибка получения данных для города '{city}': {e}")
        return None


def get_location_key_by_coords(city):
    if ' ' in city or ',' in city:
        city = city.replace(' ', '')
        city = city.split(',')
        city = ','.join(city)

        location_url = f'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={API_KEY}&q={city}'
        try:
            location_response = requests.get(location_url)
            location_response.raise_for_status()
            location_data = location_response.json()
            if location_data:
                return [location_data['Key'], location_data['AdministrativeArea']['LocalizedName']]
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения данных для города '{city}': {e}")
            return None


def get_weather_data(location_key):
    weather_url = f'http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={API_KEY}&details=true'
    try:
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        if weather_data:
            return weather_data[0]
    except requests.exceptions.RequestException as e:
        print(f"Ошибка получения данных о погоде: {e}")
        return


def get_forecast_data(location_key):
    forecast_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}?apikey={API_KEY}"
    try:
        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()
        data = forecast_response.json()
        return data['DailyForecasts'][0] if 'DailyForecasts' in data else None
    except Exception as e:
        print(f"Ошибка получения данных о прогнозе: {e}")
        return None


def check_bad_weather(conditions):
    if 10 <= conditions['temperature'] <= 25:
        good_result = 'Сейчас тепло и можно погулять'
        return good_result
    elif conditions['temperature'] < 10:
        good_result = 'Одевайтесь теплее'
        return good_result
    elif conditions['wind_speed'] >= 50:
        bad_result = 'Там ураган'
        return bad_result
    elif conditions['temperature'] > 35:
        bad_result = 'Ты расплавишься, сиди дома'
        return bad_result
    else:
        bad_result = 'Пледик с чаем дома тоже вариант'
        return bad_result


def get_json(city, type):
    name = city
    location_key = None
    if type == 'name':
        location_key = get_location_key(city)[0]
    elif type == 'coords':
        location_key, name = get_location_key_by_coords(city)

    if not location_key:
        return None
    weather_data = get_weather_data(location_key)
    forecast_data = get_forecast_data(location_key)
    if not weather_data or not forecast_data:
        return None
    probability_of_precipitation = forecast_data['Day'].get('PrecipitationProbability')
    return {
        'city': name,
        'temperature': weather_data['Temperature']['Metric']['Value'],
        'wind_speed': weather_data['Wind']['Speed']['Metric']['Value'],
        'probability_of_precipitation': probability_of_precipitation if probability_of_precipitation else 0,
        'humidity': weather_data['RelativeHumidity'],
        'weather_status': check_bad_weather({
            'temperature': weather_data['Temperature']['Metric']['Value'],
            'wind_speed': weather_data['Wind']['Speed']['Metric']['Value'],
            'probability_of_precipitation': probability_of_precipitation
        })
    }


def check_internet_connection():
    try:
        socket.create_connection(("8.8.8.8", 53))
        return True
    except OSError:
        return False


@app.route('/', methods=['GET', 'POST'])
def main():
    data = {}
    error_message = ''
    if request.method == 'POST':
        data = {}
        request_data = request.form
        type = request_data.get('type')
        if type == 'name':
            point_from = request_data.get('point_from')
            point_to = request_data.get('point_to')
            if any(char.isdigit() for char in point_to) or any(char.isdigit() for char in point_from):
                error_message = 'Введите название города, а не координаты'
            else:

                if point_from == point_to:
                    error_message = 'Города должны быть уникальными'
                else:
                    if not check_internet_connection():
                        error_message = "Вас задудосили"
                    else:
                        point_from_data = get_json(point_from, type)
                        point_to_data = get_json(point_to, type)
                        if point_from_data is None:
                            error_message = f"Город введен неправильно - {point_from}"
                        else:
                            data[point_from] = point_from_data
                            with open('data_point_from.json', 'w') as file:
                                json.dump(point_from_data, file)

                        if point_to_data is None:
                            error_message = f"Город введен неправильно - {point_to}"
                        else:
                            data[point_to] = point_to_data
                            with open('data_point_to.json', 'w') as file:
                                json.dump(point_to_data, file)
        elif type == 'coords':
            point_from = request_data.get('coords_from')
            point_to = request_data.get('coords_to')
            if bool(re.search(r'[а-яА-Я]', point_to)) or bool(re.search(r'[а-яА-Я]', point_from)):
                error_message = 'Только по делу. Только координаты'
            else:
                if point_from == point_to:
                    print('Координаты должны быть уникальными')
                else:
                    if not check_internet_connection():
                        error_message = "Вас задудосили"
                    else:
                        coords_from_data = get_json(point_from, type)
                        coords_to_data = get_json(point_to, type)
                        if coords_from_data is None:
                            error_message = f"Не удалось получить данные для города: {point_from}"
                        else:
                            data[coords_from_data['city']] = coords_from_data
                            with open('data_point_from.json', 'w') as file:
                                json.dump(coords_from_data, file)

                        if coords_to_data is None:
                            error_message = f"Не удалось получить данные для города: {point_to}"
                        else:
                            data[coords_to_data['city']] = coords_to_data
                            with open('data_point_to.json', 'w') as file:
                                json.dump(coords_to_data, file)
        if error_message == '':
            return render_template('weather.html', title='Прогнозирование маршрута', error_message=error_message,
                                   data=data)
        else:
            return render_template('weather.html', error_message=error_message)
    else:
        return render_template('index.html', title='Прогнозирование маршрута', error_message=error_message)


if __name__ == '__main__':
    app.run()
