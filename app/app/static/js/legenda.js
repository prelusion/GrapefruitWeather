$(document).ready(function() {
    $(".legenda_remove").on("click", function(){
        $(this).parent().hide();
    });

    $(".legenda_icon_container").on("click", function(){
        $(".legenda_container").show();
    });
});