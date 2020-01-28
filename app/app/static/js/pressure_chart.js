var graphAirStations = [];
var pressure_timeinterval = 120;
var pressure_call_limit = 120;
var pressure_timelist = [];
var pressurelist = [];
const pressure_refreshrate = 1000;
var pressure_ready = false;

function draw() {
    if(pressurelist.length == pressure_timeinterval && pressure_timelist.length == pressure_timeinterval){
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

function get_pressure_data() {
    if(graphAirStations.length != 0) {
        let ur = graphAirStations.join();
        $.get("http://127.0.0.1:5000/api/measurements/airpressure?pressure_call_limit=" + pressure_call_limit +"&stations=" + ur, function(result) {
            if(pressure_timelist.length == 0){
                for(x = pressure_timeinterval - 1; x >= 0; x--){
                    pressure_timelist.push(("" + result.data[x][0].substring(17,25)));
                    pressurelist.push(result.data[x][1]);
                }
                pressure_call_limit = 1;
            } else {
                if(!result.data[0][0].substring(17,25) == pressure_timelist[pressure_timelist.length - 1]) {
                    pressure_timelist.shift();
                    pressure_timelist.push("" + result.data[0][0].substring(17,25));

                    pressurelist.shift();
                    pressurelist.push(result.data[0][1]);
                }
            }       
        });  
    }
}     

function plot_pressure_graph() {
    get_pressure_data();
    draw();    
}


//Reset all datalists and load new 120 records for new history records
function setAirStations() {
    graphAirStations = [];
    pressure_timelist = [];
    pressurelist = [];
    pressure_call_limit = 120;
    graphAirStations = getAirStations();
    plot_pressure_graph();
    pressure_ready = true;
}

setInterval( function() {
    if(pressure_ready) {
        plot_pressure_graph();
    }
}, pressure_refreshrate); 




