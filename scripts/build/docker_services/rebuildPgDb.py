import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from scripts.shared.services import pg_url
from scripts.utils import CmdUtil as cmd
from scripts.utils import DockerUtil as docker
from scripts.utils import EnvUtil as env
from scripts.utils.LoggerUtil import Logger

SERVICE_NAME = env.get_var("POSTGRES_SERVICE_NAME")
POSTGRES_CONTAINER = env.get_var("POSTGRES_CONTAINER")
DB_NAME = env.get_var("POSTGRES_DB")
DB_USER = env.get_var("POSTGRES_USER")
DB_PASSWORD = env.get_var("POSTGRES_PASSWORD")
BACKUP_DIR = env.get_var("POSTGRES_BACKUP_DIR")
MAX_BACKUPS = env.get_var("POSTGRES_MAX_BACKUPS", int)
BACKUP_FILE_CONTAINER = "/tmp/backup.sql"
DATA_DIR = os.path.join(os.getcwd(), "data", "postgres")

log = Logger("rebuildPgDb")
pg_container = docker.Container(POSTGRES_CONTAINER)


def get_backup_path(filename: str) -> str:
    """Given a backup filename, return the full host-path under BACKUP_DIR."""
    return os.path.join(BACKUP_DIR, filename)


def remove_data_directory() -> None:
    """Deletes the local PostgreSQL data directory if it exists."""
    if os.path.exists(DATA_DIR):
        log.info(f"🧹 Removing old data directory: {DATA_DIR}")
        shutil.rmtree(DATA_DIR)


def wait_for_postgres(
    container: docker.Container, user: str, db: str, timeout: float = 60, interval: float = 3
) -> None:
    """Poll `pg_isready` until it returns 0 (ready) or timeout is reached."""
    log.info("⏳ Waiting for PostgreSQL to be ready...")
    elapsed = 0.0
    while elapsed < timeout:
        exit_code, stdout, stderr = container.exec_command(["pg_isready", "-U", user, "-d", db])

        if exit_code == 0:
            log.info(f"✅ PostgreSQL ready after {elapsed:.1f} seconds.")
            return

        time.sleep(interval)
        elapsed += interval

    log.error(f"❌ PostgreSQL did not become ready within {timeout} seconds.")
    sys.exit(1)


def list_backups() -> list[str]:
    """Return descending-ordered list of all `.sql` backup filenames."""
    path = Path(BACKUP_DIR)
    if not path.exists():
        return []
    backups = [f.name for f in path.iterdir() if f.suffix == ".sql"]
    backups.sort(reverse=True)
    return backups


def rotate_backups() -> None:
    """Delete oldest backups if more than MAX_BACKUPS exist."""
    backups = list_backups()
    if len(backups) <= MAX_BACKUPS:
        return

    to_delete = backups[MAX_BACKUPS:]
    for old_backup in to_delete:
        full_path = get_backup_path(old_backup)
        log.info(f"🗑️ Removing old backup: {full_path}")
        try:
            os.remove(full_path)
        except OSError as e:
            log.error(f"Failed to delete {full_path}: {e!s}")


