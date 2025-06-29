from python_on_whales import DockerClient
from python_on_whales.exceptions import NoSuchContainer

from scripts.utils.LoggerUtil import Logger

client = DockerClient()


class Container:
    def __init__(self, name: str):
        self.name = name
        self._logger = Logger(self.__class__.__name__)

    def exists(self) -> bool:
        """Return True if container exists (any status), False otherwise."""
        try:
            client.container.inspect(self.name)
            return True
        except NoSuchContainer:
            self._logger.debug(f"Container '{self.name}' does not exist.")
            return False
        except Exception as e:
            self._logger.error(f"Error checking existence: {e}")
            return False

    def is_running(self) -> bool:
        """Return True if container exists and is in 'running' state."""
        if not self.exists():
            return False

        try:
            container = client.container.inspect(self.name)
            return container.state.status == "running"
        except Exception as e:
            self._logger.error(f"Error inspecting container: {e}")
            return False

    def compose_up(self) -> bool:
        """Start container using docker compose. Returns True on success."""
        try:
            client.compose.up(detach=True, services=[self.name])
            return True
        except Exception as e:
            self._logger.error(f"Compose up failed: {e}")
            return False

    def compose_start(self) -> bool:
        """Start container using docker compose start. Returns True on success."""
        try:
            client.compose.start(services=[self.name])
            return True
        except Exception as e:
            self._logger.error(f"Compose start failed: {e}")
            return False

    def compose_down(self) -> bool:
        """Stop container using docker compose. Returns True on success."""
        try:
            client.compose.down(services=[self.name])
            return True
        except Exception as e:
            self._logger.error(f"Compose down failed: {e}")
            return False

    def compose_stop(self) -> bool:
        """Stop container using docker compose stop. Returns True on success."""
        try:
            client.compose.stop(services=[self.name])
            return True
        except Exception as e:
            self._logger.error(f"Compose stop failed: {e}")
            return False

    def copy_from_container(self, container_path: str, host_path: str) -> bool:
        """Copy file from container to host. Returns True on success."""
        try:
            client.container.copy((self.name, container_path), host_path)
            return True
        except Exception as e:
            self._logger.error(f"Copy from container failed: {e}")
            return False

    def copy_to_container(self, host_path: str, container_path: str) -> bool:
        """Copy file from host to container. Returns True on success."""
        try:
            client.container.copy(host_path, (self.name, container_path))
            return True
        except Exception as e:
            self._logger.error(f"Copy to container failed: {e}")
            return False

    def exec_command(self, command: list[str]) -> tuple[int, str, str]:
        """Execute command in container. Returns (exit_code, stdout, stderr)."""
        if not self.is_running():
            self._logger.error(f"Container {self.name} is not running")
            return (-1, "", "Container not running")

        try:
            output = client.container.execute(self.name, command, tty=False, interactive=False)
            if isinstance(output, bytes):
                output_str = output.decode("utf-8", errors="replace")
            elif isinstance(output, str):
                output_str = output
            elif output is None:
                output_str = ""
            else:
                try:
                    output_str = "".join(
                        s.decode("utf-8", errors="replace") if isinstance(s, bytes) else str(s)
                        for tup in output
                        for s in tup
                    )
                except Exception:
                    output_str = str(output)
            return (0, output_str, "")
        except Exception as e:
            return (-1, "", str(e))
