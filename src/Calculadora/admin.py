from django.contrib import admin

from Calculadora.models import Calculo, Periodo, Porcentaje, Tipo, Transformacion

# Register your models here.
admin.site.register(Periodo)
admin.site.register(Calculo)
admin.site.register(Tipo)
admin.site.register(Transformacion)
admin.site.register(Porcentaje)