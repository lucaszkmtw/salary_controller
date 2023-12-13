/* Funcion que aplica la modificacion de la descripcion de una reparticion o un cargo en el html  */
function modifico_cargo_reparticion(resultado) {
  $("#tooltip_" + resultado.id).attr('title', "Por " + resultado.user + " - " + resultado.modified);
  if (resultado.tipo == "cargo-cargo") {
    $("#cargo_" + resultado.id).text(resultado.value);
  }
  if (resultado.tipo == "reparticion-nombre") {
    $("#rep_nom_" + resultado.id).text(resultado.value);
  }
}

/* Function que informa que se activo o desactivo el modulo de una reparticion */
function activo_desactivo_modulo(estado, boton) {
  if (estado == 'activado') {
    $($(boton).children()[0]).removeClass('fa-eye-slash')
    $($(boton).children()[0]).addClass('fa-eye')
    $($(boton).children()[1]).text("Activar")
    $($($(boton).parent().children()[1])).hide()
    notificar('Se ha desactivado el modulo correctamente.', ' fa-info-circle', 'info')
  } else {
    $($(boton).children()[0]).removeClass('fa-eye')
    $($(boton).children()[0]).addClass('fa-eye-slash')
    $($(boton).children()[1]).text("Desactivar")
    $($($(boton).parent().children()[1])).show()
    notificar('Se ha activado el modulo correctamente.', ' fa-info-circle', 'success')
  }
}

/* Funcion que hace una llamada con Ajax para activar o desactivar
un cargo o una reparticion según corresponda */
function activo_desactivo_id(id, accion, tipo, nombre) {
  var conf = confirm("¿Seguro que desea " + accion + " '" + nombre + "'?")
  if (conf) {
    $.ajax({
      type: "POST",
      url: "../activo_desactivo_id/",
      data: {
        'id': id,
        'accion': accion,
        'csrfmiddlewaretoken': csrftoken,
        'tipo': tipo
      },
      success: function (response) {
        if (accion === 'activar') {
          notificar("Se activó correctamente", ' fa-info-circle', 'success')
          $("#activar-" + id).hide()
          $("#desactivar-" + id).show()
          $("#row-" + id).attr('style', '')
        } else {
          notificar("Se desactivó correctamente", ' fa-info-circle', 'success')
          $("#desactivar-" + id).hide()
          $("#activar-" + id).show()
          $("#row-" + id).attr('style', "text-decoration: line-through!important;color:#CCC")
        }
      }
    });
  }
}
function activo_desactivo_modulos(reparticion_id, nombre, boton){
  $("#spinner-div").show()
  $.ajax({
    type: "POST",
    url: "/aumentos/activo_desactivo_modulo/",
    data: {
      'csrfmiddlewaretoken': csrftoken,
      'reparticion_id': reparticion_id
    },
    success: function (response) {
      if (response.ALERT != 1) {
        activo_desactivo_modulo(response.estado, boton)
      } else {
        notificar("La reparticion debe estar activada para poder activar el modulo.", ' fa-info', 'danger')
      }
      $("#spinner-div").hide()
    }
  })
}

$(".tabla-abm").on('draw.dt',function(){
    /* Datos que luego seran enviados con Jeditable */
    var submitdata = {};

    submitdata["slow"] = true;
    submitdata["pwet"] = "youpla";
    submitdata["csrfmiddlewaretoken"] = csrftoken;
    submitdata["user_id"] = user_id;
  
    $("button.listado-cargos").on("click", function () {
      var codigo_municipio = $(this).attr("repart_id");
      var url = "../abm_cargos/?reparticion_id=";
      url += codigo_municipio;
      $(location).attr("href", url);
    });
  
  
    $(".tipos_modulo_btn").click(function (e) {
      e.preventDefault()
      siliq_modal_show("/aumentos/gestionar_tipos_modulos/?reparticion_id=" + $(this).attr('obj-id'), "Gestionar Tipos de modulos")
    })
  
  
    /* Se ejecuta cuando se clickea sobre la descripcion de un cargo o reparticion.
       Permite la edicion de las descripciones y almacenarlas ejecutando la vista 'abm_cargos_save' */
    $(".editable-text-full").editable("/aumentos/abm_cargos_save/", {
      data: function (string) {
        return $.trim(string)
      },
      indicator: "<i class='fa fa-refresh fa-spin'></i>",
      type: "text",
      onedit: function () {
        $($(this)[0]).toggleClass('edit-name');
      },
      callback: function (result, settings, submitdata) {
        modifico_cargo_reparticion(JSON.parse(result))
      },
      cancel: "Cancelar",
      maxlength: 190,
      select: true,
      showfn: function (elem) {
        elem.fadeIn("slow");
      },
      submit: "Guardar",
      submitdata: submitdata,
      tooltip: "Click para editar ...",
      width: 450,
      cssclass: 'custom-class',
      inputcssclass: 'form-control upper-c',
      cancelcssclass: 'btn btn-danger btn-sm ml-1',
      submitcssclass: 'btn btn-success btn-sm ml-1',
      onreset: function () {
        $($(this).parent()[0]).toggleClass('edit-name');
      },
      onsubmit: function () {
        $($(this).parent()[0]).toggleClass('edit-name');
      },
    })
  
    /* Se ejecuta cuando se clickea sobre los botones 'Activar' o 'Desactivar' para el Modulo
    de una Reparticion. El mismo activa o desactiva el modulo según corresponda. */
    $(".activo-desactivo-modulo").click(function (e) {
      e.preventDefault()
      activo_desactivo_modulos(
        $(this).attr('obj-id'),
        $("#rep_nom_2").text(),
        $(this)
      )
    })
  
  
    /* Desactiva un cargo o reparticion según corresponda */
    $(".desactivar-id").click(function (e) {
      e.preventDefault();
      var nombre = $($(this).parent().parent()[0]).attr('name');
      var id = $(this).attr('id').split("desactivar-")[1];
      activo_desactivo_id(id, "desactivar", $(this).attr('tipo'), nombre)
  
    });
  
    /* Activa un cargo o reparticion según corresponda */
    $(".activar-id").click(function (e) {
      e.preventDefault();
      var id = $(this).attr('id').split("activar-")[1];
      var nombre = $($(this).parent().parent()[0]).attr('name');
      activo_desactivo_id(id, "activar", $(this).attr('tipo'), nombre);
  
    });
  
  
  
  
  
    /* Agrega la clase text on hover */
    $(".edit-name").hover(function () {
      if ($(this).hasClass('edit-name')) {
        $(this).addClass("text");
      }
    }, function () {
      if ($(this).hasClass('edit-name')) {
        $(this).removeClass("text");
      }
    });
  
    $(".select_asignaciones").change(function (e) {
      e.preventDefault();
      select = this
      $.ajax({
        type: "GET",
        url: "/aumentos/asignaciones_guardar/",
        data: {
          'asignacion_id': $(this).attr("obj-id"),
          'new_tipo_id': $(this).val()
        },
        success: function (response) {
          $(select).attr('obj-id', response.new_id)
        }
      })
    })
  
    /* Al clickear crear cargo, este metodo levanta el modal para la creacion del mismo */
    $("#btn-crear-cargo").click(function (e) {
      e.preventDefault()
      $('#abm-cargos-modal').modal({
        show: true
      });
    });
  
})

