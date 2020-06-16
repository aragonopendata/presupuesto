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
    mapBounds;

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
        var map = L.map("map-canvas").setView([41.395, 0], 8);
        var baseMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 18,
            id: 'mapbox/streets-v11',
            tileSize: 512,
            zoomOffset: -1
        });
        baseMap.addTo(map);

        d3.json(dataFilename, function(regions) {
        addOverlay(obj, map, regions);
        });
    }

    function addOverlay(obj, map, regions) {
        geoJson = topojson.feature(regions, regions.objects[divisionName]);
        var layer = d3.select(map.getPanes().overlayPane)
            .append("div")
            .attr("class", "SvgOverlay");
        svg = layer.append("svg")
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
            .style("opacity", 0.8)
            .style("stroke","black")
            .style("fill", function(d){
                return getColour(getAdminDivisionExpense(d));
            })
            .style("cursor", "pointer")
            .on("mouseover", function(d){
                dispatch.hover(getDivisionName(d), getAdminDivisionExpense(d));
            })
            .on("click", function(d){
                dispatch.click(getDivisionName(d), getAdminDivisionExpense(d));
            });
    }

    function getColour(value) {
        result = '#grey';
        if (value >= (5.1 * 1000000)){
            result = '#F2F294';
        } else if (value >= (3.8 * 1000000)) {
            result = '#c2e699';
        } else if (value >= (2.9 * 1000000)) {
            result = '#78c679';
        } else if (value >= (2.0 * 1000000)) {
            result = '#31a354';
        } else {
            result = '#006837';
        }

        return result;
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

}