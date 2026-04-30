# Run on this host
workon appdaemon
appdaemon -c adconf/

# Run in docker with interactive shell
docker run --name=appdaemon  --rm -it -p 5050:5050 -v ./adconf:/conf   acockburn/appdaemon:latest

# Run in docker as daemon
docker run --name=appdaemon  -d -p 5050:5050 -v ./adconf:/conf   acockburn/appdaemon:latest
