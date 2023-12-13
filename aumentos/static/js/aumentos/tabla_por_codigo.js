$('#campos_tipo').change(function() {
    if ($(this).val() == 2) {
        document.getElementById("tipo_aumento_icon").innerHTML = "$";
    } else {
        document.getElementById("tipo_aumento_icon").innerHTML = "%";
    }
})




$.ajax({
    url: '/aumentos/cargo_codigo/' + movimiento_id + "/" + nombre,
    success: function(response) {
        var aumentos = JSON.parse(response.aumentos)

        for (let i = 0; i < aumentos.length; i++) {
            var tipo_aumento = aumentos[i]['fields']['tipo_aumento']
            var tipo_calculo = aumentos[i]['fields']['tipo_calculo']
            var valor = aumentos[i]['fields']['valor']
            let fila = '<tr class="obj-id-'+ aumentos[i]['pk']  + '">';
            fila += '<th scope="col"><strong>' + periodo + ' </strong></th>';
            if (tipo_calculo == 1) {
                fila += retonar_tipo_aumento(tipo_aumento, valor, basico);
            } else {
                fila += '<th  scope="col"><strong>' + parseFloat(basico).toFixed(2) + '</strong></th>'
            }
            if (tipo_calculo == 2) {
                fila += retonar_tipo_aumento(tipo_aumento, valor, suplemento1);
            } else {
                fila += '<th  scope="col"><strong>' + parseFloat(suplemento1).toFixed(2) + '</strong></th>'
            }
            if (tipo_calculo == 3) {
                fila += retonar_tipo_aumento(tipo_aumento, valor, suplemento2);
            } else {
                fila += '<th  scope="col"><strong>' + parseFloat(suplemento2).toFixed(2) + '</strong></th>'
            }
            if (tipo_calculo == 4) {
                fila += retonar_tipo_aumento(tipo_aumento, valor, sumafija1);
            } else {
                fila += '<th  scope="col"><strong>' + parseFloat(sumafija1).toFixed(2) + '</strong></th>'
            }
            if (tipo_calculo == 5) {
                fila += retonar_tipo_aumento(tipo_aumento, valor, sumafija2);

            } else {
                fila += '<th  scope="col"><strong>' + parseFloat(sumafija2).toFixed(2) + '</strong></th>'
            }
            if (tipo_calculo == 6) {
                fila += retonar_tipo_aumento(tipo_aumento, valor, sumafija3);
            } else {
                fila += '<th  scope="col"><strong>' + parseFloat(sumafija3).toFixed(2) + '</strong></th>'
            }
            fila += '<td> <button class="btn btn-danger btn-xs btn-flat fa fa-remove"';
            fila += 'onclick = "eliminar(' + aumentos[i]['pk'] + ');">  </button>  </td>'

            fila += '</tr>';
            $('#aumento_creado').append(fila);




        }


    }
});





document.getElementById('save').onclick = function(e) {
    e.preventDefault();



    var select1 = document.getElementById('campos_tipo');
    var tipo_aumento = select1.options[select1.selectedIndex];

    var selected = [];
    for (var option of document.getElementById('campos_aumentos_select_mult').options) {
        if (option.selected) {
            selected.push(option.value);
        }
    }
    var valor = document.getElementById("cantidad_aumento").value;

    if (valor == '') {
        notificacionError();


    } else {



        $.ajax({
            method: "POST",
            url: '/aumentos/aumento_creado/',
            data: {

                'tipo_calculo': selected[0],
                'movimiento': movimiento_id,
                'tipo_aumento': tipo_aumento.value,
                'cargo': cargo,
                'valor': valor,
                'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            success: function(response) {
                aumento_json = JSON.parse(response.aumento_creado);
                console.log(aumento_json);
                var seleccionado = tipo_aumento.value;


                let fila = '<tr class="obj-id-'+ aumento_json[aumento_json.length -1]['pk']  + '">';
                fila += '<th scope="col"><strong>' + periodo + ' </strong></th>';
                if (selected[0] == 1) {
                    fila += retonar_tipo_aumento(seleccionado, valor, basico);
                } else {
                    fila += '<th  scope="col"><strong>' + parseFloat(basico).toFixed(2) + '</strong></th>'
                }
                if (selected[0] == 2) {
                    fila += retonar_tipo_aumento(seleccionado, valor, suplemento1);
                } else {
                    fila += '<th  scope="col"><strong>' + parseFloat(suplemento1).toFixed(2) + '</strong></th>'
                }
                if (selected[0] == 3) {
                    fila += retonar_tipo_aumento(seleccionado, valor, suplemento2);
                } else {
                    fila += '<th  scope="col"><strong>' + parseFloat(suplemento2).toFixed(2) + '</strong></th>'
                }
                if (selected[0] == 4) {
                    fila += retonar_tipo_aumento(seleccionado, valor, sumafija1);
                } else {
                    fila += '<th  scope="col"><strong>' + parseFloat(sumafija1).toFixed(2) + '</strong></th>'
                }
                if (selected[0] == 5) {
                    fila += retonar_tipo_aumento(seleccionado, valor, sumafija2);

                } else {
                    fila += '<th  scope="col"><strong>' + parseFloat(sumafija2).toFixed(2) + '</strong></th>'
                }
                if (selected[0] == 6) {
                    fila += retonar_tipo_aumento(seleccionado, valor, sumafija3);
                } else {
                    fila += '<th  scope="col"><strong>' + parseFloat(sumafija3).toFixed(2) + '</strong></th>'
                }

                fila += '<td> <button class="btn btn-danger btn-xs btn-flat fa fa-remove"';
                fila += 'onclick = "eliminar(' + aumento_json[aumento_json.length - 1]['pk'] + ');">  </button>  </td>'
    
                fila += '</tr>';
                $('#aumento_creado').append(fila);


                document.getElementById('cantidad_aumento').value = "";

            }


        });
    }
}



