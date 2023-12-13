$(document).ready(function() {
  function suma_o_porcen(seleccionado){
    if (seleccionado== 1){
      return "%"
    }
    else{
      return "$"
    }
  }

    function ListadoAumentos() {

        $.ajax({
            type: "GET",
            url: "/aumentos/get_aumentos_tabla/",
            data: {
                id: movimiento_id
            },
            success: function(response) {


                aumento = JSON.parse(response.aumentos);
                console.log(aumento)

                if ($.fn.DataTable.isDataTable('#tabla_aumento_modulo')) {
                    $('#tabla_aumento_modulo').DataTable().destroy();
                }


                $('#tabla_aumento_modulo tbody').html("");
                for (let i = 0; i < aumento.length; i++) {
                  var seleccionado = aumento[i]['fields']['tipo_aumento'];


                    let fila = '<tr id="obj-id-' + aumento[i]['pk'] + '">';
                    fila += '<td class="sorting_1><span class="aumentos-orden" obj-id="' + aumento[i]['fields']['movimiento'] + 'null"</spam>';

                    fila += '<i class="fa fa-fw fa-arrows"></i></td>'
                    fila += '<td> <button class="btn btn-danger btn-xs btn-flat fa fa-remove"';
                    fila += 'onclick = "abrir_modal_eliminacion(\'/aumentos/eliminar_aumento/' + aumento[i]['pk'] + '/\');">  </button>  </td>'

                    if (aumento[i]['fields']['cargo'] == null){
                      fila += '<td>null<a class="fa fa-fw fa-info-circle pull-right info-aumento"></a></td>';
                      
                    }else{

                   
                    fila += '<td>' + aumento[i]['fields']['cargo'][1] + '<a class="fa fa-fw fa-info-circle pull-right info-aumento"></a></td>'; }


                    if (aumento[i]['fields']['tipo_calculo'] == 1) {
                        fila += '<td><strong> ' + aumento[i]['fields']['valor'] + suma_o_porcen(seleccionado) + '     </strong></td>';
                      } else {
                        fila += '<td><strong> -</strong></td>';
                      }
                      if (aumento[i]['fields']['tipo_calculo'] == 2) {
                        fila += '<td><strong> ' + aumento[i]['fields']['valor'] + suma_o_porcen(seleccionado) + '     </strong></td>';
                      } else {
                        fila += '<td><strong> -</strong></td>';
                      }
                      if (aumento[i]['fields']['tipo_calculo'] == 3) {
                        fila += '<td><strong> ' + aumento[i]['fields']['valor'] + suma_o_porcen(seleccionado) + '     </strong></td>';
                      } else {
                        fila += '<td><strong> -</strong></td>';
                      }
                      if (aumento[i]['fields']['tipo_calculo'] == 4) {
                        fila += '<td><strong> ' + aumento[i]['fields']['valor'] + suma_o_porcen(seleccionado) + '     </strong></td>';
                      } else {
                        fila += '<td><strong> -</strong></td>';
                      }
                      if (aumento[i]['fields']['tipo_calculo'] == 5) {
                        fila += '<td><strong> ' + aumento[i]['fields']['valor'] + suma_o_porcen(seleccionado) + '     </strong></td>';
                      } else {
                        fila += '<td><strong> -</strong></td>';

                      }
                      if (aumento[i]['fields']['tipo_calculo'] == 6) {
                        fila += '<td><strong> ' + aumento[i]['fields']['valor'] + suma_o_porcen(seleccionado) + '     </strong></td>';
                      } else {
                        fila += '<td><strong> -</strong></td>';

                      }

            
                    fila += '</tr>'
                    $('#tabla_aumento_modulo tbody').append(fila);
                }
                $('#tabla_aumento_modulo').DataTable({
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
            }
        });



    }

    ListadoAumentos();
});


function notificacionSuccess(mensaje) {
    Swal.fire({
        title: 'eliminado!',
        text: mensaje,
        icon: 'success'
    })

}



