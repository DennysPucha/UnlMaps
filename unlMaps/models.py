
from django.db import models

class Mapa(models.Model):
    nombre = models.CharField(max_length=30)
    grafo = models.JSONField()

    def __str__(self):
        return self.nombre

class Facultad(models.Model):
    nombre = models.CharField(max_length=100)
    sigla = models.CharField(max_length=100)
    decano = models.CharField(max_length=100)
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

    def __str__(self):
        return self.codigo

class Bloque(Punto):
    nomenclatura = models.CharField(max_length=100)
    descripcion_bloque = models.CharField(max_length=100)

    def __str__(self):
        return self.nomenclatura

class Conexion(models.Model):
    nodo_origen = models.ForeignKey('Punto', on_delete=models.CASCADE, related_name='conexiones_salientes')
    nodo_destino = models.ForeignKey('Punto', on_delete=models.CASCADE, related_name='conexiones_entrantes')

    def __str__(self):
        return f"Conexión de {self.nodo_origen} a {self.nodo_destino}"


