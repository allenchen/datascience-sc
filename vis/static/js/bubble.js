var r = 750,
format = d3.format(",d");

function fill(text) {
    if (text == "Zerg") {
	return "#EB6841";
    } else if (text == "Protoss") {
	return "#EDC951";
    } else if (text == "Terran") {
	return "#00A0B0";
    }
}

var bubble = d3.layout.pack()
    .sort(null)
    .size([r, r]);

var vis = d3.select("#bubble_chart").append("svg")
    .attr("width", r)
    .attr("height", r)
    .attr("class", "bubble");

function randomcompare() { return 0.5 - Math.random(); }
function load_bubble(parties) {
    d3.json("preprocessed-data/top_players.json", function(json) {
	$("#bubble_chart .bubble").empty();
	var party_vis = {
	    "Republican": {},
	    "Democrat": {},
	    "Libertarian": {}
	};
	
	party_vis["Democrat"] = json["children"][0];
	party_vis["Republican"] = json["children"][1];
	party_vis["Libertarian"] = json["children"][2];

	// Shuffle the children of each of these since otherwise the data
	// looks too sorted and it's harder to tell differences

	party_vis["Democrat"]["children"] = 
	    party_vis["Democrat"]["children"].sort(randomcompare);
	party_vis["Republican"]["children"] =
	    party_vis["Republican"]["children"].sort(randomcompare);
	party_vis["Libertarian"]["children"] = 
	    party_vis["Libertarian"]["children"].sort(randomcompare);

	json["children"] = [];

	// wow this is ugly
	if (parties.indexOf(0) != -1) {
	    json["children"].push(party_vis["Republican"]);
	}
	if (parties.indexOf(1) != -1) {
	    json["children"].push(party_vis["Democrat"]);
	}
	if (parties.indexOf(2) != -1) {
	    json["children"].push(party_vis["Libertarian"]);
	}

	var node = vis.selectAll("g.node")
	    .data(bubble.nodes(classes(json))
		  .filter(function(d) { return !d.children; }))
	    .enter().append("g")
	    .attr("class", "node")
	    .attr("transform", function(d) { 
		return "translate(" + d.x + "," + d.y + ")"; });
	
	node.append("title")
	    .text(function(d) { return d.className + ": " + 
				Math.round(Math.pow(d.value, 2)); });
	
	node.append("circle")
	    .attr("r", function(d) { return d.r; })
	    .style("fill", function(d) { return fill(d.packageName); });
	
	node.append("text")
	    .attr("text-anchor", "middle")
	    .attr("dy", ".1em")
	    .text(function(d) { return d.className.substring(0, d.r / 3); });
    });
}

load_bubble([0,1,2]);

// Returns a flattened hierarchy containing all leaf nodes under the root.
function classes(root) {
    var classes = [];
    
    function recurse(name, node) {
	if (node.children) node.children.forEach(function(child) { recurse(node.name, child); });
	else classes.push({packageName: name, className: node.name, value: node.size});
    }
    
    recurse(null, root);
    return {children: classes};
}
