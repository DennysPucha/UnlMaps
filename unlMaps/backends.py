from django.contrib.auth.backends import BaseBackend
from .models import Cuenta

class CuentaBackend(BaseBackend):
    def authenticate(self, request, usuario=None, contrasenia=None):
        try:
            cuenta = Cuenta.objects.get(usuario=usuario)
            if cuenta.contrasenia == contrasenia:
                return cuenta
        except Cuenta.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Cuenta.objects.get(pk=user_id)
        except Cuenta.DoesNotExist:
            return None