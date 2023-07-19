from .models import Punto, Conexion


def obtener_toda_la_informacion(request):
    # Obtener todos los objetos de la tabla MiModelo
    objetos = MiModelo.objects.all()

    # Puedes iterar sobre los objetos para acceder a sus atributos
    for objeto in objetos:
        print(objeto.nombre_atributo)
        # Aquí puedes hacer lo que necesites con cada objeto y sus atributos

    # También puedes pasar los objetos al contexto para utilizarlos en una plantilla HTML
    context = {
        'objetos': objetos,
    }

    return render(request, 'mi_template.html', context)
