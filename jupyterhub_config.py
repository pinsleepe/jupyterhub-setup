# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os

c = get_config()

# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.image = 'jupyter/minimal-notebook:77e10160c7ef'
c.DockerSpawner.image_whitelist = {'RServer': 'pinsleepe/rserver_singleuser:v0.5',
                                   'python': 'pinsleepe/python_singleuser:v0.3'}

spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD', "start-singleuser.sh")
c.DockerSpawner.extra_create_kwargs.update({ 'command': spawn_cmd })
# c.DockerSpawner.cmd = ['jupyter-labhub']
c.DockerSpawner.environment = { 'JUPYTER_ENABLE_LAB': 'yes' }


def pre_spawn(spawner):
    if __name__ == '__main__':
        spawner.environment['mynameis'] = spawner.user.name


c.DockerSpawner.pre_spawn_hook = pre_spawn

network_name = os.environ['DOCKER_NETWORK_NAME']
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name
# Pass the network name as argument to spawned containers
c.DockerSpawner.extra_host_config = { 'network_mode': network_name }
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir}
# Remove containers once they are stopped
c.DockerSpawner.remove_containers = True
# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True
# add path to pass to singleuser
c.DockerSpawner.environment.update({'TEST_PATH': '/some/path' })

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = 'jupyterhub'
c.JupyterHub.hub_port = 8080

# TLS config
c.JupyterHub.port = 443
c.JupyterHub.ssl_key = os.environ['SSL_KEY']
c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

# Authenticate users with GitHub OAuth
c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
# c.Authenticator.enable_auth_state = True

# Persist hub data on volume mounted inside container
data_dir = os.environ.get('DATA_VOLUME_CONTAINER', '/data')

c.JupyterHub.cookie_secret_file = os.path.join(data_dir,
    'jupyterhub_cookie_secret')

c.JupyterHub.db_url = 'postgresql://postgres:{password}@{host}/{db}'.format(
    host=os.environ['POSTGRES_HOST'],
    password=os.environ['POSTGRES_PASSWORD'],
    db=os.environ['POSTGRES_DB'],
)

# Whitlelist users and admins
c.Authenticator.whitelist = whitelist = set()
c.Authenticator.admin_users = admin = set()
c.JupyterHub.admin_access = True
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'userlist')) as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        name = parts[0]
        whitelist.add(name)
        if len(parts) > 1 and parts[1] == 'admin':
            admin.add(name)


# class GenericEnvOAuthenticator(GenericOAuthenticator):
#     @gen.coroutine
#     def pre_spawn_start(self, user, spawner):
#
#
#         auth_state = yield user.get_auth_state()
#         self.log.info(">>>>>>>USER = %s", user)
#         self.log.info(">>>>>>>AUTH_STATE = %s", auth_state)
#         if not auth_state:
#             return
#         spawner.environment['ACCESS_TOKEN'] = auth_state['access_token']
#         spawner.environment['REFRESH_TOKEN'] = auth_state['refresh_token']
#
#
#     @gen.coroutine
#     def authenticate(self, handler, data):
#         self.log.info("============ In GenericEnvOAuthenticator.authenticate() ==========")
#         res = yield super().authenticate(handler, data)
#         self.log.info("===== auth.result = %s", res)
#         return res
#
# c.JupyterHub.authenticator_class = GenericEnvOAuthenticator
