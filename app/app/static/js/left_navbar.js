$(document).ready(function() {
    $(".open_container").on('click', function() {
        $(this).hide();
        $(this).next().show();      
        $(this).next().next().show();
    });
    $(".close_container").on('click', function() {
        $(this).prev().show();
        $(this).hide();
        $(this).next().hide();
    });

    $(".track_container").on('click', function() {
        map.invalidateSize();
        map.setView([$(this).children("p").attr("latitude"), $(this).children("p").attr("longitude")], 13);

        
    });
});