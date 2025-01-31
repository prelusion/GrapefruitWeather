/**
 * Arrays variables.
 */
let temperatureTimeList = [];
let temperatureList = [];
let temperatureQueue = [];

/**
 * constant variables. 
 */
const temperatureRefreshRate = 1000;

/**
 * State & other variables.
 */
let temperatureFirst = true;
let temperatureFirstLoading = false;
let tempApiInterval = null;
let tempPlotInterval = null;
let temperatureSessionId = 1;
let country = "";
let temperatureHistoryInterval = 168;


/**
 * drawTempChart draws a graph from the data given by the parameters.
 * @param  array times array with timestamps for x-axis.
 * @param  array pressures array with y-axis value.
 */
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
            elements: {
                point: {
                    radius: function(){return temperatures.length > 1?0:5;}
                },
            line: {
                tension: 0 
                }
            },
            animation: false,
            responsive: true,
            maintainAspectRatio: false,
            events: []
        }
    });
    $("#temp_globe").hide();
    $("#temperature_chart").show();
    $("#temp_time_label").text("Time (latest): " + times[times.length-1]).show();
    $("#temperature_label").text("temperature (latest): " + temperatures[temperatures.length-1] + " ℃").show();
    $("#temperature_country").text("Country: " + country).show();
    $("#amount_stations").text("Amount of selected temperature stations:  " + getTemperatureStations().length).show();

    //commented for later implementation
    // $("#temperature_timezone").show();
}

/**
 * processTempData processes the json result from the api into a timestamp and temperatureList.
 * @param  json result with timestamps and temperature measurements.
 */
function processTempData(result){
    let temp = temperatureHistoryInterval;
    if(temperatureTimeList.length == 0){
        if (result.total < temperatureHistoryInterval){
            temperatureHistoryInterval = result.total;
        }
        for(x = temperatureHistoryInterval - 1; x >= 0; x--){    
            temperatureTimeList.push(("" + result.data[x][0].substring(17,25)));
            temperatureList.push(result.data[x][1]);
        }
        temperatureHistoryInterval = temp;
    } else if (temperatureList.length < temp) {
        if(result.data[0][0].substring(17,25) != temperatureTimeList[temperatureTimeList.length - 1]) {
            temperatureTimeList.push(("" + result.data[0][0].substring(17,25)));
            temperatureList.push(result.data[0][1]);
        }
    } else {
         if(result.data[0][0].substring(17,25) != temperatureTimeList[temperatureTimeList.length - 1]) {
            temperatureTimeList.shift();
            temperatureTimeList.push("" + result.data[0][0].substring(17,25));

            temperatureList.shift();
            temperatureList.push(result.data[0][1]);
         }
    }     
}

/**
 * retrieveTempData retrieves the temperature data from an api.
 * @param  array pressStations with pressure stations.
 * @param  int currentCount with id of api session.
 */
function retrieveTempData(pressStations, currentCount) { 
    if (temperatureFirst && temperatureFirstLoading) {
        return;
    } else if (temperatureFirst) {
        temperatureFirstLoading = true;
    }

    let limit = temperatureFirst ? 120 : 1;

    $.get("/api/measurements/temperature?limit=" + limit + "&stations=" + pressStations.join() + "&timezone=" + new Date().getTimezoneOffset(), function(result) {
        if (currentCount != temperatureSessionId) {
            return;
        }
        if (temperatureFirst) {
            temperatureFirst = false;
            temperatureFirstLoading = false;
        }
        temperatureQueue.push(result);
    });
}

function toCountryName(inputStr) {
    let newStr = "";
    let words = inputStr.toLowerCase().split(" ");
    for (index in words) {
    	newStr += words[index].charAt(0).toUpperCase() + words[index].slice(1) + " ";
    	newStr.trimRight();
    }
    return newStr;
}


/**
 * setNewAirStations resets necessary variables and retrieves a new array with temperaturestations.
 * @param  array statons with station id's.
 */
function setNewTempStations(stations) {
    $("#temp_time_label").hide();
    $("#temperature_label").hide();
    $("#temperature_country").hide();
    $("#temperature_chart").hide();
    $("#amount_stations").hide();

    if (temperatureSessionId > 100) {
        temperatureSessionId = 1;
    }
    
    temperatureSessionId++;

    if (tempApiInterval) {
        clearInterval(tempApiInterval);
    }
    if (tempPlotInterval) {
        clearInterval(tempPlotInterval);
    }

    temperatureTimeList = [];
    temperatureList = [];
    temperatureQueue = [];
    temperatureFirst = true;
    temperatureFirstLoading = false;
    country = toCountryName(countryName);
    
    if(stations.length != 0){
        $("#temp_status_label").text("Loading history...").show();
        $("#temp_globe").show();
        tempApiInterval = setInterval(retrieveTempData, 1000, stations, temperatureSessionId);
        tempPlotInterval = setInterval(handletemperatureQueue, temperatureRefreshRate);
    } else {
        $("#temp_status_label").text("This is the temperature graph. Please select a track to get all temperature stations in a country.").show();
        $("#temp_globe").hide();
    }
}

/**
 * handletemperatureQueue handles the processing of json objects to plots.
 */
function handletemperatureQueue() {
    while (temperatureQueue.length != 0) {
        processTempData(temperatureQueue.shift());
        drawTempChart(temperatureTimeList, temperatureList);
    }
}

/**
 * Sets refreshrate of graph.
 * @param handletemperatureQueue function to be executed.
 * @param refreshrate rate in miliseconds at which the function in first parameters should be called.   
 */
tempPlotInterval = setInterval(handletemperatureQueue, temperatureRefreshRate);

/**
 * Creates button to switch between timezones 
 */
// $("#temperature_timezone").on("click", function() {
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


