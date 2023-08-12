
from django.db import models
from .utils import get_image_path
class Mapa(models.Model):
    nombre = models.CharField(max_length=30)
    grafo = models.JSONField()

    def __str__(self):
        return self.nombre

class Facultad(models.Model):
    nombre = models.CharField(max_length=100)
    sigla = models.CharField(max_length=100)
    decano = models.CharField(max_length=100)
    foto = models.ImageField(upload_to=get_image_path)
    mapa = models.ForeignKey(Mapa, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Cuenta(models.Model):
    nombre = models.CharField(max_length=100)
    usuario = models.CharField(max_length=100)
    contrasenia = models.CharField(max_length=100)
    mapa = models.OneToOneField(Mapa, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class Punto(models.Model):
    codigo = models.CharField(max_length=100)
    latitud = models.CharField(max_length=100)
    longitud = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    facultad = models.ForeignKey(Facultad, on_delete=models.CASCADE)

    def as_dict(self):
        conexiones_salientes = [
            {
                'codigo': conexion.nodo_destino.codigo,
                'latitud': conexion.nodo_destino.latitud,
                'longitud': conexion.nodo_destino.longitud
            }
            for conexion in self.conexiones_salientes.all()
        ]

        try:
            bloque_data = {
                'valoracion': self.bloque.valoracion,
                'informacion': self.bloque.informacion,
                'foto': self.bloque.foto.path if self.bloque.foto else None,
            }
        except Bloque.DoesNotExist:
            bloque_data = {}

        return {
            'codigo': self.codigo,
            'latitud': self.latitud,
            'longitud': self.longitud,
            'descripcion': self.descripcion,
            'facultad': self.facultad.nombre,
            'conexiones_salientes': conexiones_salientes,
            **bloque_data,  # Incorporar los datos específicos de Bloque
        }

    def __str__(self):
        return self.codigo


class Bloque(Punto):
    informacion = models.CharField(max_length=100)
    valoracion = models.IntegerField(default=0)
    foto = models.ImageField(upload_to=get_image_path)

    def as_dict(self):
        punto_data = super().as_dict()
        bloque_data = {
            'valoracion': self.valoracion,
            'informacion': self.informacion,
            'foto': self.foto.path if self.foto else None,
        }
        punto_data.update(bloque_data)
        return punto_data

    def __str__(self):
        return self.codigo


class Conexion(models.Model):
    nodo_origen = models.ForeignKey('Punto', on_delete=models.CASCADE, related_name='conexiones_salientes')
    nodo_destino = models.ForeignKey('Punto', on_delete=models.CASCADE, related_name='conexiones_entrantes')

    def __str__(self):
        return f"Conexión de {self.nodo_origen} a {self.nodo_destino}"




