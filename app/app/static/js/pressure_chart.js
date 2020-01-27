var graphAirStations = [];
var timeInterval = 120;
var limit = 120;
var pressure_timelist = [];
var pressurelist = [];


function get_pressure_data() {
    if(graphAirStations.length != 0){
        let ur = graphAirStations.join();
        $.get("http://127.0.0.1:5000/api/measurements/airpressure?limit=" + limit +"&stations=" + ur, function(result) {
            if(pressure_timelist.length == 0){
                for(x = timeInterval - 1; x >= 0; x--){
                    pressure_timelist.push(("" + result.data[x][0].substring(17,25)));
                    pressurelist.push(result.data[x][1]);
                }
                limit = 1;
            } else {
                    pressure_timelist.shift();
                    pressure_timelist.push("" + result.data[0][0].substring(17,25));

                    pressurelist.shift();
                    pressurelist.push(result.data[0][1]);
            }       
        });  
    }
}     

function setAirStations() {
    graphAirStations = [];
    pressure_timelist = [];
    pressurelist = [];
    limit = 120;
    graphAirStations = getAirStations();
    plot_pressure_graph();
}

function plot_pressure_graph(){
    get_pressure_data();
    draw(pressure_timelist, pressurelist);    
}

function draw(){
    if(pressurelist.length == timeInterval && pressure_timelist.length == timeInterval){
        $("#loading_label").hide();
        var myLineChart = new Chart($("#pressure_chart"), {
            type: 'line',
            data: {
                labels: pressure_timelist,
                datasets: [{ 
                    data: pressurelist,
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
        $("#time_label").text("Time(realtime): " + pressure_timelist[pressure_timelist.length-1]);
        $("#pressure_label").text("Airpressure(realtime): " + pressurelist[pressurelist.length-1]);
    }
}

setInterval( function(){
    plot_pressure_graph();
}, 1000); 




