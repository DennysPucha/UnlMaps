import os
from django.utils import timezone

def get_image_path(instance, filename):
    # Generar un nombre de archivo único usando el nombre y la fecha actual
    name, extension = os.path.splitext(filename)
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    unique_filename = f"{name}_{timestamp}{extension}"

    # Devolver la ruta completa donde se guardará el archivo
    return os.path.join('fotos/', unique_filename)