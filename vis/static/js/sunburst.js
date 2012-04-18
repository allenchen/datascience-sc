window.load_sunburst = function() {
    var w = 500,
    h = 300,
    r = Math.min(w, h) / 2;
    
    var color = function(d) {
	//console.log(d);
	return window.party_colors[window.str_to_partyid[(d.children ? d : d.parent).name]];
    };

    var vis = d3.select("#sunburst").append("svg")
	.attr("width", w)
	.attr("height", h)
	.append("g")
	.attr("transform", "translate(" + w / 2 + "," + h / 2 + ")");

    var partition = d3.layout.partition()
	.sort(null)
	.size([2 * Math.PI, r * r])
	.value(function(d) { return 1; });

    var arc = d3.svg.arc()
	.startAngle(function(d) { return d.x; })
	.endAngle(function(d) { return d.x + d.dx; })
	.innerRadius(function(d) { return Math.sqrt(d.y); })
	.outerRadius(function(d) { return Math.sqrt(d.y + d.dy); });

    d3.json("preprocessed-data/sunburst.json", function(json) {
	var path = vis.data([json]).selectAll("path")
	    .data(partition.nodes)
	    .enter().append("path")
	    .attr("display", function(d) { return d.depth ? null : "none"; }) // hide inner ring
	    .attr("d", arc)
	    .attr("fill-rule", "evenodd")
	    .style("stroke", "#fff")
	    .style("fill", function(d) { return color(d); })
	    .attr("cand_nm", function(d) { 
		if (d.depth > 1) {
		    return d.name;
		}
	    })
	    .attr("cand_amt", function(d) {
		if (d.depth > 1) {
		    return d.size; 
		}
	    })
	    .attr("class", function(d) {
		if (d.depth > 1) {
		    return "sunburst_hover";
		}
	    })
	    .each(stash);

	path
            .data(partition.value(function(d) { return d.size; }))
	    .transition()
            .duration(1500)
            .attrTween("d", arcTween);
	
	d3.select("#size").classed("active", true);
	d3.select("#count").classed("active", false);
    });

    // Stash the old values for transition.
    function stash(d) {
	d.x0 = d.x;
	d.dx0 = d.dx;
    }

    // Interpolate the arcs in data space.
    function arcTween(a) {
	var i = d3.interpolate({x: a.x0, dx: a.dx0}, a);
	return function(t) {
	    var b = i(t);
	    a.x0 = b.x;
	    a.dx0 = b.dx;
	    return arc(b);
	};
    }
}

window.load_sunburst();