function eliminar_proyecto(proy_id, row) {
  row = $("#" + row)
  var data = {
    id: proy_id,
    csrfmiddlewaretoken: csrftoken,
  }
  $.ajax({
    type: "POST",
    url: '../eliminar_proyecto/',
    data: data,
    success: function (response) {
      $("#deleteConfirmation").modal('hide');
      if (! response['error']) {
        $(row).hide()
        notificar("El Proyecto '" + response['nombre'] + "' se eliminó correctamente", '', "success")
      } else {
        notificar("El Proyecto '" + response['nombre'] + "' no se pudo eliminar.", '', "danger")
      }
    }
  });
}

function finalizar_proyecto(proy_id, row) {
  row = $("#" + row)
  var data = {
    id: proy_id,
    csrfmiddlewaretoken: csrftoken,
  }
  $.ajax({
    type: "POST",
    url: '../finalizar_proyecto/',
    data: data,
    success: function (response) {
      $("#confirmModal").modal('hide');
      if (response['proyecto']) {
        $(row.children()[5]).text('')
        $(row.children()[5]).append("<strong class='text text-success'>Finalizado</strong>")
        $($(row.children()[6]).children()[2]).hide()
        $($(row.children()[6]).children()[3]).hide()
        $($(row.children()[6]).children()[4]).hide()
        $($(row.children()[1]).children()[0]).hide()
        notificar("El Proyecto '" + response['nombre'] + "' finalizó correctamente", '', "success")
      } else {
        notificar("El Proyecto '" + response['nombre'] + "' no se pudo finalizar. Aún tiene movimientos abiertos", '', "danger")
      }
    }
  });
}

$(document).ready(function () {

  var now = new Date(),
  minDate = now.toISOString().substring(0,10);

  $('#limite-proyecto').prop('min', minDate);

  var tabla = $("#tabla_abm").DataTable({
    "paging": true,
    "ordering": true,
    "order": [[ 5, "asc" ]],
    columnDefs: [{
      orderable: false,
      targets: "no-sort"
    }],

    "rowReorder": true,
    language: {
      sProcessing: "Procesando...",
      sLengthMenu: "Mostrar _MENU_ registros",
      sZeroRecords: "No se encontraron resultados",
      sEmptyTable: "Ningún dato disponible en esta tabla",
      sInfo: "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
      sInfoEmpty: "Mostrando registros del 0 al 0 de un total de 0 registros",
      sInfoFiltered: "(filtrado de un total de _MAX_ registros)",
      sInfoPostFix: "",
      sSearch: "Buscar:",
      sUrl: "",
      sInfoThousands: ",",
      sLoadingRecords: "Cargando...",
      oPaginate: {
        sFirst: "Primero",
        sLast: "Último",
        sNext: "Siguiente",
        sPrevious: "Anterior"
      },
      oAria: {
        sSortAscending: ": Activar para ordenar la columna de manera ascendente",
        sSortDescending: ": Activar para ordenar la columna de manera descendente"
      },
      rowReorder: true
    }
  });

  if ($("#tabla_abm").attr('is_close') == 'True') {
    tabla.rowReorder.disable();
  }

  $(".finalizar-proyecto").click(function (e) {
    e.preventDefault();
    var tr = $($(this).parent().parent())
    var proyecto = $($(tr.children()[0]).children()[0]).text().trim()
    var proy_id = tr.attr('id').slice(4)
    $(".modal-title").text("¿Seguro que desea finalizar el Proyecto '" + proyecto + "'?");
    $("#accion_modal").attr('onclick', "finalizar_proyecto(" + proy_id + ",'" + tr.attr('id') + "')");
    $("#accion_modal").text('Finalizar')
    $("#confirmModal").modal('show');
  });

  $(".eliminar-proyecto").click(function (e) {
    e.preventDefault();
    var tr = $($(this).parent().parent())
    var proyecto = $($(tr.children()[0]).children()[0]).text().trim()
    var proy_id = tr.attr('id').slice(4)
    $(".modal-title").text('')
    $(".modal-title").append("Esta seguro que desea eliminar el Proyecto '"+proyecto+"' de forma permanente ?")
    $("#eliminar-modal").attr('onclick', "eliminar_proyecto(" + proy_id + ",'" + tr.attr('id') + "')");
    $("#deleteConfirmation").modal('show');
  });

  $("button.detalle-proyecto").on("click", function () {
    $(location).attr("href", $(this).attr("href"));
  });

  /* Indica para cada proyecto cuantos dias quedan restantes para llegar a la fecha limite */
  $(".tiempo-restante").each(function (index, element) {
    $(element).countdown($(element).attr('value'), function (event) {
      if ($(element).attr('is_close') == 'False' && $(element).attr('is_active') == 'True') {
        $(element).text(
          event.strftime('¡Quedan %D dias!')
        )
      }
    })
  })

  $("#modal-default").on("hidden.bs.modal", function () {
    $("#nombre-proyecto").val('')
    $("#nombre-proyecto").attr('id_proy', '')
    $("#text-area-proyecto").val('')
    $("#limite-proyecto").val('')
    $(".modal-title").text('Crear Proyecto')
  });
  /* Al hacer click en 'Detalle' redirecciona al detalle de un Movimiento */
  $("button.detalle-movimiento").on("click", function () {
    var codigo_municipio = $(this).attr("repart_id");
    var url = "/aumentos/aumento/?";
    url += "movimiento_id=";
    url += $(this).attr("mov_id");
    url += "&municipio_id=";
    url += codigo_municipio;
    url += "&proyecto_id="
    url += $("#tabla_abm").attr('proy_id')

    $(location).attr("href", url);
  });

});