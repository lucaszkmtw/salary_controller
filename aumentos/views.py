import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder

from django.urls import reverse_lazy
from django.urls.base import reverse

from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView

from django.contrib.messages.views import SuccessMessageMixin

from main.models import BulkCreateManager
from main.mixins import AjaxTemplateMixin

from hiscar.models import Hiscar
from hiscar.models import Cargo
from hiscar.models import Reparticion
from hiscar.models import Agrupamiento
from hiscar.models import AgrupamientoCargo
from aumentos.models import Proyecto
from aumentos.models import Movimiento
from aumentos.models import Aumento


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class ProyectoListView(PermissionRequiredMixin, ListView):
    model = Proyecto
    context_object_name = 'proyectos'
    template_name = 'proyecto/list.html'
    permission_required = ('aumentos.view_proyecto',)


class ProyectoDetailView(PermissionRequiredMixin, DetailView):
    model = Proyecto
    template_name = 'proyecto/detail.html'
    context_object_name = 'proyecto'
    permission_required = ('aumentos.view_proyecto',)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context.update(
            {
                'movimientos': Movimiento.objects.filter(proyecto=self.object.id)
                                                 .select_related('creator', 'reparticion')
                                                 .order_by('orden'),
                'reparticiones_proyectos': [],
                'reparticiones': Reparticion.get_by_cache(),
                'tipos_de_movimientos': ['', 'Aumento', 'Baja Cargos', 'Alta Cargos']
            }
        )
        return self.render_to_response(context)


class ProyectoCreateView(PermissionRequiredMixin,
                         SuccessMessageMixin,
                         AjaxTemplateMixin,
                         CreateView):
    model = Proyecto
    template_name = 'proyecto/create.html'
    fields = (
        'nombre',
        'descripcion',
        'fecha_limite',
        'fecha_hiscar',
        'creator',
    )
    success_url = reverse_lazy('proyecto-list')
    permission_required = ('aumentos.add_proyecto',)


class ProyectoUpdateView(PermissionRequiredMixin, UpdateView):
    model = Proyecto
    template_name = 'proyecto/update.html'
    context_object_name = 'proyecto'
    fields = (
        'nombre',
        'descripcion',
        'fecha_limite',
        'fecha_hiscar',
    )
    permission_required = ('aumentos.change_proyecto',)

    def get_success_url(self):
        return reverse_lazy('proyecto-detail', kwargs={'pk': self.object.id})


class ProyectoDeleteView(PermissionRequiredMixin, DeleteView):
    model = Proyecto
    template_name = 'proyecto/delete.html'
    success_url = reverse_lazy('proyecto-list')
    permission_required = ('aumentos.delete_proyecto',)


def habilitar_edicion_movimiento(request):
    movimiento_id = request.POST.get('id')
    movimiento = Movimiento.objects.get(id=movimiento_id)
    movimiento.update(is_close=False)
    context = {
        'movimiento': movimiento.tipo_movimiento
    }
    return JsonResponse(context, safe=False)


def eliminar_proyecto(request):
    context = {}
    try:
        proyecto_id = request.POST.get('id')
        proyecto = Proyecto.objects.get(id=proyecto_id)
        proyecto.is_active = False
        proyecto.save()
        context['nombre'] = proyecto.nombre
        Movimiento.objects.filter(proyecto=proyecto_id).update(is_active=False)
    except:
        context['error'] = True
    return JsonResponse(context, safe=False)


def finalizar_proyecto(request):
    context = {}
    proyecto_id = request.POST.get('id')
    movimientos = Movimiento.objects.filter(
        proyecto=proyecto_id,
        is_close=False,
        is_active=True
    )
    proyecto = Proyecto.objects.get(id=proyecto_id)
    context['nombre'] = proyecto.nombre

    if not movimientos:
        movimientos = True
        proyecto.update(is_close=True)
    else:
        movimientos = False

    context['proyecto'] = movimientos
    return JsonResponse(context, safe=False)


