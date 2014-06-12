function BudgetSankey(theFunctionalBreakdown, theEconomicBreakdown, theStats, i18n) {

  var functionalBreakdown = theFunctionalBreakdown;
  var economicBreakdown = theEconomicBreakdown;
  var stats = theStats;
  var _ = i18n;
  var maxAmountEver = 0;

  var svg;
  var sankey;
  var uiState;
  var popUp = $("div#pop-up");
  var color = d3.scale.category20();

  var transitionLength = 1000;
  var transitionDelay = 100;

  this.maxAmountEver = function(_) {
    if (!arguments.length) return maxAmountEver;
    maxAmountEver = _;
    return this;
  };

  this.getSankeyData = function(year) {
    function real(value) {
      return adjustInflation(value, stats, year);
    }

    function getNodes(breakdown, ids, field, linkGenerator) {
      var nodes = [];
      var accumulatedTotal = 0;
      var accumulatedActualTotal = 0;
      $.each(ids, function(i, v) {
        var amount = real(breakdown.sub[v] && breakdown.sub[v][field][year]);
        accumulatedTotal += amount;

        var actualAmount = real(breakdown.sub[v] && breakdown.sub[v][field]["actual_"+year]);
        accumulatedActualTotal += actualAmount;

        var label = breakdown.sub[v] && breakdown.sub[v].label;
        nodes.push( { "name": label,
                      "value": amount,
                      "budgeted": amount,
                      "actual": actualAmount,
                      "link": linkGenerator(v, label) } );
      });

      // Add an extra node for the remaining amount
      var budgetedRemainder = real(breakdown[field][year]) - accumulatedTotal;
      var actualRemainder = real(breakdown[field]["actual_"+year]) - accumulatedActualTotal;
      nodes.push( { "name": _['other'],
                    "value": budgetedRemainder,
                    "budgeted": budgetedRemainder,
                    "actual": actualRemainder,
                    "link": linkGenerator(null, null) });
      return nodes;
    }

    function getIncomeNodes() {
      // Sobre la Renta, IVA, Impuestos Especiales, Financiación Autonómica, FEAGA, Capital
      return getNodes(economicBreakdown, ['10', '21', '22', '40', '49', '11'], 'income', getIncomeArticleLink);
    }

    function getExpenseNodes() {
      // Sanidad, Educación, Agricultura, Protección Social, Deuda Pública, Infraestructuras
      return getNodes(functionalBreakdown, ['241', '242', '371', '231', '001', '351'], 'expense', getPolicyLink);
    }

    function addFlow(source, target, node) {
      result.links.push( {"source": source,
                          "target": target,
                          "value": node.value,
                          "budgeted": node.budgeted,
                          "actual": node.actual,
                          "missingData": node.missingData,
                          "link": node.link} );
    }

    function addSourceFlows(nodes, target) {
      for (var i in nodes) {
        var node_id = result.nodes.length;
        result.nodes[node_id] = nodes[i];
        addFlow(node_id, target, nodes[i]);
      }
    }

    function addTargetFlows(source, nodes) {
      for (var i in nodes) {
        var node_id = result.nodes.length;
        result.nodes[node_id] = nodes[i];
        addFlow(source, node_id, nodes[i]);
      }
    }

    // A general note about the fields for each node:
    //  - 'actual' has the execution information
    //  - 'budgeted' has the budget information
    //  - 'value' is used by the Sankey layout algorithm, and is the budget data when available
    var result = { "nodes": [], "links": [] };

    result.nodes.push({ "name": _['government'], "budgeted": real(functionalBreakdown.income[year]) });
    var government_id = result.nodes.length-1;
    addSourceFlows(getIncomeNodes(), government_id);
    addTargetFlows(government_id, getExpenseNodes());

    sankey
        .nodes(result.nodes)
        .links(result.links)
        .layout(32);

    return result;
  };

  // Visualize the data with D3
  this.draw = function(selector, newUIState) {
    uiState = newUIState;

    var margin = {top: 1, right: 1, bottom: 25, left: 1},
        width = $(selector).width() - margin.left - margin.right,
        height = ($(selector).width()/2+20) - margin.top - margin.bottom;

    var color = d3.scale.category20();

    svg = d3.select(selector).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    sankey = d3.sankey(width, height)
        .nodeWidth(2)
        .nodePadding(10)
        .size([width, height]);
    if ( maxAmountEver != 0 )
      sankey.maxAmountEver(maxAmountEver);

    var path = sankey.link();

    var budget = this.getSankeyData(uiState.year);

    var link = svg.append("g").selectAll(".link")
        .data(budget.links)
      .enter().append("path")
        .call(setupLink)
        .call(setupCallbacks);

    var executionLinks = svg.append("g").selectAll(".link-execution")
        .data(budget.links)
      .enter().append("path")
        .call(setupExecutionLink)
        .call(setupCallbacks);

    var node = svg.append("g").selectAll(".node")
        .data(budget.nodes)
      .enter().append("g")
        .attr("class", "node")
        .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

    node.append("rect")
        .call(setupNodeRect)
        .call(setupCallbacks);

    node.append("text")
        .attr("x", -6)
        .attr("dy", ".35em")
        .attr("text-anchor", "end")
        .attr("transform", null)
        .text(function(d) { return d.name; })
        .call(setupNodeText)
      .filter(function(d) { return d.x < width / 2; })
        .attr("x", 6 + sankey.nodeWidth())
        .attr("text-anchor", "start");

    // Add a basic legend. Not the most elegant implementation...
    var legend = svg.append('g').attr("transform", "translate(5,"+height+")");
    addLegendItem(legend, 0, _['budgeted'], 'legend-budget');
    addLegendItem(legend, 1, _['executed'], 'legend-execution');
    var note = svg.append('g').attr("transform", "translate(-10,"+(height+15)+")");
    addLegendItem(note, 0, _['amounts.are.real'], 'legend-note');
  };

  this.update = function(newUIState) {
    if ( uiState && uiState.year == newUIState.year )
      return; // Do nothing if the year hasn't changed. We don't care about the other fields
    uiState = newUIState;

    var newBudget = this.getSankeyData(uiState.year);

    var nodes = svg.selectAll(".node")
      .data(newBudget.nodes);

    nodes
    .transition().duration(transitionLength).delay(transitionDelay)
      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })
    .select("rect")
      .call(setupNodeRect);

    nodes.select("text")
    .transition().duration(transitionLength).delay(transitionDelay)
      .call(setupNodeText);

    svg.selectAll(".link")
      .data(newBudget.links)
    .transition().duration(transitionLength).delay(transitionDelay)
      .call(setupLink);

    svg.selectAll(".link-execution")
      .data(newBudget.links)
    .transition().duration(transitionLength).delay(transitionDelay)
      .call(setupExecutionLink);
  };

  function addLegendItem(legend, i, text, cssClass) {
    var g = legend.append('g')
      .attr("class", 'legend-item')
      .attr("transform", "translate("+i*150+",0)");
    g.append("circle")
      .attr("class", cssClass)
      .attr("r", "5");
    g.append("text")
      .attr("text-anchor", "start")
      .attr("x", 10)
      .attr("dy", ".32em")
      .text(text);
  }

  function setupLink(link) {
    link
      .attr("d", sankey.link())
      .attr("class", function(d) { return d.missingData ? "link no-data" : "link with-data"; })
      .style("stroke-width", function(d) { return Math.max(1, d.dy); });
  }

  function setupExecutionLink(link) {
    link
      .attr("d", sankey.link())
      .attr("class", function(d) { return d.missingData ? "link-execution no-data" : "link-execution with-data"; })
      .style("display", function(d) { return (d.actual || 0) ? '': 'none'; })
      .style("stroke-width", function(d) { return (d.actual || 0) / d.value * d.dy; });
  }

  function setupNodeRect(rect) {
    rect
      .attr("height", function(d) { return d.dy; })
      .attr("width", sankey.nodeWidth())
      .style("fill", function(d) { return d.color = "#666"; })
      .style("stroke", function(d) { return d3.rgb(d.color).darker(2); });
  }

  function setupNodeText(text) {
    text
      .attr("y", function(d) { return d.dy / 2; });
  }
  
  function setupCallbacks() {
    this.on("mouseover", mover)
        .on("mouseout", mout)
        .on("click", click);
  }

  function mover(d) {
    d.name ? $("#pop-up-title").html(d.name) : $("#pop-up-title").html(d.source.name + " → " + d.target.name);
    if ( d.missingData ) {
      $("#pop-up-content").html('');
    } else {  // Flow
      $("#pop-up-content").html((d.budgeted ? _['budgeted']+': '+formatAmount(d.budgeted)+'<br/>' : '') +
                                (d.actual ? _['executed']+': '+formatAmount(d.actual) : '') );
    }

    var popLeft = d3.event.pageX - popUp.width() / 2;
    var popTop = d3.event.pageY - popUp.height() - 15;
    popUp.css({"left":popLeft,"top":popTop}).show();
  }
  
  function mout(d) {
    popUp.hide();
  }

  function click(d) {
    if ( d.link )  window.location = d.link;
  }
}