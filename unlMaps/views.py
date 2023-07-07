from locale import format_string

from django.shortcuts import render, redirect
from .models import Punto, Conexion
from .algoritmos.algoritmo import crear_grafo, dijkstra


def crear_conexion(request):
    if request.method == 'POST':
        punto_origen_id = request.POST.get('punto_origen')
        punto_destino_id = request.POST.get('punto_destino')

        punto_origen = Punto.objects.get(id=punto_origen_id)
        punto_destino = Punto.objects.get(id=punto_destino_id)

        Conexion.objects.create(nodo_origen=punto_origen, nodo_destino=punto_destino)
        Conexion.objects.create(nodo_origen=punto_destino, nodo_destino=punto_origen)

        return redirect('calcular_distancia')

    puntos = Punto.objects.all()

    context = {
        'puntos': puntos,
    }

    return render(request, 'crear_conexion.html', context)


def calcular_distancia(request):
    if request.method == 'POST':
        start_node_id = request.POST.get('start_node')
        end_node_id = request.POST.get('end_node')

        start_node = Punto.objects.get(id=start_node_id)
        end_node = Punto.objects.get(id=end_node_id)

        puntos = Punto.objects.all()
        graph = crear_grafo(puntos)

        if start_node.codigo not in graph or end_node.codigo not in graph:
            # Manejar el caso cuando los nodos de inicio o fin no existen en el grafo
            # Puedes mostrar un mensaje de error o redireccionar a una página de error
            return render(request, 'error.html')

        formatted_distance = dijkstra(graph, start_node.codigo, end_node.codigo)

        context = {
            'start_node': start_node,
            'end_node': end_node,
            'puntos': puntos,
            'formatted_distance': formatted_distance,
        }

        return render(request, 'calcular_distancia.html', context)

    puntos = Punto.objects.all()

    context = {
        'puntos': puntos,
    }

    return render(request, 'calcular_distancia.html', context)
