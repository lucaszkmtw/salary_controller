from django.urls import path
from cuadricula.views import CuadriculaListView
from cuadricula.views import CuadriculaView
from cuadricula.views import CuadriculaCreateView
from cuadricula.views import CuadriculaUpdateView
from cuadricula.views import CuadriculaDeleteView
from cuadricula.views import CuadriculaTemplate


urlpatterns = [
    path('', CuadriculaTemplate.as_view(), name="cuadricula-view"),
    path('lista', CuadriculaListView.as_view(), name='cuadricula-list'),
    path('<int:pk>', CuadriculaView.as_view(), name='cuadricula-detail'),
    path('create', CuadriculaCreateView.as_view(), name='cuadricula-create'),
    path('<int:pk>/update', CuadriculaUpdateView.as_view(), name='cuadricula-update'),
    path('<int:pk>/delete', CuadriculaDeleteView.as_view(), name='cuadricula-delete'),
]
