function abrir_modal_eliminacion(url) {
    $('#eliminacion').load(url, function() {
        $(this).modal('show');
    });
}

function eliminar(pk) {
    $.ajax({
        data: {
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val()
        },
        url: '/aumentos/eliminar_aumento/' + pk + '/',
        type: 'post',
        success: function(response) {
            console.log('elimino!');
            cerrar_modal_eliminacion();
            $('#obj-id-' + pk).remove();
            notificacionSuccess();

        },

    });
}


function cerrar_modal_eliminacion() {
    $('#eliminacion').modal('hide');
}