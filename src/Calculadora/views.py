from django.shortcuts import render
import numpy as np
import math

# Create your views here.
def calculadora(request):
    return render(request, 'calculadora.html')