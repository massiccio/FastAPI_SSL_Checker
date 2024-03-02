# alpine images fail to install the pyOpenSSL module due to some gcc issue
FROM python:3.13.0a4-slim

COPY conf/requirements.txt /
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r /requirements.txt \
    && apt-get purge -y --auto-remove gcc

COPY app/certificate_checker.py /app/certificate_checker.py

WORKDIR /app
ENTRYPOINT ["python"]
CMD ["certificate_checker.py"]