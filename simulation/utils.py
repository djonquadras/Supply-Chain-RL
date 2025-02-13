import requests

# Função para calcular distância real usando OSRM API
def calculate_osrm_distance(origin_lat, origin_lon, dest_lat, dest_lon):
    url = f"http://router.project-osrm.org/route/v1/driving/{origin_lon},{origin_lat};{dest_lon},{dest_lat}?overview=false"
    response = requests.get(url)
    data = response.json()
    if data['code'] == 'Ok':
        distance = data['routes'][0]['distance']  # Distância em metros
        return distance / 1000  # Convertendo para quilômetros
    else:
        raise Exception(f"Erro ao buscar dados de distância: {data['code']}")


"""
# Exemplo de uso
origin_lat, origin_lon = 43.474649, 11.878045  # Localização do fornecedor
dest_lat, dest_lon = 43.801232, 11.245057  # Localização da fábrica

distance = calculate_osrm_distance(origin_lat, origin_lon, dest_lat, dest_lon)
print(f"Distância real: {distance} km")
"""