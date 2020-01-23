$(document).ready(function() {
    //$(#track).val() = the track id+1.
    $("#track").change(function() {
        $("#latitude").val(jsonArray[$(this).val()-1].latitude);
        $("#longitude").val(jsonArray[$(this).val()-1].longitude);
        $("#country").val(jsonArray[$(this).val()-1].country);
        getTrackFilter(true);
    });

    $("#latitude").on('input', function() {
        getTrackFilter();
    });
    $("#longitude").on('input', function() {
        getTrackFilter();
    });

    $("#limit").on('input', function() {
        getTrackFilter();
    });

    $("#range").on('input', function() {
        getTrackFilter();
    });

    function getTrackFilter(bool, obj) {
        var trackID = $("#track").val();
        var latitude = $("#latitude").val();
        var longitude = $("#longitude").val();
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

        setMapView(latitude, longitude);
        $.get("http://127.0.0.1:5000/api/tracks?id="+trackID+"&country="+country, function(result) {
            
        });
    }
});