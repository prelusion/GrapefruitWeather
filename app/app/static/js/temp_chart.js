//global vars for history
var temperatureTimelist = [];
var temperaturelist = [];
var graphTempStations = [];
var temperatureCallLimit = 120;
var intervalId = null;
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
            animation: false,
            events: []
        }
    });
    $("#temperature_chart").show();
    $("#temp_time_label").text("Time (realtime): " + temperatureTimelist[temperatureTimelist.length-1]);
    $("#temperature_label").text("Temperature (realtime): " + temperaturelist[temperaturelist.length-1]);
}

function processTemperatureData(result){
    if(temperatureTimelist.length == 0){
        for(x = chartTimeInterval - 1; x >= 0; x--){
            temperatureTimelist.push(("" + result.data[x][0].substring(17,25)));
            temperaturelist.push(result.data[x][1]);
        }
        temperatureCallLimit = 1;
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
    if(graphTempStations.length != 0) {
        console.log(temperatureCallLimit);
        $.get("http://127.0.0.1:5000/api/measurements/airpressure?limit=" + temperatureCallLimit +"&stations=" + graphTempStations.join(), function(result) {
            console.log("stations die in de url komen: ", graphTempStations)
            console.log(result);
            console.log(temperatureCallLimit);
            processTemperatureData(result);
            if(temperatureTimelist.length == chartTimeInterval && temperaturelist.length == chartTimeInterval){
                drawTempChart(temperatureTimelist, temperaturelist);
            }
        });  
    } else {
        console.log("NO STATIONS SELECTED!!");
        $("#temperature_chart").hide();
    }
}

function setNewTempStations(stations){
    console.clear();
    clearInterval(intervalId);
    console.log("stations die deo vraagt: ", stations);
    temperatureTimelist = [];
    temperaturelist = [];
    graphTempStations = [];
    temperatureCallLimit = 120;
    graphTempStations = stations;
    if(stations.length != 0){
        intervalId = setInterval(plotTemperature, temperatureRefreshrate); 
    }
}
