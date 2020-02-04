$(document).ready(function() {
    //$(#track).val() = the track id+1.
    $("#filter_button").on("click", function() {
        $(".track_container").css({"color": "#848689"});
        if($("#track").val() == "-1") {
            return;
        }
        setFilterValues(jsonArray[$("#track").val()-1].latitude, jsonArray[$("#track").val()-1].longitude, jsonArray[$("#track").val()-1].country_id, jsonArray[$("#track").val()-1].country);
        setMapView($("#latitude").val(), $("#longitude").val(), map.getZoom());
        updateMarker($("#track").val()-1);
        getStationsFilter();
    });
    $("#filter_button").trigger("click");

    $("#download_button").on("click", function() {
        let pressureStations = getPressureStations();
        let tempStations = getTemperatureStations();
        let url = "/api/measurements/export/xml?timezone="+new Date().getTimezoneOffset();
        if (pressureStations.length) {
            url = url + "&pressurestations="+ pressureStations;
        }
        if (tempStations.length) {
            url = url + "&tempstations="+ tempStations;
        }
        window.open(url, "_blank");
    });
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

function getStationsFilter(custom = false, track_id, custom_country_id) {
    let trackID = (custom === false) ?  $("#track").val() : track_id;
    let country = (custom === false) ?  $("#country").attr("countryid") : custom_country_id;
    countryName = $("#country").val();
    let limit = $("#limit").val();
    let radius = $("#range").val();
    let error = false;
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

    setTimeout(function(){
        let url = "/api/stations?track_id="+trackID+"&limit="+limit
        $.get(url, function(result) {
            setAirStationsFromAPI(result);
        });
     }, 150);   
     
    setTimeout(function(){
        url = "/api/stations?track_id="+trackID+"&country="+country;
        if (radius > 0) {
            url = url + "&radius=" + radius;
        }
        $.get(url, function(result) {
            setTemperatureStationsFromAPI(result);
        });
     }, 300);

    

}