from flask import Flask, render_template, request
from weather_service import get_location_key, get_weather_data, get_coordinates
import plotly.graph_objs as go
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

def create_map_with_route(coordinates, locations):
    route_coordinates = [{"lat": coord[0], "lon": coord[1]} for coord in coordinates]

    fig = px.scatter_mapbox(
        lat=[coord[0] for coord in coordinates],
        lon=[coord[1] for coord in coordinates],
        hover_name=locations,
        zoom=5,
        height=500
    )

    fig.add_trace(go.Scattermapbox(
        mode="lines",
        lon=[coord["lon"] for coord in route_coordinates],
        lat=[coord["lat"] for coord in route_coordinates],
        line=dict(width=2, color="blue"),
        name="Маршрут"
    ))

    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    return fig

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'locations' not in request.form:
            return render_template('weather.html', error="Ошибка: не указаны точки маршрута.")

        locations = request.form['locations'].splitlines()
        days = int(request.form['days'])

        weather_data_list = []
        coordinates = []

        for location in locations:
            if not location.strip():
                return render_template('weather.html', error=f"Ошибка: пустая строка в точках маршрута.")

            original_location = location

            location = location.strip()

            location_key = get_location_key(location)
            if location_key is None:
                return render_template('weather.html', error=f"Ошибка: локация '{original_location}' не найдена.")

            weather_data = get_weather_data(location_key)
            if weather_data is None:
                return render_template('weather.html', error=f"Ошибка: не удалось получить данные о погоде для локации '{original_location}'.")

            weather_data['DailyForecasts'] = weather_data['DailyForecasts'][:days]
            weather_data_list.append({
                'location': original_location,
                'data': weather_data
            })
            coord = get_coordinates(location)
            if coord:
                coordinates.append(coord)

        graphs = []
        for data in weather_data_list:
            forecasts = data['data']['DailyForecasts']
            dates = [forecast['Date'] for forecast in forecasts]
            temps_min = [forecast['Temperature']['Minimum']['Value'] for forecast in forecasts]
            temps_max = [forecast['Temperature']['Maximum']['Value'] for forecast in forecasts]
            precipitation = [forecast['Day']['PrecipitationProbability'] for forecast in forecasts]
            wind_speed = [forecast['Day']['Wind']['Speed']['Value'] for forecast in forecasts]

            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(x=dates, y=temps_min, mode='lines+markers', name='Min Temp'))
            fig_temp.add_trace(go.Scatter(x=dates, y=temps_max, mode='lines+markers', name='Max Temp'))
            fig_temp.update_layout(title=f"Температура в {data['location']}")

            fig_precip = go.Figure()
            fig_precip.add_trace(go.Bar(x=dates, y=precipitation, name='Вероятность осадков'))
            fig_precip.update_layout(title=f"Вероятность осадков в {data['location']}")

            fig_wind = go.Figure()
            fig_wind.add_trace(go.Line(x=dates, y=wind_speed, name='Скорость ветра'))
            fig_wind.update_layout(title=f"Скорость ветра в {data['location']}")

            graphs.append({
                'location': data['location'],
                'temp_graph': pio.to_json(fig_temp),
                'precip_graph': pio.to_json(fig_precip),
                'wind_graph': pio.to_json(fig_wind)
            })

        if coordinates:
            fig_map = create_map_with_route(coordinates, locations)
            map_json = pio.to_json(fig_map)
        else:
            map_json = None
        print(graphs)
        print(map_json)
        return render_template('weather.html', graphs=graphs, map_json=map_json)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
