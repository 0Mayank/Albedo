import requests
from bs4 import BeautifulSoup
import json

async def get_waifu():
    source = requests.get("https://mywaifulist.moe/random")
    new_source = requests.get(str(source.url))
    html_content = new_source.text
    soup = BeautifulSoup(html_content, 'lxml')

    data = str(soup.find('script', type="application/ld+json"))
    data = json.loads(data.split(">", 1)[1].split("<",1)[0])
    return data["name"], data["image"]
    