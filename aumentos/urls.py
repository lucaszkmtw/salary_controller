from django.urls import path
from aumentos.views import habilitar_edicion_movimiento
from aumentos.views import eliminar_proyecto
from aumentos.views import finalizar_proyecto
from aumentos.views import editar_proyecto
from aumentos.views import crear_proyecto
from aumentos.views import eliminar_movimiento
from aumentos.views import get_aumentos_tabla
from aumentos.views import guardar_aumentocargo
from aumentos.views import guardar_aumento
from aumentos.views import editar_movimiento
from aumentos.views import crear_movimiento
from aumentos.views import modal_test
# Agrupamientos
from aumentos.views import eliminar_agrupamiento
from aumentos.views import modificar_agrupamiento
from aumentos.views import modificar_agrupamiento_save
from aumentos.views import crear_agrupamiento
from aumentos.views import template_alta_agrupamiento
from aumentos.views import actualizar_orden
from aumentos.views import valor_cargo_actual
from aumentos.views import guardar_aumento_modulo
from aumentos.views import get_cargos_modulo
from aumentos.views import cargo_baja

# Class based views
from aumentos.views import ProyectoListView
from aumentos.views import ProyectoDetailView
from aumentos.views import ProyectoCreateView
from aumentos.views import ProyectoUpdateView
from aumentos.views import ProyectoDeleteView
from aumentos.views import AumentoCargoListView
from aumentos.views import AumentoCreateView
from aumentos.views import EliminarAumento
from aumentos.views import MovimientoDetailView
from aumentos.views import MovimientoCreateView

urlpatterns = [
    # Proyecto
    path('proyecto', ProyectoListView.as_view(), name='proyecto-list'),
    path('proyecto/create', ProyectoCreateView.as_view(), name='proyecto-create'),
    path('proyecto/<int:pk>', ProyectoDetailView.as_view(), name='proyecto-detail'),
    path('proyecto/<int:pk>/update', ProyectoUpdateView.as_view(), name='proyecto-update'),
    path('proyecto/<int:pk>/delete', ProyectoDeleteView.as_view(), name='proyecto-delete'),


    path('crear_proyecto/', crear_proyecto, name='crear_proyecto'),
    path('eliminar_proyecto/', eliminar_proyecto, name='eliminar_proyecto'),
    path('editar_proyecto/', editar_proyecto, name='editar_proyecto'),
    path('finalizar_proyecto/', finalizar_proyecto, name='finalizar_proyecto'),

    # Movimiento
    path('movimiento/create', MovimientoCreateView.as_view(), name='movimiento-create'),
    path('modal/', modal_test, name='modal_test'),

    path('movimiento/<int:pk>', MovimientoDetailView.as_view(), name='movimiento-detail'),
    path('crear_movimiento/', crear_movimiento, name="crear_movimiento"),  # este tendria que volar
    path('editar_movimiento/', editar_movimiento, name='editar_movimiento'),
    path('habilitar_edicion_movimiento/', habilitar_edicion_movimiento),
    path('eliminar_movimiento/', eliminar_movimiento, name='eliminar_movimiento'),
    path('get_aumentos_tabla/', get_aumentos_tabla, name='get_aumentos_tabla'),
    path('guardar_aumentocargo/', guardar_aumentocargo, name='guardar_aumentocargo'),
    path('guardar_aumento/', guardar_aumento, name='guardar_aumento'),
    path('actualizar_orden/', actualizar_orden, name='actualizar_orden'),
    path('valor_cargo_actual/', valor_cargo_actual, name='valor_cargo_actual'),
    path('guardar_aumento_modulo/', guardar_aumento_modulo, name='guardar_aumento_modulo'),
    path('get_cargos_modulo/', get_cargos_modulo, name='get_cargos_modulo'),
    path('cargo_baja/', cargo_baja, name='cargo_baja'),

    # Agrupamiento
    path('eliminar_agrupamiento/', eliminar_agrupamiento, name='eliminar_agrupamiento'),
    path('modificar_agrupamiento/', modificar_agrupamiento, name='modificar_agrupamiento'),
    path('modificar_agrupamiento_save/', modificar_agrupamiento_save, name='modificar_agrupamiento_save'),  # FIXME
    path('crear_agrupamiento/', crear_agrupamiento, name='crear_agrupamiento'),
    path('template_alta_agrupamiento/', template_alta_agrupamiento, name='template_alta_agrupamiento'),
    path('eliminar_aumento/<int:pk>/', EliminarAumento.as_view(), name="eliminar_aumento"),
    path('cargo_codigo/<str:movimiento_id>/<str:cargo>/', AumentoCargoListView.as_view(), name="crear_cargo_codigo"),
    path('aumento_creado/', AumentoCreateView.as_view(), name="aumento_creado"),
]
 