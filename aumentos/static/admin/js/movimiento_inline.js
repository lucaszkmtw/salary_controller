$(document).ready(function () {
    $(".original > p").each(function (index, element) {
        $(element).hide();
    });

});

$(window).on('load', function () {
    $(".ui-sortable > tbody > tr > td").each(function (index, element) {
        $(element).each(function (index, element) {
            $(this).css("padding-top", "8px");
        });
    });
})