//global vars for history
var pressureTimeList = [];
var pressureList = [];
var graphPressureStations = [];
var pressureCallLimit = 120;
var intervalId = null;
const pressureHistoryInterval = 120;
const pressureLock = 1000;
var lock = false;

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
    // $("#temp_time_label").text("Time (realtime): " + pressureTimeList[pressureTimeList.length-1]);
    // $("#temperature_label").text("Temperature (realtime): " + pressureList[pressureList.length-1]);
}

function processPressureData(result){
    if(pressureTimeList.length == 0){
        for(x = pressureHistoryInterval - 1; x >= 0; x--){
            pressureTimeList.push(("" + result.data[x][0].substring(17,25)));
            pressureList.push(result.data[x][1]);
        }
        pressureCallLimit = 1;
    } else {
        // if(!result.data[0][0].substring(17,25) == pressureTimeList[pressureTimeList.length - 1]) {
            pressureTimeList.shift();
            pressureTimeList.push("" + result.data[0][0].substring(17,25));

            pressureList.shift();
            pressureList.push(result.data[0][1]);
        // }
    }     
}

//function is done before api is done
function plotPressure(apilimit, pressStations) {
    if(!lock){
        lock = true;
        $.get("http://127.0.0.1:5000/api/measurements/airpressure?limit=" + apilimit +"&stations=" + pressStations.join(), 
            function(result) {
                console.log(apilimit);
                processPressureData(result);
                if(pressureTimeList.length == pressureHistoryInterval && pressureList.length == pressureHistoryInterval){
                    drawPressureChart(pressureTimeList, pressureList);
            }
        }); 
        lock = false;
    }else {
        console.log("lock occured!");
    }
}

function setNewAirStations(newstations){
    console.log("called");
    //if stations are changed, there is no need to keep downloading and plotting
    clearInterval(intervalId);

    graphPressureStations = newstations;
    pressureTimeList = [];
    pressureList = [];
    pressureCallLimit = 120;

    if(graphPressureStations.length != 0){
        intervalId = setInterval(plotPressure, pressureLock,
             pressureCallLimit, graphPressureStations);
    }
}

// setInterval(refresh_pressure, pressure_refreshrate); 


// $("#air_timezone").on("click", function() {
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