from scripts.utils import DockerUtil as docker
from scripts.utils import EnvUtil as env

PG_SERVICE_NAME = env.get_var("POSTGRES_SERVICE_NAME")
PG_USER = env.get_var("POSTGRES_USER")
PG_PASSWORD = env.get_var("POSTGRES_PASSWORD")
PG_NAME = env.get_var("POSTGRES_DB")
PG_PORT = env.get_var("POSTGRES_PORT")

MB_SERVICE_NAME = env.get_var("METABASE_SERVICE_NAME")
docker_services = [
    docker.Container(PG_SERVICE_NAME),
    docker.Container(MB_SERVICE_NAME)
]

pg_url = f"postgresql://{PG_USER}:{PG_PASSWORD}@localhost:{PG_PORT}/{PG_NAME}"