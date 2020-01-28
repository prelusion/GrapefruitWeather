var graphTempStations = [];
const temperature_timeInterval = 120;
var temperature_call_limit = 120;
var temperature_timelist = [];
var temperaturelist = [];
const temperature_refreshrate = 1000;
var temperature_ready = false;

function draw_temp() {
    if(temperaturelist.length == temperature_timeInterval && temperature_timelist.length == temperature_timeInterval){
        $("#temp_status_label").hide();
        new Chart($("#temperature_chart"), {
            type: 'line',
            data: {
                labels: temperature_timelist,
                datasets: [{ 
                    data: temperaturelist,
                    label: "Temperature",
                    borderColor: "#091e49",
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
        $("#temp_time_label").text("Time (realtime): " + temperature_timelist[temperature_timelist.length-1]);
        $("#temperature_label").text("Temperature (realtime): " + temperaturelist[temperaturelist.length-1]);
    }
}

function get_temperature_data() {
    if(graphTempStations.length != 0) {
        let temperature_station_string = graphTempStations.join();
        $.get("http://127.0.0.1:5000/api/measurements/airpressure?limit=" + temperature_call_limit +"&stations=" + temperature_station_string, function(result) {
            if(temperature_timelist.length == 0){
                for(x = temperature_timeInterval - 1; x >= 0; x--){
                    temperature_timelist.push(("" + result.data[x][0].substring(17,25)));
                    temperaturelist.push(result.data[x][1]);
                }
                temperature_call_limit = 1;
            } else {
                // if(!result.data[0][0].substring(17,25) == temperature_timelist[temperature_timelist.length - 1]) {
                    temperature_timelist.shift();
                    temperature_timelist.push("" + result.data[0][0].substring(17,25));

                    temperaturelist.shift();
                    temperaturelist.push(result.data[0][1]);
                // }
            }       
        });  
    }
}     

function plot_temperature_graph() {
    get_temperature_data();
    draw_temp();    
}


//Reset all datalists and load new 120 records for new history records
function setTemperatureStations() {
    graphTempStations = [];
    temperature_timelist = [];
    temperaturelist = [];
    temperature_call_limit = 120;
    graphTempStations = getTemperatureStations();
    if(graphTempStations.length != 0){
        plot_temperature_graph();
        temperature_ready = true;
    } else {
        $("#temp_status_label").text("This country has no temperature stations!");
        $("#temperature_chart").hide();
        $("#temp_status_label").show();
    }
}

function refresh_temperature() {
    if(temperature_ready) {
        plot_temperature_graph();
    }
}

setInterval(refresh_temperature, temperature_refreshrate); 