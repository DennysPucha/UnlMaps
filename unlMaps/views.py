from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy

from .models import Punto, Conexion, Mapa, Cuenta
from .algoritmos.algoritmo import crear_grafo, dijkstra
from django.shortcuts import render, redirect
from .models import Bloque, Punto, Facultad
from django.template import RequestContext
from django.shortcuts import render
from .algoritmos.algoritmo import calcular_distancia as ca
from django.http import JsonResponse

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import render, HttpResponse
from .models import Punto, Conexion
from django.db.models import Q
def crear_conexion(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'crear':
            punto_origen_id = request.POST.get('punto_origen')
            punto_destino_id = request.POST.get('punto_destino')

            if punto_origen_id == punto_destino_id:
                return HttpResponse('Error: El punto de origen y destino son iguales. Selecciona puntos diferentes.')

            try:
                # Verificar si la conexión ya existe
                conexion_existente = Conexion.objects.filter(nodo_origen_id=punto_origen_id,
                                                             nodo_destino_id=punto_destino_id).exists()
                if conexion_existente:
                    return HttpResponse('Error: La conexión ya existe.')

                # Obtener los objetos de los puntos
                punto_origen = Punto.objects.get(id=punto_origen_id)
                punto_destino = Punto.objects.get(id=punto_destino_id)

                # Crear la conexión
                Conexion.objects.create(nodo_origen=punto_origen, nodo_destino=punto_destino)

                # Llamar a la función para actualizar el grafo
                # actualizar_grafo()

                #return redirect('calcular_distancia')

            except Punto.DoesNotExist:
                return HttpResponse('Error: Uno o ambos puntos seleccionados no existen.')
        elif accion == 'borrar':
            punto_origen_id = request.POST.get('punto_origen')
            punto_destino_id = request.POST.get('punto_destino')

            if punto_origen_id == punto_destino_id:
                return HttpResponse('Error: El punto de origen y destino son iguales. Selecciona puntos diferentes.')

            try:
                conexiones_a_borrar = Conexion.objects.filter(
                    Q(nodo_origen_id=punto_origen_id, nodo_destino_id=punto_destino_id) |
                    Q(nodo_origen_id=punto_destino_id, nodo_destino_id=punto_origen_id)
                )

                # Borrar las conexiones
                conexiones_a_borrar.delete()

            except Conexion.DoesNotExist:
                return HttpResponse('Error: La conexión seleccionada no existe.')

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
def selector(request):
    facultades = Facultad.objects.all()
    return render(request, 'vistaUsuario.html', {'facultades': facultades})


def buscar(request):

    if request.method == 'POST':
        selector = request.POST['selector']
        buscar = request.POST['buscar']

        if selector == 'Bloque':
            # Buscar todos los bloques que coincidan con la entrada de búsqueda
            bloques_encontrados = Bloque.objects.filter(codigo=buscar)
        else:
            # Buscar todos los bloques que coincidan con la facultad
            bloques_encontrados = Bloque.objects.filter(facultad__nombre=buscar)

    return render(request, 'vistaUsuario.html', {'bloques_encontrados': bloques_encontrados})



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

@login_required
def crear_punto(request):
    print(request.user)
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



def iniciar_sesion(request):
    if request.method == 'POST':
        usuario = request.POST['usuario']
        contrasenia = request.POST['password']
        user = authenticate(request, username=usuario, password=contrasenia)
        if user is not None:
            login(request, user)
            return redirect('inicio')  # Reemplaza 'inicio' con el nombre de la vista a la que deseas redirigir después del inicio de sesión
        else:
            error_message = "Credenciales inválidas. Inténtalo nuevamente."
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')

def inicio(request):
    # Lógica de la vista de inicio
    return render(request, 'inicio.html')

def cerrar_sesion(request):
    logout(request)
    return redirect(reverse_lazy('login'))

def puntos(request):
    # Usar prefetch_related para obtener los puntos con sus conexiones salientes y entrantes en una sola consulta
    puntos_queryset = Punto.objects.all().prefetch_related('conexiones_salientes')
    puntos_list = [punto.as_dict() for punto in puntos_queryset]

    # Convertir la lista de puntos a formato JSON
    puntos_json = json.dumps(puntos_list)

    return render(request, 'vistaUsuario.html', {'puntos_json': puntos_json})

def allPuntos(request):
    puntos_queryset = Punto.objects.all()
    puntos_list = [punto.as_dict() for punto in puntos_queryset]
    puntos_json = json.dumps(puntos_list)

    return render(request, 'crear_conexion.html', {'puntos_json': puntos_json})


def obtener_puntos(request):
    puntos = Punto.objects.all().values()  # Obtiene todos los puntos desde la base de datos

    return JsonResponse(list(puntos), safe=False)
