$(document).ready(function() {
  toolTiper();
});

function sinAyuda(effect) {
  console.log('Sin Ayudas');
  return;
}

function toolTiper(effect) {
  $('.tooltiper').each(function() {
    var eLcontent = $(this).attr('data-tooltip'),
      eLtop = $(this).position().top,
      eLleft = $(this).position().left;
    var btnCerrar = '<button type="button" class="close" aria-label="Close" onclick="sinAyuda()"><span aria-hidden="true">&times;</span></button>'
    $(this).append('<span class="tooltip">'+btnCerrar + eLcontent + '</span>');
    var eLtw = $(this).find('.tooltip').width(),
      eLth = $(this).find('.tooltip').height();
    $(this).find('.tooltip').css({
      "top": (0 - eLth - 20) + 'px',
      "left": '-20px'
    });
  });
}