function notificacionCreado(mensaje) {
    Swal.fire({
        title: 'Creado!',
        text: mensaje,
        icon: 'success'
    })
}




function notificacionError(mensaje) {
    Swal.fire({
        icon: 'error',
        title: 'Error!',
        text: 'Debe Completar todos los campos!',
    })
}

function CalcularDiferencia(b, a) {
    var valor_nuevo = (a < b ? "-" + ((b - a) * 100) / a : ((a - b) * 100) / b);
    valor_nuevo = parseFloat(valor_nuevo).toFixed(2);

    return valor_nuevo;

}

function CalcularPorcentaje(tipo, valor) {
    var porcentaje = tipo * valor;
    porcentaje = porcentaje / 100;
    var val = parseFloat(tipo);
    var aumento = (parseFloat(porcentaje) + val).toFixed(2);
    return aumento;
}



function CalcularSumafija(valor) {
    var html = '&nbsp;<small class="text-red"><i class="glyphicon glyphicon-plus"></i><span>&nbsp;' + valor + '$</span>';
    html += '</small>'
    console.log(valor);
}


function Icono(valor) {

    if (parseFloat(valor).toFixed(2) < 0) {
        var html = '&nbsp;<small class="text-red"><i class="glyphicon glyphicon-arrow-down"></i><span>&nbsp;' + (parseFloat(valor).toFixed(2)) + '%</span>';

    } else {
        var html = '&nbsp;<small class="text-blue"><i class="glyphicon glyphicon-arrow-up"></i><span>&nbsp;' + (parseFloat(valor).toFixed(2)) + '%</span>';
        html += '</small>';

    }

    return html;
}



function retonar_tipo_aumento(select, valor, valor_anterior) {

    if (select == 1) {
        var fila = '<th  scope="col"><strong>' + CalcularPorcentaje(valor_anterior, valor) + "  " + Icono(valor) + '</strong></th>';
    }
    if (select == 2) {

        if (valor > 0) {
            var suma = parseFloat(valor) + parseInt(valor_anterior);
            var fila = '<th  scope="col"><strong>' + parseFloat(suma).toFixed(2);

            fila += '&nbsp;<small class="text-blue"><strong>+</strong><span>' + valor + '&nbsp$</span>';
            fila += '</small>';
            fila += '</strong></th>';
        } else {

            var resta = (parseFloat(valor_anterior) + parseFloat(valor));

            var fila = '<th  scope="col"><strong>' + parseFloat(resta).toFixed(2);
            fila += '&nbsp;<small class="text-red"><strong></strong><span> ' + valor + '&nbsp$</span>';
            fila += '</small>';
            fila += '</strong></th>';
        }



    }
    return fila
}




function eliminar(pk) {
    $.ajax({
        data: {
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val()
        },
        url: '/aumentos/eliminar_aumento/' + pk + '/',
        type: 'post',
        success: function(response) {
            $('.obj-id-' + pk).remove();

        },

    });
}

