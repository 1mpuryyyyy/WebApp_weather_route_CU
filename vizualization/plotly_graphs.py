import plotly.express as px
import pandas as pd

def process_weather_data(weather_data):
    daily_forecasts = weather_data['DailyForecasts']
    processed_data = []
    for forecast in daily_forecasts:
        processed_data.append({
            "date": forecast["Date"],
            "temperature": forecast["Temperature"]["Maximum"]["Value"],
            "wind_speed": forecast["Day"]["Wind"]["Speed"]["Value"],
            "precipitation_probability": forecast["Day"]["PrecipitationProbability"]
        })
    return processed_data

def create_weather_graph(weather_data, param):
    processed_data = process_weather_data(weather_data)
    df = pd.DataFrame(processed_data)
    if param == "temperature":
        fig = px.line(df, x="date", y="temperature", title="Температура")
    elif param == "wind_speed":
        fig = px.line(df, x="date", y="wind_speed", title="Скорость ветра")
    elif param == "precipitation_probability":
        fig = px.bar(df, x="date", y="precipitation_probability", title="Вероятность осадков")
    return fig