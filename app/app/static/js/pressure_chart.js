/**
 * Arrays variables.
 */
let pressureTimeList = [];
let pressureList = [];
let queue = [];

/**
 * constant variables. 
 */
const pressureRefreshRate = 1000;

/**
 * State variables.
 */
let first = true;
let firstLoading = false;
let apiInterval = null;
let plotInterval = null;
let sessionId = 1;
let pressureHistoryInterval = 120;


/**
 * drawPressureChart draws a graph from the data given by the parameters.
 * @param  array times array with timestamps for x-axis.
 * @param  array pressures array with y-axis value.
 */
function drawPressureChart(times, pressures) {
    $("#pressure_status_label").hide();
    new Chart($("#pressure_chart"), {
        type: 'line',
        data: {
            labels: times,
            datasets: [{ 
                data: pressures,
                label: "pressure",
                borderColor: "#ea1c2e",
                fill: true
            }]
        },
        options: {
            title: {
                display: true,
                text: "pressure"
            },
            elements: {
                point:{
                    radius: 0
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
    $("#pressure_chart").show();
    $("#pressure_time_label").text("Time (latest): " + times[times.length-1]).show();
    $("#pressure_label").text("Pressure (latest): " + pressureList[pressures.length-1] + " mbar").show();
    $("#pressure_globe").hide();

    //commented for later implementation
    // $("#air_timezone").show();
}

/**
 * processPressureData processes the json result from the api into a timestamp and pressurelist.
 * @param  json result with timestamps and airpressure measurements.
 */
function processPressureData(result){
    let temporary = pressureHistoryInterval;
    if(pressureTimeList.length == 0){
        if (result.total < pressureHistoryInterval){
            pressureHistoryInterval = result.total;
        }
        for(x = pressureHistoryInterval - 1; x >= 0; x--){
            pressureTimeList.push(("" + result.data[x][0].substring(17,25)));
            pressureList.push(result.data[x][1]);
        }
        pressureHistoryInterval = temporary;
    } else if (pressureList.length < temporary) {
        pressureTimeList.push(("" + result.data[0][0].substring(17,25)));
        pressureList.push(result.data[0][1]);
    } else {
        //following is commented for test purposes
         if(result.data[0][0].substring(17,25) != pressureTimeList[pressureTimeList.length - 1]) {
            pressureTimeList.shift();
            pressureTimeList.push("" + result.data[0][0].substring(17,25));

            pressureList.shift();
            pressureList.push(result.data[0][1]);
         }
    }     
}

/**
 * retrieveData retrieves the airpressure data from an api.
 * @param  array pressStations with pressure stations.
 * @param  int currentCount with id of api session.
 */
function retrieveData(pressStations, currentCount) { 
    if (first && firstLoading) {
        return;
    } else if (first) {
        firstLoading = true;
    }

    let limit = first ? 120 : 1;

    $.get("/api/measurements/airpressure?limit=" + limit +"&stations=" + pressStations.join() + "&timezone=" + new Date().getTimezoneOffset(), function(result) {
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

/**
 * setNewAirStations resets necessary variables and retrieves a new array with pressurestations.
 * @param  array statons with station id's.
 */
function setNewAirStations(stations) {
    $("#pressure_time_label").hide();
    $("#pressure_label").hide();
    $("#pressure_chart").hide();

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
        $("#pressure_globe").show();
        apiInterval = setInterval(retrieveData, 1000, stations, sessionId);
        plotInterval = setInterval(handleQueue, pressureRefreshRate);
    } else {
        $("#pressure_status_label").text("This is the air pressure graph. Please select a track or station.").show();
        $("#pressure_globe").hide();
    }
}

/**
 * handleQueue handles the processing of json objects to plots.
 */
function handleQueue() {
    while (queue.length != 0) {
        processPressureData(queue.shift());
        drawPressureChart(pressureTimeList, pressureList);
    }
}

/**
 * Sets refreshrate of graph.
 * @param handleQueue function to be executed.
 * @param refreshrate rate in miliseconds at which the function in first parameters should be called.   
 */
plotInterval = setInterval(handleQueue, pressureRefreshRate);

/**
 * Creates button to switch between timezones 
 */
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
