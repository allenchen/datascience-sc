// We should be using delegates for the click handlers, but w/e

Shadowbox.init();

window.jan1 = new Date(2011, 0, 1);
window.party_strings = {
    "0": "Zerg",
    "1": "Terran",
    "2": "Protoss"
};

window.party_named_strings = {
    "0": "Zerg",
    "1": "Terran",
    "2": "Protoss"
};

window.str_to_partyid = {
    "Zerg": 0,
    "Terran": 1,
    "Protoss": 2
}

window.party_colors = {
    "0": "#B2182B",
    "1": "#4393c3",
    "2": "#FCB514"
};

window.bar_status = {
    "stacked": true,
    "bar_width": 900,
    "bar_height": 335
};

window.boxwhisker_status = {
    "show_outliers": true
}

$(document).ready(function() {

    
    function get_checked_parties(checkboxes) {
	var checked_parties = [];
	for (party in checkboxes) {
	    if ($(checkboxes[party]).is(':checked')) {
		checked_parties.push(parseInt(party));
	    }
	}
	return checked_parties;
    }

    var bubble_party_checkboxes = [ "#bubble_checkbox_republican",
				    "#bubble_checkbox_democrat",
				    "#bubble_checkbox_libertarian" ];
    $(".bubble_checkbox").attr("checked", "checked");
    $(".bubble_checkbox").change(function(e) {
	load_bubble(get_checked_parties(bubble_party_checkboxes));
    });

    var barchart_party_checkboxes = [ "#barchart_checkbox_republican",
				      "#barchart_checkbox_democrat",
				      "#barchart_checkbox_libertarian" ];
    $(".barchart_checkbox").attr("checked", "checked");
    $(".barchart_checkbox").change(function(e) {
	load_barchart(get_checked_parties(barchart_party_checkboxes), bar_status.bar_width, bar_status.bar_height);
	if (!window.bar_status.stacked) {
	    window.bar_status.stacked = true;
	    $("#bars_stack").text("[ + ]");
	}
    });
    

    window.set_gbar_hover = function() {
	$("g.bar").hover(function() {
	    var pid = $(this).find("rect").attr("party");
	    // WHY IS THE MONTH ZERO-INDEXED IN JAVASCRIPT?
	    // -_-
	    
	    var hover_date = new Date(jan1.getTime() + 
				      parseInt($(this)
					       .find("rect")
					       .attr("week"))*1000*86400*7);
	    $("#barchart_hover_value")
		.text(parseFloat($(this).find("rect")
				     .attr("bar_value")));
	    $("#barchart_hover_text")
		.html("<span class=\"party_" + pid + "\">" + 
		      party_named_strings[pid] + "</span>");
	});
    }
    $("#bars_stack").click(function() {

	if (window.bar_status.stacked) {
	    barTransitions.transitionGroup();
	    window.bar_status.stacked = false;
	    $(this).text("[ - ]");
	} else {
	    barTransitions.transitionStack();
	    window.bar_status.stacked = true;
	    $(this).text("[ + ]");
	}
	return false;
    });

    $("#bars_expand").click(function() {
	
	Shadowbox.open({
            content:    "<div id='shadowbox_popup'></div>",
            player:     "html",
            title:      "Donations over Time",
            height:     500,
            width:      950, 
	    options:    {
		onFinish:   
		function () { 
		    $("#barchart_container").appendTo("#shadowbox_popup");
		    $(".barchart_checkbox").attr("checked", "checked");
		    bar_status.bar_width = 920;
		    bar_status.bar_height = 335;
		    load_barchart([0,1,2], bar_status.bar_width, bar_status.bar_height); 
		    $("#barchart_container").animate({ 'width': '950px' }, 1000);
		},
                overlayColor: "#000"
	    }
	});
	window.handle_bar_close = function() 
	{ 
	    
	    $("#barchart_container").appendTo("#barchart_placeholder"); 
	    $("#barchart_container").animate({ 'width': '500px' });
	    console.log($("#barchart_container"));
	    $(".barchart_checkbox").attr("checked", "checked");
	    bar_status.bar_width = 900;
	    bar_status.bar_height = 335;
	    load_barchart([0,1,2], bar_status.bar_width, bar_status.bar_height); 
	};
	
	return false;
    });


});