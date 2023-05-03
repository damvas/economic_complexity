import pandas as pd
import requests

url = "https://oec.world/olap-proxy/data"
params = {
    "cube": "trade_i_baci_a_92",
    "drilldowns": "Year,HS4",
    "measures": "Trade Value",
    "parents": "true",
    "Year": "2021",
    "Exporter Country": "sabra"
}

response = requests.get(url, params=params)
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data['data'])
else:
    print("Request failed with status code:", response.status_code)
