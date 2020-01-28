$(document).ready(function() {
    $(".legenda_remove").on("click", function(){
        $(this).parent().hide();
    });

    $(".btn-outline-danger").on("click", function(){
        $(".legenda_container").show();
    });
});