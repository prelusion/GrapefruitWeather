$(document).ready(function() {

    function check_window_size(){
        var windowsize = window.innerWidth;
        if(windowsize <= 1200){
            $(".dropdown_second_navbar").css("display", "block");
        }else {
            $(".dropdown_second_navbar").css("display", "none");
        }

        if(windowsize >= 1200 && ($(".menu_second_navbar").css("display") == "block")){
            $(".menu_second_navbar").css("display", "none");
        }
    }

    check_window_size();

    $(window).resize(function(){
        check_window_size();
    });

    $(".dropdown_second_navbar").click(function() {
        if($(".menu_second_navbar").css("display") == "none") {
            $(".menu_second_navbar").slideDown();
        } else {
            $(".menu_second_navbar").slideUp();
        }
    });
});




