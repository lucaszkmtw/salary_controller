$('#pre-selected-options').multiSelect({

  selectableHeader: "<input type='text' class='search-input form-control' autocomplete='on' placeholder='Cargo ..'>",
  selectionHeader: "<input type='text' class='search-input form-control' autocomplete='on' placeholder='Cargo ..'>",
  afterInit: function (ms) {
    var that = this,
      $selectableSearch = that.$selectableUl.prev(),
      $selectionSearch = that.$selectionUl.prev(),

      selectableSearchString = '#' + that.$container.attr('id') + ' .ms-elem-selectable:not(.ms-selected)',
      selectionSearchString = '#' + that.$container.attr('id') + ' .ms-elem-selection.ms-selected';

    that.qs1 = $selectableSearch.quicksearch(selectableSearchString)
      .on('keydown', function (e) {
        if (e.which === 40) {
          that.$selectableUl.focus();
          return false;
        }
      });

    that.qs2 = $selectionSearch.quicksearch(selectionSearchString)
      .on('keydown', function (e) {
        if (e.which == 40) {
          that.$selectionUl.focus();
          return false;
        }
      });
  },
  afterSelect: function () {
    this.qs1.cache();
    this.qs2.cache();
  },
  afterDeselect: function () {
    this.qs1.cache();
    this.qs2.cache();
  }
});



$('#crear-agrupamiento').click(function () {
  if ($("#agrupacion-nombre").val()) {
    var vector = new Array(),
      i = 0;
    $('.ms-elem-selection:visible').each(function () {
      vector[i] = $(this).attr("id_bd");
      i = i + 1
    })
    agrupacion_nombre = $('#agrupacion-nombre').val()

    reparticion = $("#cod_muni").attr("repart-id");
    data = {
      'vector[]': JSON.stringify(vector),
      'agrupacion_nombre': agrupacion_nombre,
      'reparticion': reparticion,
      'csrfmiddlewaretoken': csrftoken
    }

    $.ajax({
      data: data,
      url: '/aumentos/crear_agrupamiento/',
      type: 'GET',
      success: function (data) {
        var option = new Option(data['agrupamiento'], data['agrupamiento']);
        $(option).html(data['agrupamiento_nombre']);
        $("#cargo-agrupamiento").append(option);
        $('#siliq_modal_windows').modal('hide');
      },
      error: function (data) {
        alert('Error en sessionadd')
      }
    })

  } else {
    alert("Ingrese un nombre para el agrupamiento")
  }
});


$('#modificar-agrupamiento-save').click(function () {
  if ($("#agrupacion-nombre").val()) {
    var vector = new Array(),
      i = 0;
    $('.ms-elem-selection:visible').each(function () {
      vector[i] = $(this).attr("id_bd");
      i = i + 1
    })
    agrupacion = $("#modificar-agrupamiento-save").attr("agrup-id");
    agrupacion_nombre = $('#agrupacion-nombre').val()
    reparticion = $("#modificar-agrupamiento-save").attr("muni-id");
    movimiento = $("#mov-id").attr("aumento-id");
    data = {
      'vector[]': JSON.stringify(vector),
      'agrupacion': agrupacion,
      'reparticion': reparticion,
      'agrupacion_nombre': agrupacion_nombre,
      'movimiento': movimiento,
      'csrfmiddlewaretoken': csrftoken
    }

    $.ajax({
      data: data,
      url: '/aumentos/modificar_agrupamiento_save/',
      type: 'POST',
      success: function (data) {
        $('#siliq_modal_windows').modal('hide');
        $("option[value=" + agrupacion + "]", $("#cargo-agrupamiento"))[0].remove()
        var option = new Option(data['agrupamiento'], data['agrupamiento']);
        $(option).html(data['agrupamiento_nombre']);
        $("#cargo-agrupamiento").append(option);
        load_aumentos()
      },
      error: function (data) {
        alert('Error en sessionadd')
      }
    })
  } else {
    alert("Ingrese un nombre para el agrupamiento")
  }
});

$(document).ready(function () {
  $("#cancelar-agrupamiento").click(function (e) {
    e.preventDefault();
    $('#siliq_modal_windows').modal('hide');
  });
});