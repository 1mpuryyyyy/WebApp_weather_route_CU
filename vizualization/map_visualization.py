import plotly.express as px

def create_route_map(locations, weather_data):
    # locations = [{'name': 'Москва', 'latitude': 55.75, 'longitude': 37.61}, {'name': 'Санкт-Петербург', 'latitude': 59.93, 'longitude': 30.3}]
    # weather_data = [{'temperature': 20, 'wind_speed': 5, 'precipitation_probability': 10}, {'temperature': 15, 'wind_speed': 10, 'precipitation_probability': 20}]

    for i, location in enumerate(locations):
        location['temperature'] = weather_data[i].get('temperature', 'N/A')
        location['wind_speed'] = weather_data[i].get('wind_speed', 'N/A')
        location['precipitation_probability'] = weather_data[i].get('precipitation_probability', 'N/A')

    fig = px.scatter_mapbox(
        locations,
        lat="latitude",
        lon="longitude",
        hover_name="name",
        hover_data={
            "latitude": False,
            "longitude": False,
            "temperature": True,
            "wind_speed": True,
            "precipitation_probability": True
        },
        mapbox_style="open-street-map",
        zoom=5,
        title="Маршрут с прогнозом погоды"
    )

    if len(locations) > 1:
        fig.add_trace(
            px.line_mapbox(
                locations,
                lat="latitude",
                lon="longitude",
                mapbox_style="open-street-map"
            ).data[0]
        )

    return fig