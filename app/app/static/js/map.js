$(document).ready(function() {
    map = L.map('mapid').setView([51.505, -0.09], 13);
    markers = L.featureGroup().addTo(map).on("click", markerClick);

    map.on('dblclick', movingTrigger);

    stations = [];
    selectedAirStations = [];
    selectedTemperatureStations = [];

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);  
     
    racetrackIconSelected = new L.Icon({
        iconUrl: '/static/resources/images/racetrack_marker.gif',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [48, 48],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [61, 61]
    });

    racetrackIcon = new L.Icon({
        iconUrl: '/static/resources/images/racetrack_marker.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [48, 48],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [61, 61]
    });
    
    
    weatherstationIcon = new L.Icon({
        iconUrl: '/static/resources/images/weatherstation_marker.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [48, 48],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [61, 61]
    });

    weatherstationIconSelected = new L.Icon({
        iconUrl: '/static/resources/images/weatherstation_marker.gif',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [48, 48],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [61, 61]
    });  
});
function movingTrigger(event) {
    getCurrentMapCoordsStations(event.target._lastCenter.lat, event.target._lastCenter.lng);
}

function getCurrentMapCoordsStations(latitude, longitude) {
    $.get("http://127.0.0.1:5000/api/stations?latitude="+latitude+"&longitude="+longitude+"&limit="+$("#limit").val()+"&range="+$("#range").val(), function(result) {
        for(station in result.data) {
            console.log(result.data);
            if(!stations.includes(result.data[station].id)) {
                stations.push(result.   data[station].id);
                var marker = L.marker([result.data[station].latitude, result.data[station].longitude], {icon: weatherstationIcon} ).addTo(markers)
                .bindPopup("Name:" + result.data[station].name);
                marker.highlighted = false;
                marker.profile = "station";     
                marker.distance = result.data[station].distance;
                marker.station_id = result.data[station].id;
                marker.latitude = result.data[station].latitude;
                marker.longitude = result.data[station].longitude;       
            }
        }
    });
}

function markerClick(event) {
    if(event.layer.highlighted) {
        if(event.layer.profile === "track") {
            deselectMarkers();
            event.layer.setIcon(racetrackIcon);
        } else {
            event.layer.setIcon(weatherstationIcon);
            selectedAirStations = removeValueOutArray(selectedAirStations, event.layer.station_id);
        }
        event.layer.highlighted = false;
    } else {
        if(event.layer.profile === "track") {
            deselectMarkers();
            event.layer.setIcon(racetrackIconSelected);
            getStationsFilter("temperature", true, event.layer.latitude, event.layer.longitude, event.layer.country_id);      
            event.layer.highlighted = true;   
        } else {
            event.layer.setIcon(weatherstationIconSelected);
            event.layer.highlighted = true;
            selectedAirStations.push(event.layer.station_id);
        }  
    }
    console.log(selectedAirStations);
}

function removeValueOutArray(array, value) {
    const index = array.indexOf(value);
    if (index > -1) {
        array.splice(index, 1);
    }
    return array;
}

//Can be more effcient!!
function updateMarker(marker_id) {
    deselectMarkers();
    for(mark in markers._layers) {
        if(markers._layers[mark].profile === "track" && markers._layers[mark].track_id === marker_id) {
            markers._layers[mark].setIcon(racetrackIconSelected);
            markers._layers[mark].highlighted = true;
        } else if(markers._layers[mark].profile === "station" && markers._layers[mark].station_id === marker_id) {
            markers._layers[mark].setIcon(weatherstationIconSelected); 
            markers._layers[mark].highlighted = true;
        }    
    }
}

function deselectMarkers() {
    selectedAirStations = [];
    selectedTemperatureStations = [];
    for(mark in markers._layers) {
        markers._layers[mark].highlighted = false;        
        if(markers._layers[mark].profile === "track") {    
            markers._layers[mark].setIcon(racetrackIcon); 
        } else {
            markers._layers[mark].setIcon(weatherstationIcon); 
        }
    }
}

function markOrCreateStations(result) {
    for(station in result.data) {
        selectedAirStations.push(result.data[station].id);
        if(!stations.includes(result.data[station].id)){
            stations.push(result.data[station].id);

            var marker = L.marker([result.data[station].latitude, result.data[station].longitude], {icon: weatherstationIconSelected} ).addTo(markers)
            .bindPopup("Name:" + result.data[station].name);
            marker.highlighted = true;
            marker.profile = "station";     
            marker.distance = result.data[station].distance;
            marker.station_id = result.data[station].id;
            marker.latitude = result.data[station].latitude;
            marker.longitude = result.data[station].longitude;
        } else {
            for(index in markers._layers) {
                if(markers._layers[index].station_id === result.data[station].id) {
                    var marker = markers._layers[index];
                    marker.setIcon(weatherstationIconSelected);
                    marker.highlighted = true;
                }
            }
        }
    }
    console.log("air stations ", selectedAirStations);
}

function setMapView(latitude, longitude, zoom) {
    map.invalidateSize();
    map.setView([latitude, longitude], zoom);
}

function getAirStations() {
    return selectedAirStations;
}
function getTemperatureStations() {
    return selectedTemperatureStations;
}

function setTemperatureStations(result) {
    for(station in result.data) {
        if(!selectedAirStations.includes(result.data[station].id)) {
            selectedTemperatureStations.push(result.data[station].id);
        }
    }
    console.log("temperature stations ", selectedTemperatureStations);
}

