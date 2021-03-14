# FastAPI_SSL_Checker
[FastAPI](https://fastapi.tiangolo.com/) Python service that checks if the SSL certificate associated to the given URL is valid.
*Note: FastAPI requires Python 3.6+*

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
 
### Examples
```bash
$curl http://localhost:5000/check/www.google.com
{"subject":"www.google.com","issuer":"Google Trust Services","isValid":true}
$curl http://localhost:5000/check/self-signed.badssl.com 
{"subject":"*.badssl.com","issuer":"BadSSL","isValid":true}
$curl http://localhost:5000/check/expired.badssl.com 
{"subject":"*.badssl.com","issuer":"COMODO CA Limited","isValid":false}
```

[Prometheus](https://prometheus.io/) metrics are exposed at port 8000 via the [Python client](https://github.com/prometheus/client_python)
```bash
$curl -s http://localhost:8000/ |grep SSL_checks_total{
SSL_checks_total{check="valid",endpoint="www.google.com",self_signed="no"} 1.0
SSL_checks_total{check="valid",endpoint="self-signed.badssl.com",self_signed="yes"} 3.0
SSL_checks_total{check="not valid",endpoint="expired.badssl.com",self_signed="n/a"} 2.0
```

## Create Docker image and start the application in a container
```bash
$cd scripts
$./service_start.sh
Building image...
...
Starting container...
INFO:     Started server process [1]
03/14/2021 10:22:38 AM Started server process [1]
INFO:     Waiting for application startup.
03/14/2021 10:22:38 AM Waiting for application startup.
INFO:     Application startup complete.
03/14/2021 10:22:38 AM Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
03/14/2021 10:22:38 AM Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

Note: the application is started on the foreground

## Start Prometheus
```
cd scripts
./prometheus_start.sh
```

The Prometheus web interface can be accessed at http://172.17.0.1:9090.
It is already configured to scrape metrics of type _SSL_checks_ from the application

## Start Grafana

A Grafana container can be easily started with the command
```bash
docker run --name grafana -p 3000:3000 grafana/grafana
```