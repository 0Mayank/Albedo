import requests
from bs4 import BeautifulSoup
import json

async def get_waifu():
    while 5:
        source = requests.get("https://mywaifulist.moe/random")
        source = requests.get(str(source.url))
        soup = BeautifulSoup(source.text, 'lxml')
        data = str((soup.find('script', type='application/ld+json')))
        strip_data = data[40:-14]
        json_data = json.loads(strip_data)
        if json_data['gender'] == 'female':
            return json_data['name'], json_data['image'], json_data['url']
            break
        else:
            print('male')
            print(json_data['name'])
            continue
        # print('male')
    