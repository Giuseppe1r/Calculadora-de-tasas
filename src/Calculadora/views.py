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
            # Si el cálculo seleccionado es 'efectiva', convertir la tasa efectiva
            # a la tasa por periodo: ((1 + efectiva)^(1/nper)) - 1
            if calculo and calculo.nombre.lower() == 'efectiva':
                if not periodo:
                    error = 'Seleccione un periodo para calcular desde efectiva.'
                else:
                    nper = periodo.nper
                    if porcentaje == 0:
                        error = 'El porcentaje no puede ser 0.'
                    else:
                        # porcentaje viene en % -> convertir a decimal
                        efectiva = porcentaje / 100.0
                        result = (1 + efectiva) ** (1.0 / nper) - 1
            else:
                # Comportamiento previo: ejemplo de conversión nominal -> efectiva
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
                        result = ((1 + ((porcentaje / 100.0) / nper)) ** nper) - 1
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