
var columnInfo = {
  "uid": { "index": "uid", "text": "User ID", "show": false, "scale": "linear"},
  "username": { "index": "username", "text": "Username", "show": false, "scale": "linear"},
  "count-linear": { "index": "count", "text": "Total edited nodes (linear scale)", "show": true, "scale": "linear"},
  "count-log": { "index": "count", "text": "Total edited nodes (log scale)", "show": true, "scale": "log"},
  "v1count-linear": { "index": "v1count", "text": "Nodes created (linear scale)", "show": true, "scale": "linear"},
  "v1count-log": { "index": "v1count", "text": "Nodes created (log scale)", "show": true, "scale": "log"},
  "v2count-linear": { "index": "v2count", "text": "Nodes modified (linear scale)", "show": true, "scale": "linear"},
  "v2count-log": { "index": "v2count", "text": "Nodes modified (log scale)", "show": true, "scale": "log"},
  "blankspot-nodes-linear": { "index": "blankcount", "text": "Blankspot nodes (linear scale)", "show": true, "scale": "linear"},
  "blankspot-nodes-log": { "index": "blankcount", "text": "Blankspot nodes (log scale)", "show": true, "scale": "log"},
  "count_area-linear": { "index": "count_area", "text": "Total edited nodes per sq km (linear scale)", "show": true, "scale": "linear"},
  "count_area-log": { "index": "count_area", "text": "Total edited nodes per sq km (log scale)", "show": true, "scale": "log"},
  "v1count_area-linear": { "index": "v1count_area", "text": "Nodes created per sq km (linear scale)", "show": true, "scale": "linear"},
  "v1count_area-log": { "index": "v1count_area", "text": "Nodes created per sq km (log scale)", "show": true, "scale": "log"},
  "v2count_area-linear": { "index": "v2count_area", "text": "Nodes modified per sq km (linear scale)", "show": true, "scale": "linear"},
  "v2count_area-log": { "index": "v2count_area", "text": "Nodes modified per sq km (log scale)", "show": true, "scale": "log"},
  "blankspot-nodes-area-linear": { "index": "blankcount_area", "text": "Blankspot nodes per sq km (linear scale)", "show": true, "scale": "linear"},
  "blankspot-nodes-area-log": { "index": "blankcount_area", "text": "Blankspot nodes per sq km (log scale)", "show": true, "scale": "log"},
  "count_pop-linear": { "index": "count_pop", "text": "Total edited nodes per thousand inhabitants (linear scale)", "show": true, "scale": "linear"},
  "count_pop-log": { "index": "count_pop", "text": "Total edited nodes per thousand inhabitants (log scale)", "show": true, "scale": "log"},
  "v1count_pop-linear": { "index": "v1count_pop", "text": "Nodes created per thousand inhabitants (linear scale)", "show": true, "scale": "linear"},
  "v1count_pop-log": { "index": "v1count_pop", "text": "Nodes created per thousand inhabitants (log scale)", "show": true, "scale": "log"},
  "v2count_pop-linear": { "index": "v2count_pop", "text": "Nodes modified per thousand inhabitants (linear scale)", "show": true, "scale": "linear"},
  "v2count_pop-log": { "index": "v2count_pop", "text": "Nodes modified per thousand inhabitants (log scale)", "show": true, "scale": "log"},
  "blankspot-nodes-pop-linear": { "index": "blankcount_pop", "text": "Blankspot nodes per thousand inhabitants (linear scale)", "show": true, "scale": "linear"},
  "blankspot-nodes-pop-log": { "index": "blankcount_pop", "text": "Blankspot nodes per thousand inhabitants (log scale)", "show": true, "scale": "log"},
  "date": { "index": "date", "text": "Date", "show": false, "scale": "time"}
};
  //"nodes-linear": { "index": "nodes", "text": "Total edited nodes (linear scale) via userstats", "show": true, "scale": "linear"},
  //"nodes-log": { "index": "nodes", "text": "Total edited nodes (log scale) via userstats", "show": true, "scale": "log"},
  //"nodes-created-linear": { "index": "nodes_created", "text": "Nodes created (linear scale) via userstats", "show": true, "scale": "linear"},
  //"nodes-created-log": { "index": "nodes_created", "text": "Nodes created (log scale) via userstats", "show": true, "scale": "log"},
  //"nodes-current-linear": { "index": "nodes_current", "text": "Nodes currently existing (linear scale) via userstats", "show": true, "scale": "linear"},
  //"nodes-current-log": { "index": "nodes_current", "text": "Nodes currently existing (log scale) via userstats", "show": true, "scale": "log"},

