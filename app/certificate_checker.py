from markupsafe import escape
import sys

import prometheus_client as prom

import socket
from OpenSSL import SSL, crypto
from ssl import PROTOCOL_TLSv1_2
from fastapi import FastAPI, HTTPException
import uvicorn
import logging

logging.basicConfig(format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO)

app = FastAPI()

# Prometheus counter
counter = prom.Counter('SSL_checks', 'Invalid SSL certificates found', ['endpoint', 'check', 'self_signed'])

def filter_hostname(host: str):
    """Remove unused characters and split by address and port."""
    host = host.replace('http://', '').replace('https://', '').replace('/', '')
    port = 443
    if ':' in host:
        host, port = host.split(':')

    return host, port

def get_cert(host: str, port: int):
    ''' https://gist.github.com/gdamjan/55a8b9eec6cf7b771f92021d93b87b2c '''
    host, port = filter_hostname(host)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ctx = SSL.Context(SSL.TLSv1_METHOD)
        #ctx = SSL.Context(PROTOCOL_TLSv1_2)
        ctx.set_timeout(2) # 2 seconds timeout
        sock.connect((host, port))
        con = SSL.Connection(ctx, sock)
        con.set_tlsext_host_name(host.encode())
        con.set_connect_state()
        con.do_handshake()
        # type OpenSSL.crypto.X509, see https://www.pyopenssl.org/en/stable/api/crypto.html#x509-objects
        cert = con.get_peer_certificate()
        sock.close()
        return cert
    except Exception as e:
        logging.error('Error while retrieving the certificate %s', str(e))
        return None


def get_cert_info(cert: crypto.X509, host):
        """Get all the information about cert"""
        context = {}
        if not cert:
            return context

        cert_subject = cert.get_subject()

        context['issued_to'] = cert_subject.CN # common name
        context['issued_o'] = cert_subject.O # organization name
        context['issuer_o'] = cert.get_issuer().O
        context['cert_valid'] = False if cert.has_expired() else True
        context['self_signed'] = True if context['issuer_o'] == context['issued_o'] else False

        # Prometheus metrics
        if context['cert_valid']:
            if context['self_signed']:
                counter.labels(endpoint=host, check='valid', self_signed='yes').inc()
            else:
                counter.labels(endpoint=host, check='valid', self_signed='no').inc()
        else:
            counter.labels(endpoint=host, check='not valid', self_signed='n/a').inc()

        return context


def get_context(url: str):
    '''Get the SSL certificate info as JSON'''
    logging.debug('Subpath %s' % url)
    host, port = filter_hostname(url)
    cert = get_cert(host, port)
    context = get_cert_info(cert, host)
    if not context:
        raise HTTPException(status_code=404, detail="Certificate not found")

    return context


@app.get('/check/{url}')
def check_ssl_url(url: str):
    '''Check the SSL certificate of the specified URL'''
    cleaned_input = escape(url.strip())

    logging.debug('Subpath %s' % cleaned_input)
    host, port = filter_hostname(cleaned_input)
    cert = get_cert(host, port)
    context = get_cert_info(cert, host)

    if context:
        return {
            "subject": context['issued_to'],
            "issuer": context['issuer_o'],
            "isValid": context['cert_valid']
        }
    else:
        raise HTTPException(status_code=404, detail="Certificate not found")


if __name__ == '__main__':
    # valid = 'google.com'
    # self_signed = 'self-signed.badssl.com'
    # not_valid = 'expired.badssl.com'

    try:
        # Start the server to expose the metrics.
        prom.start_http_server(8000)
        # Start the application
        uvicorn.run(app, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        sys.exit(1)
    

