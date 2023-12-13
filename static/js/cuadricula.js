function CuadriculaListado() {
  $.ajax({
      url: "/cuadricula/lista",
      type: "get",
      dataType: "json",
      success: function (response) {
          if ($.fn.DataTable.isDataTable('#tabla_cuadricula')) {
              $('#tabla_cuadricula').DataTable().destroy();
          }
          console.log(response);
          $('#tabla_cuadricula tbody').html("");
          for (let i = 0; i < response.length; i++) {
              let fila = '<tr>';
              fila += '<th>' + response[i]["fields"]['codigo'] + '</th>';
              fila += '<th>' + response[i]["fields"]['nombre'] + '</th>';
              fila += '<th>' + response[i]["fields"]['reparticion'] + '</th>';
              fila += '<th>' + response[i]["fields"]['periodo_dd'] + '</th>';
              fila += '<th>' + response[i]["fields"]['periodo_ht'] + '</th>';
              fila += '<th>' + response[i]["fields"]['creator'] + '</th>';


             
              fila += '<th><a href="/cuadricula/' + response[i]['pk'] +'/update " class="btn btn-default btn-sm pull-right">';
              fila += '<span class="fa fa-edit fa-align-justify"></span> Modificar</a>';
              fila += '<a href="/cuadricula/' + response[i]['pk'] +'/delete" class="btn btn-default btn-sm finalizar-proyecto pull-right">';
              fila += '<span class="fa fa-fw fa-check-square-o"></span> Eliminar</a>';
              fila += '<a href="/cuadricula/' + response[i]['pk'] +'" class="btn btn-default btn-sm pull-right">';
              fila += '<i class="fa fa-fw fa-align-justify"></i> Ver</a>';
              fila += '</th>';
              fila += '</tr>';
              $('#tabla_cuadricula tbody').append(fila);
          }
          $('#tabla_cuadricula').DataTable({
              language: {
                  "decimal": "",
                  "emptyTable": "No hay información",
                  "info": "Mostrando _START_ a _END_ de _TOTAL_ Entradas",
                  "infoEmpty": "Mostrando 0 to 0 of 0 Entradas",
                  "infoFiltered": "(Filtrado de _MAX_ total entradas)",
                  "infoPostFix": "",
                  "thousands": ",",
                  "lengthMenu": "Mostrar _MENU_ Entradas",
                  "loadingRecords": "Cargando...",
                  "processing": "Procesando...",
                  "search": "Buscar:",
                  "zeroRecords": "Sin resultados encontrados",
                  "paginate": {
                      "first": "Primero",
                      "last": "Ultimo",
                      "next": "Siguiente",
                      "previous": "Anterior"
                  },
              },
          });
      },
      error: function (error) {
          console.log(error);
      }
  });
}


$(document).ready(function () {
  CuadriculaListado();
});

