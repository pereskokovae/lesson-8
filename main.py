import json
import folium
import requests
import os
from geopy import distance
from dotenv import load_dotenv



def fetch_coordinates(apikey, user_address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": user_address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0] 
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return float(lat), float(lon)


def calculate_distance(user_coords, coffee_coords):
    return distance.distance(user_coords, coffee_coords).km


def get_distance(coffee):
    return coffee[1]


def sorter(coffee_list, user_coords, count=5):
    distances = []  
    for coffee in coffee_list:
        coffee_coords = (coffee['latitude'], coffee['longitude'])
        dist = calculate_distance(user_coords, coffee_coords)
        distances.append((coffee, dist))
    distances.sort(key=get_distance)
    return [coffee[0] for coffee in distances[:count]]


def main():
    load_dotenv()


    apikey = os.getenv('APIKEY')
    user_address = input('Где вы находитесь? ')

    user_coords = fetch_coordinates(apikey, user_address)
    with open("coffee.json", "r", encoding="CP1251") as coffee_json:
        file_contents = json.load(coffee_json)
        coffee_list = [] 
        for coffee_file in file_contents:
            coffee_coords = { 
                'coffee_name': coffee_file['Name'],
                'latitude': coffee_file['geoData']['coordinates'][1],  
                'longitude': coffee_file['geoData']['coordinates'][0]  
            }
            coffee_list.append(coffee_coords)
    sorted_coffees = sorter(coffee_list, user_coords, count=5)
    m = folium.Map(location=user_coords, zoom_start=12)
    for coffee in sorted_coffees:
        folium.Marker(
            location=[coffee['latitude'], coffee['longitude']],
            popup=coffee['coffee_name'],
            icon=folium.Icon(icon="coffee"),
        ).add_to(m)
    m.save("index.html")


if __name__ == "__main__":
    main()
