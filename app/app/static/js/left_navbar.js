$(document).ready(function() {
    $(".open_container").on('click', function() {
        $(this).hide();
        $(this).next().show();      
        $(this).next().next().slideDown();
    });
    $(".close_container").on('click', function() {
        $(this).prev().show();
        $(this).hide();
        $(this).next().slideUp();
    });
    $(".track_container").on('click', function() { 
        setMapView($(this).children("p").attr("latitude"), $(this).children("p").attr("longitude"), 13);
        updateMarker(($(this).children("p").attr("trackID")-1));
        $("#track option:eq("+($(this).children("p").attr("trackID")-1)+")").prop("selected", true);
        $("#latitude").val($(this).children("p").attr("latitude"));
        $("#longitude").val($(this).children("p").attr("longitude"));
        $("#country").val($(this).children("p").attr("country"));
        $("#country").attr("countryid", $(this).children("p").attr("countryid"));
        getStationsFilter();
    });
}); 