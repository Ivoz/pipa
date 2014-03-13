import time
from random import SystemRandom
from os.path import join
from OpenSSL import crypto


def make_key(bits=2048):
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    return key


def make_csr(key, CN, digest='sha256'):
    request = crypto.X509Req()
    subject = request.get_subject()
    subject.CN = CN

    request.set_pubkey(key)
    request.sign(key, digest)
    return request


def sign_request(request, CA_cert, CA_key, valid_period,
                 serial=None, digest='sha256'):
    serial = SystemRandom().randint(0, 2**32)

    cert = crypto.X509()
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(valid_period)
    cert.set_issuer(CA_cert.get_subject())
    cert.set_subject(request.get_subject())
    cert.set_pubkey(request.get_pubkey())
    cert.sign(CA_key, digest)
    return cert


def gen_certs(host='localhost', dir='.', days=None, save_all=False):

    print('Creating CA...')
    CA_key = make_key()
    CA_request = make_csr(CA_key, 'Generic Pipa Certificate Authority')

    days = days or 365

    period = 60*60*24 * days

    CA_cert = sign_request(CA_request, CA_request, CA_key, period)

    time.sleep(1)

    if save_all:
        print('Writing CA key...')
        with open(join(dir, 'CA.key'), 'wb') as keyfile:
            key = crypto.dump_privatekey(crypto.FILETYPE_PEM, CA_key)
            keyfile.write(key)
        print('Writing CA cert...')
        with open(join(dir, 'CA.crt'), 'wb') as certfile:
            cert = crypto.dump_certificate(crypto.FILETYPE_PEM, CA_cert)
            certfile.write(cert)

    print('Generating server for %s...' % host)

    server_key = make_key()
    server_req = make_csr(server_key, host)
    server_cert = sign_request(server_req, CA_cert, CA_key, period)

    print('Writing Server key...')
    with open(join(dir, 'server.key'), 'wb') as keyfile:
        key = crypto.dump_privatekey(crypto.FILETYPE_PEM, server_key)
        keyfile.write(key)
    if save_all:
        print('Writing Server cert...')
        with open(join(dir, 'server.crt'), 'wb') as certfile:
            cert = crypto.dump_certificate(crypto.FILETYPE_PEM, server_cert)
            certfile.write(cert)

    print('Writing cert bundle...')
    with open(join(dir, 'bundle.pem'), 'wb') as bundle:
        cert = crypto.dump_certificate(crypto.FILETYPE_PEM, server_cert)
        bundle.write(cert)
        cert = crypto.dump_certificate(crypto.FILETYPE_PEM, CA_cert)
        bundle.write(cert)

    print('Done!')