def editar_proyecto(request):
    proyecto_id = request.POST.get('id')
    proyecto_nombre = request.POST.get('nombre')
    proyecto_descripcion = request.POST.get('descripcion')
    proyecto_fecha_limite = request.POST.get('fecha_limite')

    if proyecto_id:
        Proyecto.objects\
            .get(id=proyecto_id)\
            .update(
                nombre=proyecto_nombre,
                descripcion=proyecto_descripcion,
                fecha_limite=proyecto_fecha_limite
            )
    return JsonResponse({}, safe=False)


def crear_proyecto(request):
    proyecto_nombre = request.POST.get('nombre')
    proyecto_descripcion = request.POST.get('descripcion')
    proyecto_fecha_limite = request.POST.get('fecha_limite')

    proyecto = Proyecto(
        nombre=proyecto_nombre,
        descripcion=proyecto_descripcion,
        fecha_limite=proyecto_fecha_limite,
        creator=request.user
    )
    proyecto.save()
    return JsonResponse({}, safe=False)


def eliminar_movimiento(request):
    movimiento_id = request.POST.get('mov_id')
    movimiento = Movimiento.objects.get(id=movimiento_id)
    movimiento.delete()
    return JsonResponse({}, safe=False)


def get_aumentos_tabla(request):
    """Devuelve el listado de Cargos con Aumento en un Movimiento"""
    context = {}
    movimiento_id = request.GET.get('id')
    movimiento = Movimiento.objects.get(id=movimiento_id)
    aumentos = Aumento.objects.filter(movimiento=movimiento_id)
    context['aumentos'] = serializers.serialize(
        'json',
        aumentos,
        use_natural_foreign_keys=True,
    )
    context['movimiento'] = model_to_dict(movimiento)

    context['cantidad'] = aumentos.count()

    return JsonResponse(context, safe=False)


def guardar_aumentocargo(request):
    """Guardar aumento cargo

    Arguments:
        request {modo_aumento,aume_id,
        tipo_aumento_id,tipo_calculo_id,cash,
        modulo,agrupamiento_id, cargo_codigo, regla,
        periodo, } -- Guarda un aumento de un cargo en
        un Movimiento.

    Returns:
        Context { hiscar } -- Devuelve a la vista el
        aumento formateado para ser renderizado en la
        tabla por js.
    """
    context = {}
    tipos_calculos = dict(map(reversed, Aumento.TIPOS_CALCULOS))
    tipos_aumentos = dict(map(reversed, Aumento.TIPOS_AUMENTOS))

    # Campos del Aumento
    movimiento = Movimiento.objects.get(
        id=request.GET.get('movimiento_id')
    )
    if 'cargo_id' in request.GET:
        cargo = Cargo.objects.get(
            id=request.GET.get('cargo_id')
        )

    if 'json_aumentos' in request.GET:
        bulk_mgr = BulkCreateManager(chunk_size=10_000)

        aumentos_dict = json.loads(request.GET['json_aumentos'])
        for campo, aume in aumentos_dict.items():
            if isinstance(aume, list):
                for au in aume:
                    for tipo_aumento, cantidad in au.items():
                        bulk_mgr.add(
                            Aumento(
                                movimiento=movimiento,
                                tipo_aumento=tipos_aumentos[tipo_aumento],
                                tipo_calculo=tipos_calculos[campo],
                                valor=cantidad,
                                cargo=cargo
                            )
                        )
            else:
                for tipo_aumento, cantidad in aume.items():
                    bulk_mgr.add(
                        Aumento(
                            movimiento=movimiento,
                            tipo_aumento=tipos_aumentos[tipo_aumento],
                            tipo_calculo=tipos_calculos[campo],
                            valor=cantidad,
                            cargo=cargo
                        )
                    )
        bulk_mgr.done()
        return JsonResponse({}, safe=False)
    else:
        tipo_aumento = request.GET.get('tipo_aumento_id')
        tipo_calculo = request.GET.get('tipo_calculo_id')

        # Si es cant_aumento
        cant_aumento = request.GET.get('cant_aumento')

        tipo_aumento_nombre = request.GET.get('tipo_aumento_nombre')
        tipo_aumento_valor = request.GET.get('tipo_aumento_valor')
        regla = ""

        if tipo_aumento_nombre == 'agrupamiento':
            try:
                agrupamiento = Agrupamiento.objects.get(id=tipo_aumento_valor)
            except:
                return JsonResponse({'ALERT': 1, 'OBJECT': 'Agrupamiento'}, safe=False)
        else:
            agrupamiento = None

        if tipo_aumento_nombre == 'cargo':
            try:
                cargo = Cargo.objects.get(id=tipo_aumento_valor)
            except:
                return JsonResponse({'ALERT': 1, 'OBJECT': 'Cargo'}, safe=False)
        else:
            cargo = None

        if tipo_aumento_nombre == 'regla':
            regla = tipo_aumento_valor

        aumento = Aumento(
            movimiento=movimiento,
            tipo_aumento=tipo_aumento,
            tipo_calculo=tipo_calculo,
            valor=cant_aumento,
            cargo=cargo,
            agrupamiento=agrupamiento,
            regla=regla
        )

        aumento.add_orden()
        aumento.save()

        context = serializers.serialize(
            'json',
            [aumento],
            use_natural_foreign_keys=True,
            use_natural_primary_keys=True
        )

        context = {
            'tipo': tipos_calculos,
        }

        return JsonResponse(context, safe=False)


