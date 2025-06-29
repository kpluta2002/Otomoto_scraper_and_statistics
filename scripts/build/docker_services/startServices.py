import time

from scripts.shared.services import docker_services
from scripts.utils import EnvUtil as env
from scripts.utils.LoggerUtil import Logger

POSTGRES = env.get_var("POSTGRES_SERVICE_NAME")

log = Logger("startServices")

TIMEOUT = 10
INTERVAL = 0.5


if __name__ == "__main__":
    for container in docker_services:
        elapsed = 0
        if container.exists():
            container.compose_start()
            log.info(f"⏳ Starting {container.name}")
            while elapsed < TIMEOUT:
                if container.is_running():
                    log.info(f"🟢 {container.name} started after {elapsed:.1f} seconds.")
                    break
                time.sleep(INTERVAL)
                elapsed += INTERVAL
            else:
                log.error(
                    f"⏱️ Timed out: {container.name} did not start after {elapsed:.1f} seconds."
                )
        else:
            log.error(f"❌ Could not start service {container.name} because it does not exist!")
