
var bardata = [];
var n = 3;
var m = 143;
var barchart_color_selector = function() {};

function load_barchart(parties, total_width, total_height) {
    d3.json("preprocessed-data/bars.json", function(json) {
	var barchart_data_array = [];
	var barchart_colors = [];
	if (parties.indexOf(0) != -1) {
	    barchart_data_array.push(json["Zerg"]);
	    barchart_colors.push("#B2182B");
	}
	if (parties.indexOf(1) != -1) {
	    barchart_data_array.push(json["Protoss"]);
	    barchart_colors.push("#4393c3");
	}
	if (parties.indexOf(2) != -1) {
	    barchart_data_array.push(json["Terran"]);
	    barchart_colors.push("#FCB514");
	}
	bardata = d3.layout.stack()(barchart_data_array);

	barchart_color_selector = function(i) { return barchart_colors[i]; };

	postprocess_bars(total_width, total_height);
    });
}

load_barchart([0,1,2], 900, 335);

/*
  var n = 4, // number of layers
  m = 64, // number of samples per layer
  data = d3.layout.stack()(stream_layers(n, m, .1)),
  color = d3.interpolateRgb("#aad", "#556");
*/


function postprocess_bars(total_width, total_height) {
    $("#barchart").empty();
    var p = 20,
    w = total_width,
    h = total_height,
    mx = m,
    my = d3.max(bardata, function(d) {
	return d3.max(d, function(d) {
            return d.y0 + d.y;
	});
    }),
    mz = d3.max(bardata, function(d) {
	return d3.max(d, function(d) {
            return d.y;
	});
    }),
    x = function(d) { return d.x * w / mx; },
    y0 = function(d) { return h - d.y0 * h / my; },
    y1 = function(d) { return h - (d.y + d.y0) * h / my; },
    y2 = function(d) { return d.y * h / mz; }; // or `my` to not rescale

    var maximum_x = 0;
    var maximum_value = 0;
    
    for (var i = 0; i < 53; i++) {
	var v = 0;
	for (var pt in bardata) {
	    v += bardata[pt][i].y;
	}
	if (v > maximum_value) {
	    maximum_x = i;
	    maximum_value = v;
	}
    }

    var vis = d3.select("#barchart")
	.append("svg")
	.attr("width", w)
	.attr("height", h+p);

    var layers = vis.selectAll("g.layer")
	.data(bardata)
	.enter().append("g")
	.style("fill", function(d, i) { return barchart_color_selector(i); })
	.attr("class", "layer");

    var bars = layers.selectAll("g.bar")
	.data(function(d) { return d; })
	.enter().append("g")
	.attr("class", "bar")
	.attr("transform", function(d) { return "translate(" + x(d) + ",0)"; })
    
    bars.append("title").text(function(d) { return Math.round(d.y); });

    bars.append("rect")
	.attr("width", x({x: .9}))
	.attr("x", 0)
	.attr("y", h)
	.attr("height", 0)
	.transition()
	.delay(function(d, i) { return i * 10; })
	.attr("y", y1)
	.attr("height", function(d) { return y0(d) - y1(d); })
	.attr("bar_value", function(d) { return Math.round(d.y); })
	.attr("week", function(d) { return d.x; })
	.attr("party", function(d) { return d.p; } );
    

    /*    var labels = vis.selectAll("text.label")
	  .data(bardata[0])
	  .enter().append("text")
	  .attr("class", "label")
	  .attr("x", x)
	  .attr("y", h + 6)
	  .attr("dx", x({x: .45}))
	  .attr("dy", ".71em")
	  .attr("text-anchor", "middle")
	  .text(function(d, i) { return (i+1)%10; });
    */
    vis.append("text")
	.attr("class", "goobly")
	.attr("x", maximum_x*w/mx - 70)
	.attr("y", 0)
	.attr("text-anchor", "middle")
	.attr("dx", ".45em")
	.attr("dy", ".71em")
	.attr("font-size", "1.3em")
	.attr("style", "font-weight:bold; fill: green;")
	.text(my);
    
    vis.append("line")
	.attr("x1", 0)
	.attr("x2", w - x({x: .1}))
	.attr("y1", h)
	.attr("y2", h);

    function transitionGroup() {
	var group = d3.selectAll("#barchart");

	group.select("#group")
	    .attr("class", "first active");

	group.select("#stack")
	    .attr("class", "last");

	group.selectAll("g.layer rect")
	    .transition()
	    .duration(500)
	    .delay(function(d, i) { return (i % m) * 10; })
	    .attr("x", function(d, i) { return x({x: .9 * ~~(i / m) / n}); })
	    .attr("width", x({x: .9 / n}))
	    .each("end", transitionEnd);

	function transitionEnd() {
	    d3.select(this)
		.transition()
		.duration(500)
		.attr("y", function(d) { return h - y2(d); })
		.attr("height", y2);
	}
    }

    function transitionStack() {
	var stack = d3.select("#barchart");

	stack.select("#group")
	    .attr("class", "first");

	stack.select("#stack")
	    .attr("class", "last active");

	stack.selectAll("g.layer rect")
	    .transition()
	    .duration(500)
	    .delay(function(d, i) { return (i % m) * 10; })
	    .attr("y", y1)
	    .attr("height", function(d) { return y0(d) - y1(d); })
	    .each("end", transitionEnd);

	function transitionEnd() {
	    d3.select(this)
		.transition()
		.duration(500)
		.attr("x", 0)
		.attr("width", x({x: .9}));
	}
    }

    window.barTransitions = {
	"transitionStack" : transitionStack,
	"transitionGroup" : transitionGroup
    };

    set_gbar_hover();
}