import requests
import requests_cache
import decimal
import json


requests_cache.install_cache(cache_name = 'image_cache', backend = 'sqlite', expire_after=900)

def get_image(search):

    url = "https://google-search72.p.rapidapi.com/imagesearch"

    querystring = {"q":search,"gl":"us","lr":"lang_en","num":"1","start":"0"}

    headers = {
        "X-RapidAPI-Key": "ea104aa93amsh4d59e1dddb29571p11bd0djsn261ad6148142",
        "X-RapidAPI-Host": "google-search72.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data = response.json()
    img_url = data['items'][0]['originalImageUrl'] #traversing data dictionary to get the image url that we want
    return img_url

class TheREALJason(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return json.JSONEncoder(TheREALJason, self).default(obj) #if it's not decimal then the regular jsonencoder is just fine