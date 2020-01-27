$(document).ready(function() {
    $(".legenda_remove").on("click", function(){
        $(this).parent().hide();
    });

    $("#filter_button").on("click", function(){
        $(".legenda_container").show();
    });
});