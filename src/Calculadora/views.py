from django.shortcuts import render
from .models import Periodo, Calculo, Tipo, Transformacion

# Create your views here.
def calculadora(request):
    periodos = Periodo.objects.all()
    calculos = Calculo.objects.all()
    tipos = Tipo.objects.all()
    transformaciones = Transformacion.objects.all()

    result = None
    error = None

    if request.method == 'POST':
        try:
            porcentaje = float(request.POST.get('porcentaje', 0))
            periodo_id = request.POST.get('periodo')
            calculo_id = request.POST.get('calculo')
            tipo_id = request.POST.get('tipo')
            transformacion_id = request.POST.get('transformacion')

            periodo = Periodo.objects.get(id=periodo_id) if periodo_id else None
            calculo = Calculo.objects.get(id=calculo_id) if calculo_id else None
            tipo = Tipo.objects.get(id=tipo_id) if tipo_id else None
            transformacion = Transformacion.objects.get(id=transformacion_id) if transformacion_id else None

            # Condición pedida: cualquier periodo y calculo es Nominal,
            # tipo es vencida, transformacion es efectiva -> aplicar fórmula
            if (
                periodo
                and calculo
                and tipo
                and transformacion
                and calculo.nombre.lower() == 'nominal'
                and tipo.nombre.lower().startswith('venc')
                and transformacion.nombre.lower() == 'efectiva'
            ):
                nper = periodo.nper
                if porcentaje == 0:
                    error = 'El porcentaje no puede ser 0.'
                else:
                    # Aplicar fórmula: ((1 + nper/porcentaje) ** nper) - 1
                    result = ((1 + ((porcentaje /100 ) / nper)) ** nper) - 1
            else:
                result = None
        except Exception as e:
            error = str(e)

    context = {
        'periodos': periodos,
        'calculos': calculos,
        'tipos': tipos,
        'transformaciones': transformaciones,
        'result': result,
        'error': error,
    }
    return render(request, 'Calculadora.html', context)