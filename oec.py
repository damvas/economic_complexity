import pandas as pd
import os
import requests
import matplotlib.pyplot as plt
import squarify
import seaborn as sns
import math
import numpy as np

input_path = './input'

def download_country_data(country: str) -> pd.DataFrame:
    iso3 = pd.read_csv(os.path.join(os.getcwd(),'oec_iso3.csv'))
    country = country.title()
    i = np.where(iso3['Country'] == country)[0][0]
    country_id = iso3.loc[i,'Country ID']
    country = iso3.loc[i,'Country']
    print("Processing:", country)
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

def download_all_country_data():
    iso3 = pd.read_csv(os.path.join(os.getcwd(),'oec_iso3.csv'))
    for country in iso3['Country']:
        download_country_data(country)

country = "China"
df = download_country_data(country)

trade_sum = df['Trade Value'].sum()/10**9
if trade_sum >= 1000:
    trade_sum = trade_sum/10**3
    trade_sum = 'US$ ' + str(trade_sum.round(1)) + 'T'
else:
    trade_sum = 'US$ ' + str(trade_sum.round(1)) + 'B'

df['percent'] = df['Trade Value']/ df['Trade Value'].sum()

fig = px.treemap(df, path = ["Section", 'HS4'], values = 'percent', color = 'Section', custom_data=['percent'])

fig.update_layout(
                margin = dict(t=50, l=0, r=0, b=0),
                autosize=False,
                width=1050,
                height=600,
                title={
                'text' : f'What does {country} export? (2021)',
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
