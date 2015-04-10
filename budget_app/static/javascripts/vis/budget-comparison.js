function BudgetComparison(container_id, leftBreakdown, rightBreakdown, leftStats, rightStats, side) {
  var leftData = loadBreakdown(leftBreakdown, side, leftStats);
  var rightData = loadBreakdown(rightBreakdown, side, rightStats);
  var categories = getCategories(leftData, rightData);
  var formatPercent = d3.format(".2%");

  var bars = "<ul class='meters__list'> \
                  <li class='meter meter__left'> \
                    <div class='meter__legend'> \
                      <span class='meter__entity'>{{ county_left }}</span> \
                      <span class='meter__euros icon-budget'></span> \
                    </div> \
                    <div class='meter__base'> \
                      <div class='meter__bar meter__bar--entity1'></div> \
                    </div> \
                  </li> \
                  <li class='meter meter__right'> \
                    <div class='meter__base'> \
                      <div class='meter__bar meter__bar--entity2'></div> \
                    </div> \
                    <div class='meter__legend'> \
                      <span class='meter__entity'>{{ county_right }}</span> \
                      <span class='meter__euros icon-budget'></span> \
                    </div> \
                  </li> \
                </ul>";

  this.update = function(uiState) {
    var container = d3.select(container_id);
    var items = container.selectAll(".comparison__policy").data(categories)
    
    items.enter()
        .append("div")
          .attr("class", "comparison__policy")
        .call(appendTitle)
        .append("div")
          .attr("class", "meters")
          .html(bars);

    var width = $(container_id+' .meter__base').width();
    var scale = d3.scale.linear()
                  .domain([0, getMaxValue(leftData, rightData, uiState)])
                  .range([0, width]);

    var leftValues = getValues(leftData, categories, uiState);
    var rightValues = getValues(rightData, categories, uiState);

    // Note: I tried using widths in %, but didn't interpolate well
    items.select(".meter__left .meter__euros").data(leftValues)
        .text(function(d) { return d === undefined ? 'n/d' : format(d, uiState.format); });
    items.select(".meter__left .meter__bar").data(leftValues)
        .transition()
          .style("width", function(d) { return scale(d) + "px"; })
          .style("opacity", function(d) { return d === undefined ? 0 : 1; });

    items.select(".meter__right .meter__euros").data(rightValues)
        .text(function(d) { return d === undefined ? 'n/d' : format(d, uiState.format); });
    items.select(".meter__right .meter__bar").data(rightValues)
        .transition()
          .style("width", function(d) { return scale(d) + "px"; })
          .style("opacity", function(d) { return d === undefined ? 0 : 1; });
  }

  function appendTitle() {
    this.append("h2")
          .attr("class", "comparison__policy__title")
          .text(function(d) { return getCategoryTitle(d); });
  }

  // Get the max value across categories and years for both left and right data, in order
  // to scale the horizontal visualization bars.
  function getMaxValue(leftData, rightData, uiState) {
    var maxCategory = _.max(categories, function(category_id) { 
      return Math.max(  leftData.items[category_id] ? leftData.items[category_id].max[uiState.format] : 0,
                        rightData.items[category_id] ? rightData.items[category_id].max[uiState.format] : 0 );
    });
    return Math.max(  leftData.items[maxCategory] ? leftData.items[maxCategory].max[uiState.format] : 0, 
                      rightData.items[maxCategory] ? rightData.items[maxCategory].max[uiState.format] : 0 );
  }

  function getCategories(leftData, rightData) {
    var categories = _.union(_.keys(leftData.items), _.keys(rightData.items));
    var lastYear = Math.max(_.max(leftData.years), _.max(rightData.years));
    // Sort by amounts in the left for the last year. Break ties at the bottom using right amounts.
    return _.sortBy(categories, function(category_id) {
      var left = leftData.items[category_id] ? leftData.items[category_id][lastYear] : undefined;
      var right = rightData.items[category_id] ? rightData.items[category_id][lastYear] : 1;
      // Breaking ties at the bottom requires a bit of a trick (1/right), since we want big
      // right amounts first, i.e. they need to be lower numbers, without interfering with left ones.
      return (left === undefined || left == 0) ? 1/right : -left;
    });
  }

  function getCategoryTitle(id) {
    var label = leftBreakdown.sub[id] ? leftBreakdown.sub[id].label : rightBreakdown.sub[id].label;
    return label ? label : id;  // Fallback
  }

  function loadBreakdown(breakdown, field, stats) {
    var items = {};

    // Pick the right dataset for each year: execution preferred over 'just' budget
    var columns = [];
    for (var column_name in breakdown.years) {
      var year = breakdown.years[column_name];
      if ( !columns[year] || column_name.indexOf("actual_") === 0 )
        columns[year] = column_name;
    }

    // Calculate year totals, needed for percentage calculations later on
    var yearTotals = {};
    for (var year in columns) {
      var column_name = columns[year];
      yearTotals[year] = breakdown[field][column_name] || 0;
    }

    // Convert the item data to the format we need
    for (var id in breakdown.sub) {
      if ($.isEmptyObject(breakdown.sub[id][field])) continue;
      var policy = {
        id: id,
        name: breakdown.sub[id].label,
        max: {'nominal': 0, 'real': 0, 'percentage': 0, 'per_capita': 0}
      };
      for (var year in columns) {
        var column_name = columns[year];
        policy[year] = breakdown.sub[id][field][column_name] || 0;

        // Keep track of max value along time
        // Note that we're forced to track different max values, one for each 'format', since
        // real, per-capita and percentage amounts are not directly proportional to the original nominal ones
        _.keys(policy.max).forEach(function(format) {
          policy.max[format] = Math.max(policy.max[format], getValue(policy[year], format, year, stats, yearTotals));
        });
      }
      items[id] = policy;
    }

    return { 
      'items': items, 
      'years': _.keys(columns),
      'yearTotals': yearTotals,
      'stats': stats
    };
  }

  function getValues(data, categories, uiState) {
    return _.map(categories, function(category_id) {
      if ( _.contains(data.years, uiState.year) )
        return data.items[category_id] ? getValue(data.items[category_id][uiState.year], uiState.format, uiState.year, data.stats, data.yearTotals) : 0;
      else
        return undefined;
    });
  }

  function getValue(value, format, year, stats, yearTotals) {
    switch (format) {
      case "nominal":
        return value;
      case "real":
        return adjustInflation(value, stats, year);
      case "percentage":
        return value/yearTotals[year];
      case "per_capita":
        var population = getPopulationFigure(stats, year);
        return adjustInflation(value, stats, year) / population;
    }
  }

  function format(value, format) {
    switch (format) {
      case "nominal":
        return formatAmount(value);
      case "real":
        return formatAmount(value);
      case "percentage":
        return formatPercent(value).replace(".",",");
      case "per_capita":
        return formatDecimal(value/100) + " €";
    }
  }
}
