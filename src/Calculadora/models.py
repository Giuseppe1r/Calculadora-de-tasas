from django.db import models

class Periodo(models.Model):
    nombre = models.CharField(max_length=100)
    nper = models.IntegerField()
    sigla = models.CharField(max_length=10)
    def __str__(self):
        return self.nombre
    
class Calculo(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre
    
class Tipo(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre
    
class Transformacion(models.Model):#lo mismo que calculo pero es al que se transformara
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre