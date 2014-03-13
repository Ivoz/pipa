import hashlib
import os
from collections import namedtuple

import cherrypy
from jinja2 import Environment, PackageLoader

from .util import get_config, digest, DistutilsUpload

Package = namedtuple('Package', ['filename', 'url', 'md5'])
env = Environment(loader=PackageLoader('pipa', 'templates'))

PACKAGE_DIR = 'packages'

PYPI = 'https://pypi.python.org'


def users():
    return dict(cherrypy.request.app.root.users)


class Root:

    # Horrible hack because setup.py upload breaks MIME spec
    cherrypy.tools.distutils = DistutilsUpload

    @cherrypy.expose
    @cherrypy.tools.distutils()
    @cherrypy.tools.basic_auth(realm='pipa', encrypt=digest, users=users)
    def upload(self, **args):
        name = args['name']
        filename = args['content'].filename
        content = args['content'].file
        if store(name, filename, content):
            return "Success"


class Simple:

    @cherrypy.expose
    def default(self, project=None, version=None):
        if project is None:
            return self.simple()
        else:
            return self.package(project, version)

    def simple(self):
        projects = project_index()
        tmpl = env.get_template('simple.html')
        return tmpl.render(projects=projects)

    def package(self, project, version):
        packages = list_project(project)
        tmpl = env.get_template('project.html')
        return tmpl.render(project=project, packages=packages)


def project_index():
    return os.listdir(PACKAGE_DIR)


def list_project(project):
    projects = []
    project_dir = os.path.join(PACKAGE_DIR, project)
    if not os.path.isdir(project_dir):
        return
    for filename in os.listdir(project_dir):
        filepath = os.path.join(project_dir, filename)
        contents = open(filepath, 'rb').read()
        digest = hashlib.md5(contents).hexdigest()
        url = '/%s/%s/%s' % ('packages', project, filename)
        projects.append(Package(filename, url, digest))
    return projects


def store(name, filename, content):
    dirpath = os.path.join(PACKAGE_DIR, name)
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)
    filepath = os.path.join(dirpath, filename)
    with open(filepath, 'wb') as f:
        f.write(content.read())
    return True


def run_server(host=None, port=None, conf_file=None,
               key=None, cert=None, no_ssl=False):

    root = Root()
    root.simple = Simple()
    config = get_config(conf_file)
    root.pipa = config['pipa']
    root.users = config['users']

    # TODO: Don't be this hacky
    global PACKAGE_DIR
    PACKAGE_DIR = root.pipa['packages']

    cherrypy.server.socket_host = host or root.pipa['host']
    cherrypy.server.socket_port = port or root.pipa.getint('port')
    if not no_ssl:
        cherrypy.server.ssl_module = 'builtin'
        cherrypy.server.ssl_private_key = key or root.pipa['key']
        cherrypy.server.ssl_certificate = cert or root.pipa['cert']

    current_dir = os.path.abspath(os.path.curdir)
    app_config = {
        '/': {
            'tools.staticdir.root': current_dir,
        },
        '/packages': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'packages',
            'tools.staticdir.content_types': {
                'whl': 'application/zip',
            }
        },
    }

    cherrypy.tree.mount(root, '', config=app_config)
    # cherrypy.log.screen = False
    print('Starting local pypi server %s/simple/' % cherrypy.server.base())
    cherrypy.engine.start()
    cherrypy.engine.block()
