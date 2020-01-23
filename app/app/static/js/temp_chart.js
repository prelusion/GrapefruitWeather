
$(document).ready(function(){
    timestamplist = [];
    templist = [];



    function plot(timestamps, pressure){

        var myLineChart = new Chart($("#temperature_chart"), {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{ 
                    data: pressure,
                    //label: "pressure",
                    borderColor: "#3e95cd",
                    fill: true
                }]

            },
            options: {
                title: {
                    display: true,
                    text: "Temperature"
                },
                animation: false

            }
        });
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


    function get_data() {

    }

    var time = list_generator(timestamplist, createTimeStamp()); 
    var data = list_generator(templist, Math.floor((Math.random() * 30) + 0));
    plot(time, data);


}, 1000);

});