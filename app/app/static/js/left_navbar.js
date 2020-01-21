$(document).ready(function() {
    $(".open_tracks").on('click', function() {
        $(this).hide();
        $(this).next().show();      
        $(this).next().next().show();
    });
    $(".close_tracks").on('click', function() {
        $(this).prev().show();
        $(this).hide();
        $(this).next().hide();
    });
});