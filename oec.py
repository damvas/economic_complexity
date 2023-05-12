import pandas as pd
import os
import requests
import plotly.express as px
import numpy as np

input_path = './input'

def download_country_data(country: str, iso3: pd.DataFrame) -> pd.DataFrame:
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
        df.to_csv(os.path.join(input_path,f'{country.lower()}.csv'))
    else:
        print("Request failed with status code:", response.status_code)
        print("Country:", country)
    return df

def download_all_country_data(iso3: pd.DataFrame):
    for country in iso3['Country']:
        download_country_data(country)

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

def get_treemap(country: str, iso3: pd.DataFrame) -> None:
    df = download_country_data(country, iso3)
    trade_sum = get_trade_sum(df)
    df['percent'] = df['Trade Value']/ df['Trade Value'].sum()

    fig = px.treemap(df, path = ["Section", 'HS4'], values = 'percent', color = 'Section', custom_data=['percent'])

    fig.update_layout(
                    margin = dict(t=50, l=0, r=0, b=0),
                    autosize=False,
                    width=1050,
                    height=600,
                    title={
                    'text' : f'Guess which country exports these products! (2021)',
                    'y' : 0.97,
                    'x' : 0.5
                    },
                    legend_title="Section", 
                    legend_traceorder="reversed",

                    annotations=[dict(
                        x=0.5,
                        y=1.02,
                        xref='paper',
                        yref='paper',
                        showarrow=False,
                        text=f"Total: {trade_sum}",
                        font=dict(size=16)
                    )]
    )

    fig.update_layout()
    fig.show()

def play(iso3: pd.DataFrame, max_attempts: int = 5) -> None:
    country = pd.Series.sample(iso3['Country']).iloc[0]
    get_treemap(country, iso3)
    correct = False
    attempts = 0
    while not correct and attempts < max_attempts: 
        answer = input('Guess the country: ')
        if answer.lower() == country.lower():
            print(f'Correct! The country is {country}.')
            correct = True
        else:
            print('Incorrect. Try again.')
            attempts += 1
    if not correct:
        print(f'Sorry, you have used up all {max_attempts} attempts. The country was {country}.')
