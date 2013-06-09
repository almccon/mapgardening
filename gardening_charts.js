
  var columnInfo = {
    "uid": { "text": "User ID", "show": false, "scale": "linear"},
    "username": { "text": "Username", "show": false, "scale": "linear"},
    "count": { "text": "Total edited nodes", "show": true, "scale": "log"},
    "v1count": { "text": "Version 1 edits", "show": true, "scale": "log"},
    "blankcount": { "text": "Blank spot edits", "show": true, "scale": "log"},
    "firstedit": { "text": "First edit date", "show": true, "scale": "time"},
    "firsteditv1": { "text": "First v1 edit date", "show": true, "scale": "time"},
    "firsteditblank": { "text": "First blank spot edit date", "show": true, "scale": "time"},
    "mean_date": { "text": "Mean edit date", "show": true, "scale": "time"},
    "mean_date_weighted": { "text": "Weighted mean edit date", "show": true, "scale": "time"},
    "days_active": { "text": "Number of days active", "show": true, "scale": "log"}
  };
  
  var indexX = 'count'; // The currently active column for the X axis
  var indexY = 'blankcount'; // The currently active column for the Y axis
  var indexR = 'days_active'; // The currently active column for the radius
  
function createScatter(data) {
  
  // Use mbostock's margin convention from http://bl.ocks.org/mbostock/3019563
  var margin = {top: 20, right: 50, bottom: 40, left: 50};
      
  //Width and height
  var w = 500 - margin.left - margin.right,
      h = 500 - margin.top - margin.bottom;
          
  //For displaying numbers in the axes
  var numberFormat = d3.format(",f");
 
  var dateFormat = d3.time.format("%Y-%m-%d"); 
  
  var xScaleLog = d3.scale.log();
  var yScaleLog = d3.scale.log();
  
  var xScaleTime = d3.time.scale();
  var yScaleTime = d3.time.scale();

  var xScaleLinear = d3.scale.linear();
  var yScaleLinear = d3.scale.linear();

  var xAxis = d3.svg.axis();

  var yAxis = d3.svg.axis();

  var rScale = d3.scale.sqrt();
  
  var minima = {};
  var maxima = {};
  
  var svg;
  
  function chart(selection) {
    selection.each(function(data) {
      
      dataset.forEach(function(d) {
        // convert strings to numbers and dates
        d.count = +d.count;
        d.v1count = +d.v1count;
        d.blankcount = +d.blankcount;
        d.days_active = +d.days_active;
        d.uid = +d.uid;
        d.firstedit = dateFormat.parse(d.firstedit);
        d.firsteditv1 = dateFormat.parse(d.firsteditv1);
        d.firsteditblank = dateFormat.parse(d.firsteditblank);
        d.mean_date = dateFormat.parse(d.mean_date);
        d.mean_date_weighted = dateFormat.parse(d.mean_date_weighted);
      });

      var keys = d3.keys(data[0]);
      for (var i = 0; i < keys.length; i++) {
        minima[keys[i]] = d3.min(data, function(d) { return d[keys[i]]; });
        maxima[keys[i]] = d3.max(data, function(d) { return d[keys[i]]; });
      }
        
        xScaleLog 
            .domain([1, maxima[indexX]])
            .range([0, w]);

        yScaleLog
          .domain([1, maxima[indexY]])
          .range([h, 0]); // Inverted so greater values are at top
          
        xScaleTime
          .domain([minima[indexX],maxima[indexX]])
          .range([0, w]);
          
        yScaleTime
          .domain([minima[indexY],maxima[indexY]])
          .range([h, 0]); // Inverted so greater values are at top

        xScaleLinear
          .domain([0, maxima[indexX]])
          .range([0, w]);
          
        yScaleLinear
          .domain([0, maxima[indexY]])
          .range([h, 0]); // Inverted so greater values are at top

        xAxis
          .scale(xScaleLog) // Just for the initial state
          .orient("bottom")
          .ticks(5, numberFormat); // Show only 5 divisions
          // Setting ticks also sets tickFormat

        yAxis
          .scale(yScaleLog) // Just for the initial state
          .orient("left")
          .ticks(5, numberFormat); // Show only 5 divisions
          // Setting ticks also sets tickFormat

        rScale
          .domain([0, maxima[indexR]])
          .range([1, 10]);

      // Append the SVG element. In the html file we create a div, 
      // bind the data, then use call() to call this function.
      // See: http://bost.ocks.org/mike/chart/
      svg = d3.select(this).append("svg")
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
     
      // Create the menus to control X and Y 
      var controls = d3.select("body")
          .append("div")
          .attr("id", "controls");
      
      controls.append("div")
        .html("X axis ")
        .append("select")
          .attr("label", "xaxis")
          .attr("id", "xaxis")
          .selectAll("option")
          .data(d3.entries(columnInfo)) // Use entries because columnInfo is an associative array
          .enter().append("option")
            .attr("value", function(d) { return d.key; }) // d.key comes from d3.entries
            .text(function(d) { return d.value.text; })   // d.value comes from d3.entries
            .each(function(d) {
              if (d.key == indexX) d3.select(this).attr("selected", "yes");
            });
        
      d3.select("#xaxis")
        .on("change", function() { 
          updateX(this.options[this.selectedIndex].value) 
        });

      controls.append("div")
        .html("Y axis ")
        .append("select")
          .attr("label", "yaxis")
          .attr("id", "yaxis")
          .selectAll("option")
          .data(d3.entries(columnInfo)) // Use entries because columnInfo is an associative array
          .enter().append("option")
            .attr("value", function(d) { return d.key; }) // d.key comes from d3.entries
            .text(function(d) { return d.value.text; })   // d.value comes from d3.entries
            .each(function(d) {
              if (d.key == indexY) d3.select(this).attr("selected", "yes");
            });
        
      d3.select("#yaxis")
        .on("change", function() { updateY(this.options[this.selectedIndex].value) }); 
   
      // Add the circles to the plot 
      svg.selectAll("circle")
          .data(data)
        .enter().append("circle")
          .attr({
            cx : function(d) { return xScaleLog(d[indexX] + 1); },
            cy : function(d) { return yScaleLog(d[indexY] + 1); },
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
            //	.style("left", xScaleLog(d.count + 1) + "px")
            //	.style("top", yScaleLog(d.blankcount + 1) + "px");
            if (columnInfo[indexX].scale == "time")
              x_value_string = dateFormat(d[indexX]);
            else
              x_value_string = d[indexX];
            if (columnInfo[indexY].scale == "time")
              y_value_string = dateFormat(d[indexY]);
            else
              y_value_string = d[indexY];
            info_div.html("User:&nbsp;" + d.username + "<br>" + columnInfo[indexX].text + ":&nbsp;" + x_value_string + "<br>" + columnInfo[indexY].text + ":&nbsp;" + y_value_string + "<br>" + columnInfo[indexR].text + ":&nbsp;" + d[indexR]);
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
        .attr("id", "xAxisLabel")
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
        .attr("id", "yAxisLabel")
        .attr("transform", "translate(" + 0 + "," + (h / 2) + ")rotate(-90)")
        // See http://stackoverflow.com/questions/11252753/rotate-x-axis-text-in-d3
        .attr("dy", "-3em")
        .style("text-anchor", "middle")
        .text(columnInfo[indexY].text);
    
      // TODO: add legend for symbol size
    });

  }
  
  function updateX(newX) {
    indexX = newX;
    if (columnInfo[indexX].scale == "log") xScale = xScaleLog.domain([1, maxima[indexX]]);
    else if (columnInfo[indexX].scale == "time") xScale = xScaleTime.domain([minima[indexX], maxima[indexX]]);
    else xScale = xScaleLinear.domain([0, maxima[indexX]]);
    svg.selectAll("circle")
      .transition()
      .ease("linear")
      .duration(1000)
      .attr("cx", function(d) { 
        if (columnInfo[indexX].scale == "log") 
          return xScale(d[indexX] + 1); 
        else 
          return xScale(d[indexX] || 0); 
      }); 
    xAxis.scale(xScale);
    xa.call(xAxis);
    xa.select("#xAxisLabel")
      .text(columnInfo[indexX].text);
  };
  
  function updateY(newY) {
    indexY = newY;
    if (columnInfo[indexY].scale == "log") yScale = yScaleLog.domain([1, maxima[indexY]]);
    else if (columnInfo[indexY].scale == "time") yScale = yScaleTime.domain([minima[indexY], maxima[indexY]]);
    else yScale = yScaleLinear.domain([0, maxima[indexY]]);
    svg.selectAll("circle")
      .transition()
      .ease("linear")
      .duration(1000)
      .attr("cy", function(d) { 
        if (columnInfo[indexY].scale == "log") 
          return yScale(d[indexY] + 1); 
        else
          return yScale(d[indexY] || 0); 
      }); 
    yAxis.scale(yScale);
    ya.call(yAxis);
    ya.select("#yAxisLabel")
      .text(columnInfo[indexY].text);
  };
  
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