def guardar_aumento(request):
    context = {}
    tipos_calculos = dict(map(reversed, Aumento.TIPOS_CALCULOS))

    tipos_aumentos = dict(map(reversed, Aumento.TIPOS_AUMENTOS))

    aumento = Aumento(
        movimiento=Movimiento.objects.get(id=request.POST.get('movimiento_id')),
        tipo_calculo=tipos_calculos[request.POST.get('tipo_calculo')],
        tipo_aumento=tipos_aumentos[request.POST.get('tipo_aumento')],
        valor=request.POST.get('cant_aumento'),
        cargo=Cargo.objects.get(id=request.POST.get('cargo_id')),
    )

    aumento.add_orden()
    aumento.save()
    return JsonResponse(context, safe=False)


def eliminar_agrupamiento(request):
    agrupamiento_id = request.GET.get('id')
    Agrupamiento.eliminarObjectoSeleccionado(agrupamiento_id)
    return JsonResponse({'id': agrupamiento_id}, safe=False)


def editar_movimiento(request, context={}):
    movimiento_id = request.POST.get('movimiento_id')
    movimiento_nombre = request.POST.get('movimiento_nombre')
    movimiento_periodo_dd = request.POST.get('movimiento_periodo_dd') + '-01'
    movimiento_periodo_ht = request.POST.get('movimiento_periodo_ht') + '-01'

    try:
        movimiento = Movimiento.objects.get(id=movimiento_id)
        movimiento.nombre = movimiento_nombre
        movimiento.periodo_dd = movimiento_periodo_dd
        movimiento.periodo_ht = movimiento_periodo_ht
        movimiento.save()

    except Movimiento.DoesNotExist:
        context['error'] = f"Movimiento {movimiento_id} no existe."

    except ValidationError as error:
        context['error'] = error

    else:
        context['movimiento'] = json.dumps(
            model_to_dict(movimiento),
            sort_keys=True,
            indent=1,
            cls=DjangoJSONEncoder
        )

    return JsonResponse(context, safe=False)