var indexX = 'date'; // The currently active column for the X axis
var modeX = 'date'; // The currently active column for the X axis
var indexY = 'count'; // The currently active column for the Y axis
var modeY = 'count-log'; // The currently active column for the Y axis
var indexR = 'username'; // The currently active column for the radius
var modeR = 'username'; // The currently active column for the radius
var indexColor = 'place'; // The currently active column for the coloring
  
// Use mbostock's margin convention from http://bl.ocks.org/mbostock/3019563
var margin = {top: 20, right: 50, bottom: 40, left: 100};
      
//Width and height
var w = 1200 - margin.left - margin.right,
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

//var colorScaleOrdinal = d3.scale.ordinal();
var colorScaleOrdinal = d3.scale.category20();

var xAxis = d3.svg.axis();

var yAxis = d3.svg.axis();

var rScale = d3.scale.sqrt();

var minima = {};
var maxima = {};

var overrideY;

var blankspottotals = {};

var svg,
    xa,
    ya;

// for storing the monthly and yearly charts, as svg groups
var paths = {};

// The line drawing function, in the default state
var line = d3.svg.line()
    .x(function(d) { return xScaleTime(d[indexX]); })
    .y(function(d) { return yScaleLinear(d[indexY]); });
    //.y(function(d) { return yScaleLog(d[indexY] + 1); });

// The possible data fields
var fields = [
  "nodes",
  "nodes_created",
  "nodes_current",
  "count",
  "v1count",
  "v2count",
  "blankcount",
  "count_area",
  "v1count_area",
  "v2count_area",
  "blankcount_area",
  "count_pop",
  "v1count_pop",
  "v2count_pop",
  "blankcount_pop"
];

function createNewValue(uid, username, place, date) {
  // creates a blank data entry
  var newValue = {};
  newValue.uid = uid;
  newValue.username = username;
  newValue.place = place;
  fields.forEach(function(field) {
    newValue[field] = 0;
  });
  newValue.date = date;
  return newValue;
}

