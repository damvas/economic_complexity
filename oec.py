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

country = 'brazil'
df = pd.read_csv(os.path.join(input_path,f'{country}.csv'))
df = df.sort_values(by = 'Trade Value', ascending=False).reset_index(drop=True)

sections_df = pd.DataFrame(df.groupby(by = 'Section')['Trade Value'].sum())

sections = sections_df.index
colors = sns.color_palette('muted', n_colors=len(sections))

plt.figure(figsize=(20, 10))
sizes = sections_df['Trade Value']/10**6

labels = sections_df.index

font_sizes = [min(max(math.ceil(size / max(sizes) * 60), 15), 60) for size in sizes]

squarify.plot(sizes,
            alpha=0.6,
            pad=True,
            color=colors)

ax = plt.gca()
for i, rectangle in enumerate(ax.patches):
    label = labels[i]
    font_size = font_sizes[i]
    x, y = rectangle.xy
    w, h = rectangle.get_width(), rectangle.get_height()
    cx, cy = x + w/2, y + h/2
    label_lines = '\n'.join(label.split(' '))
    plt.annotate(label_lines, (cx, cy), fontsize=font_size, ha='center', va='center')

plt.title(f'What does {country.title()} export? (2021)', fontsize = 50)
plt.axis('off')
plt.annotate('Source: OEC', xy=(0.1, -0.05), xycoords='axes fraction', ha='right', fontsize=30, color='black')
plt.show()
