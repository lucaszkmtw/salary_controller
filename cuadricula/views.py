from django.http.response import HttpResponse
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.core.serializers import serialize

from cuadricula.models import CuadriculaMovimiento


class CuadriculaTemplate(TemplateView):
    template_name = "cuadricula/list.html"


class CuadriculaListView(ListView):
    model = CuadriculaMovimiento
    context_object_name = "cuadriculas"


class CuadriculaView(DetailView):
    model = CuadriculaMovimiento
    template_name = 'cuadricula/detail.html'
    context_object_name = 'cuadricula'


class CuadriculaCreateView(CreateView):
    model = CuadriculaMovimiento
    template_name = 'cuadricula/create.html'
    fields = (
        'creator',
        'proyecto',
        'reparticion',
        'nombre',
        'codigo',
        'periodo_dd',
        'periodo_ht',
        'observaciones',
    )
    success_url = reverse_lazy('cuadricula-list')


class CuadriculaUpdateView(UpdateView):
    model = CuadriculaMovimiento
    template_name = 'cuadricula/update.html'
    context_object_name = 'cuadricula'
    fields = (
        'id',
        'proyecto',
        'reparticion',
        'nombre',
        'codigo',
        'periodo_dd',
        'periodo_ht',
        'observaciones',
        'modifier',
        'modified',
    )

    def get_success_url(self):
        return reverse_lazy('cuadricula-detail', kwargs={'pk': self.object.id})


class CuadriculaDeleteView(DeleteView):
    model = CuadriculaMovimiento
    template_name = 'cuadricula/delete.html'
    context_object_name = 'cuadricula'
    success_url = reverse_lazy('cuadricula-list')
