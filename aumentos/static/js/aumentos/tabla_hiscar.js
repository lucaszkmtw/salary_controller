$.ajax({
    url: '/aumentos/cargo_codigo/' + movimiento_id + "/" + nombre,
    success: function(response) {

        hiscar = JSON.parse(response.hiscar);



        if ($.fn.DataTable.isDataTable('#tabla_aumento_cargo')) {
            $('#tabla_aumento_cargo').DataTable().destroy();
        }
        $('#tabla_aumento_cargo tbody').html("");
        for (let i = 0; i < hiscar.length; i++) {
            let fila = "";
            fila += '<tr >';
            fila += '<td   ><strong> ' + hiscar[i]['fields']['periodo'] + ' </strong></td>';
            fila += '<td ><strong>' + hiscar[i]['fields']['basico'] + AgregarPorcentaje(response.basico[i]) + '</strong></td>';
            fila += '<td><strong>' + hiscar[i]['fields']['suplemento1'] + AgregarPorcentaje(response.suplemento1[i]) + '</strong> </td>';
            fila += '<td ><strong>' + hiscar[i]['fields']['suplemento2'] + AgregarPorcentaje(response.suplemento2[i]) + '</strong> </td>';
            fila += '<td ><strong>' + hiscar[i]['fields']['sumafija1'] + AgregarPorcentaje(response.sumafija1[i]) + '</strong> </td>';
            fila += '<td ><strong>' + hiscar[i]['fields']['sumafija2'] + AgregarPorcentaje(response.sumafija2[i]) + '</strong> </td>';
            fila += '<td><strong>' + hiscar[i]['fields']['sumafija3'] + AgregarPorcentaje(response.sumafija3[i]) + '</strong> </td>';
            fila += '<td ><strong> -null-</strong></td>';
            fila += '<td><strong> </td>';
            fila += '</tr>';
            $('#tabla_aumento_cargo tbody').append(fila);

        }

        $('#tabla_aumento_cargo').DataTable({
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






function AgregarPorcentaje(valor) {

    if (valor > 0) {
        var html = '&nbsp;<small class="text-blue"><i class="glyphicon glyphicon-arrow-up"></i><span>&nbsp;' + parseFloat(valor).toFixed(2) + '%</span>';
    }
    if (valor < 0) {
        var html = '&nbsp;<small class="text-red"><i class="glyphicon glyphicon-arrow-down"></i><span>&nbsp;' + parseFloat(valor).toFixed(2) + '%</span>';
    }
    if (valor == 0) {
        var html = '';

    }
    return html;
}