def crear_movimiento(request):
    """ Crea o modifica un Movimiento """
    proyecto_id = request.POST.get('proyecto_id')
    reparticion_id = request.POST.get('reparticion_id')
    periodo_dd = request.POST.get('periodo_dd') + '-01'
    periodo_ht = request.POST.get('periodo_ht') + '-01'
    observaciones = request.POST.get('observaciones')
    aume_id = request.POST.get('aume_id')
    tipo_movimiento = request.POST.get('tipo_movimiento')
    proyecto = Proyecto.objects.get(id=proyecto_id)
    reparticion = Reparticion.objects.get(id=reparticion_id)
    usuario = User.objects.get(id=request.user.id)

    if not aume_id:
        orden = Movimiento.objects.filter(
            proyecto=proyecto,
            is_active=True).count() + 1
    else:
        orden = Movimiento.objects.get(id=aume_id).orden

    id = Movimiento.new_update(
        periodo_dd,
        periodo_ht,
        observaciones,
        reparticion,
        usuario,
        aume_id,
        proyecto,
        orden,
        tipo_movimiento)

    if id:
        aume_id = id
    else:
        pass

    return JsonResponse({'aume_id': aume_id}, safe=False)


def modificar_agrupamiento(request):
    reparticion_id = request.GET.get('reparticion_id')
    agrupamiento_id = request.GET.get('agrupamientoID')
    reparticion = Reparticion.objects.get(id=reparticion_id)

    cargos = Cargo.getCargosByCache(reparticion_id)

    agrupamientos = Agrupamiento.objects.filter(
        reparticion_id=reparticion_id,
        creator_id=request.user.id
    )

    cargos_agrupamientos = []
    for agrupamiento in agrupamientos:
        cargos_agrupamientos += AgrupamientoCargo.objects.filter(
            agrupamiento_id=agrupamiento.id).values_list('cargo', flat=True)

    agrupamiento = Agrupamiento.objects.get(id=agrupamiento_id)

    cargos_agrupamiento = AgrupamientoCargo.objects.filter(
        agrupamiento_id=agrupamiento_id).values_list('cargo', flat=True)

    context = {
        'municipio': reparticion,
        'codigo': reparticion,
        'cargos': cargos,
        'agrupamiento': agrupamiento,
        'cargos_agrupamiento': cargos_agrupamiento,
        'cargos_agrupamientos': cargos_agrupamientos
    }
    return render(request, 'agrupamiento/update_in_movimiento.html', context)


def modificar_agrupamiento_save(request):
    agrupamiento = Agrupamiento.update(
        json.loads(request.POST['vector[]']),
        request.POST.get('agrupacion'),
        request.POST.get('reparticion'),
        request.POST.get('agrupacion_nombre'),
        request.POST.get('movimiento'),
        request.user)

    return JsonResponse({'agrupamiento': agrupamiento.id, 'agrupamiento_nombre': agrupamiento.nombre}, safe=False)


def crear_agrupamiento(request):
    nombre_agrupamiento = request.GET.get('agrupacion_nombre')
    vector_agrupamientos = json.loads(request.GET['vector[]'])
    reparticion_id = request.GET.get('reparticion')
    agrupamiento = AgrupamientoCargo.new(
        vector_agrupamientos,
        nombre_agrupamiento,
        reparticion_id,
        request.user
    )
    return JsonResponse(
        {
            'agrupamiento': agrupamiento.id,
            'agrupamiento_nombre': agrupamiento.nombre
        },
        safe=False
    )


def template_alta_agrupamiento(request):
    repart_id = request.GET.get('municipio')

    agrupamientos = Agrupamiento.objects.filter(
        reparticion_id=repart_id,
        creator_id=request.user.id
    )

    cargos_agrupamiento = []
    for agrupamiento in agrupamientos:
        cargos_agrupamiento += AgrupamientoCargo.objects.filter(
            agrupamiento_id=agrupamiento.id).values_list('cargo', flat=True)

    cargos = Cargo.getCargosByCache(repart_id)
    municipio = Reparticion.objects.get(id=repart_id)

    context = {
        'municipio': municipio,
        'cargos': cargos,
        'cargos_agrupamiento': cargos_agrupamiento
    }

    return render(request, 'agrupamiento/create_in_movimiento.html', context)


