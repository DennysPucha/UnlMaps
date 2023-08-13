from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Conexion, Mapa, Cuenta
from .algoritmos.algoritmo import crear_grafo, dijkstra
from django.shortcuts import redirect, get_object_or_404
from .models import Bloque, Punto, Facultad
from django.shortcuts import render
from .algoritmos.algoritmo import calcular_distancia as ca
import json

@login_required
def crear_conexion(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'crear':
            punto_origen_codigo = request.POST.get('punto_origen')
            punto_destino_codigo = request.POST.get('punto_destino')

            if punto_origen_codigo == punto_destino_codigo:
                return render(request, 'error_puntos_iguales.html')

            try:
                conexion_existente = Conexion.objects.filter(nodo_origen__codigo=punto_origen_codigo,
                                                             nodo_destino__codigo=punto_destino_codigo).exists()
                if conexion_existente:
                    return render(request, 'error_conexion_existente.html')

                punto_origen = Punto.objects.get(codigo=punto_origen_codigo)
                punto_destino = Punto.objects.get(codigo=punto_destino_codigo)

                Conexion.objects.create(nodo_origen=punto_origen, nodo_destino=punto_destino)
                Conexion.objects.create(nodo_origen=punto_destino, nodo_destino=punto_origen)

                actualizar_grafo()

            except Punto.DoesNotExist:
                return render(request, 'error_no_existen.html')
        elif accion == 'borrar':
            punto_origen_codigo = request.POST.get('punto_origen')
            punto_destino_codigo = request.POST.get('punto_destino')

            if punto_origen_codigo == punto_destino_codigo:
                return render(request, 'error_puntos_iguales.html')

            try:
                conexiones_a_borrar = Conexion.objects.filter(
                    Q(nodo_origen__codigo=punto_origen_codigo, nodo_destino__codigo=punto_destino_codigo) |
                    Q(nodo_origen__codigo=punto_destino_codigo, nodo_destino__codigo=punto_origen_codigo)
                )
                conexiones_a_borrar.delete()

            except Conexion.DoesNotExist:
                return render(request, 'error_conexion_no_existente.html')

    mapas_queryset = Mapa.objects.prefetch_related(
        'facultad_set__punto_set__conexiones_salientes',
        'facultad_set__punto_set__bloque'
    ).all()

    grafo = {}
    for mapa in mapas_queryset:
        puntos = []

        for facultad in mapa.facultad_set.all():
            for punto in facultad.punto_set.all():
                punto_data = punto.as_dict()
                punto_data['conexiones'] = [
                    {
                        'origen': conexion.nodo_origen.codigo,
                        'destino': conexion.nodo_destino.codigo,
                    }
                    for conexion in punto.conexiones_salientes.all()
                ]
                if isinstance(punto, Bloque):
                    bloque = punto.bloque
                    punto_data.update({
                        'valoracion': bloque.valoracion,
                        'informacion': bloque.informacion,
                        'foto': bloque.foto.path if bloque.foto else None,
                    })
                puntos.append(punto_data)

        grafo[mapa.nombre] = {
            'puntos': puntos,
        }

    grafo_json = json.dumps(grafo)

    return render(request, 'crear_conexion.html', {'grafo_json': grafo_json})


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


# "{\"A17\": {}, \"A41\": {}, \"A40\": {} }"--> forma en como guarda los puntos

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

def actualizar_grafo():
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

    # Obtener el mapa existente o crear uno nuevo si no existe
    mapa, _ = Mapa.objects.get_or_create(nombre='Mapa')

    # Guardar el grafo actualizado en el objeto Mapa
    grafo_json = json.dumps(grafo)
    mapa.grafo = grafo_json
    mapa.save()


def iniciar_sesion(request):
    if request.method == 'POST':
        usuario = request.POST['usuario']
        contrasenia = request.POST['password']
        user = authenticate(request, username=usuario, password=contrasenia)
        if user is not None:
            login(request, user)
            return redirect(
                'inicio')
        else:
            error_message = "Credenciales inválidas. Inténtalo nuevamente."
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')


@login_required
def inicio(request):
    if 'success_message' in request.session:
        success_message = request.session['success_message']
        del request.session['success_message']
    else:
        success_message = None

    return render(request, 'inicio.html', {'success_message': success_message})


@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect(reverse_lazy('login'))


def index(request):
    return render(request, 'index.html')


@login_required
def gestionar_facultades(request):
    facultades = Facultad.objects.all()

    if request.method == 'POST':
        # Si hay una solicitud POST, significa que se está enviando un formulario para agregar una nueva facultad
        nombre = request.POST.get('nombre')
        sigla = request.POST.get('sigla')
        decano = request.POST.get('decano')
        foto = request.FILES.get('foto')
        mapa = Mapa.objects.first()

        # Validar que los campos requeridos no estén vacíos
        if not nombre or not sigla or not decano:
            messages.error(request, "Por favor, complete todos los campos.")
            return redirect('gestionar_facultades')

        # Verificar que el archivo de foto sea una imagen válida
        if foto:
            if not foto.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                messages.error(request, "El archivo de foto debe ser una imagen en formato JPG, JPEG, PNG o GIF.")
                return redirect('gestionar_facultades')

        # Crear una nueva facultad con los valores del formulario y guardarla en la base de datos
        facultad = Facultad(nombre=nombre, sigla=sigla, decano=decano, foto=foto, mapa=mapa)
        facultad.save()

        # Mostrar mensaje de éxito si se agregó la facultad correctamente
        messages.success(request, "Nueva facultad creada correctamente.")
        return redirect('gestionar_facultades')

    return render(request, 'gestionar_facultades.html', {'facultades': facultades})


@login_required
def editar_facultad(request, facultad_id):
    facultad = get_object_or_404(Facultad, id=facultad_id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        sigla = request.POST.get('sigla')
        decano = request.POST.get('decano')
        foto = request.FILES.get('foto')

        # Verificar que el archivo de foto sea una imagen válida
        if foto and not foto.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            messages.error(request, "El archivo de foto debe ser una imagen en formato JPG, JPEG, PNG o GIF.")
            return redirect('editar_facultad', facultad_id=facultad_id)

        facultad.nombre = nombre
        facultad.sigla = sigla
        facultad.decano = decano
        if foto:
            facultad.foto = foto

        facultad.save()

        messages.success(request, "La facultad ha sido actualizada correctamente.")
        return redirect('gestionar_facultades')

    else:
        foto_url = facultad.foto.url if facultad.foto else None
        return render(request, 'editar_facultad.html', {'facultad': facultad, 'foto_url': foto_url})


@login_required
def eliminar_facultad(request, facultad_id):
    facultad = get_object_or_404(Facultad, id=facultad_id)

    if request.method == 'POST':
        facultad.delete()
        actualizar_grafo()
        messages.success(request, "La facultad ha sido eliminada correctamente.")
        return redirect('gestionar_facultades')

    return render(request, 'eliminar_facultad.html', {'facultad': facultad})


@login_required
def gestionar_bloques_puntos(request):
    bloques = Bloque.objects.all()
    facultades = Facultad.objects.all()
    puntos = Punto.objects.exclude(bloque__isnull=False)

    if 'success_message' in request.session:
        success_message = request.session['success_message']
        del request.session['success_message']
    else:
        success_message = None

    return render(request, 'gestionar_bloques_puntos.html',
                  {'bloques': bloques, 'puntos': puntos, 'facultades': facultades, 'success_message': success_message})


@login_required
def crear_bloque(request):
    if request.method == 'POST':

        codigo = request.POST.get('codigo')
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        descripcion = request.POST.get('descripcion')
        informacion = request.POST.get('informacion')
        valoracion = request.POST.get('valoracion')
        foto = request.FILES.get('foto')
        facultad_id = request.POST.get('facultad')  # Obtener el ID de la facultad seleccionada

        facultad = Facultad.objects.get(id=facultad_id)

        # Verificar que latitud y longitud sean números float válidos
        try:
            latitud = float(latitud)
            longitud = float(longitud)
        except ValueError:
            messages.error(request, "Latitud y longitud deben ser valores numéricos.")
            return redirect('crear_bloque')

        # Verificar que la valoración esté en el rango permitido (1 al 5)
        if not 1 <= int(valoracion) <= 5:
            messages.error(request, "La valoración debe estar en el rango de 1 a 5.")
            return redirect('crear_bloque')

        # Verificar que el archivo de foto sea una imagen válida
        if foto:

            if foto and not foto.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                messages.error(request, "El archivo de foto debe ser una imagen en formato JPG, JPEG, PNG o GIF.")
                return redirect('crear_bloque')

        # Actualizar los campos del bloque
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

        messages.success(request, "El bloque ha sido creado correctamente.")
        return redirect('gestionar_bloques_puntos')

    else:
        facultades = Facultad.objects.all()
        return render(request, 'crear_bloque.html', {'facultades': facultades})


@login_required
def crear_punto(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        codigo = request.POST.get('codigo')
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        descripcion = request.POST.get('descripcion')
        facultad_id = request.POST.get('facultad')

        facultad = Facultad.objects.get(id=facultad_id)

        try:
            latitud = float(latitud)
            longitud = float(longitud)
        except ValueError:
            messages.error(request, "Latitud y longitud deben ser valores numéricos.")
            return redirect('crear_punto')

        punto = Punto(
            codigo=codigo,
            latitud=latitud,
            longitud=longitud,
            descripcion=descripcion,
            facultad=facultad
        )

        punto.save()
        actualizar_grafo()
        messages.success(request, "El punto ha sido actualizado correctamente.")
        return redirect('gestionar_bloques_puntos')

    else:
        facultades = Facultad.objects.all()
        return render(request, 'crear_punto.html', {'facultades': facultades})


@login_required
def editar_bloque(request, bloque_id):
    bloque = get_object_or_404(Bloque, id=bloque_id)

    if request.method == 'POST':
        # Obtener los datos del formulario
        codigo = request.POST.get('codigo')
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        descripcion = request.POST.get('descripcion')
        informacion = request.POST.get('informacion')
        valoracion = request.POST.get('valoracion')
        foto = request.FILES.get('foto')
        facultad_id = request.POST.get('facultad')  # Obtener el ID de la facultad seleccionada

        # Verificar que latitud y longitud sean números float válidos
        try:
            latitud = float(latitud)
            longitud = float(longitud)
        except ValueError:
            messages.error(request, "Latitud y longitud deben ser valores numéricos.")
            return redirect('editar_bloque', bloque_id=bloque_id)

        # Verificar que la valoración esté en el rango permitido (1 al 5)
        if not 1 <= int(valoracion) <= 5:
            messages.error(request, "La valoración debe estar en el rango de 1 a 5.")
            return redirect('editar_bloque', bloque_id=bloque_id)

        # Verificar que el archivo de foto sea una imagen válida

        if foto and not foto.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            messages.error(request, "El archivo de foto debe ser una imagen en formato JPG, JPEG, PNG o GIF.")
            return redirect('editar_bloque', bloque_id=bloque_id)

        # Actualizar los campos del bloque
        bloque.codigo = codigo
        bloque.latitud = latitud
        bloque.longitud = longitud
        bloque.descripcion = descripcion
        bloque.informacion = informacion
        bloque.valoracion = valoracion

        if foto:
            bloque.foto = foto

        # Actualizar el campo facultad usando el ID obtenido
        bloque.facultad = get_object_or_404(Facultad, id=facultad_id)

        bloque.save()
        actualizar_grafo()
        messages.success(request, "El bloque ha sido actualizado correctamente.")
        return redirect('gestionar_bloques_puntos')

    else:
        foto_url = bloque.foto.url if bloque.foto else None
        facultades = Facultad.objects.all()  # Obtener todas las facultades para mostrar en el formulario
        return render(request, 'editar_bloque.html', {'bloque': bloque, 'foto_url': foto_url, 'facultades': facultades})


@login_required
def editar_punto(request, punto_id):
    punto = get_object_or_404(Punto, id=punto_id)

    if request.method == 'POST':
        # Obtener los datos del formulario
        codigo = request.POST.get('codigo')
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        descripcion = request.POST.get('descripcion')
        facultad_id = request.POST.get('facultad')  # Obtener el ID de la facultad seleccionada

        # Verificar que latitud y longitud sean números float válidos
        try:
            latitud = float(latitud)
            longitud = float(longitud)
        except ValueError:
            messages.error(request, "Latitud y longitud deben ser valores numéricos.")
            return redirect('editar_punto', punto_id=punto_id)

        # Actualizar los campos del punto
        punto.codigo = codigo
        punto.latitud = latitud
        punto.longitud = longitud
        punto.descripcion = descripcion

        # Actualizar el campo facultad usando el ID obtenido
        punto.facultad = get_object_or_404(Facultad, id=facultad_id)

        punto.save()
        actualizar_grafo()
        messages.success(request, "El punto ha sido actualizado correctamente.")
        return redirect('gestionar_bloques_puntos')

    else:
        facultades = Facultad.objects.all()  # Obtener todas las facultades para mostrar en el formulario
        return render(request, 'editar_punto.html', {'punto': punto, 'facultades': facultades})


@login_required
def buscar_facultades(request):
    if request.method == 'GET':
        search_text = request.GET.get('search_text')
        facultades = Facultad.objects.filter(nombre__icontains=search_text)
        return render(request, 'resultados_busqueda_facultades.html', {'facultades': facultades})


@login_required
def buscar_bloques(request):
    if request.method == 'GET':
        search_text = request.GET.get('search_text')
        facultad_id = request.GET.get('facultad')  # Obtener la facultad seleccionada

        bloques = Bloque.objects.all()

        if search_text:
            bloques = bloques.filter(codigo__icontains=search_text)

        if facultad_id:
            bloques = bloques.filter(facultad__id=facultad_id)

        return render(request, 'resultados_busqueda_bloques.html', {'bloques': bloques})


@login_required
def buscar_puntos(request):
    if request.method == 'GET':
        search_text = request.GET.get('search_text_puntos')
        facultad_id = request.GET.get('facultad_puntos')  # Obtener la facultad seleccionada

        puntos = Punto.objects.exclude(bloque__isnull=False)

        if search_text:
            puntos = puntos.filter(codigo__icontains=search_text)

        if facultad_id:
            puntos = puntos.filter(facultad__id=facultad_id)

        return render(request, 'resultados_busqueda_puntos.html', {'puntos': puntos})


@login_required
def gestionar_cuenta_view(request):
    mapa = get_object_or_404(Mapa, nombre="Mapa")
    cuenta = mapa.cuenta

    if request.method == 'POST':
        # Obtener los datos del formulario enviado
        nombre = request.POST.get('nombre', '')
        usuario = request.POST.get('usuario', '')
        old_contrasenia = request.POST.get('old_contrasenia', '')
        new_contrasenia = request.POST.get('new_contrasenia', '')
        confirm_new_contrasenia = request.POST.get('confirm_new_contrasenia', '')

        # Verificar que la contraseña anterior sea correcta
        if old_contrasenia != cuenta.contrasenia:
            messages.error(request, "La contraseña actual es incorrecta.")
            return render(request, 'gestionar_cuenta.html', {'cuenta': cuenta})

        if new_contrasenia and not confirm_new_contrasenia:
            messages.error(request, "Debes confirmar la nueva contraseña.")
            return render(request, 'gestionar_cuenta.html', {'cuenta': cuenta})

        if new_contrasenia != confirm_new_contrasenia:
            messages.error(request, "Las contraseñas nuevas no coinciden.")
            return render(request, 'gestionar_cuenta.html', {'cuenta': cuenta})

        # Si los campos de la nueva contraseña están vacíos, no cambiar la contraseña
        if not new_contrasenia:
            new_contrasenia = cuenta.contrasenia

        # Actualizar los datos de la cuenta, incluida la contraseña
        cuenta.nombre = nombre
        cuenta.usuario = usuario
        cuenta.contrasenia = new_contrasenia  # Actualizamos la contraseña con la nueva
        cuenta.save()

        messages.success(request, "La cuenta ha sido actualizada correctamente.")
        return redirect('inicio')

    return render(request, 'gestionar_cuenta.html', {'cuenta': cuenta})


@login_required
def eliminar_bloque(request, bloque_id):
    bloque = get_object_or_404(Bloque, id=bloque_id)

    if request.method == 'POST':
        bloque.delete()
        messages.success(request, "El bloque ha sido eliminado correctamente.")
        actualizar_grafo()
        return redirect('gestionar_bloques_puntos')

    return render(request, 'eliminar_bloque.html', {'bloque': bloque})


@login_required
def eliminar_punto(request, punto_id):
    punto = get_object_or_404(Punto, id=punto_id)

    if request.method == 'POST':
        punto.delete()
        messages.success(request, "El punto ha sido eliminado correctamente.")
        actualizar_grafo()
        return redirect('gestionar_bloques_puntos')

    return render(request, 'eliminar_punto.html', {'punto': punto})


@login_required
def vista_grafo_admin(request):
    mapa = Mapa.objects.get(nombre='Mapa')
    grafo_data = mapa.grafo
    grafo_dict = json.loads(grafo_data)

    nodes = []
    links = []

    for source_node, connections in grafo_dict.items():
        nodes.append({"id": source_node})
        for target_node in connections:
            links.append({"source": source_node, "target": target_node})

    return render(request, 'vista_grafo_admin.html', {'nodes': nodes, 'links': links})


def puntos(request):
    mapas_queryset = Mapa.objects.prefetch_related(
        'facultad_set__punto_set__conexiones_salientes',
        'facultad_set__punto_set__bloque'
    ).all()

    grafo = {}
    for mapa in mapas_queryset:
        puntos = []

        for facultad in mapa.facultad_set.all():
            for punto in facultad.punto_set.all():
                punto_data = punto.as_dict()
                punto_data['conexiones'] = [
                    {
                        'origen': conexion.nodo_origen.codigo,
                        'destino': conexion.nodo_destino.codigo,
                    }
                    for conexion in punto.conexiones_salientes.all()
                ]
                if isinstance(punto, Bloque):
                    bloque = punto.bloque
                    punto_data.update({
                        'valoracion': bloque.valoracion,
                        'informacion': bloque.informacion,
                        'foto': bloque.foto.path if bloque.foto else None,
                    })
                puntos.append(punto_data)

        grafo[mapa.nombre] = {
            'puntos': puntos,
        }

    grafo_json = json.dumps(grafo)

    return render(request, 'vistaUsuario.html', {'grafo_json': grafo_json})



def allPuntos(request):
    puntos_queryset = Punto.objects.all()
    puntos_list = [punto.as_dict() for punto in puntos_queryset]
    puntos_json = json.dumps(puntos_list)

    return render(request, 'crear_conexion.html', {'puntos_json': puntos_json})


def obtener_puntos(request):
    puntos = Punto.objects.all().values()

    return JsonResponse(list(puntos), safe=False)