$(document).ready(function(){

    var timelist = [];
    var pressurelist = [];
    var stations = [93590,589210];
    var timeInterval = 120;
    var limit = 120;


    function plot(timestamps, pressure){
        var myLineChart = new Chart($("#pressure_chart"), {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{ 
                    data: pressure,
                    label: "pressure",
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
        $("#time_label").text("Time(realtime): " + timelist[timelist.length-1]);
        $("#pressure_label").text("Airpressure(realtime): " + pressurelist[pressurelist.length-1]);
        $(".air .footer_container").css("background-color", "white");
    }

    function setAirStations() {
        stations = getAirStations();
    }

    
    function get_data() {
        let ur = stations.join();
        $.get("http://127.0.0.1:5000/api/measurements/airpressure?limit=" + limit +"&stations=" + ur, function(result) {
            if(timelist.length == 0){
                for(x = timeInterval - 1; x >= 0; x--){
                    timelist.push(("" + result.data[x][0].substring(17,25)));
                    pressurelist.push(result.data[x][1]);
                    limit = 1;
                }
            } else {
                    console.log(limit);
                    timelist.shift();
                    timelist.push("" + result.data[0][0].substring(17,25));

                    pressurelist.shift();
                    pressurelist.push(result.data[0][1]);
            }       
        });  
    }      

    setInterval(function() {
        get_data();
        plot(timelist, pressurelist);        
    }, 1000);

    
});

