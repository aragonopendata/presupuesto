function BudgetSummary(selector, breakdown, areaNames, colorScale, field, year) {

  // Group breakdown by area
  var areaAmounts = {};
  var totalAmount = 0;
  for (var i in breakdown.sub) {
    var policyAmount = breakdown.sub[i][field][year];
    if ( policyAmount != undefined ) {
      var area = i[0];
      areaAmounts[area] = (areaAmounts[area]||0) + policyAmount;
      totalAmount = totalAmount + policyAmount;
    }
  }

  // Sort areas
  var existingAreas = [];
  for (var area in areaAmounts) existingAreas.push(area);
  existingAreas.sort(function(a, b) { return areaAmounts[b] - areaAmounts[a] });

  // Render
  $(selector).empty();
  $(selector).append( '<table style="table-layout: fixed; border-collapse: separate; margin-bottom: 1em">'+
                        '<tr class="budget-summary-top"></tr>'+
                        '<tr class="budget-summary-bottom"></tr>'+
                      '</table>');
  var topRow = $(selector+" tr.budget-summary-top");
  var bottomRow = $(selector+" tr.budget-summary-bottom");

  for (var i = 0; i < existingAreas.length; i++) {
    var area = existingAreas[i];
    var percentage = 100 * areaAmounts[area] / totalAmount;
    var label = (percentage > 4 ) ? (areaNames[area]+' ('+formatDecimal(percentage, 1)+'%)') : '';
    if ( i%2 == 0 ) {
      topRow.append('<td style="width: '+percentage+
                    '%; border-bottom-style: solid; border-bottom-color: '+colorScale[Number(area)]+
                    '; border-bottom-width: 10px; vertical-align: bottom;">'+label+'</td>');
      bottomRow.append('<td></td>');
    } else {
      topRow.append('<td style="width: '+percentage+
                    '%; border-bottom-style: solid; border-bottom-color: '+colorScale[Number(area)]+
                    '; border-bottom-width: 10px; "></td>');
      bottomRow.append('<td>'+label+'</td>');
    }
  }
}
