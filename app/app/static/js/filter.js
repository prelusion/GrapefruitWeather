$(document).ready(function() {
    //$(#track).val() = the track id+1.
    $("#filter_button").on("click", function() {
        $("#latitude").val(jsonArray[$("#track").val()-1].latitude);
        $("#longitude").val(jsonArray[$("#track").val()-1].longitude);
        $("#country").attr("countryid", jsonArray[$("#track").val()-1].country_id);
        $("#country").val(jsonArray[$("#track").val()-1].country);
        setMapView($("#latitude").val(), $("#longitude").val(), map.getZoom());
        updateMarker($("#track").val()-1);
        getStationsFilter();
    });
    $("#filter_button").trigger("click");
});

function getStationsFilter(stationType = "air", custom = false, custom_latitude, custom_longitude, custom_country_id) {
    let trackID = $("#track").val();
    let latitude = (custom === false) ? $("#latitude").val() : custom_latitude;
    let longitude = (custom === false) ? $("#longitude").val() : custom_longitude;
    let country = (custom === false) ?  $("#country").attr("countryid") : custom_country_id;
    let limit = $("#limit").val();
    let range = $("#range").val();
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
    if(isNaN(range)) {
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
    console.log(trackID);
    $.get("http://127.0.0.1:5000/api/stations?track_id="+trackID+"&limit="+limit+"&range="+range, function(result) {
        console.log(result);
        setAirStationsFromAPI(result);
        // setMapView(latitude, longitude, map.getZoom());
    });
    if(stationType === "temperature") {
        $.get("http://127.0.0.1:5000/api/stations?country="+country, function(result) {
            setTemperatureStationsFromAPI(result);
        });
    }
}

// $.get("http://127.0.0.1:5000/api/stations?latitude="+latitude+"&longitude="+longitude+"&country="+country+"&limit="+limit+"&range="+range, function(result) {
//         setAirStationsFromAPI(result);
//         setMapView(latitude, longitude, map.getZoom());
// });

// console.log(range);
// $.get("http://127.0.0.1:5000/api/stations?latitude="+latitude+"&longitude="+longitude+"&limit="+limit+"&range="+range, function(result) {
//     setAirStationsFromAPI(result);
//     setMapView(latitude, longitude, map.getZoom());
// });
// if(stationType === "temperature") {
//     $.get("http://127.0.0.1:5000/api/stations?country="+country+"&limit="+limit, function(result) {
//         setTemperatureStations(result);
//     });
// }