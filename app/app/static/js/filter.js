$(document).ready(function() {
    //$(#track).val() = the track id+1.
    $("#track").change(function() {
        console.log("test");
        $("#latitude").val(jsonArray[$(this).val()-1].latitude);
        $("#longitude").val(jsonArray[$(this).val()-1].longitude);
        $("#country").val(jsonArray[$(this).val()-1].country);
        updateMarker($("#track").val()-1);
        getStationsFilter();
    });

    $("#latitude").on('input', function() {
        getStationsFilter();
    });
    $("#longitude").on('input', function() {
        getStationsFilter();
    });

    $("#limit").on('input', function() {
        getStationsFilter();
    });

    $("#range").on('input', function() {
        getStationsFilter();
    });
    $("#track").trigger("change");
});

function getStationsFilter(custom = false, custom_latitude, custom_longitude) {
    var trackID = $("#track").val();
    var latitude = (custom === false) ? $("#latitude").val() : custom_latitude;
    var longitude = (custom === false) ? $("#longitude").val() : custom_longitude;
    var country = $("#country").val();
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
    $.get("http://127.0.0.1:5000/api/stations?latitude="+latitude+"&longitude="+longitude+"&country="+3+"&limit="+limit+"&range="+range, function(result) {
        createStations(result);
        setMapView(latitude, longitude);
    });
}