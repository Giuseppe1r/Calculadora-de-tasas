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
            tipo_inicial_id = request.POST.get('tipo_inicial')
            tipo_final_id = request.POST.get('tipo_final')
            transformacion_id = request.POST.get('transformacion')

            periodo = Periodo.objects.get(id=periodo_id) if periodo_id else None
            periodo_a = Periodo.objects.get(id=periodo_a_id) if periodo_a_id else None
            calculo = Calculo.objects.get(id=calculo_id) if calculo_id else None
            tipo_inicial = Tipo.objects.get(id=tipo_inicial_id) if tipo_inicial_id else None
            tipo_final = Tipo.objects.get(id=tipo_final_id) if tipo_final_id else None
            transformacion = Transformacion.objects.get(id=transformacion_id) if transformacion_id else None
            # Si el cálculo seleccionado es 'efectiva', convertir la tasa efectiva
            # a la tasa por periodo: ((1 + efectiva)^(1/nper)) - 1
            if calculo.nombre.lower() == 'efectiva' and transformacion.nombre.lower() == 'nominal' and periodo_a:
                nper_a = periodo_a.nper
                efectiva = porcentaje / 100.0

                tasa_vencida = (1 + efectiva) ** (1.0 / nper_a) - 1

                if tipo_final and tipo_final.nombre.lower().startswith('antic'):
                    tasa = tasa_vencida / (1 + tasa_vencida)
                else:  # vencida
                    tasa = tasa_vencida

                resultIp = tasa * 100
                result = tasa * 100 * nper_a
            ##
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
                        tasa_periodo = (porcentaje / 100.0) / nper

                        # Si es anticipada convertir a vencida
                        if tipo_inicial and tipo_inicial.nombre.lower().startswith('antic'):
                            tasa_periodo = tasa_periodo / (1 - tasa_periodo)

                        result = ((1 + tasa_periodo) ** nper - 1) * 100
                # Conversión nominal vencida -> nominal anticipada
                elif (
                    periodo
                    and periodo_a
                    and calculo
                    and transformacion
                    and tipo_final
                    and calculo.nombre.lower() == 'nominal'
                    and transformacion.nombre.lower() == 'nominal'
                    and tipo_final.nombre.lower().startswith('antic')
                     
                ):
                    nper = periodo.nper
                    nper_a = periodo_a.nper
                    if porcentaje == 0:
                        error = 'El porcentaje no puede ser 0.'
                    else:
                        # Convertir tasa nominal vencida (periodo DE) a tasa por período vencida
                        tasa_vencida_periodo = (porcentaje / 100.0) / nper
                        if tipo_inicial and tipo_inicial.nombre.lower().startswith('antic'):
                            tasa_vencida_periodo = tasa_vencida_periodo / (1 - tasa_vencida_periodo)

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
                    and transformacion.nombre.lower() == 'nominal'
                    and transformacion
                    and calculo.nombre.lower() == 'nominal'
                    and transformacion.nombre.lower() == 'nominal'
                    and tipo_final.nombre.lower().startswith('venc')
                ):
                    nper = periodo.nper
                    nper_a = periodo_a.nper
                    if porcentaje == 0:
                        error = 'El porcentaje no puede ser 0.'
                    else:
                        # Convertir tasa nominal vencida (periodo DE) a tasa por período vencida
                        tasa_vencida_periodo = (porcentaje / 100.0) / nper
                        
                        #Convertir anticipada inicial a vencida
                        if tipo_inicial and tipo_inicial.nombre.lower().startswith('antic'):
                            tasa_vencida_periodo = tasa_vencida_periodo / (1 - tasa_vencida_periodo)

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

    # valores enviados (para conservarlos)
    form_data = {
        'porcentaje': request.POST.get('porcentaje', ''),
        'calculo': request.POST.get('calculo', ''),
        'periodo': request.POST.get('periodo', ''),
        'transformacion': request.POST.get('transformacion', ''),
        'periodo_a': request.POST.get('periodo_a', ''),
        'tipo_inicial': request.POST.get('tipo_inicial', ''),
        'tipo_final': request.POST.get('tipo_final', ''),
    }

    context = {
        'periodos': periodos,
        'calculos': calculos,
        'tipos': tipos,
        'transformaciones': transformaciones,
        'result': result,
        'resultIp': resultIp,
        'error': error,
        'form_data': form_data
    }
    return render(request, 'Calculadora.html', context)