# FIXME Generalizar una vista para actualizar orden de todo lo que tenga order o priority
def actualizar_orden(request):
    movimientos = json.loads(request.POST.get('datos'))

    for movimiento_id in movimientos:
        movimiento = Movimiento.objects.get(id=movimiento_id)
        movimiento.orden = int(movimientos[movimiento_id])
        movimiento.save()

    return JsonResponse({}, safe=False)


def valor_cargo_actual(request):
    """
    valor_cargo_actual 'Devuelve valores de modulo o sueldo del cargo
        seleccionado'

    Args:
        request (cargo_codigo,has_modulo):

    Returns:
        html
    """
    cargo = Cargo.objects.get(codigo=request.GET.get('cargo_codigo'),
                              reparticion__codigo=request.GET.get('reparticion_codigo'))
    hiscar = Hiscar.objects.filter(
        periodo__range=[
            f"{request.GET.get('periodo_dd')}-01",
            f"{request.GET.get('periodo_ht')}-01"
        ],
        reparticion=request.GET.get('reparticion_codigo'),
        cargo__startswith=cargo.codigo[4:]
    ).order_by('periodo').values()

    return render(
        request,
        'aumento/create_by_cargo_tabla_periodos.html',
        {
            'periodos': hiscar,
            'cargo': cargo
        }
    )


def guardar_aumento_modulo(request):
    if request.POST.get('cargo'):
        try:
            cargo = Cargo.objects.get(id=request.POST.get('cargo_id'))
        except:
            return JsonResponse({'ALERT': 1, 'OBJECT': 'Cargo'}, safe=False)
    else:
        cargo = None

    if request.POST.get('agrupamiento'):
        try:
            agrupamiento = Agrupamiento.objects.get(id=request.POST.get('agrupamiento'))
        except:
            return JsonResponse({'ALERT': 1, 'OBJECT': 'Agrupamiento'}, safe=False)

    else:
        agrupamiento = None

    if request.POST.get('regla'):
        regla = request.POST.get('reparticion_codigo')[:4] + request.POST.get('regla')
    else:
        regla = None

    try:
        aumento = Aumento(
            regla=regla,
            valor=request.POST.get('cantidad'),
            agrupamiento=agrupamiento,
            cargo=cargo,
            movimiento=Movimiento.objects.get(id=int(request.POST.get('movimiento'))),
            tipo_aumento=Aumento.TIPOS_AUMENTOS[request.POST.get('campo-aumento')][0],
            tipo_calculo=Aumento.TIPOS_AUMENTOS[request.POST.get('valor-aumento')][0],
            has_modulo=request.POST.get('has_modulo')
        )
        # FIXME aumento on save set orden
        aumento.add_orden()
        aumento.save()

    except:
        return JsonResponse({'ALERT': 1, 'OBJECT': 'Aumento save'}, safe=False)

    return JsonResponse({'ALERT': 0}, safe=False)


def get_cargos_modulo(request):
    context = {}
    aumento_id = request.GET.get('aumento_id')

    if aumento_id:
        aumento = Aumento.objects.get(id=aumento_id)
        if aumento.regla != "":
            context = serializers.serialize(
                'json',
                aumento.getHiscarRegla()
            )

        if aumento.agrupamiento:
            context = serializers.serialize(
                'json',
                aumento.agrupamiento.getCargos()
            )

    return JsonResponse(context, safe=False)


