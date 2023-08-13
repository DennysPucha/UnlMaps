"""
URL configuration for ProyectoIntegrador project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.template.context_processors import static
from django.urls import path

from django.urls import path

from ProyectoIntegrador import settings
from unlMaps import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('gestionar_mapa/', views.crear_conexion, name='crear_conexion'),
    path('crear_bloque/', views.crear_bloque, name='crear_bloque'),
    path('crear_punto/', views.crear_punto, name='crear_punto'),
    path('admin/', admin.site.urls),
    path('login/', views.iniciar_sesion, name='login'),
    path('inicio/', views.inicio, name='inicio'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('', views.index, name='index'),
    path('gestionar_facultades/', views.gestionar_facultades, name='gestionar_facultades'),
    path('editar_facultad/<int:facultad_id>/', views.editar_facultad, name='editar_facultad'),
    path('editar_bloque/<int:bloque_id>/', views.editar_bloque, name='editar_bloque'),
    path('editar_punto/<int:punto_id>/', views.editar_punto, name='editar_punto'),
    path('buscar_facultades/', views.buscar_facultades, name='buscar_facultades'),
    path('buscar_bloques/', views.buscar_bloques, name='buscar_bloques'),
    path('buscar_puntos/', views.buscar_puntos, name='buscar_puntos'),
    path('eliminar_facultad/<int:facultad_id>/', views.eliminar_facultad, name='eliminar_facultad'),
    path('eliminar_punto/<int:punto_id>/', views.eliminar_punto, name='eliminar_punto'),
    path('eliminar_bloque/<int:bloque_id>/', views.eliminar_bloque, name='eliminar_bloque'),
    path('gestionar_bloques_puntos/', views.gestionar_bloques_puntos, name='gestionar_bloques_puntos'),
    path('gestionar_cuenta/', views.gestionar_cuenta_view, name='gestionar_cuenta'),
    path('vista_grafo_admin/', views.vista_grafo_admin, name='vista_grafo_admin'),
    path('vistaUsuario/',views.puntos,name='puntos'),
]
