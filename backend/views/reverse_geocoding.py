import requests

def get_location(lat, lng):
    url = "https://nominatim.openstreetmap.org/reverse?format=geojson&lat=" + str(lat) + "&lon=" + str(lng)
    r = requests.get(url)
    data = r.json()
    return data