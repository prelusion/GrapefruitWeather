$(document).ready(function() {
    //$(#track).val() = the track id+1.
    $("#filter_button").on("click", function() {
        $("#latitude").val(jsonArray[$("#track").val()-1].latitude);
        $("#longitude").val(jsonArray[$("#track").val()-1].longitude);
        $("#country").val(jsonArray[$("#track").val()-1].country_id);
        updateMarker($("#track").val()-1);
        getStationsFilter();
    });
    $("#filter_button").trigger("click");
});

function getStationsFilter(stationType = "Air", custom = false, custom_latitude, custom_longitude, custom_country_id) {
    var trackID = $("#track").val();
    var latitude = (custom === false) ? $("#latitude").val() : custom_latitude;
    var longitude = (custom === false) ? $("#longitude").val() : custom_longitude;
    var country = (custom === false) ? $("#country").val() : custom_country_id;
    var limit = $("#limit").val();
    var range = $("#range").val();
    var error = false;
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
     $.get("http://127.0.0.1:5000/api/stations?latitude="+latitude+"&longitude="+longitude+"&limit="+limit+"&range="+range, function(result) {
        markOrCreateStations(result);
        setMapView(latitude, longitude, map.getZoom());
    });
    if(stationType === "temperature") {
        $.get("http://127.0.0.1:5000/api/stations?country="+country, function(result) {
            setTemperatureStations(result);
        });
    }
}

// $.get("http://127.0.0.1:5000/api/stations?latitude="+latitude+"&longitude="+longitude+"&country="+country+"&limit="+limit+"&range="+range, function(result) {
//         markOrCreateStations(result);
//         setMapView(latitude, longitude, map.getZoom());
// });

// console.log(range);
// $.get("http://127.0.0.1:5000/api/stations?latitude="+latitude+"&longitude="+longitude+"&limit="+limit+"&range="+range, function(result) {
//     markOrCreateStations(result);
//     setMapView(latitude, longitude, map.getZoom());
// });
// if(stationType === "temperature") {
//     $.get("http://127.0.0.1:5000/api/stations?country="+country+"&limit="+limit, function(result) {
//         setTemperatureStations(result);
//     });
// }