$(document).ready(function() {
    var highestCol = Math.min($('#intro-img1').height(),$('#intro-img2').height());
    $('.intro-img-container').height(highestCol);
});

var margin = {top: 30, right: 20, bottom: 30, left: 50},
    width = 600 - margin.left - margin.right,
    height = 600 - margin.top - margin.bottom;
 
// Parse the date / time
var parseDate = d3.time.format("%d-%b-%y").parse;
 
// Set the ranges
var x = d3.time.scale().range([0, width]);
var y = d3.scale.linear().range([height, 0]);
 
// Define the axes
var xAxis = d3.svg.axis().scale(x)
    .orient("bottom").ticks(5);
 
var yAxis = d3.svg.axis().scale(y)
    .orient("left").ticks(5);
 
var valueline = d3.svg.line()
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.close); });
    
var svg = d3.select("#graph")
    .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
    .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var movies;

var margin = {top: 30, right: 20, bottom: 10, left: 50},
    width = 600 - margin.left - margin.right,
    height = 600 - margin.top - margin.bottom;
 
// Parse the date / time
var parseDate = d3.time.format("%d-%b-%y").parse;
 
// Set the ranges
var x = d3.time.scale().range([0, width]);
var y = d3.scale.linear().range([height, 0]);
 
// Define the axes
var xAxis = d3.svg.axis().scale(x)
    .orient("bottom").ticks(5);
 
var yAxis = d3.svg.axis().scale(y)
    .orient("left").ticks(5);

var xValue = function(d) { return d.naver_user;}, // data -> value
    xScale = d3.scale.linear().range([0, width]), // value -> display
    xMap = function(d) { return xScale(xValue(d));}, // data -> display
    xAxis = d3.svg.axis().scale(xScale).orient("bottom");

// setup y
var yValue = function(d) { return d.naver_critic;}, // data -> value
    yScale = d3.scale.linear().range([height, 0]), // value -> display
    yMap = function(d) { return yScale(yValue(d));}, // data -> display
    yAxis = d3.svg.axis().scale(yScale).orient("left");

var tooltip = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

d3.csv("/carpedm20/critic/static/movie.csv", function(error, data) {
    movies = data;

    pop_list = [];
    for (var idx in movies) {
        var movie = movies[idx];

        movie.time = parseDate(movie.time);

        if (movie.naver_user == -1 || movie.naver_critic == -1) {
            //console.log(idx);
            pop_list.push(idx);
        }
    }

    for (var idx in pop_list) {
        movies.pop(pop_list[idx]);
    }

    xScale.domain(d3.extent(movies, function(d) { return d.naver_user; }));
    yScale.domain([0, d3.max(movies, function(d) { return d.naver_critic; })]);
 
    // Add the valueline path.
    svg.selectAll(".dot")
       .data(movies)
      .enter().append("circle")
       .attr("class", "dot")
       .attr("r", 3.5)
       .attr("cx", xMap)
       .attr("cy", yMap)
       .style("fill", function(d) {
          return 'black';
       })
      .on("mouseover", function(d) {
          tooltip.transition()
               .duration(200)
               .style("opacity", .9);
          tooltip.html(d.title + "<br/> (" + xValue(d) 
            + ", " + yValue(d) + ")")
               .style("left", (d3.event.pageX + 5) + "px")
               .style("top", (d3.event.pageY - 28) + "px");
      })
      .on("click", function(d) {
         window.open('http://movie.naver.com/movie/bi/mi/basic.nhn?code='+d.naver,'_blank');
      });
 
    // Add the X Axis
    svg.append("g")     
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);
 
    // Add the Y Axis
    svg.append("g")     
        .attr("class", "y axis")
        .call(yAxis);
 
});