$(document).ready(function () {



  /* Se Inicializa la tabla */
  $("#tabla_abm").DataTable({
    searchable:true,
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
      }
    },
    "serverSide": true,
    "ajax": "/djangorestframework/reparticiones/?format=datatables",
    "columnDefs": [
      {
          "targets": [0],
          "visible": false,
          "searchable": false
      },
      {
        "targets": [1],
        "visible": false,
        "searchable": false
      },
      {
        "targets": [4],
        "searchable": false
      },
      {
        "targets": [5],
        "searchable": false
      },

    ],
    "columns": [
      {
        "data":'is_active',
      },
      {
        "data":'modified',
      },
      {
        "data": "codigo"
      },
      {
        "data": "nombre",
        "render": function (data,type,full,meta) {
          return `<p id="rep_nom_1" class="editable-text-full upper-c edit-name" tipo="reparticion-nombre" valor="`+full.nombre+`" title="Click para editar ...">`+full.nombre+`</p>`
        }
      },
      {
        "data": "has_modulo",
        "render": function (data, type, full, meta) {
          var html = `
                <button type="button" obj-id="` + full.DT_RowId.slice(4) + `" class="btn btn-default btn-flat activo-desactivo-modulo">
                  <i class="fa fa-eye` + ((full.has_modulo) ? '-slash' : '') + `" aria-hidden="true"></i>
                        <span>` + ((full.has_modulo) ? 'Desactivar' : 'Activar') +
            `
                        </span>
              </button>
              <button type="button" class="btn btn-default btn-flat tipos_modulo_btn" obj-id="` + full.DT_RowId.slice(4) + `"
              ` + ((full.has_modulo) ? '' : "style='display: none;'") + `>
                Tipos de modulos
              </button>
              `
          return html;
        }
      },
      {
        "data": "user",
        "render": function (data, type, full, meta) {
          var button1 = `<button type="button" tipo="reparticion" class="btn btn-default btn-flat btn activar-id"
          id="activar-` + full.DT_RowId.slice(4) + `" style="display: none;"><i class="fa fa-eye"
            aria-hidden="true"></i>&nbsp;Activar</button>
        <button type="button" tipo="reparticion" class="btn btn-default btn-flat desactivar-id"
          id="desactivar-` + full.DT_RowId.slice(4) + `"><i class="fa fa-eye-slash"
            aria-hidden="true"></i>&nbsp;Desactivar</button>`
          var button2 = `
          <button type="button" tipo="reparticion" class="btn btn-default btn-flat desactivar-id"
          id="desactivar-` + full.DT_RowId.slice(4) + `" style="display: none;"><i class="fa fa-eye-slash"
            aria-hidden="true"></i>&nbsp;Desactivar</button>
        <button type="button" tipo="reparticion" class="btn btn-default btn-flat activar-id"
          id="activar-` + full.DT_RowId.slice(4) + `"><i class="fa fa-eye" aria-hidden="true"></i>&nbsp;Activar</button>
          `
          var html = `<button type="button" repart_id="` + full.DT_RowId.slice(4) + `" class="btn btn-default btn-flat listado-cargos">
                            Cargos
                      </button>` + ((full.is_active) ? button1 : button2) +
            `<div class="btn-group">
                      <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown"
                        aria-expanded="false">
                        <span class="fa fa-user"></span>
                        <span class="caret"></span>
                      </button>
                      <ul class="dropdown-menu">
                        <li><a href="#">` + full.user.username + ` - ` + full.modified + `</a></li>
                      </ul>
                    </div>`
          return html
        }
      }
    ]

  });

  $("#tabla_abm_cargos").DataTable({
    "paging": true,
    "order": [
      [2, "asc"]
    ],
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
      }
    }
  });
});