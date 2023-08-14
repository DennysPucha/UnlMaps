import os
from django.utils import timezone

def get_image_path(instance, filename):
    name, extension = os.path.splitext(filename)
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    unique_filename = f"{name}_{timestamp}{extension}"
    return os.path.join('fotos/', unique_filename)

