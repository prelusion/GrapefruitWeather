CREATE TABLE countries(
    id SERIAL PRIMARY KEY,
    name VARCHAR(30)
);

CREATE TABLE stations(
    id INT PRIMARY KEY,
    name VARCHAR(100),
    country_id INT REFERENCES countries(id),
    location POINT
);

CREATE TABLE measurements(
    id SERIAL PRIMARY KEY,
    station_id INT REFERENCES stations(id),
    "timestamp" TIMESTAMP,
    temperature SMALLINT,
    dew_point SMALLINT,
    station_air_pressure SMALLINT,
    sea_air_pressure SMALLINT,
    visibility SMALLINT,
    air_speed SMALLINT,
    rain_fall SMALLINT,
    snow_fall SMALLINT,
    is_freezing BOOLEAN,
    is_raining BOOLEAN,
    is_snowing BOOLEAN,
    is_hail BOOLEAN,
    is_thunder BOOLEAN,
    is_strong_wind BOOLEAN,
    cloud_percentage SMALLINT,
    wind_direction SMALLINT
);