def backup_from_container() -> str:
    """Create timestamped dump from Postgres container."""
    os.makedirs(BACKUP_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_filename = f"pgsql-backup-{timestamp}.sql"
    backup_path = get_backup_path(backup_filename)

    # Backup database to container's temporary file
    log.info("🔄 Backing up database inside container...")
    exit_code, stdout, stderr = pg_container.exec_command(
        [
            "pg_dump",
            "--format=custom",
            "--data-only",
            "--compress=9",
            "--no-owner",
            "--no-privileges",
            "-U",
            DB_USER,
            "-d",
            DB_NAME,
            "-f",
            BACKUP_FILE_CONTAINER,
        ]
    )

    if exit_code != 0:
        log.error(f"❌ pg_dump failed with exit code {exit_code}")
        if stderr:
            log.error(f"pg_dump stderr: {stderr}")
        sys.exit(1)

    # Copy backup from container to host
    log.info(f"🧹 Copying backup to host: {backup_path}")
    if not pg_container.copy_from_container(BACKUP_FILE_CONTAINER, backup_path):
        log.error("❌ Failed to copy backup from container")
        sys.exit(1)

    rotate_backups()
    return backup_path


def restore_backup(backup_path: str) -> None:
    """Restore backup into freshly restarted Postgres container."""
    log.info("🧹 Shutting down containers before restore...")
    if not pg_container.compose_down():
        log.error("❌ Failed to shut down PostgreSQL container. Aborting restore.")
        sys.exit(1)

    remove_data_directory()

    log.info("🚀 Starting containers fresh for restore...")
    if not pg_container.compose_up():
        log.error("❌ Failed to start PostgreSQL container. Aborting restore.")
        sys.exit(1)

    wait_for_postgres(pg_container, DB_USER, DB_NAME)

    log.info(f"📥 Copying backup {backup_path} into container...")
    if not pg_container.copy_to_container(backup_path, BACKUP_FILE_CONTAINER):
        log.error("❌ Failed to copy backup to container")
        sys.exit(1)

    log.info("📥 Restoring data from backup inside container...")
    exit_code, stdout, stderr = pg_container.exec_command(
        [
            "pg_restore",
            "--data-only",
            "--disable-triggers",
            "--jobs=4",
            "--exit-on-error",
            "--verbose",
            "-U",
            DB_USER,
            "-d",
            DB_NAME,
            BACKUP_FILE_CONTAINER,
        ]
    )

    if exit_code != 0:
        log.error(f"❌ psql restore failed with exit code {exit_code}")
        if stderr:
            log.error(f"psql stderr: {stderr}")
        sys.exit(1)

    log.info("✅ Restore complete!")

    output_path = "./scripts/shared/Models.py"
    log.info(f"🔧 Generating SQLAlchemy models to '{output_path}' ...")
    if generate_sqlalchemy_models(pg_url, output_path=output_path):
        log.info(f"✅ Models generated successfully: {output_path}")
    else:
        log.error("❌ Failed to generate SQLAlchemy models.")


def generate_sqlalchemy_models(db_url: str, output_path: str) -> bool:
    """Run sqlacodegen against database URL, writing to output_path."""
    parsed = urlparse(db_url)
    safe_url = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}{parsed.path}"
    log.info(f"🔧 Generating models from: {safe_url}")

    cmd_list = ["sqlacodegen", db_url, "--outfile", output_path]

    try:
        log.info(f"⏳ Running command: {' '.join(cmd_list)}")
        process = cmd.subprocess.Popen(
            cmd_list,
            stdout=cmd.subprocess.PIPE,
            stderr=cmd.subprocess.PIPE,
            universal_newlines=True,
        )

        stdout, stderr = process.communicate()

        if stdout:
            log.info(f"sqlacodegen output:\n{stdout}")
        if stderr:
            log.error(f"sqlacodegen errors:\n{stderr}")

        exit_code = process.returncode
        if exit_code == 0:
            return True
        else:
            log.error(f"❌ sqlacodegen failed with exit code: {exit_code}")
            return False

    except FileNotFoundError:
        log.error("❌ `sqlacodegen` not found. Did you `pip install sqlacodegen`?")
        return False
    except Exception as e:
        log.error(f"❌ Unexpected error running sqlacodegen: {e}")
        return False


def main():
    prompt = (
        "\n---------------------------------------------------\n"
        "Select an option:\n"
        "1. Import from existing backup file\n"
        "2. Create backup from running container and restore\n"
        "Enter 1 or 2: "
        "\n---------------------------------------------------"
    )
    log.info(prompt)
    choice = input().strip()

    if choice == "1":
        backups = list_backups()
        if not backups:
            log.warning(f"No backups found in {BACKUP_DIR}")
            sys.exit(1)

        menu = "\n---------------------------------------------------\n"
        menu += "Available backups:\n"
        for idx, fname in enumerate(backups, start=1):
            menu += f"{idx}. {fname}\n"
        menu += f"Choose backup to restore (1-{len(backups)}): "
        menu += "\n---------------------------------------------------"
        log.info(menu)

        sel = input().strip()
        try:
            sel_idx = int(sel) - 1
            if sel_idx < 0 or sel_idx >= len(backups):
                raise ValueError
        except ValueError:
            log.error("❌ Invalid selection.")
            sys.exit(1)

        chosen_file = backups[sel_idx]
        backup_path = get_backup_path(chosen_file)
        restore_backup(backup_path)

    elif choice == "2":
        if not pg_container.is_running():
            log.error(f"❌ Container {POSTGRES_CONTAINER} is not running.")
            sys.exit(1)

        backup_path = backup_from_container()
        restore_backup(backup_path)

    else:
        log.error("❌ Invalid choice. Exiting.")
        sys.exit(1)


if __name__ == "__main__":
    main()
