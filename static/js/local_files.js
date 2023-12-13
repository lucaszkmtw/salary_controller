$(document).ready(function() {
    jQuery.ajax({
        url: "/local_files/",
        type: "GET",
        success: function(response) {
            for (var i = response.files.length - 1; i >= 0; i--) {
                var option = document.createElement("option");
                var select = document.getElementById("id_archivo_local");

                option.text = response.files[i];
                option.value = response.files[i];
                select.appendChild(option);
            }
        }

    });
});