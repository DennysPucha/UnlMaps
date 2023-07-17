import heapq
from math import radians, sin, cos, sqrt, atan2
from locale import format_string

from unlMaps.models import Conexion


def calcular_distancia(lat1, alt1, lat2, alt2):

    R = 6371000.0  # Radio de la Tierra en metros

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    dlat = lat2_rad - lat1_rad
    dalt = alt2 - alt1

    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dalt / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = (R * c) * 0.243
    return distance


def dijkstra(graph, start, end):
    distances = {vertex: float('inf') for vertex in graph}
    distances[start] = 0
    previous_nodes = {}  # Registro de nodos previos en el camino más corto
    visited = set()
    queue = [(0, start)]

    while queue:
        current_distance, current_vertex = heapq.heappop(queue)

        if current_distance > distances[current_vertex]:
            continue

        visited.add(current_vertex)

        if current_vertex == end:
            break

        for neighbor, distance in graph[current_vertex].items():
            new_distance = distances[current_vertex] + distance
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous_nodes[neighbor] = current_vertex
                heapq.heappush(queue, (new_distance, neighbor))

    if end not in visited:
        return None  # No se encontró un camino desde el nodo de inicio hasta el nodo de destino

    # Construir el camino desde el nodo de inicio hasta el nodo de destino
    path = []
    current_node = end
    while current_node != start:
        path.append(current_node)
        current_node = previous_nodes[current_node]
    path.append(start)
    path.reverse()

    return distances[end], path


def conectar_nodos(points, nodo1, nodo2):
    points[nodo1]['neighbors'][nodo2] = None
    points[nodo2]['neighbors'][nodo1] = None


def crear_grafo(puntos):
    graph = {}

    for punto in puntos:
        neighbors = {}
        lat1, alt1 = float(punto.latitud), float(punto.longitud)

        conexiones = Conexion.objects.filter(nodo_origen=punto)

        for conexion in conexiones:
            neighbor = conexion.nodo_destino
            lat2, alt2 = float(neighbor.latitud), float(neighbor.longitud)
            distance = calcular_distancia(lat1, alt1, lat2, alt2)
            neighbors[neighbor.codigo] = distance

        graph[punto.codigo] = neighbors

    return graph

