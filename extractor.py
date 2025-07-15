import os
import math
import xml.etree.ElementTree as ET
from PIL import Image

current_directory = os.path.dirname(os.path.abspath(__file__));
osm_file_path = os.path.join(current_directory, 'limeira.osm')
base_model_file_path = os.path.join(current_directory, 'base_model.txt')
created_model_file_path = os.path.join(current_directory, '..', 'LimeiraPilot', 'config', 'model.txt')
latitudes, longitudes = [], []
lat_limit = 0
lon_limit = 0

def get_image_dimensions():
    image_path = os.path.join(current_directory, '..', 'LimeiraPilot', 'config', 'background.png')

    with Image.open(image_path) as img:
        lat_limit, lon_limit= img.size

    return lat_limit, lon_limit

lat_limit, lon_limit = get_image_dimensions()

def extract_streets_data(osm_file_path):
    tree = ET.parse(osm_file_path)
    root = tree.getroot()

    streets = {}
    street_count = {}
    allowed_paths = [
        'highway', 'trunk', 'primary', 'secondary', 'tertiary', 
        'tertiary_walk', 'residential', 'living_street', 
        'path', 'pedestrian', 'road', 'cycleway', 'crossing', 
        'junction', 'roundabout', 'mini_roundabout', 'multipolygon', 'circular'
    ]

    for way in root.findall('way'):
        street_name = None
        coordinates = []
        is_path_alllowed = False

        for tag in way.findall('tag'):
            if tag.attrib['v'] in allowed_paths:
                street_type = tag.attrib['v']
                is_path_alllowed = True
            if tag.attrib['k'] == 'name':
                street_name = tag.attrib['v']

        if is_path_alllowed and street_name:
            for nd in way.findall('nd'):
                ref = nd.attrib['ref']
                node = root.find(f'./node[@id="{ref}"]')
                if node is not None:
                    lat = float(node.attrib['lat'])
                    lon = float(node.attrib['lon'])
                    latitudes.append(lat)
                    longitudes.append(lon)
                    coordinates.append((lat, lon))
            
            if street_name in street_count:
                try:
                    street_suffix = street_count[street_name]
                    street_name_with_letter = f'{street_name} {street_suffix}'
                    street_count[street_name] += 1
                except:
                    print(street_count[street_name])
            else:
                street_name_with_letter = f'{street_name} 1'
                street_count[street_name] = 1


            if street_name_with_letter not in streets:
                streets[street_name_with_letter] = { 'type': street_type, 'coordinates': [] }

            street_id = way.attrib['id']
            street_key = f"{street_name}_{street_id}"

            if street_key not in streets:
                streets[street_key] = {'type': street_type, 'coordinates': []}

            streets[street_key]['coordinates'].extend(coordinates)
    
    return streets

def calculate_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2)

def normalize_street_coordinates(street_coordinates, max_distance):
    lat_min, lat_max = min(latitudes), max(latitudes)
    lon_min, lon_max = min(longitudes), max(longitudes)
    coefficient = 40000

    normalized_streets = {}
    for street, data in street_coordinates.items():
        coordinates = data['coordinates']
        if len(coordinates) < 2:  
            continue

        total_distance = 0
        for i in range(1, len(coordinates)):
            lat1, lon1 = coordinates[i - 1]
            lat2, lon2 = coordinates[i] 
            total_distance += calculate_distance(lat1, lon1, lat2, lon2)
        
        if total_distance > max_distance:
            continue

        normalized_coords = [
            (
                (lon - lon_min) * coefficient,
                (lat_max - lat) * coefficient
            )
            for lat, lon in coordinates
        ]
        normalized_streets[street] = {
            'type': data['type'],
            'coordinates': normalized_coords
        }

    return normalized_streets

def print_streets_with_coordinates(street_coordinates):
    for street, coords in street_coordinates.items():
        print(f'Rua: {street}')
        for coord in coords:
            print(f' - Coordenada: {coord}')

def convert_street_coordinantes_to_string(street_coordinates):
    string_street_coordinates = []
    lat_max, lon_max = 0, 0

    for street, data in street_coordinates.items():
        coords = data['coordinates']
        street_type = data['type']
        string_line_coords = ''
        remove_street = False

        for coord in coords:
            lat, lon = coord
            string_line_coords += f'[{round(coord[1])},{round(coord[0])}]-'

            if lat > lat_limit or lon > lon_limit:
                remove_street = True

            if (lon > lon_max):
                lon_max = lon
            if (lat > lat_max):
                lat_max = lat

        if not remove_street:
            string_line_coords = string_line_coords[:-1]  # Remove o último traço
            string_street_coordinates.append(f'{street} [{street_type.upper()}]{string_line_coords}\n')

    print(lat_max)
    print(lon_max)

    return ''.join(string_street_coordinates)

def create_model_txt(street_coordinates):

    with open(base_model_file_path, 'r') as base_file:
        file_lines = base_file.readlines()

    for i, line in enumerate(file_lines):
        if '#ROADMAP' in line:
            file_lines.insert(i + 1, street_coordinates)
            break

    with open(created_model_file_path, 'w', encoding='utf-8') as new_file:
        new_file.writelines(file_lines)


street_coordinates = extract_streets_data(osm_file_path);
normalized_street_coordinates = normalize_street_coordinates(street_coordinates, 0.9)
string_street_coordinates = convert_street_coordinantes_to_string(normalized_street_coordinates)
create_model_txt(string_street_coordinates)



