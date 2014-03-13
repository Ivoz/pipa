import os
import random
import string
from configparser import ConfigParser
from hashlib import sha256

import cherrypy
from cherrypy import Tool
from cherrypy._cpcompat import ntob
from cherrypy._cpreqbody import Part
from cherrypy.lib import httputil


defaults = """
[pipa]
host = localhost
port = 5351
key = server.key
cert = bundle.pem
salt = fj48fn4kvi548gj56j20f934nvo490dsj3nv
packages = packages

[users]
"""


def user_mod(**args):
    conf = get_config(args['conf_file'])
    if not conf.has_section('users'):
        conf.add_section('users')

    if args['list']:
        for user in conf.options('users'):
            print(user)

    elif args['add']:
        user = args['add'][0]
        password = args['add'][1]
        password = digest(password, conf['pipa'])
        conf.set('users', user, password)
        with open(args['conf_file'], 'w') as c:
            conf.write(c)

    elif args['delete']:
        user = args['delete'][0]
        if conf.has_option('users', user):
            conf.remove_option('users', user)
            with open(args['conf_file'], 'w') as c:
                conf.write(c)
        else:
            print('user "%s" not found in %s' % (user, args['conf_file']))


def do_init(salt=None, packages=None, conf_file=None, no_certs=False):
    print('Generating config...')
    if salt is None:
        letters = string.ascii_letters + string.digits
        salt = ''.join(random.choice(letters) for i in range(32))

    packages = packages or 'packages'
    if not os.path.isdir(packages):
        os.makedirs(packages)

    config = get_config()
    config['pipa']['salt'] = salt
    config['pipa']['packages'] = packages
    with open(conf_file, 'w') as c:
        config.write(c)
    print('Config written!')

    if not no_certs:
        from .certs import gen_certs
        gen_certs()


def get_config(conf_file=None):
    config = ConfigParser()
    config.read_string(defaults)
    if conf_file is not None:
        config.read(conf_file)
    return config


def digest(password, conf=None):

    if conf is None:
        conf = cherrypy.request.app.root.pipa

    password = ntob(password)
    salt = ntob(conf['salt'])
    digest = sha256(b'36'*16).digest()

    for i in range(5000):
        password = sha256(password + digest).digest()
        digest = sha256(digest + password + salt).digest()
    return sha256(salt + digest).hexdigest()


class DistUtilsPart(Part):

    def read_headers(cls, fp):
        headers = httputil.HeaderMap()
        while True:
            line = fp.readline()
            if not line:
                # No more data--illegal end of headers
                raise EOFError("Illegal end of headers.")

            if line == ntob('\n'):
                # Normal end of headers
                break
            # if not line.endswith(ntob('\r\n')):
            #     raise ValueError("MIME requires CRLF terminators: %r" % line)

            if line[0] in ntob(' \t'):
                # It's a continuation line.
                v = line.strip().decode('ISO-8859-1')
            else:
                k, v = line.split(ntob(":"), 1)
                k = k.strip().decode('ISO-8859-1')
                v = v.strip().decode('ISO-8859-1')

            existing = headers.get(k)
            if existing:
                v = ", ".join((existing, v))
            headers[k] = v

        return headers
    read_headers = classmethod(read_headers)


def distutils_form(force=True, debug=False):
    request = cherrypy.serving.request

    def process(entity):
        entity.part_class = DistUtilsPart
        cherrypy._cpreqbody.process_multipart(entity)

        kept_parts = []
        for part in entity.parts:
            if part.name is None:
                kept_parts.append(part)
            else:
                if part.filename is None:
                    # It's a regular field
                    value = part.fullvalue()
                else:
                    # It's a file upload. Retain the whole part so consumer
                    # code has access to its .file and .filename attributes.
                    value = part

                if part.name in entity.params:
                    if not isinstance(entity.params[part.name], list):
                        entity.params[part.name] = [entity.params[part.name]]
                    entity.params[part.name].append(value)
                else:
                    entity.params[part.name] = value

        entity.parts = kept_parts
    request.body.processors['multipart/form-data'] = process

DistutilsUpload = Tool('before_request_body', distutils_form)
