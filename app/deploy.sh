cd /home/weatherstation/GrapefruitWeather
sudo -H -u weatherstation git pull origin master
cd app
modprobe nfs
modprobe nfsd
docker-compose up --build -d
