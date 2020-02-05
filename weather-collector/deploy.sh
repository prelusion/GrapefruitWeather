cd /home/weathercollector/GrapefruitWeather
sudo -H -u weathercollector git pull origin master
cd weather-collector
docker-compose up --build -d