def cargo_baja(request):
    context = {}
    movimiento_id = int(request.GET.get('movimiento_id'))
    cargo_codigo = request.GET.get('cargo_codigo')

    if movimiento_id:
        try:
            movimiento = Movimiento.objects.get(id=movimiento_id)
        except:
            context['ALERT'] = 1
            context['OBJECT'] = 'Movimiento'
        else:
            if cargo_codigo:
                try:
                    aumento = Aumento(
                        movimiento=movimiento,
                        cargo=None,
                        regla=cargo_codigo,
                        has_modulo=False
                    )
                    aumento.add_orden()
                    aumento.save()
                    context['ALERT'] = 0
                except:
                    context['ALERT'] = 1
                    context['OBJECT'] = 'Aumento'

    return JsonResponse(context, safe=False)


class MovimientoDetailView(DetailView):
    model = Movimiento
    context_object_name = 'movimiento'
    template_name = 'movimiento/detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context['proyecto'] = self.object.proyecto
        context['cargos'] = Cargo.objects.filter(
            reparticion_id=self.object.reparticion_id
        ).values('id', 'codigo', 'cargo')
        context['reparticion'] = self.object.reparticion
        context['periodo_dd'] = self.object.get_periodo_desde()
        context['periodo_ht'] = self.object.get_periodo_hasta()
        context['aumentos'] = Aumento.objects.filter(movimiento=self.object)
        context['tipos_aumento'] = dict(Aumento.TIPOS_AUMENTOS)

        if self.object.tipo_movimiento == 1:
            context['tipos_calculo'] = dict(Aumento.TIPOS_CALCULOS)
            context['agrupamientos'] = Agrupamiento.objects.filter(
                reparticion=self.object.reparticion)
        return self.render_to_response(context)


def modal_test(request, **kwargs):
    return render(request, 'modal_for_template_view.html', **kwargs)


