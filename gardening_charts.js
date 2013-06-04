function createScatter(data) {
  
  // Use mbostock's margin convention from http://bl.ocks.org/mbostock/3019563
  var margin = {top: 20, right: 50, bottom: 40, left: 50};
      
  //Width and height
  var w = 500 - margin.left - margin.right,
      h = 500 - margin.top - margin.bottom;
          
  //For displaying numbers in the axes
  var numberFormat = d3.format(",f");
  
  var columnInfo = {
    'uid': { 'text': "User ID", 'log': false},
    'username': { 'text': "Username", 'log': false},
    'count': { 'text': "Total edited nodes", 'log': true},
    'blankcount': { 'text': "Blank spot edits", 'log': true},
    'v1count': { 'text': "Version 1 edits", 'log': true},
    'firstedit': { 'text': "First edit date", 'log': false},
    'firsteditv1': { 'text': "First v1 edit date", 'log': false},
    'firsteditblank': { 'text': "First blank spot edit date", 'log': false},
    'days_active': { 'text': "Number of days active", 'log': true},
    'mean_date': { 'text': "Mean edit date", 'log': false},
    'mean_date_weighted': { 'text': "Weighted mean edit date", 'log': false}
  };
  
  var indexX = 'count'; // The currently active column for the X axis
  var indexY = 'blankcount'; // The currently active column for the Y axis
  var indexR = 'days_active'; // The currently active column for the radius

  var xScale = d3.scale.log();

  var yScale = d3.scale.log();

  var xAxis = d3.svg.axis();

  var yAxis = d3.svg.axis();

  var rScale = d3.scale.sqrt();
                     
  function chart(selection) {
    selection.each(function(data) {

        xScale
          .domain([1, d3.max(data, function(d) { return d[indexX]; })])
          .range([0, w]);

        yScale
          .domain([1, d3.max(data, function(d) { return d[indexY]; })])
          .range([h, 0]); // Inverted so greater values are at top

        xAxis
          .scale(xScale)
          .orient("bottom")
          .ticks(5, numberFormat); // Show only 5 divisions
          // Setting ticks also sets tickFormat

        yAxis
          .scale(yScale)
          .orient("left")
          .ticks(5, numberFormat); // Show only 5 divisions
          // Setting ticks also sets tickFormat

        rScale
          .domain([0, d3.max(data, function(d) { return d[indexR]; })])
          .range([1, 10]);

      // Select SVG element. In the html file we create the svg, 
      // bind the data, then use call() to call this function.
      // See: http://bost.ocks.org/mike/chart/
      var svg = d3.select(this)
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
          .data(data)
        .enter().append("circle")
          .attr({
            cx : function(d) { return xScale(d[indexX] + 1); },
            cy : function(d) { return yScale(d[indexY] + 1); },
            r : function(d) { return rScale(d[indexR]); },
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
            info_div.html("User:&nbsp;" + d.username + "<br>" + columnInfo[indexX].text + ":&nbsp;" + d[indexX] + "<br>" + columnInfo[indexY].text + ":&nbsp;" + d[indexY] + "<br>" + columnInfo[indexR].text + ":&nbsp;" + d[indexR]);
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
        .text(columnInfo[indexX].text);

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
        .text(columnInfo[indexY].text);
    
      // TODO: add legend for symbol size
    });

  }
  
  chart.setX = function(xstring) {
    indexX = xstring;
    return chart;
  };

  chart.setY = function(ystring) {
    indexY = ystring;
    return chart;
  };

  chart.setR = function(rstring) {
    indexR = rstring;
    return chart;
  };

  chart.margin = function(_) {
    if (!arguments.length) return margin;
    margin = _;
    return chart;
  };

  chart.width = function(_) {
    if (!arguments.length) return width;
    width = _;
    return chart;
  };

  chart.height = function(_) {
    if (!arguments.length) return height;
    height = _;
    return chart;
  };

  return chart;
}
