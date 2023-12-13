var formAjaxSubmit = function(form, modal) {
    $(form).submit(function (e) {
        e.preventDefault();
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (xhr, ajaxOptions, thrownError) {
                if ( $(xhr).find('.errorlist').length > 0 ) {
                    $(modal).find('.modal-body').html(xhr);
                    formAjaxSubmit(form, modal);
                } else {
                    $(modal).modal('toggle');
                    notificar('Se ha creado el movimiento.', ' fa-info-circle', 'success')

                }
            },
            error: function (xhr, ajaxOptions, thrownError) {
                $(modal).modal('toggle');
                notificar('Error en la creacion del movimiento', ' fa-info-circle', 'danger')
            }
        });
    });
}

$('#modal-create-movimiento').click(function() {
    $('#form-modal-body').load($(this).attr('action'), function () {
        $('#siliq_modal_windows').modal('toggle');
        formAjaxSubmit('#form-modal-body form', '#siliq_modal_windows');
    });
});