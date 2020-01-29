//global vars for history
var temperatureTimelist = [];
var temperaturelist = [];
var graphTempStations = [];
var temperatureCallLimit = 120;
var tempPlotPermission = false;
const chartTimeInterval = 120;
const temperatureRefreshrate = 1000;

function drawTempChart(times, temperatures) {
    $("#temp_status_label").hide();
    new Chart($("#temperature_chart"), {
        type: 'line',
        data: {
            labels: times,
            datasets: [{ 
                data: temperatures,
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
            options: {
                title: {
                    display: true,
                    text: "Temperature"
                },
                animation: false
            }
        });
        $("#temp_time_label").text("Time (realtime): " + temperature_timelist[temperature_timelist.length-1]);
        $("#temperature_label").text("Temperature (realtime): " + temperaturelist[temperaturelist.length-1]);;
        $("#temperature_timezone").show();
    }
}

function process_temperature_data(result){
    if(temperatureTimelist.length == 0){
        for(x = chartTimeInterval - 1; x >= 0; x--){
            temperatureTimelist.push(("" + result.data[x][0].substring(17,25)));
            temperaturelist.push(result.data[x][1]);
        }
        temperatureCallLimit = 1;
        tempPlotPermission = true;
    } else {
        // if(!result.data[0][0].substring(17,25) == temperatureTimelist[temperatureTimelist.length - 1]) {
            temperatureTimelist.shift();
            temperatureTimelist.push("" + result.data[0][0].substring(17,25));

            temperaturelist.shift();
            temperaturelist.push(result.data[0][1]);
        // }
    }     
}

function plotTemperature() {
    if(tempPlotPermission){
        if(graphTempStations.length != 0) {
            $.get("http://127.0.0.1:5000/api/measurements/airpressure?limit=" + temperatureCallLimit +"&stations=" + graphTempStations.join(), function(result) {
                process_temperature_data(result);
                if(temperatureTimelist.length == chartTimeInterval && temperaturelist.length == chartTimeInterval){
                    drawTempChart(temperatureTimelist, temperaturelist);
                }
            });  
        } else {
            console.log("NO STATIONS SELECTED!!");
        }
    } else {
        console.log("no permission");
    }
}

function setNewTempStations(stations){
    tempPlotPermission = false;
    temperatureTimelist = [];
    temperaturelist = [];
    graphTempStations = [];
    graphTempStations = stations
    plotTemperature();
}

function refresh_temperature() {
    if(temperature_ready) {
        plot_temperature_graph();
    }
}

setInterval(refresh_temperature, temperature_refreshrate); 


$("#temperature_timezone").on("click", function() {
    if($(this).text() === "Local timezone") {
        $(this).text("Destination timezone");
        $(this).addClass("btn-danger");
        $(this).removeClass("btn-success");
    } else {
        $(this).text("Local timezone");
        $(this).addClass("btn-success");
        $(this).removeClass("btn-danger");
    }
});



setInterval(plotTemperature, temperatureRefreshrate); 