function createTimelines(data, metadata) {
  var yearlydata = {};
  data.forEach(function(d) {
    // convert strings to numbers and dates
    d.nodes = +d.nodes;
    d.nodes_created = +d.nodes_created;
    d.nodes_current = +d['cur nodes'];
    d.count = +d.count;
    d.v1count = +d.v1count;
    d.v2count = d.count - d.v1count; // technically, this is version 2 or beyond, incl v3, v4, etc.
    d.blankcount = +d.blankcount;
    d.count_area = d.count / metadata[d.place].land_area * 1000000; // per sq km
    d.v1count_area = d.v1count / metadata[d.place].land_area * 1000000; // per sq km
    d.v2count_area = d.v2count / metadata[d.place].land_area * 1000000; // per sq km
    d.blankcount_area = d.blankcount / metadata[d.place].land_area * 1000000; // per sq km
    d.count_pop = d.count / metadata[d.place].population * 1000; // per 1 thousand inhabitants
    d.v1count_pop = d.v1count / metadata[d.place].population * 1000; // per 1 thousand inhabitants
    d.v2count_pop = d.v2count / metadata[d.place].population * 1000; // per 1 thousand inhabitants
    d.blankcount_pop = d.blankcount / metadata[d.place].population * 1000; // per 1 thousand inhabitants
    d.uid = +d.uid;
    d.date = dateFormat.parse(d.year);

    // sum the blankspots for each user
    if(!(d.place in blankspottotals)) blankspottotals[d.place] = {};
    if(!(d.username in blankspottotals[d.place])) blankspottotals[d.place][d.username] = 0;
    blankspottotals[d.place][d.username] += d.blankcount;

    // create yearly totals
    if(!(d.place in yearlydata)) yearlydata[d.place] = {};
    if(!(d.username in yearlydata[d.place])) yearlydata[d.place][d.username] = {};

    var yearIndex = d.date.getFullYear();
    var firstOfYearDateObj = new Date(d.date);
    firstOfYearDateObj.setMonth(0);
    if(!(yearIndex in yearlydata[d.place][d.username])) yearlydata[d.place][d.username][yearIndex] = createNewValue(d.uid, d.username, d.place, firstOfYearDateObj);

    fields.forEach(function(field) {
      if (!(field in yearlydata[d.place][d.username][yearIndex])) yearlydata[d.place][d.username][yearIndex][field] = 0;
      yearlydata[d.place][d.username][yearIndex][field] += d[field];
    });
  });

  var dataByPlaceAndUser = d3.nest()
    .key(function(d) { return d.place + '-' + d.username;})
    //.key(function(d) { return d.uid;})
    .entries(data);

  var dataByPlaceAndUserYearly = [];
  for (var placekey in yearlydata) {
    if (yearlydata.hasOwnProperty(placekey)) {
      var place = yearlydata[placekey];
      for (var userkey in place) {
        if (place.hasOwnProperty(userkey)) {
          var user = place[userkey];
          var yearlyTotals = [];
          for (var yearkey in user) {
            if (user.hasOwnProperty(yearkey)) {
              yearlyTotals.push(user[yearkey]);
            }
          }
          // Create a data structure resembling d3.nest
          var dataObj = {};
          dataObj.key = placekey + '-' + userkey;
          dataObj.values = yearlyTotals;
          dataByPlaceAndUserYearly.push(dataObj);
        }
      }
    }
  }

  dataByPlaceAndUser.forEach(function(entry) {
    entry.values.forEach(function(d) {
      // Add zero values for date before and after each entry, if data doesn't exist
      // Works if the date cadence is one month
      var prevDate = new Date(d.date);
      prevDate.setMonth(d.date.getMonth() - 1);
      var nextDate = new Date(d.date);
      nextDate.setMonth(d.date.getMonth() + 1);
      if (entry.values.filter(function(d) { return d.date.getMonth() == prevDate.getMonth() && d.date.getFullYear() == prevDate.getFullYear(); }).length == 0) {
        entry.values.push(createNewValue(d.uid, d.username, d.place, prevDate));
      }
      if (entry.values.filter(function(d) { return d.date.getMonth() == nextDate.getMonth() && d.date.getFullYear() == nextDate.getFullYear(); }).length == 0) {
        entry.values.push(createNewValue(d.uid, d.username, d.place, nextDate));
      }
    });
  });

  dataByPlaceAndUserYearly.forEach(function(entry) {
    entry.values.forEach(function(d) {
      // Add zero values for date before and after each entry, if data doesn't exist
      // For a date cadence of one year
      var prevDate = new Date(d.date);
      prevDate.setFullYear(d.date.getFullYear() - 1);
      var nextDate = new Date(d.date);
      nextDate.setFullYear(d.date.getFullYear() + 1);
      // Don't add data for 2004 or earlier
      if (prevDate.getFullYear() > 2004 && entry.values.filter(function(d) { return d.date.getMonth() == prevDate.getMonth() && d.date.getFullYear() == prevDate.getFullYear(); }).length == 0) {
        entry.values.push(createNewValue(d.uid, d.username, d.place, prevDate));
      }
      // Don't add data for 2016 or later
      if (nextDate.getFullYear() < 2016 && entry.values.filter(function(d) { return d.date.getMonth() == nextDate.getMonth() && d.date.getFullYear() == nextDate.getFullYear(); }).length == 0) {
        entry.values.push(createNewValue(d.uid, d.username, d.place, nextDate));
      }
    });
  });


  var keys = d3.keys(data[0]);
  for (var i = 0; i < keys.length; i++) {
    minima[keys[i]] = d3.min(data, function(d) { return d[keys[i]]; });
    maxima[keys[i]] = d3.max(data, function(d) { return d[keys[i]]; });
  }

  var earliestDate = new Date(minima[indexX]);
  earliestDate.setMonth(earliestDate.getMonth() - 1);

  xScaleLog 
      .domain([1, maxima[indexX]])
      .range([0, w]);

  yScaleLog
    .domain([1, maxima[indexY]])
    .range([h, 0]); // Inverted so greater values are at top
    
  xScaleTime
    .domain([new Date("2005-01-01"),new Date("2016-01-01")])
    //.domain([earliestDate,maxima[indexX]])
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

  colorScaleOrdinal
    .domain(d3.map(data, function(d) { return d[indexColor]; }).values());
    //.range(["#af8dc3","#7fbf7b"]); // not needed if using d3.scale.category20()

  xAxis
    .scale(xScaleTime) // Just for the initial state
    .orient("bottom")
    .ticks(10, numberFormat); // Show only 5 divisions
    // Setting ticks also sets tickFormat

  yAxis
    .scale(yScaleLinear) // Just for the initial state
    .orient("left")
    .ticks(5); // Show only 5 divisions
    //.ticks(5, numberFormat); // Show only 5 divisions
    // Setting ticks also sets tickFormat

  rScale
    .domain([0, maxima[indexR]])
    .range([1, 10]);

  // Append the SVG element. In the html file we create a div, 
  // bind the data, then use call() to call this function.
  // See: http://bost.ocks.org/mike/chart/
  svg = d3.select("#chart").append("svg")
      .attr("width", w + margin.left + margin.right)
      .attr("height", h + margin.top + margin.bottom)
    .append("g")// Use mbostock's margin convention from http://bl.ocks.org/mbostock/3019563
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
  var tooltip_div = d3.select("body").append("div")
  	.attr("class", "tooltip")
  	.style("opacity", 0);

  var info_div = d3.select("body")
      .append("div")
      .attr("class", "infobox")
      .style("opacity", 0);

  var legend_div = d3.select("body")
      .append("div")
      .attr("class", "legend");

  legend_div.selectAll("div")
      .data(places) // defined in the other file
    .enter()
      .append("div")
      .style("color", function(d) { return colorScaleOrdinal(d); })
      .text(function(d) { return d; });


  // Create the menus to control X and Y 
  var controls = d3.select("body")
      .append("div")
      .attr("id", "controls");
  
/*
  controls.append("div")
    .html("X axis ")
    .append("select")
      .attr("label", "xaxis")
      .attr("id", "xaxis")
      .selectAll("option")
      // Use entries because columnInfo is an associative array.
      // Use filter to only include entries where d.value.show == true
      .data(d3.entries(columnInfo).filter(function(d) { return d.value.show; }))
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
*/

  controls.append("div")
    .html("Y axis ")
    .append("select")
      .attr("label", "yaxis")
      .attr("id", "yaxis")
      .selectAll("option")
      // Use entries because columnInfo is an associative array.
      // Use filter to only include entries where d.value.show == true
      .data(d3.entries(columnInfo).filter(function(d) { return d.value.show; }))
      .enter().append("option")
        .attr("value", function(d) { return d.key; }) // d.key comes from d3.entries
        .text(function(d) { return d.value.text; })   // d.value comes from d3.entries
        .each(function(d) {
          if (d.key == indexY) d3.select(this).attr("selected", "yes");
        });
    
  d3.select("#yaxis")
    .on("change", function() { updateY(this.options[this.selectedIndex].value) }); 
  

  // Add radio buttons for "yearly" or "monthly" mode
  var modes = ["yearly", "monthly"];
  controls.append("div")
    .selectAll("label")
    .data(modes)
    .enter()
    .append("label")
    .text(function(d) { return d;})
    .insert("input")
    .attr("type", "radio")
    .attr("name", "mode")
    .attr("value", function(d, i) { return i;})
    .property("checked", function(d, i) { return i == 0; /* first one starts checked */ })
    .on("change", function() {
      updateCadence(modes[this.value]);
    });

  paths["yearly"] = svg.append("g").classed("yearly", true);
  paths["monthly"] = svg.append("g").classed("monthly", true).style("display", "none");

  // Add the lines to the plot 
  chartifyData(dataByPlaceAndUserYearly,paths["yearly"]);
  chartifyData(dataByPlaceAndUser,paths["monthly"]);

  function chartifyData(data, svg) {
    data
    //.filter(function(d) { return d.key.match(/vancouver-/);}) // Match user name = starts with place
    //.filter(function(d) { return d.key.match(/tirana-/);}) // Match user name = starts with place
    //.filter(function(d) { return d.key.match(/london-/);}) // Match user name = starts with place
    .filter(function(d) { return d.key.match(/-total$/);}) // Match user name = total
    .sort(function(a,b) { if (a.values.length < b.values.length) return 1; if (a.values.length > b.values.length) return -1; return 0; })
    .forEach(function(d) {
      //console.log(d.values[0].username, d.values[0].place);

    svg.append("path")
      //.datum(data.filter(function(d) { return d.username == "total";}))
      .datum(d.values.filter(function(d) { return d.date.getFullYear() < 2016; }).sort(function(a,b) { if (a.date > b.date) return 1; if (a.date < b.date) return -1; return 0; }))
      .attr("class", "lineclass")
      .attr("d", line)
      .attr("fill", "none")
      .attr("fill-opacity", 0)
      .attr("stroke-width", 2)
      .attr("stroke-opacity", function(d) { return d[0].username == "total" ? 0.8 : 0.1 + (d.length * .005) }) // longer arrays (active more months) are more opaque
      // If user has blankspots (and is not "total", color them red
      .attr("stroke", function(d) { return (d[0].username != "total" && blankspottotals[d[0].place][d[0].username]) ? "red" : colorScaleOrdinal(d[0]['place']); })
      // Add tooltips on mouseover
      // http://www.d3noob.org/2013/01/adding-tooltips-to-d3js-graph.html
      .on("mouseover", function(d) {
        d3.select(this).attr("stroke","black")
          .attr("stroke-opacity", 0.8);

        //console.log(d[0].uid, d[0].username, d[0].place);
/*
        tooltip_div.transition()
        	.duration(200)
        	.style("opacity", .9);
*/
        info_div.transition().duration(200).style("opacity", .9);
/*
        tooltip_div.html(d[0].username)
          .style("left", 100 + "px") // TODO: follow mouse
          .style("top", 100 + "px");
*/

          //.style("left", xScaleLog(d.count + 1) + "px")
          //.style("top", yScaleLog(d.blankcount + 1) + "px");

/*
        if (columnInfo[modeX].scale == "time")
          x_value_string = dateFormat(d[indexX]);
        else
          x_value_string = d[indexX];
        if (columnInfo[modeY].scale == "time")
          y_value_string = dateFormat(d[indexY]);
        else
          y_value_string = d[indexY];
*/
        info_div.html("Place:&nbsp;" + d[0].place + "<br>User:&nbsp;" + d[0].username + "<br>Blankspots:&nbsp;" + blankspottotals[d[0].place][d[0].username]);
        //info_div.html("User:&nbsp;" + d.username + "<br>" + columnInfo[modeX].text + ":&nbsp;" + x_value_string + "<br>" + columnInfo[modeY].text + ":&nbsp;" + y_value_string);

      }).on("mouseout", function(d) {
        d3.select(this).attr("stroke", function(d) { return (d[0].username != "total" && blankspottotals[d[0].place][d[0].username]) ? "red" : colorScaleOrdinal(d[0]['place']); })
          .attr("stroke-opacity", function(d) { return d[0].username == "total" ? 0.8 : 0.1 + (d.length * .005) }) // longer arrays (active more months) are more opaque
        //tooltip_div.transition()
        //	.duration(500)
        //	.style("opacity", 0);
        info_div.transition().duration(500).style("opacity", 0);
      });
    });
  }
  
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
    .text(columnInfo[modeX].text);

  // Add y axis
  ya = svg.append("g")
          .attr("class", "axis")
          .call(yAxis);

  // Add y axis label
  ya.append("text")
    .attr("class", "axis")
    .attr("id", "yAxisLabel")
    .attr("transform", "translate(" + -35 + "," + (h / 2) + ")rotate(-90)")
    // See http://stackoverflow.com/questions/11252753/rotate-x-axis-text-in-d3
    .attr("dy", "-3em")
    .style("text-anchor", "middle")
    .text(columnInfo[modeY].text);
  
  // TODO: add legend for symbol size
}

