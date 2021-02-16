"""This is the main module for map generating"""
import folium
from math import sin, cos, sqrt, atan2, radians
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from geopy.extra.rate_limiter import RateLimiter


def finding_places_by_year(year):
    """
    Reads the file with locations and
    finds all the places by year
    :param year: integer, year
    :return: list of lists of places
    """
    year_string = '(' + year + ')'
    places = []
    with open("locations.list", encoding='ISO-8859-1') as file:
        file = file.readlines()[14:10000]
    for line in file:
        if year_string in line:
            new_line = line.split("\t")
            location_place = new_line[-1].rstrip()
            if location_place.startswith('('):
                location_place = new_line[-2]
            places.append([new_line[0], location_place])
    return places


def finding_coordinates(initial_point, places):
    """
    Finds coordinates of places
    :return: list of lists of places with coordinates
    """
    new_places = []
    geolocator = Nominatim(user_agent="Movies'_Places")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    for place in places:
        try:
            location = geolocator.geocode(place[-1])
            coordinates = [location.latitude, location.longitude]
            distance = calculating_distance(initial_point, coordinates)
            place.append(coordinates)
            place.append(distance)
        except GeocoderUnavailable:
            while place in places:
                places.remove(place)
            pass
        except AttributeError:
            while place in places:
                places.remove(place)
    return places


def calculating_distance(initial_point, final_point):
    """
    Calculates distance with longitude and latitude
    :param initial_point: list of two coordinates
    :param final_point: list of two coordinates
    :return: distance, float number
    """
    radius = 6373.0

    lon1, lat1 = initial_point[0], initial_point[1]
    lon2, lat2 = final_point[0], final_point[1]

    lon1 = radians(float(lon1))
    lon2 = radians(float(lon2))
    lat1 = radians(float(lat1))
    lat2 = radians(float(lat2))

    dis_lon = lon2 - lon1
    dis_lat = lat2 - lat1

    argument1 = sin(dis_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dis_lon / 2) ** 2
    argument_c = 2 * atan2(sqrt(argument1), sqrt(1 - argument1))

    distance = radius * argument_c
    return distance


def nearest_locations(places):
    """
    Filters all locations to the nearest 10
    :param places: list of lists of locations
    :return: list of nearest 10 locations to the point
    """
    new_places = []
    for place in places:
        try:
            new = float(place[-1])
            new_places.append(place)
        except:
            continue
    sorted_locations = sorted(new_places, key=lambda x: x[-1])
    return sorted_locations[:10]


def main():
    """
    Combines and runs all modules to generate a map with three layers
    """
    print("Please enter a year you would like to have a map for: ")

    year = input()
    places = finding_places_by_year(year)
    print("Please enter your location (format: lat, long): ")

    initial_point = input().split(', ')
    print("Map is generating...")
    places_with_distance = finding_coordinates(initial_point, places)
    nearest = nearest_locations(places_with_distance)
    print("Please wait...")
    raw_map = folium.Map(location=initial_point)
    # map_with_movies = places_layer(nearest, raw_map)
    movies_map = folium.FeatureGroup(name="Markers")
    for lst in nearest:
        title = lst[0]
        location = lst[-2]
        folium.Marker(location=location, popup=title).add_to(movies_map)
    raw_map.add_child(movies_map)
    lines_map = folium.FeatureGroup(name="Distance")

    locations_for_layer = []

    for coordinate in nearest:
        locations_for_layer.append(coordinate[-2])

    folium.PolyLine(locations_for_layer, color='red').add_to(lines_map)

    raw_map.add_child(lines_map)
    raw_map.add_child(folium.LayerControl())
    raw_map.save("Your_Map.html")
    print("Finished. Please have look at the map - Your_Map.html")


main()
