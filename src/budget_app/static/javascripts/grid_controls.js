// Helper methods for handling controls related to data displays

function setRedrawOnButtonGroupChange(selector, callback) {
  $('.btn-group').click(function(event) {
    $(event.target).siblings().removeClass('active');
    $(event.target).addClass('active').blur();
    callback();
    event.preventDefault();
  });
}

function getActiveButton(selector) {
  var button = $(selector+' > .btn.active')[0];
  return button==undefined ? undefined : button.id;
}

// Activar slider de años (Documentation: http://egorkhmelev.github.com/jslider/)
function initSlider(selector, years, callback, startValue, labels) {
  var mostRecentYear = Number(years[years.length-1]);
  if ( years.length > 1 ) {
    $(selector).val(startValue ? startValue : mostRecentYear);
    jQuery(selector).slider({
      from: Number(years[0]),
      // JSlider gets stuck if from==to (i.e. only one year), so workaround that #wtf
      to: mostRecentYear + 0.01,
      step: 1,
      format: { format: '####', locale: 'es' }, 
      skin: "presus",
      callback: callback
    });
  } else {
    $(selector).val(mostRecentYear).hide();
    $(selector).parent().append('<p>'+mostRecentYear+'</p>');
  }
}

function getUIState() {
  return {
    field: getActiveButton('#btn-field') == 'income' ? 'income' : 'expense',
    view: getActiveButton('#btn-field'),
    format: $('#select-format').val(),
    year: $("#year-selection").val()
  }
}

function sameUIState(a, b) {
  return a.view==b.view && a.field==b.field && a.year==b.year && a.format==b.format;
}