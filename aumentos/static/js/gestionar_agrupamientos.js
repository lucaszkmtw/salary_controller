function confirmarEliminacion() {
    var i = 0
    $.each($("input[name='prueba']:checked"), function() {
      i++
    });
  
    if (i != 0) {
      if (i > 1) {
        $('#cant').html('los siguientes ' + i + ' archivos')
      } else {
        $('#cant').html('el siguiente archivo')
      }
      $('#deleteConfirmation').modal('show')
    } else {
      alert('Seleccione al menos un archivo para eliminar.');
    }
  }
  
  function eliminarSeleccionados() {
    var data = ''
    var i = 0
  
    $.each($("input[name='prueba']:checked"), function() {
      i++
      data += "id=" + $(this).val() + "&"
    });
    data = data.slice(0, -1)
    data += ''
  
    if (i != 0) {
  
      $.ajax({
        data: data,
        type: 'GET',
        url: '/aumentos/eliminar_seleccionada/',
        processData: true,
        success: function(data) {
          location.reload();
        }
      });
  
    }
  
  }
  
  function integrarSeleccionados() {
    var data = ''
    var i = 0
  
    $.each($("input[name='prueba']:checked"), function() {
      i++
      data += "id=" + $(this).val() + "&"
    });
    data = data.slice(0, -1)
    data += ''
  
    if (i != 0) {
  
      $.ajax({
        data: data,
        type: 'GET',
        url: '/comparaHiscar/integrarSeleccionados/',
        processData: true,
        success: function(data) {
          location.reload();
        }
      });
  
    }
  
  }
  
  function editarNombreArchivo(Obj) {
    var id = $(Obj).attr('valor')
    $('#text' + id).css("display", "none")
    $('#input' + id).css("display", "block")
    $('#input' + id).val('value', '')
  }
  
  function mostrarTexto(Obj) {
    var id = $(Obj).attr('valor')
    var nombreArchivo = $('#input-val' + id).val()
    $('#text' + id).html(nombreArchivo)
    $('#text' + id).css("display", "block");
    $('#input' + id).css("display", "none");
  }
  
  function guardarNombreArchivo(Obj) {
    var id = $(Obj).attr('valor')
    var nombreArchivo = $('#input-val' + id).val()
    console.log(nombreArchivo)
  
    $.ajax({
      data: {
        'pruebaID': id,
        'nombreArchivo': nombreArchivo,
      },
      type: 'GET',
      url: '/comparaHiscar/nomArchivo/',
  
      success: function(data) {
        mostrarTexto(Obj)
      }
    });
  }
  
  function LockUnlock(ObjLock) {
  
    $.ajax({
      data: {
        'pruebaID': $(ObjLock).attr('id'),
      },
      type: 'GET',
      url: '/comparaHiscar/locker/',
  
      success: function(data) {
        console.log('cambio ?', data.bandera)
        if (data.bandera) {
  
          if ($(ObjLock).attr('value') == "False") {
            $(ObjLock).removeClass("btn-warning fa-lock");
            $(ObjLock).addClass("btn-info fa-unlock-alt");
            $(ObjLock).attr('value', 'True');
  
          } else {
            $(ObjLock).removeClass("btn-info fa-unlock-alt");
            $(ObjLock).addClass("btn-warning fa-lock");
            $(ObjLock).attr('value', 'False');
          }
        }
      }
    });
  }
  
  function sinAyuda() {
    $.ajax({
      data: {
        'SinAyudas': 'True',
      },
      type: 'GET',
      url: '/comparaHiscar/sinAyudas/',
      success: function(data) {
        console.log('Sin Ayudas')
        alert('Ayudas Desactivadas, puede activarlas ingresando a configuracion/ayudas')
      }
    })
  }
  
  function cargando() {
    $("#loadMe").modal({
      backdrop: "static", //remove ability to close modal with click
      keyboard: false, //remove option to close with keyboard
      show: true //Display loader!
    });
    //$("#loadMe").modal("hide");
  }
  
  function integrarPrueba(Obj) {
    $.ajax({
      data: {
        'pruebaID': $(Obj).attr('id'),
        'time': event.timeStamp
      },
      type: 'GET',
      url: '/comparaHiscar/integrarPrueba/',
  
      success: function(data) {
        if (data.bandera) {
  
          if ($(Obj).attr('value') == "False") {
  
  
            $(Obj).removeClass("btn-danger fa-chevron-circle-left ");
            $(Obj).addClass("btn-success fa-chevron-circle-right");
            $(Obj).attr('value', 'True');
  
          } else {
            $(Obj).removeClass("btn-success fa-chevron-circle-right");
            $(Obj).addClass("btn-danger fa-chevron-circle-left ");
            $(Obj).attr('value', 'False');
            var id = $(Obj).attr('id').toString()
            $('#informe-' + id).hide();
          }
        }
      }
    });
  }
  