function updateX(newX) {
  modeX = newX;
  indexX = columnInfo[modeX].index;
  if (columnInfo[modeX].scale == "log") xScale = xScaleLog.domain([1, maxima[indexX]]);
  else if (columnInfo[modeX].scale == "time") xScale = xScaleTime.domain([minima[indexX], maxima[indexX]]);
  else xScale = xScaleLinear.domain([0, maxima[indexX]]);


  svg.selectAll("path")
    .transition()
    .ease("linear")
    .duration(1000)
    .attr("cx", function(d) { 
      if (columnInfo[modeX].scale == "log") 
        return xScale(d[indexX] + 1); 
      else 
        return xScale(d[indexX] || 0); 
    }); 
  xAxis.scale(xScale);
  xa.call(xAxis);
  xa.select("#xAxisLabel")
    .text(columnInfo[modeX].text);
};

function updateY(newY, maxY) {
  // maxY is a temporary override for the maximum vertical scale
  modeY = newY;
  indexY = columnInfo[modeY].index;
  var yScale;

  // Use a global override if exists. If not, use temporary override, if exists. If not, use range of data.
  var newMaxY =  overrideY ? overrideY : maxY ? maxY : maxima[indexY];
  if (columnInfo[modeY].scale == "log") yScale = yScaleLog.domain([1, newMaxY]);
  else yScale = yScaleLinear.domain([0, newMaxY]);
  //if (columnInfo[modeY].scale == "linear") yScale = yScaleLinear.domain([0, maxY ? maxY : maxima[indexY]]);
  //else yScale = yScaleLog.domain([1, maxY ? maxY : maxima[indexY]]);

  // update only the line.y() function. Or do I not even need to do this?

  line.y(function(d) { return yScale(d[indexY] + 1); });

  svg.selectAll(".lineclass")
    .transition()
    .ease("linear")
    .duration(1000)
    .attr("d", line);

  yAxis.scale(yScale);
  ya.call(yAxis);
  ya.select("#yAxisLabel")
    .text(columnInfo[modeY].text);
};

function setX(xstring) {
  modeX = xstring;
};

function setY(ystring) {
  modeY = ystring;
};

function setR(rstring) {
  modeR = rstring;
};

function updateCadence(cadence) {
  if (cadence == "yearly") {
    paths["yearly"].style("display","block");
    paths["monthly"].style("display","none");
  } else {
    paths["yearly"].style("display","none");
    paths["monthly"].style("display","block");
  }
};

function updateMaxY(maxY) {
  updateY(modeY, maxY);
}

function setOverrideY(maxY) {
  overrideY = maxY;
  updateMaxY(maxY);
}

function unsetOverrideY() {
  overrideY = undefined;
  updateMaxY();
}
