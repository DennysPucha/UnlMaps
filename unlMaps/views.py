
from .models import Punto, Conexion, Mapa
from .algoritmos.algoritmo import crear_grafo, dijkstra
from django.shortcuts import render, redirect
from .models import Bloque, Punto, Facultad

from .algoritmos.algoritmo import calcular_distancia as ca

def crear_conexion(request):
    if request.method == 'POST':
        punto_origen_id = request.POST.get('punto_origen')
        punto_destino_id = request.POST.get('punto_destino')

        punto_origen = Punto.objects.get(id=punto_origen_id)
        punto_destino = Punto.objects.get(id=punto_destino_id)

        Conexion.objects.create(nodo_origen=punto_origen, nodo_destino=punto_destino)
        Conexion.objects.create(nodo_origen=punto_destino, nodo_destino=punto_origen)

        # Llamar a la función para actualizar el grafo
        actualizar_grafo()

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

        if not start_node_id or not end_node_id:
            return render(request, 'error.html')

        try:
            start_node = Punto.objects.get(id=start_node_id)
            end_node = Punto.objects.get(id=end_node_id)
        except Punto.DoesNotExist:
            return render(request, 'error.html')

        puntos = Punto.objects.all()
        graph = crear_grafo(puntos)

        if start_node.codigo not in graph or end_node.codigo not in graph:
            return render(request, 'error.html')

        result = dijkstra(graph, start_node.codigo, end_node.codigo)
        if result is None:
            return render(request, 'error.html')

        distance, path = result

        distance = round(distance, 2)

        context = {
            'start_node': start_node,
            'end_node': end_node,
            'puntos': puntos,
            'distance': distance,
            'path': path,
        }

        return render(request, 'calcular_distancia.html', context)

    puntos = Punto.objects.all()

    context = {
        'puntos': puntos,
    }

    return render(request, 'calcular_distancia.html', context)


def crear_objeto(request):
    if request.method == 'POST':
        tipo_objeto = request.POST.get('tipo_objeto')
        if tipo_objeto == 'bloque':
            return redirect('crear_bloque')
        elif tipo_objeto == 'punto':
            return redirect('crear_punto')

    return render(request, 'crear_objeto.html')
def admin(request):
    facultades = Facultad.objects.all()
    return render(request, 'admin.html', {'facultades': facultades})