class MovimientoCreateView(PermissionRequiredMixin,
                           SuccessMessageMixin,
                           AjaxTemplateMixin,
                           CreateView):
    model = Movimiento
    template_name = 'movimiento/create.html'
    fields = (
        'creator',
        'proyecto',
        'nombre',
        'tipo_movimiento',
        'reparticion',
        'periodo_dd',
        'periodo_ht',
        'observaciones',
    )
    permission_required = ('aumentos.add_movimiento',)
    success_url = None

    def get_context_data(self, **kwargs):
        context = super(MovimientoCreateView, self).get_context_data(**kwargs)
        context['reparticiones'] = Reparticion.objects.all()
        context['proyecto_id'] = self.request.GET.get('proyecto_id')
        return context

    def form_valid(self, form):
        form.instance.creator = self.request.user
        if form.instance.periodo_dd > form.instance.periodo_ht:
            form.add_error('periodo_dd', 'No puede ser mayor que el periodo hasta')
            return self.form_invalid(form)
        return super(MovimientoCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class EliminarAumento(SuccessMessageMixin,
                      AjaxTemplateMixin,
                      DeleteView):
    model = Aumento
    template_name = 'aumento/eliminar_aumento.html'

    def get_success_url(self):
        return reverse('proyecto-list')

    def delete(self, request, pk, *args, **kwargs):
        aumento = self.get_object()
        aumento.eliminar_ordenado()
        aumento.save()
        mensaje = f'{self.model.__name__} eliminado correctamente!'
        error = 'No hay error!'
        response = JsonResponse({'mensaje': mensaje, 'error': error})
        response.status_code = 201


class AumentoCargoListView(ListView):
    template_name = "aumento/cargo_codigo.html"
    model = Movimiento

    def get_context_data(self, **kwargs):
        context = {}
        movimiento = Movimiento.objects\
            .get(id=self.kwargs['movimiento_id'])
        aumento = Aumento.objects\
            .filter(movimiento=movimiento)
        rep = movimiento.reparticion
        hiscar_cargo = Hiscar.objects\
            .filter(reparticion=rep.codigo,
                    cargo=self.kwargs['cargo'],).\
            order_by('periodo')

        cargo_id = Cargo.objects\
            .get(codigo=self.kwargs['cargo'],
                 reparticion=Reparticion.objects.get(nombre=rep.codigo))

        hiscar_ultima = Hiscar\
            .objects\
            .filter(reparticion=rep.codigo,
                    cargo=self.kwargs['cargo'],)\
            .last()

        for hiscar in hiscar_cargo:
            hiscar.periodo = str(hiscar.periodo.strftime('%Y-%m'))

        context = {
            'movimiento': movimiento,
            'hiscar_cargo': hiscar_cargo,
            'cargo_id': cargo_id,
            'periodo': movimiento.periodo_dd.strftime('%Y-%m'),
            'aumento': aumento,
            'hiscar_ultima': hiscar_ultima,
            'aumento': aumento
        }
        return context

    def get(self, request, *args, **kwargs):
        context = {}
        movimiento = Movimiento.objects.get(id=self.kwargs['movimiento_id'])
        rep = movimiento.reparticion

        cargo_id = Cargo.objects.get(codigo=self.kwargs['cargo'],
                                     reparticion=Reparticion.objects.get(nombre=rep.codigo))

        hiscar = Hiscar.objects.filter(reparticion=rep.codigo,
                                       cargo=self.kwargs['cargo'],)\
                                .order_by('periodo')
        if is_ajax(request=request):
            aumento = Aumento.objects\
                .filter(cargo=cargo_id.id,
                        movimiento=movimiento,
                        )

            context['hiscar'] = serializers.serialize('json',
                                                   hiscar,
                                                   use_natural_foreign_keys=True,
                                                   use_natural_primary_keys=True
                                                   )

            context['aumentos'] = serializers.serialize('json',
                                                     aumento,
                                                     use_natural_foreign_keys=True,
                                                     use_natural_primary_keys=True
                                                     )

            hisca = Hiscar.objects.values('basico', 'suplemento1', 'suplemento2', 'sumafija1', 'sumafija2', 'sumafija3').filter(
                reparticion=rep.codigo, cargo=self.kwargs['cargo']).order_by('periodo')
            elements = ['basico', 'suplemento1', 'suplemento2', 'sumafija1', 'sumafija2', 'sumafija3']
            for elem in elements:
                lista = []
                valor_viejo = 0.0
                for hisc in hisca:
                    if valor_viejo != 0 and hisc[elem] != 0:

                        if valor_viejo < hisc[elem]:
                            valor_nuevo = hisc[elem] / valor_viejo * 100 - 100
                            lista.append(float(valor_nuevo))
                        if valor_viejo > hisc[elem]:
                            valor_nuevo = valor_viejo / hisc[elem] * 100 - 100
                            lista.append(float(-valor_nuevo))
                        if valor_viejo == hisc[elem]:
                            lista.append(0.0)    
                    else:
                        lista.append(0.0)
                    valor_viejo = hisc[elem]
                context[elem] = lista
            return JsonResponse(context)
        else:
            return super(AumentoCargoListView, self).get(request, *args, **kwargs)
class AumentoCreateView(CreateView):
    def post(self, request, *args, **kwargs):
        data = {}
        aumento_creado = None
        if request.method == "POST":
            tipo_calculo = request.POST.get('tipo_calculo')
            movimiento = request.POST.get('movimiento')
            cargo = request.POST.get('cargo')
            valor = request.POST.get('valor')
            tipo_aumento = request.POST.get('tipo_aumento')

            aumento = Aumento(movimiento=Movimiento
                              .objects.get(id=movimiento),
                              tipo_aumento=tipo_aumento,
                              tipo_calculo=tipo_calculo,
                              cargo=Cargo.objects.get(id=cargo),
                              valor=valor,
                              )
            aumento.save()
            aumento_creado = Aumento.objects.filter(cargo=cargo,
                                                    movimiento=Movimiento.objects.get(id=movimiento),
                                                    )
            data['aumento_creado'] = serializers.serialize('json',
                                                           aumento_creado,
                                                           use_natural_foreign_keys=True,
                                                           use_natural_primary_keys=True
                                                           )

        return JsonResponse(data, safe=True)
