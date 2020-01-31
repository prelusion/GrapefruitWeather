//global vars for history
var pressureTimeList = [];
var pressureList = [];


var queue = [];
const pressureHistoryInterval = 120;
let first = true;
let firstLoading = false;
let apiInterval = null;
let plotInterval = null;
let sessionId = 1;


function drawPressureChart(times, pressures) {
    $("#pressure_status_label").hide();
    new Chart($("#pressure_chart"), {
        type: 'line',
        data: {
            labels: times,
            datasets: [{ 
                data: pressures,
                label: "pressure",
                borderColor: "#091e49",
                fill: true
            }]
        },
        options: {
            title: {
                display: true,
                text: "pressure"
            },
            animation: false,
            events: []
        }
    });
    $("#pressure_chart").show();
    $("#pressure_time_label").text("Time (latest): " + pressures[pressures.length-1]).show();
    $("#pressure_label").text("Pressure (latest): " + pressureList[pressures.length-1]).show();
    //$("#amount_temperature_stations").text("Temperature stations: " + getTemperatureStations().length);
}

function processPressureData(result){
    if(pressureTimeList.length == 0){
        for(x = pressureHistoryInterval - 1; x >= 0; x--){
            // console.log(result.data[x][0].substring(17,25));
            // console.log(result.data[x][1]);
            pressureTimeList.push(("" + result.data[x][0].substring(17,25)));
            pressureList.push(result.data[x][1]);
        }
    } else {
        // if(!result.data[0][0].substring(17,25) == pressureTimeList[pressureTimeList.length - 1]) {
            pressureTimeList.shift();
            pressureTimeList.push("" + result.data[0][0].substring(17,25));

            pressureList.shift();
            pressureList.push(result.data[0][1]);
        // }
    }     
}


function retrieveData(pressStations, currentCount) { 
    console.log("retrievedata count", currentCount);
    if (first && firstLoading) {
        return;
    } else if (first) {
        firstLoading = true;
    }

    let limit = first ? 120 : 1;
    console.log(limit);

    $.get("http://127.0.0.1:5000/api/measurements/airpressure?limit=" + limit +"&stations=" + pressStations.join(), function(result) {
        console.log("callback count", currentCount);

        if (currentCount != sessionId) {
            return;
        }
        if (first) {
            first = false;
            firstLoading = false;
        }
        queue.push(result);
    });
}

function setNewAirStations(stations) {
    $("#pressure_time_label").hide();
    $("#pressure_label").hide();
    $("#pressure_chart").hide();
    console.log("stations from deo: ", stations);

    if (sessionId > 100) {
        sessionId = 1;
    }
    
    sessionId++;

    if (apiInterval) {
        clearInterval(apiInterval);
    }
    if (plotInterval) {
        clearInterval(plotInterval);
    }

    pressureTimeList = [];
    pressureList = [];
    queue = [];
    first = true;
    firstLoading = false;
    
    if(stations.length != 0){
        $("#pressure_status_label").text("Loading history...").show();
        apiInterval = setInterval(retrieveData, 1000, stations, sessionId);
        plotInterval = setInterval(handleQueue, 1000);
    } else {
        $("#pressure_status_label").text("There are no airpressure stations available!").show();
    }
}

function handleQueue() {
    while (queue.length != 0) {
        processPressureData(queue.shift());
        drawPressureChart(pressureTimeList, pressureList);
    }
}

plotInterval = setInterval(handleQueue, 1000);


$("#air_timezone").on("click", function() {
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
