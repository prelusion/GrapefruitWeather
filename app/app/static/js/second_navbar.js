$(document).ready(function(){
    $(".dropdown").click(function(){
        if( $(".menu_items").css("display") == "none"){

            $(".menu_items").css("display", "block");
            $(".menu_items").slideDown();

        }else{
            
            $(".menu_items").css("display", "none");
            $(".menu_items").slideUp();

        }
    });
});


