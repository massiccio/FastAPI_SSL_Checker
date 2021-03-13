# FastAPI_SSL_Checker
Fast API Python service that checks if the SSL certificate associated to the given URL is valid

## Install required packages and run unit tests
```bash
# Install virtualenv package 
python3 -m pip install --user virtualenv
# Create virtual env
python3 -m venv env
# Activate virtual env
source env/bin/activate
# Install libraries for application
pip install -r conf/requirements.txt
# Install libraries for unit tests
pip install -r conf/requirements_test.txt
# Run unit tests
cd app/
pytest
```

## Run application locally
```bash
# Install required libraries (if not done before)
pip install -r conf/requirements.txt
cd app
python certificate_checker.py
```
The application start is ready to serve requests at http://localhost:5000/check/<url>
Prometheus metrics are exposed at http://172.17.0.1:8000
  
As an example, the query http://localhost:5000/check/google.com returns
```json
{"subject":"Google LLC","issuer":"Google Trust Services","isValid":true}
```

Similarly, the query http://localhost:5000/check/self-signed.badssl.com returns
```json
{"subject":"BadSSL","issuer":"BadSSL","isValid":true}
```


## Create Docker image and start the application in a container
```bash
cd scripts
./service_start.sh
```
The container application is exposed at port 5000

If required, another container running Grafana can be easily started
```bash
docker run --name grafana -p 3000:3000 grafana/grafana
```

## Start Prometheus
```
cd scripts
./prometheus_start.sh
```

The Prometheus web interface can be accessed at http://172.17.0.1:9090.
It is already configured to scrape metrics of type SSL_checks from the application

A Grafana container can be easily started
```bash
docker run --name grafana -p 3000:3000 grafana/grafana
```
