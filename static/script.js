$(document).ready(function() {
    var highestCol = Math.min($('#intro-img1').height(),$('#intro-img2').height());
    $('.intro-img-container1').height(highestCol);
    highestCol = Math.min($('#intro-img3').height(),$('#intro-img4').height());
    $('.intro-img-container2').height(highestCol);
});

var margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = 600 - margin.left - margin.right,
    height = 600 - margin.top - margin.bottom;

var Graph = function(data, arg1, arg2) {
    var arg1 = arg1;
    var arg2 = arg2;

    var get_label = function(param) {
        if (param == 'nu') return 'Naver user';
        else if (param == 'nc') return 'Naver critic';
        else if (param == 'cu') return 'Cine21 user';
        else if (param == 'cc') return 'Cine21 critic';
        else if (param == 'iu') return 'IMDb user';
        else if (param == 'ic') return 'IMDb critic';
    }

    var get_data = function(d, param) {
        if (param == 'nu') return d.naver_user / 10;
        else if (param == 'nc') return d.naver_critic / 10;
        else if (param == 'cu') return d.cine_user;
        else if (param == 'cc') return d.cine_critic;
        else if (param == 'iu') return d.imdb_user;
        else if (param == 'ic') return d.metacritic * 10;
    }

    var xValue = function(d) { return get_data(d, arg1); },
        xScale = d3.scale.linear().range([0, width]),
        xMap = function(d) { return xScale(xValue(d));},
        xAxis = d3.svg.axis().scale(xScale).orient("bottom");

    var yValue = function(d) { return get_data(d, arg2);},
        yScale = d3.scale.linear().range([height, 0]),
        yMap = function(d) { return yScale(yValue(d));},
        yAxis = d3.svg.axis().scale(yScale).orient("left");

    var cValue = function(d) {
            var d1 = get_data(d, arg1);
            var d2 = get_data(d, arg2);
            return Math.floor(Math.abs(d1-d2));
        },
        color = d3.scale.category10();

    var svg = d3.select("#graph").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var tooltip = d3.select("#graph").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

    xScale.domain([0, 10]);
    yScale.domain([0, 10]);

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .append("text")
        .attr("class", "label")
        .attr("x", width)
        .attr("y", -6)
        .style("text-anchor", "end")
        .text(get_label(arg1));

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("class", "label")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(get_label(arg2));

    svg.selectAll(".dot")
        .data(data)
        .enter().append("circle")
        .attr("class", "dot")
        .attr("r", 5.5)
        .attr("cx", xMap)
        .attr("cy", yMap)
        .attr('opacity', 0.5)
        .style("fill", function(d) { return color(cValue(d));}) 
        .attr("visibility", function(d,i){
            if(get_data(d, arg1) <= 0 || get_data(d, arg2) <= 0 ) return "hidden";
        })
    .on("mouseover", function(d) {
        tooltip.transition()
        .duration(100)
        .style("opacity", 1.0);
    tooltip.html(d.title + "<br/> (" + xValue(d) 
        + ", " + yValue(d) + ")")
        .style("left", (d3.event.pageX + 5) + "px")
        .style("top", (d3.event.pageY - 28 - $(".splash-container").height()) + "px");
    })
    .on("mouseout", function(d) {
        tooltip.transition()
        .duration(800)
        .style("opacity", 0);
    });
};

var movies;
d3.csv("/carpedm20/critic/static/movie.csv", function(error, data) {
    movies = data;

    Graph(data, 'nu', 'nc');
    Graph(data, 'cu', 'cc');
    Graph(data, 'iu', 'ic');
    Graph(data, 'nc', 'ic');
});
