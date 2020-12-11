function BudgetMap(map, dataGrid, 
  years,
  mapContainerId,
  mapLegendId,
  dataFilename, 
  divisionName,
  propertyName,
  stats) {

  var overlay,
  adminDivisions,
  geoJson,
  color,
  uiState,
  mapContainer = $(mapContainerId),
  dispatch = d3.dispatch("hover", "click"),
  map;

  var data = d3.map();
  dataGrid.map(function(d) {
      data.set(d.key, d);
  });

  this.initializeOnLoad = function(newUIState) {
      var obj = this;
      uiState = newUIState;
      initialize(obj);
  }

  function initialize(obj) {
      //Create the map
      map = L.map("map-canvas", {
          zoomControl: false,
          dragging: false
      }).setView([41.395, 0], 8);

      //Create the base layer
      var baseMap = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiYXJhZ29ub3BlbmRhdGEiLCJhIjoiY2tiajN5NXhvMGxpcTM1cXZnbWlvNTAwcSJ9.tXrdKdItiV0ExfIqIKrGwA', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
          minZoom: 8,
          maxZoom: 8,
          id: 'mapbox/light-v10',
          tileSize: 512,
          zoomOffset: -1
      });
      baseMap.addTo(map);

      d3.json(dataFilename, function(regions) {
          addOverlay(obj, map, regions);
      });
  }

  function addOverlay(obj, map, regions) {
      //Transform geoJson file. Type GeometryCollection to Feature collection.
      geoJson = topojson.feature(regions, regions.objects[divisionName]);

      //Get all amounts values
      var values = getAllAmounts(years, uiState.field, uiState.format);
      
      //Define color scale from values.
      color = d3.scale.linear().domain(
          [d3.quantile(values, .05),
          d3.quantile(values, .3),
          d3.quantile(values, .5),
          d3.quantile(values, .7),
          d3.quantile(values, .95)])
          .range(["#F2F294","#c2e699","#78c679","#31a354","#006837"])
          .clamp(true);
      overlay = d3.select(map.getPanes().overlayPane)
          .append("div")
          .attr("class", "SvgOverlay");
      svg = overlay.append("svg")
          .attr("width", mapContainer.width())
          .attr("height", mapContainer.height());
      adminDivisions = svg.append("g").attr("class", "AdminDivisions");
      transform = d3.geo.transform({point: projectPoint});
      path = d3.geo.path().projection(transform);
      function projectPoint(x, y) {
          var point = map.latLngToLayerPoint(new L.LatLng(y, x));
          this.stream.point(point.x, point.y);
      }

      divisions = adminDivisions.selectAll("path").data(geoJson.features);
      divisions.enter().append("svg:path")
          .attr("d", path)
          .style("stroke","white")
          .style("fill", function(d){
              aColor = color(getAdminDivisionExpense(d));
              return (aColor===undefined || aColor=='#NaNNaNNaN') ? 'grey' : aColor;
          })
          .style("cursor", "pointer")
          .on("mouseover", function(d){
              dispatch.hover(getDivisionName(d), getAdminDivisionExpense(d));
          })
          .on("click", function(d){
              dispatch.click(getDivisionName(d), getAdminDivisionExpense(d));
          });

      // We use quantiles to spread out the color categories: a purely linear scale is a bad idea
      // when there are a few outliers at the top, as is the case often (f.ex. a capital city/region).
      // We could cover the whole value domain here, but cropping the extremes gives better results.
      color.domain([
          d3.quantile(values, .05),
          d3.quantile(values, .3),
          d3.quantile(values, .5),
          d3.quantile(values, .7),
          d3.quantile(values, .95)
      ]);
  
      // In the original d3.js example, the legend was drawn using the color domain items directly.
      // However, in that case the color scale was a threshold one, not linear like ours. So what
      // we're going to do is use the mid-points of the domain ranges above, which is more accurate.
      // (Ideally we'd have a gradient instead of a block of colors)
      var midPoints = [
          (color.domain()[0] + color.domain()[1]) / 2,
          (color.domain()[1] + color.domain()[2]) / 2,
          (color.domain()[2] + color.domain()[3]) / 2,
          (color.domain()[3] + color.domain()[4]) / 2
      ];
  
      // Draw the legend
      // We crop on the top to cope with outliers; otherwise tick values would pile up at the bottom.
      var y = d3.scale.linear()
          .domain([d3.quantile(values, .01), d3.quantile(values, .93)])
          .range([0, 240]);
      var yAxis = d3.svg.axis()
          .scale(y)
          .orient("right")
          .tickSize(13)
          .tickValues(midPoints)
          .tickFormat(function(d) {
              return format(d, uiState.format);
          });
  
      var g = d3.select(mapLegendId).html("").append("svg").append("g")
          .attr("transform", "translate(0,10)");
  
      g.selectAll("rect")
          .data(color.range().map(function(d, i) {
              return {
                  y0: i ? y(midPoints[i - 1]) : y.range()[0],
                  y1: i < midPoints.length ? y(midPoints[i]) : y.range()[1],
                  z: d
              };
          }))
          .enter().append("rect")
          .attr("width", 8)
          .attr("y", function(d) { return d.y0; })
          .attr("height", function(d) { return d.y1 - d.y0; })
          .style("fill", function(d) { return d.z; })
          .style("opacity", "0.5");
  
      g.call(yAxis);
  }

  function getAdminDivisionExpense(d) {
      return getAmount( data.get(getDivisionName(d)), uiState.field, uiState.format, uiState.year );
  }

  // Return a expense/income for the current year, prioritizing actual spending over budget
  function getAmount(d, field, format, year) {
      if ( d===undefined )
          return undefined;
      var data = ( field == 'expense' ) ? d&&d.expense : d&&d.income;
      var amount = data ? (data['actual_'+year] || data[year]) : undefined;
      return transformValue(amount, format, year, stats, d.key);
  }

  // Returns all values for all admin divisions, across years, for the current data format
  function getAllAmounts(years, field, format) {
      var amounts = data.values().map(function(d) { 
                      return years.map(function(year) { return getAmount(d, field, format, year); }); 
                  });
      var flattened = [].concat.apply([], amounts);
      return flattened
              .filter(function(d) { return d!==undefined; })
              .sort(function(a, b) { return a - b; });
  }

  function getDivisionName(d) {
      return d.properties[propertyName];
  }

  function transformValue(value, format, year, stats, entity_id) {
      if ( value === undefined ) {
        return undefined;
      }
      switch (format) {
        case "nominal":
          return value;
        case "real":
          return adjustInflation(value, stats, year);
        // case "percentage":
        //   return value/yearTotals[year];
        case "per_capita":
          var population = getPopulationFigure(stats, year, entity_id);
          return adjustInflation(value, stats, year) / population;
      }
  }

  function format(value, format) {
      switch (format) {
          case "nominal":
              return formatSimplifiedAmount(value);
          case "real":
              return formatSimplifiedAmount(value);
          case "percentage":
              return formatPercent(value).replace(".",",");
          case "per_capita":
              return formatDecimal(value/100, 1) + " €";
      }
  }

  this.onHover = function(f) {
      dispatch.on("hover", f);
  }

  this.onClick = function(f) {
      dispatch.on("click", f);
  }

  this.reset = function(newUIState) {
      map.remove();
      this.initializeOnLoad(newUIState);
  }

}