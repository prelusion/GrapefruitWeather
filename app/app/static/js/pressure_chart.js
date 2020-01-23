$(document).ready(function(){

    timelist = [];
    pressurelist = [];
    stations = [93590,589210];
    var plottime = null;
    var plotdata = null;


    function plot(timestamps, pressure){

        var myLineChart = new Chart($("#pressure_chart"), {
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
                    text: "Airpressure"
                },
                animation: false

            }
        });
    }

    function set_stations(stationlist){
        this.stations = stationlist;
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

    setInterval(function() {

        function get_data() {
            ur = stations.join();
            $.get("http://127.0.0.1:5000/api/airpressure?limit=1&stations=" + ur, function(result) {
                for(index in result.data){
                    var jsontime = "" + result.data[index][0].substring(17,25);
                    var jsondata = result.data[index][1];


                    plottime = list_generator(timelist, jsontime); 
                    plotdata = list_generator(pressurelist, jsondata);
                }
                    
            });
        }

        get_data();
        plot(plottime, plotdata);
    }, 1000);

});