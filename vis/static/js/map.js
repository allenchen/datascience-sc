var data; // loaded asynchronously

var path = d3.geo.path();

var svg = d3.select("#map_graph")
    .append("svg");

var counties = svg.append("g")
    .attr("id", "counties")
    .attr("class", "RdBu");

var states = svg.append("g")
    .attr("id", "states");

d3.json("us_states.json", function(json) {
    states.selectAll("path")
	.data(json.features)
	.enter().append("path")
	.attr("d", path);
});

d3.json("us_counties.json", function(json) {
    counties.selectAll("path")
	.data(json.features)
	.enter().append("path")
	.attr("class", data ? quantize : null)
	.attr("d", path);
});

function load_map(data_file) {
    d3.json(data_file, function(json) {
	data = json;
	counties.selectAll("path")
	    //.attr("style", fillcolor);
	    .attr("class", quantize);
    });
}

load_map("preprocessed-data/normalized_diff_donations.json");
$("#map_all_party_li").addClass("selected");

function fillcolor(d) {
    console.log(data[d.id]);
    var fillstr = "fill:rgb(" + ((1/Math.max(1, data[d.id]+1))*255) + ", " + (1/Math.max(1, data[d.id]+1)*0) + ", " + ((1 - 1/Math.max(1, data[d.id]+1))*255) + ");"; 
    console.log(fillstr);
    return fillstr;
}

function quantize(d) {
    return "q" + Math.min(8, ~~(data[d.id]*25)) + "-9";
}
