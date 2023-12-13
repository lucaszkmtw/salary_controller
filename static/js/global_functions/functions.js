function notificar(texto,icon,type) {
    $.notify(
      { icon: 'fa ' + icon, message: texto },
      { type: type,
        allow_dismiss: true,
        newest_on_top: false,
        placement: { from: "top", align: "right" },
        offset: { x: 15, y: 60 },
        spacing: 10,
        z_index: 1031,
        delay: 5000,
        timer: 1000,
        animate: { enter: 'animated fadeInDown', exit: 'animated fadeOutUp' }
      }
    )
  }

$(".delete-object").click(function (e) {
  ajax_delete_object($(this).attr('obj-class'), $(this).attr('obj-id'))
});

function ajax_delete_object(obj_class, obj_id) {
  $.ajax({
    type: "POST",
    url: "/ajax_delete_object/",
    data: {
      'obj_class': obj_class,
      'obj_id': obj_id,
      'csrfmiddlewaretoken': csrftoken
    },
    success: function (response) {
      if (Boolean(response.ok)) {
        notificar('El objeto ha sido eliminado.','fa fa-trash', 'success')
        $(".item-obj-class").each(function (index, element) {
          if ($(element).attr('item-obj-class') == obj_class + '-' + obj_id) {
            $(element).remove();
          }
        });
      }else{
        notificar('El objeto no se ha podido eliminar.','fa fa-trash', 'danger')
      }
    }
  });
}