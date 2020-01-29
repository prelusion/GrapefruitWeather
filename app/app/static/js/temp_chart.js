$(document).ready(function(){

    timestamplist = [];
    templist = [];

    $("#temp_status_label").show();

    function plot(timestamps, temperature){
        $("#temp_status_label").hide();
        var myLineChart = new Chart($("#temperature_chart"), {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{ 
                    data: temperature,
                    label: "temperature",
                    borderColor: "#3e95cd",
                    fill: true
                }]

            },
            options: {
                title: {
                    display: true,
                    text: "Temperature"
                },
                animation: false,
                events: []
            }
        });
        $("#temp_time_label").text("Time (realtime): " + timestamplist[timestamplist.length-1]);
        $("#temperature_label").text("Temperature (realtime): " + templist[templist.length-1]);
    }
    



setInterval(function() {

    var hours = new Date().getHours();
    var minutes = new Date().getMinutes();
    var seconds = new Date().getSeconds();

    function convert_time(input){
        if(input < 10){
            return "0" + input;
        } else {
            return ""+ input;
        }
    }

    function createTimeStamp(){
        return convert_time(hours) + ":" + convert_time(minutes) + ":" + convert_time(seconds);
    }

    function list_generator(list, data) {
        if(list.length == 6){
            list.shift();
            list[5] = data;
            return list;
        } else {
            list.push(data);
            return list;
        } 
    } 


    var time = list_generator(timestamplist, createTimeStamp()); 
    var data = list_generator(templist, Math.floor((Math.random() * 1) + 15));
    plot(time, data);

    }, 1000);
});

function setNewTempStations(parameter){}

// $("#temperature_timezone").on("click", function() {
//     if($(this).text() === "Local timezone") {
//         $(this).text("Destination timezone");
//         $(this).addClass("btn-danger");
//         $(this).removeClass("btn-success");
//     } else {
//         $(this).text("Local timezone");
//         $(this).addClass("btn-success");
//         $(this).removeClass("btn-danger");
//     }
// });


