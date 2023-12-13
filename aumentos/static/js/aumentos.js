// DOCUMENT READY PAPY
$(document).ready(function() {
    $(".select2").css("width", "100%");
    $("#elegir_cargos").removeClass("col-md-5");
    $("#elegir_cargos").addClass("col-md-12");

    $(".select2").select2({
        placeholder: "Select cargo",
        allowClear: true
    });

});