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
    resultIp = None

    if request.method == 'POST':
        try:
            porcentaje = float(request.POST.get('porcentaje', 0))
            periodo_id = request.POST.get('periodo')
            periodo_a_id = request.POST.get('periodo_a')
            calculo_id = request.POST.get('calculo')
            tipo_id = request.POST.get('tipo')
            transformacion_id = request.POST.get('transformacion')

            periodo = Periodo.objects.get(id=periodo_id) if periodo_id else None
            periodo_a = Periodo.objects.get(id=periodo_a_id) if periodo_a_id else None
            calculo = Calculo.objects.get(id=calculo_id) if calculo_id else None
            tipo = Tipo.objects.get(id=tipo_id) if tipo_id else None
            transformacion = Transformacion.objects.get(id=transformacion_id) if transformacion_id else None
            # Si el cálculo seleccionado es 'efectiva', convertir la tasa efectiva
            # a la tasa por periodo: ((1 + efectiva)^(1/nper)) - 1
            if calculo and calculo.nombre.lower() == 'efectiva':
                if transformacion and transformacion.nombre.lower() == 'nominal' and periodo_a:
                    # Efectiva -> Nominal: necesita Periodo A
                    nper_a = periodo_a.nper
                    if porcentaje == 0:
                        error = 'El porcentaje no puede ser 0.'
                    else:
                        efectiva = porcentaje / 100.0
                        tasa_vencida_periodo_a = (1 + efectiva) ** (1.0 / nper_a) - 1
                        resultIp = tasa_vencida_periodo_a * 100
                        result = (tasa_vencida_periodo_a * 100) * nper_a
                else:
                    result = None
            else:
                # Conversión nominal vencida -> efectiva
                if (
                    periodo
                    and calculo
                    and transformacion
                    and calculo.nombre.lower() == 'nominal'
                    and transformacion.nombre.lower() == 'efectiva'
                ):
                    nper = periodo.nper
                    if porcentaje == 0:
                        error = 'El porcentaje no puede ser 0.'
                    else:
                        result = (((1 + ((porcentaje / 100.0) / nper)) ** nper) - 1) * 100
                # Conversión nominal vencida -> nominal anticipada
                elif (
                    periodo
                    and periodo_a
                    and calculo
                    and tipo
                    and transformacion
                    and calculo.nombre.lower() == 'nominal'
                    and transformacion.nombre.lower() == 'nominal'
                    and tipo.nombre.lower().startswith('antic')
                ):
                    nper = periodo.nper
                    nper_a = periodo_a.nper
                    if porcentaje == 0:
                        error = 'El porcentaje no puede ser 0.'
                    else:
                        # Convertir tasa nominal vencida (periodo DE) a tasa por período vencida
                        tasa_vencida_periodo = (porcentaje / 100.0) / nper
                        # Calcular tasa efectiva anual
                        tasa_efectiva = (1 + tasa_vencida_periodo) ** nper - 1
                        # Convertir tasa efectiva a tasa por período vencida (periodo A)
                        tasa_vencida_periodo_a = (1 + tasa_efectiva) ** (1.0 / nper_a) - 1
                        # Convertir a tasa por período anticipada: d = j / (1 + j)
                        tasa_anticipada_periodo_a = tasa_vencida_periodo_a / (1 + tasa_vencida_periodo_a)
                        # Dar la tasa anticipada del período (sin multiplicar por nper_a)
                        resultIp = tasa_anticipada_periodo_a * 100
                        result = (tasa_anticipada_periodo_a * 100) * nper_a
                # Conversión nominal vencida -> nominal vencida (cambio de período)
                elif (
                    periodo
                    and periodo_a
                    and calculo
                    and tipo
                    and transformacion
                    and calculo.nombre.lower() == 'nominal'
                    and transformacion.nombre.lower() == 'nominal'
                    and tipo.nombre.lower().startswith('venc')
                ):
                    nper = periodo.nper
                    nper_a = periodo_a.nper
                    if porcentaje == 0:
                        error = 'El porcentaje no puede ser 0.'
                    else:
                        # Convertir tasa nominal vencida (periodo DE) a tasa por período vencida
                        tasa_vencida_periodo = (porcentaje / 100.0) / nper
                        # Calcular tasa efectiva anual
                        tasa_efectiva = (1 + tasa_vencida_periodo) ** nper - 1
                        # Convertir tasa efectiva a tasa por período vencida (periodo A)
                        tasa_vencida_periodo_a = (1 + tasa_efectiva) ** (1.0 / nper_a) - 1
                        # Dar la tasa vencida del período (sin multiplicar por nper_a)
                        resultIp = tasa_vencida_periodo_a * 100
                        result = (tasa_vencida_periodo_a * 100)* nper_a
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
        'resultIp': resultIp,
        'error': error,
    }
    return render(request, 'Calculadora.html', context)