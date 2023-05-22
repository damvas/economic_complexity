import pandas as pd
import os
import requests
import plotly.express as px
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geographiclib.geodesic import Geodesic

def download_country_data(country: str) -> pd.DataFrame:
    iso3 = pd.read_csv(os.path.join(os.getcwd(),'oec_iso3.csv'))
    country = country.title()
    i = np.where(iso3['Country'] == country)[0][0]
    country_id = iso3.loc[i,'Country ID']
    country = iso3.loc[i,'Country']
    # print("Processing:", country)
    url = "https://oec.world/olap-proxy/data"
    params = {
        "cube": "trade_i_baci_a_92",
        "drilldowns": "Year,HS4",
        "measures": "Trade Value",
        "parents": "true",
        "Year": "2021",
        "Exporter Country": f"{country_id}"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data['data'])
        df['percent'] = (df['Trade Value']/ df['Trade Value'].sum())*100
        df['Trade Value m'] = df['Trade Value']/1000
        # df.to_csv(os.path.join(input_path,f'{country.lower()}.csv'))
    else:
        print("Request failed with status code:", response.status_code)
        print("Country:", country)
    return df

def get_trade_sum(df: pd.DataFrame) -> str:
    trade_sum = df['Trade Value'].sum()
    if trade_sum < 10**9:
        trade_sum = trade_sum/10**6
        trade_sum = 'US$ ' + str(trade_sum.round(1)) + 'M'
    elif (trade_sum >= 10**9) & (trade_sum < 10**12):
        trade_sum = trade_sum/10**9
        trade_sum = 'US$ ' + str(trade_sum.round(1)) + 'B'
    else:
        trade_sum = trade_sum/10**12
        trade_sum = 'US$ ' + str(trade_sum.round(1)) + 'T'
    return trade_sum

def create_plot(df):
    trade_sum = get_trade_sum(df)
    fig = px.treemap(df, path=["Section", 'HS4'], values='Trade Value m', color='Section', custom_data=['percent'])
    fig.update_traces(textinfo='label+text+value+percent entry', textfont=dict(color='white', size=20))
    fig.update_layout(
        margin=dict(t=50, l=0, r=0, b=0),  # Adjust the top margin value as needed
        autosize=False,
        width=1100,
        height=300,
        legend_title="Section",
        legend_traceorder="reversed",
        title=dict(
            text=f"Total: {trade_sum}",
            x=0.5
    ))

    fig.show()

def get_country_coordinates(country):
    geolocator = Nominatim(user_agent="distance_app")
    location = geolocator.geocode(country)
    return (location.latitude, location.longitude)

def calculate_distance_and_direction(country1, country2):
    coordinates1 = get_country_coordinates(country1)
    coordinates2 = get_country_coordinates(country2)
    distance = geodesic(coordinates1, coordinates2).kilometers
    geod = Geodesic.WGS84
    result = geod.Inverse(coordinates1[0], coordinates1[1], coordinates2[0], coordinates2[1])
    direction = result["azi1"]
    return distance, direction

def degrees_to_cardinal(direction):
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(direction / 22.5) % 16
    return directions[index]

def play(iso3: pd.DataFrame, max_attempts: int = 5) -> None:
    country = pd.Series.sample(iso3['Country']).iloc[0]
    df = download_country_data(country)
    create_plot(df)
    correct = False
    attempts = 0
    while not correct and attempts < max_attempts: 
        answer = input('Guess the country: ')
        if answer.lower() == country.lower():
            print(f'Correct! The country is {country}.')
            correct = True
        else:
            distance, direction = calculate_distance_and_direction(answer.lower(), country.lower())
            cardinal_direction = degrees_to_cardinal(direction)
            print(f'Incorrect. Go {cardinal_direction}.')
            attempts += 1
    if not correct:
        print(f'Game over. The country was {country}.')

iso3 = pd.read_csv(os.path.join(os.getcwd(),'oec_iso3.csv'))
subset = iso3.nlargest(10,'Trade Value')
