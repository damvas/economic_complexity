import pandas as pd
import os
import requests
import numpy as np
import plotly.express as px
import plotly
import json
from flask import Flask, render_template, request

input_path = 'input'

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


def create_plot(country: str):
    df = download_country_data(country)
    df['percent'] = (df['Trade Value']/ df['Trade Value'].sum())*100
    df['Trade Value m'] = df['Trade Value']/1000
    fig = px.treemap(df, path = ["Section", 'HS4'], values = 'Trade Value m', color = 'Section', custom_data=['percent'])
    fig.update_traces(textinfo='label+text+value+percent entry', textfont=dict(color='white', size=20))
    fig.update_layout(margin = dict(t=0, l=0, r=0, b=0), 
                  autosize=False, 
                  width=800, 
                  height=600, 
                  legend_title="Section", 
                  legend_traceorder="reversed")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', plot=None)

@app.route('/plot', methods=['GET', 'POST'])
def plot():
    if request.method == 'POST':
        country = request.form.get('country')
        fig = create_plot(country)
        return fig
    else:
        return "Invalid request"

if __name__ == '__main__':
    app.run()

