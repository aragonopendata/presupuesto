// See:
//   - http://bost.ocks.org/mike/map/ (intro)
//   - http://stackoverflow.com/questions/11909099/overlay-d3-paths-onto-google-maps (panning)
//   - http://bl.ocks.org/mbostock/5144735 (legend, color scheme)
//   - http://bl.ocks.org/mbostock/6320825 (legend range using quartiles)
//   - http://vis4.net/blog/posts/choropleth-maps/ (best practices on colors / categories)
//
function BudgetMap( dataGrid, 
                    years,
                    mapContainerId,
                    mapLegendId,
                    dataFilename, 
                    divisionName,
                    propertyName,
                    stats) {

  // Instance state
  var overlay,
      adminDivisions,
      geoJson,
      color,
      uiState,
      mapContainer = $(mapContainerId),
      dispatch = d3.dispatch("hover", "click"),
      mapBounds;

  // Convert given data to a more usable format (indexed by admin division name)
  var data = d3.map();
  dataGrid.map(function(d) { data.set(d.id, d); })

  // Register the map to be created on page load
  this.initializeOnLoad = function(newUIState) {
    var obj = this;
    uiState = newUIState;
    google.maps.event.addDomListener(window, 'load', function() { initialize(obj); } );
  }

  // Draw the map
  this.draw = function(newUIState, creatingMap) {
    // Do nothing before initialization
    if ( adminDivisions === undefined )
      return;

    uiState = newUIState;

    // Create a color gradient
    color = d3.scale.linear()
        .range(["#F2F294","#c2e699","#78c679","#31a354","#006837"])
        .clamp(true);
    var values = getAllAmounts(years, uiState.field, uiState.format);

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
        .tickFormat(function(d) { return format(d, uiState.format); });

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

    // Draw the admin divisions
    overlay.draw = function() {
      var path = d3.geo.path().projection(getGoogleMapProjection(this));
      var divisions = adminDivisions.selectAll("path")
          .data(geoJson.features);

      divisions.enter().append("svg:path")
                .on("mouseover", function(d){ dispatch.hover(getDivisionName(d), getAdminDivisionExpense(d)); })
                .on("click", function(d){ dispatch.click(getDivisionName(d), getAdminDivisionExpense(d)); });

      // Redraw admin divisions only if needed (after zooming basically). This saves quite a lot of time.
      var newMapBounds = this.map.getBounds().toString();
      if ( mapBounds != newMapBounds ) {
        mapBounds = newMapBounds;
        divisions.attr("d", path);
      }

      divisions
          .style("fill", function(d) { 
            aColor = color(getAdminDivisionExpense(d));
            return (aColor===undefined || aColor=='#NaNNaNNaN') ? 'grey' : aColor; 
          });
    };

    if ( !creatingMap )
      overlay.draw();
  }

  // Register events
  this.onHover = function(f) {
    dispatch.on("hover", f);
  }

  this.onClick = function(f) {
    dispatch.on("click", f);
  }


  // Create the map and do a bunch of stuff
  function initialize(obj) {
    // Map Styles:
    // - Shades of Grey (http://snazzymaps.com/style/38/shades-of-grey)
    // - Light Monochrome (http://snazzymaps.com/style/29/light-monochrome)
    var lightMono = [
      {
          "featureType": "water",
          "elementType": "all",
          "stylers": [
              {
                  "hue": "#e9ebed"
              },
              {
                  "saturation": -78
              },
              {
                  "lightness": 67
              },
              {
                  "visibility": "simplified"
              }
          ]
      },
      {
          "featureType": "landscape",
          "elementType": "all",
          "stylers": [
              {
                  "hue": "#ffffff"
              },
              {
                  "saturation": -100
              },
              {
                  "lightness": 100
              },
              {
                  "visibility": "simplified"
              }
          ]
      },
      {
          "featureType": "road",
          "elementType": "geometry",
          "stylers": [
              {
                  "hue": "#bbc0c4"
              },
              {
                  "saturation": -93
              },
              {
                  "lightness": 31
              },
              {
                  "visibility": "simplified"
              }
          ]
      },
      {
          "featureType": "poi",
          "elementType": "all",
          "stylers": [
              {
                  "hue": "#ffffff"
              },
              {
                  "saturation": -100
              },
              {
                  "lightness": 100
              },
              {
                  "visibility": "off"
              }
          ]
      },
      {
          "featureType": "road.local",
          "elementType": "geometry",
          "stylers": [
              {
                  "hue": "#e9ebed"
              },
              {
                  "saturation": -90
              },
              {
                  "lightness": -8
              },
              {
                  "visibility": "simplified"
              }
          ]
      },
      {
          "featureType": "transit",
          "elementType": "all",
          "stylers": [
              {
                  "hue": "#e9ebed"
              },
              {
                  "saturation": 10
              },
              {
                  "lightness": 69
              },
              {
                  "visibility": "on"
              }
          ]
      },
      {
          "featureType": "administrative.locality",
          "elementType": "all",
          "stylers": [
              {
                  "hue": "#2c2e33"
              },
              {
                  "saturation": 7
              },
              {
                  "lightness": 19
              },
              {
                  "visibility": "on"
              }
          ]
      },
      {
          "featureType": "road",
          "elementType": "labels",
          "stylers": [
              {
                  "hue": "#bbc0c4"
              },
              {
                  "saturation": -93
              },
              {
                  "lightness": 31
              },
              {
                  "visibility": "on"
              }
          ]
      },
      {
          "featureType": "road.arterial",
          "elementType": "labels",
          "stylers": [
              {
                  "hue": "#bbc0c4"
              },
              {
                  "saturation": -93
              },
              {
                  "lightness": -2
              },
              {
                  "visibility": "simplified"
              }
          ]
      }
    ];

    var mapOptions = {
      zoom: 8,
      center: new google.maps.LatLng(41.395, 0),
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      backgroundColor: '#ffffff',
      noClear: true,
      disableDefaultUI: false,
      keyboardShortcuts: true,
      disableDoubleClickZoom: false,
      draggable: true,
      scrollwheel: false,
      draggableCursor: 'move',
      draggingCursor: 'move',

      mapTypeControl: true,
      mapTypeControlOptions: {
        style: google.maps.MapTypeControlStyle.HORIZONTAL_MENU
        , position: google.maps.ControlPosition.TOP_LEFT
        , mapTypeIds: [google.maps.MapTypeId.SATELLITE, 'mymap']
      },

      navigationControl: true,
      streetViewControl: false,
      navigationControlOptions: {
        position: google.maps.ControlPosition.TOP_RIGHT
        , style: google.maps.NavigationControlStyle.ANDROID
      },

      zoomControl: true,
        zoomControlOptions: {
          position: google.maps.ControlPosition.TOP_LEFT
        , style: google.maps.ZoomControlStyle.SMALL
      },

      scaleControl: true,
      scaleControlOptions: {
        position: google.maps.ControlPosition.BOTTOM_LEFT
        , style: google.maps.ScaleControlStyle.DEFAULT
      }

    };

    // Create a new StyledMapType object, passing it the array of styles, 
    // as well as the name to be displayed on the map type control.
    var mymapType = new google.maps.StyledMapType(lightMono, {name: "Mapa"});
    var map = new google.maps.Map(mapContainer[0], mapOptions);
    // Associate the styled map with the MapTypeId and set it to display.
    map.mapTypes.set('mymap', mymapType);
    map.setMapTypeId('mymap');

    // Load the border data. When the data comes back, create an overlay.
    d3.json(dataFilename, function(regions) {
      addOverlay(obj, map, regions);
    });
  }

  function addOverlay(obj, map, regions) {
    overlay = new google.maps.OverlayView();

    // Create the SVG container when the overlay is added to the map.
    overlay.onAdd = function() {
      var layer = d3.select(this.getPanes().overlayLayer)
                    .append("div")
                    .attr("class", "SvgOverlay");
      var svg = layer.append("svg")
                    .attr("width", mapContainer.width())
                    .attr("height", mapContainer.height());

      adminDivisions = svg.append("g").attr("class", "AdminDivisions");
      geoJson = topojson.feature(regions, regions.objects[divisionName]);

      obj.draw(uiState, true);
    };

    // Bind our overlay to the map…
    overlay.setMap(map);
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
    return transformValue(amount, format, year, stats, d.id);
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

  // Turn the overlay projection into a d3 projection
  function getGoogleMapProjection(markerOverlay) {
    var overlayProjection = markerOverlay.getProjection();
    return function(coordinates) {
      var googleCoordinates = new google.maps.LatLng(coordinates[1], coordinates[0]);
      var pixelCoordinates = overlayProjection.fromLatLngToDivPixel(googleCoordinates);
      return [pixelCoordinates.x+4000, pixelCoordinates.y+4000];
    }
  }

  function transformValue(value, format, year, stats, entity_id) {
    if ( value === undefined )
      return undefined;

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
}