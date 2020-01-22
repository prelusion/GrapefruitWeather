$(document).ready(function() {
    $(".dropdown_second_navbar").click(function() {
        if($(".menu_second_navbar").css("display") == "none") {
            $(".menu_second_navbar").slideDown();
        } else {
            $(".menu_second_navbar").slideUp();
        }
    });
});


