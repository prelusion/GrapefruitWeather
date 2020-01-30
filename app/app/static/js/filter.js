$(document).ready(function() {
    //$(#track).val() = the track id+1.
    $("#filter_button").on("click", function() {
        setFilterValues(jsonArray[$("#track").val()-1].latitude, jsonArray[$("#track").val()-1].longitude, jsonArray[$("#track").val()-1].country_id, jsonArray[$("#track").val()-1].country);
        setMapView($("#latitude").val(), $("#longitude").val(), map.getZoom());
        updateMarker($("#track").val()-1);
        getStationsFilter();
    });
    $("#filter_button").trigger("click");
});

function setFilterValues(latitude, longitude, countryID, countryName) {
    $("#latitude").val(latitude);
    $("#longitude").val(longitude);
    $("#country").attr("countryid", countryID);
    $("#country").val(countryName);
}

$("#zoom_button").on("click", function(){
    setMapView($("#latitude").val(), $("#longitude").val(), 11);
});

$("#clear_button").on("click", function(){
    clearMapOfStations();
});

$("#limit").on("input", function(){
    if($(this).val() > 300) {
        $(this).popover('show')
    } else {
        $(this).popover('hide')
    }
});

function getStationsFilter(custom = false, custom_latitude, custom_longitude, custom_country_id) {
    let trackID = $("#track").val();
    let latitude = (custom === false) ? $("#latitude").val() : custom_latitude;
    let longitude = (custom === false) ? $("#longitude").val() : custom_longitude;
    let country = (custom === false) ?  $("#country").attr("countryid") : custom_country_id;
    let limit = $("#limit").val();
    let radius = $("#range").val();
    let error = false;
    if (isNaN(latitude)) {
        $("#latitude_error").show();
        error = true;
    }
    if(isNaN(longitude)) {
        $("#longitude_error").show();
        error = true;
    }
    if(isNaN(limit)) {
        $("#limit_error").show();
        error = true;
    }
    if(isNaN(radius)) {
        $("#range_error").show();
        error = true;
    }
    if(error === true) return;
    $("#latitude_error").hide();
    $("#longitude_error").hide();
    $("#limit_error").hide();
    $("#range_error").hide();
    if(limit === "") {
        limit = 50;
    }

    let url = "/api/stations?track_id="+trackID+"&limit="+limit
    if (radius > 0) {
        url = url + "&radius=" + radius;
    }
    console.log(url);
    $.get(url, function(result) {
        setAirStationsFromAPI(result);
    });
    $.get("/api/stations?country="+country, function(result) {
        setTemperatureStationsFromAPI(result);
    });
}