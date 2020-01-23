$(document).ready(function() {
    //$(#track).val() = the track id+1.
    $("#track").change(function() {
        $("#latitude").val(jsonArray[$(this).val()-1].latitude);
        $("#longitude").val(jsonArray[$(this).val()-1].longitude);
        $("#country").val(jsonArray[$(this).val()-1].country);
        getTrackFilter();
    });

    $("#limit").change(function() {
        getTrackFilter();
    });

    $("#range").change(function() {
        getTrackFilter();
    });

    function getTrackFilter() {
        var trackID = $("#track").val();
        var latitude = $("#latitude").val();
        var longitude = $("#longitude").val();
        var country = $("#country").val();
        var limit = $("#limit").val();
        var range = $("#range").val();
        $.get("http://127.0.0.1:5000/api/tracks?id="+trackID+"&country="+country, function(result) {
            console.log(result);
        });
    }
});