# def crear_bloque(request):
#     if request.method == 'POST':
#         # Obtener los datos del formulario
#         codigo = request.POST['codigo']
#         latitud = request.POST['latitud']
#         longitud = request.POST['longitud']
#         descripcion = request.POST['descripcion']
#         informacion = request.POST['informacion']
#         valoracion = request.POST['valoracion']
#         foto = request.FILES['foto']
#         facultad_id = request.POST['facultad']
#
#         # Obtener la facultad seleccionada
#         facultad = Facultad.objects.get(id=facultad_id)
#
#         # Crear el objeto Bloque y guardar en la base de datos
#         bloque = Bloque(
#             codigo=codigo,
#             latitud=latitud,
#             longitud=longitud,
#             descripcion=descripcion,
#             informacion=informacion,
#             valoracion=valoracion,
#             foto=foto,
#             facultad=facultad
#         )
#         bloque.save()
#
#         # Redireccionar a la página de administración o la página deseada
#         return redirect('/')
#
#     # Si la solicitud es GET, renderizar el formulario
#     facultades = Facultad.objects.all()
#     return render(request, 'crear_bloque.html', {'facultades': facultades})
def crear_bloque(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        codigo = request.POST['codigo']
        latitud = request.POST['latitud']
        longitud = request.POST['longitud']
        descripcion = request.POST['descripcion']
        informacion = request.POST['informacion']
        valoracion = request.POST['valoracion']
        foto = request.FILES['foto']
        facultad_id = request.POST['facultad']

        # Obtener la facultad seleccionada
        facultad = Facultad.objects.get(id=facultad_id)

        # Crear el objeto Bloque y guardar en la base de datos
        bloque = Bloque(
            codigo=codigo,
            latitud=latitud,
            longitud=longitud,
            descripcion=descripcion,
            informacion=informacion,
            valoracion=valoracion,
            foto=foto,
            facultad=facultad
        )
        bloque.save()

        # Llamar a la función para actualizar el grafo
        actualizar_grafo()

        # Redireccionar a la página de administración o la página deseada
        return redirect('/')

    # Si la solicitud es GET, renderizar el formulario
    facultades = Facultad.objects.all()
    return render(request, 'crear_bloque.html', {'facultades': facultades})

# def crear_punto(request):
#     if request.method == 'POST':
#         # Obtener los datos del formulario
#         codigo = request.POST['codigo']
#         latitud = request.POST['latitud']
#         longitud = request.POST['longitud']
#         descripcion = request.POST['descripcion']
#         facultad_id = request.POST['facultad']
#
#         # Obtener la facultad seleccionada
#         facultad = Facultad.objects.get(id=facultad_id)
#
#         # Crear el objeto Punto y guardar en la base de datos
#         punto = Punto(
#             codigo=codigo,
#             latitud=latitud,
#             longitud=longitud,
#             descripcion=descripcion,
#             facultad=facultad
#         )
#         punto.save()
#
#         # Redireccionar a la página de administración o la página deseada
#         return redirect('/')
#
#     # Si la solicitud es GET, renderizar el formulario
#     facultades = Facultad.objects.all()
#     return render(request, 'crear_punto.html', {'facultades': facultades})
def crear_punto(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        codigo = request.POST['codigo']
        latitud = request.POST['latitud']
        longitud = request.POST['longitud']
        descripcion = request.POST['descripcion']
        facultad_id = request.POST['facultad']

        # Obtener la facultad seleccionada
        facultad = Facultad.objects.get(id=facultad_id)

        # Crear el objeto Punto y guardar en la base de datos
        punto = Punto(
            codigo=codigo,
            latitud=latitud,
            longitud=longitud,
            descripcion=descripcion,
            facultad=facultad
        )
        punto.save()

        # Llamar a la función para actualizar el grafo
        actualizar_grafo()

        # Redireccionar a la página de administración o la página deseada
        return redirect('/')

    # Si la solicitud es GET, renderizar el formulario
    facultades = Facultad.objects.all()
    return render(request, 'crear_punto.html', {'facultades': facultades})
import json


def actualizar_grafo():
    # Obtener el grafo existente desde el objeto Mapa
    mapa = Mapa.objects.first()
    grafo_existente = mapa.grafo if mapa else {}

    # Convertir la cadena de texto JSON en un diccionario
    json_existente = json.loads(grafo_existente) if grafo_existente else {}

    # Obtener todos los puntos y conexiones existentes
    puntos = Punto.objects.all()
    conexiones = Conexion.objects.all()

    # Actualizar el grafo con los puntos y conexiones existentes
    grafo = {}
    for punto in puntos:
        grafo[punto.codigo] = {}

    for conexion in conexiones:
        nodo_origen_id = conexion.nodo_origen.codigo
        nodo_destino_id = conexion.nodo_destino.codigo
        latitud_origen = float(conexion.nodo_origen.latitud)
        longitud_origen = float(conexion.nodo_origen.longitud)
        latitud_destino = float(conexion.nodo_destino.latitud)
        longitud_destino = float(conexion.nodo_destino.longitud)

        distancia = ca(latitud_origen, longitud_origen, latitud_destino, longitud_destino)
        grafo[nodo_origen_id][nodo_destino_id] = distancia

    # Combinar el grafo existente con las nuevas conexiones y distancias
    json_actualizado = json_existente.copy()

    for nodo_origen_id, conexiones_destino in grafo.items():
        json_actualizado.setdefault(str(nodo_origen_id), {}).update(conexiones_destino)

    # Guardar el JSON actualizado en el objeto Mapa
    if mapa:
        mapa.grafo = json.dumps(json_actualizado)  # Convertir a cadena de texto JSON
        mapa.save()
    else:
        Mapa.objects.create(nombre='Mapa', grafo=json.dumps(json_actualizado))

    # Imprimir el JSON del mapa en la consola
    print(json.dumps(json_actualizado, indent=4))