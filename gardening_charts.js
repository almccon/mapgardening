function drawScatter(dataset) {
  
  // Use mbostock's margin convention from http://bl.ocks.org/mbostock/3019563
  var margin = {top: 20, right: 50, bottom: 40, left: 50};
      
  //Width and height
  var w = 500 - margin.left - margin.right,
      h = 500 - margin.top - margin.bottom;
          
  //For displaying numbers in the axes
  var numberFormat = d3.format(",f");

  var xScale = d3.scale.log()
                       .domain([1, d3.max(dataset, function(d) { return d.count; })])
                       .range([0, w]);

  var yScale = d3.scale.log()
                       .domain([1, d3.max(dataset, function(d) { return d.blankcount; })])
                       .range([h, 0]); // Inverted so greater values are at top

  var xAxis = d3.svg.axis()
                    .scale(xScale)
                    .orient("bottom")
                    .ticks(5, numberFormat); // Show only 5 divisions
                    // Setting ticks also sets tickFormat

  var yAxis = d3.svg.axis()
                    .scale(yScale)
                    .orient("left")
                    .ticks(5, numberFormat); // Show only 5 divisions
                    // Setting ticks also sets tickFormat

  var rScale = d3.scale.sqrt()
                       .domain([0, d3.max(dataset, function(d) { return d.days_active; })])
                       .range([1, 10]);

  //Create SVG element
  var svg = d3.select("body")
      .append("svg")
      .attr("width", w + margin.left + margin.right)
      .attr("height", h + margin.top + margin.bottom)
    .append("g")// Use mbostock's margin convention from http://bl.ocks.org/mbostock/3019563
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
  //var tooltip_div = d3.select("body").append("div")
  //	.attr("class", "tooltip")
  //	.style("opacity", 0);

  var info_div = d3.select("body")
      .append("div")
      .attr("class", "infobox")
      .style("opacity", 0);

  svg.selectAll("circle")
      .data(dataset)
    .enter().append("circle")
      .attr({
        cx : function(d) { return xScale(d.count + 1); },
        cy : function(d) { return yScale(d.blankcount + 1); },
        r : function(d) { return rScale(d.days_active); },
        opacity : 0.5,
        })
      // Add tooltips on mouseover
      // http://www.d3noob.org/2013/01/adding-tooltips-to-d3js-graph.html
      .on("mouseover", function(d) {
        //tooltip_div.transition()
        //	.duration(200)
        //	.style("opacity", .9);
        info_div.transition().duration(200).style("opacity", .9);
        //tooltip_div.html(d.username)
        //	.style("left", xScale(d.count + 1) + "px")
        //	.style("top", yScale(d.blankcount + 1) + "px");
        info_div.html("User:&nbsp;" + d.username + "<br>" + "Total edited nodes:&nbsp;" + d.count + "<br>" + "\"Blank spot\" edits:&nbsp;" + d.blankcount + "<br>" + "Days active:&nbsp;" + d.days_active);
      }).on("mouseout", function(d) {
        //tooltip_div.transition()
        //	.duration(500)
        //	.style("opacity", 0);
        info_div.transition().duration(500).style("opacity", 0);
      });
      
  // Add x axis
  xa = svg.append("g")
          .attr("class", "axis")
          .attr("transform", "translate(0," + h + ")")
          .call(xAxis);

  // Add x axis label
  xa.append("text")
    .attr("class", "axis")
    .attr("transform", "translate(" + (w / 2) + "," + 0 + ")")
    .attr("dy", "3em")
    .style("text-anchor", "middle")
    .text("total edited nodes");

  // Add y axis
  ya = svg.append("g")
          .attr("class", "axis")
          .call(yAxis);

  // Add y axis label
  ya.append("text")
    .attr("class", "axis")
    .attr("transform", "translate(" + 0 + "," + (h / 2) + ")rotate(-90)")
    // See http://stackoverflow.com/questions/11252753/rotate-x-axis-text-in-d3
    .attr("dy", "-3em")
    .style("text-anchor", "middle")
    .text("total blankspot edits");
}
